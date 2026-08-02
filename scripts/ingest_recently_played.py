"""Fetch recent Spotify plays and store valid events in PostgreSQL."""

import argparse
import os
import time
from datetime import datetime
from pathlib import Path

import psycopg2
import requests
import spotipy
from spotipy.exceptions import SpotifyOauthError
from spotipy.oauth2 import SpotifyOAuth


SCOPE = "user-read-recently-played"
CACHE_PATH = Path(__file__).resolve().parents[1] / ".cache"
REQUIRED_ENVIRONMENT_VARIABLES = (
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
    "SPOTIFY_REDIRECT_URI",
    "DATABASE_URL",
)
INSERT_EVENT_SQL = """
    INSERT INTO listening_events (
        spotify_track_id,
        track_title,
        artist,
        played_at
    )
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (spotify_track_id, played_at) DO NOTHING
    RETURNING id
"""
CHECKPOINT_SQL = "SELECT MAX(played_at) FROM listening_events"
MAX_SPOTIFY_ATTEMPTS = 3


def limit_between_1_and_50(value: str) -> int:
    """Convert the command-line limit to an integer accepted by Spotify."""
    try:
        limit = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "--limit must be a whole number from 1 to 50"
        ) from error

    if not 1 <= limit <= 50:
        raise argparse.ArgumentTypeError("--limit must be from 1 to 50")
    return limit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Store a small batch of recently played Spotify tracks."
    )
    parser.add_argument(
        "--limit",
        type=limit_between_1_and_50,
        default=5,
        help="plays per Spotify page (default: 5; allowed: 1-50)",
    )
    return parser.parse_args()


def configuration_from_environment() -> dict[str, str]:
    """Read required settings without displaying their values."""
    configuration = {
        variable: os.environ.get(variable, "").strip()
        for variable in REQUIRED_ENVIRONMENT_VARIABLES
    }
    missing = [name for name, value in configuration.items() if not value]

    if missing:
        names = ", ".join(missing)
        raise SystemExit(f"Missing required environment configuration: {names}")

    return configuration


def validated_event(item: dict) -> tuple[str, str, str, datetime] | None:
    """Return database values for a complete event, or reject the item."""
    if not isinstance(item, dict):
        return None

    track = item.get("track") or {}
    if not isinstance(track, dict):
        return None

    track_id = str(track.get("id") or "").strip()
    track_title = str(track.get("name") or "").strip()
    artists = track.get("artists") or []
    if not isinstance(artists, list):
        return None

    artist_names = []
    for artist in artists:
        if not isinstance(artist, dict):
            continue
        artist_name = str(artist.get("name") or "").strip()
        if artist_name:
            artist_names.append(artist_name)
    played_at_value = item.get("played_at")

    if not track_id or not track_title or not artist_names:
        return None
    if not isinstance(played_at_value, str):
        return None

    try:
        played_at = datetime.fromisoformat(played_at_value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if played_at.tzinfo is None or played_at.utcoffset() is None:
        return None

    return track_id, track_title, ", ".join(artist_names), played_at


def read_checkpoint(database_url: str) -> datetime | None:
    """Read the latest stored playback time using a short read-only connection."""
    connection = None

    try:
        connection = psycopg2.connect(database_url)
        connection.set_session(readonly=True, autocommit=True)
        with connection.cursor() as cursor:
            cursor.execute(CHECKPOINT_SQL)
            row = cursor.fetchone()
            return row[0]
    except psycopg2.Error:
        raise SystemExit("Database checkpoint read failed.") from None
    finally:
        if connection is not None:
            connection.close()


def checkpoint_as_spotify_after(checkpoint: datetime | None) -> int | None:
    """Convert a checkpoint to epoch milliseconds with a one-ms overlap."""
    if checkpoint is None:
        return None
    if checkpoint.tzinfo is None or checkpoint.utcoffset() is None:
        raise SystemExit("Database checkpoint is missing timezone information.")

    checkpoint_milliseconds = int(checkpoint.timestamp() * 1000)
    return max(0, checkpoint_milliseconds - 1)


def spotify_request_with_retry(request):
    """Run one Spotify request with bounded retries for temporary failures."""
    for attempt in range(1, MAX_SPOTIFY_ATTEMPTS + 1):
        try:
            return request()
        except spotipy.SpotifyException as error:
            status = error.http_status
            retryable = status == 429 or (status is not None and 500 <= status <= 599)
            if not retryable or attempt == MAX_SPOTIFY_ATTEMPTS:
                raise
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt == MAX_SPOTIFY_ATTEMPTS:
                raise

        wait_seconds = 2 ** (attempt - 1)
        print(
            f"spotify_retry next_attempt={attempt + 1}/{MAX_SPOTIFY_ATTEMPTS} "
            f"wait_seconds={wait_seconds}"
        )
        time.sleep(wait_seconds)


def fetch_recently_played(
    configuration: dict[str, str], limit: int, after: int | None
) -> list[dict]:
    """Authorize with Spotify and collect every server-provided page."""
    try:
        authentication = SpotifyOAuth(
            client_id=configuration["SPOTIFY_CLIENT_ID"],
            client_secret=configuration["SPOTIFY_CLIENT_SECRET"],
            redirect_uri=configuration["SPOTIFY_REDIRECT_URI"],
            scope=SCOPE,
            cache_path=str(CACHE_PATH),
        )
        spotify = spotipy.Spotify(
            auth_manager=authentication,
            retries=0,
            status_retries=0,
        )
        if after is None:
            response = spotify_request_with_retry(
                lambda: spotify.current_user_recently_played(limit=limit)
            )
        else:
            response = spotify_request_with_retry(
                lambda: spotify.current_user_recently_played(limit=limit, after=after)
            )

        items = []
        while True:
            items.extend(response.get("items", []))
            if not response.get("next"):
                break
            response = spotify_request_with_retry(lambda: spotify.next(response))
    except SpotifyOauthError:
        raise SystemExit("Spotify authorization failed.") from None
    except spotipy.SpotifyException as error:
        status = error.http_status or "unknown"
        raise SystemExit(f"Spotify request failed with HTTP status {status}.") from None
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise SystemExit("Spotify request failed after temporary network errors.") from None

    return items


def insert_events(database_url: str, events: list[tuple[str, str, str, datetime]]) -> int:
    """Insert the complete batch in one transaction and return its new-row count."""
    connection = None
    inserted = 0

    try:
        connection = psycopg2.connect(database_url)
        with connection:
            with connection.cursor() as cursor:
                for event in events:
                    cursor.execute(INSERT_EVENT_SQL, event)
                    if cursor.fetchone() is not None:
                        inserted += 1
    except psycopg2.Error:
        raise SystemExit("Database ingestion failed; the transaction was rolled back.") from None
    finally:
        if connection is not None:
            connection.close()

    return inserted


def main() -> None:
    args = parse_args()
    configuration = configuration_from_environment()
    checkpoint = read_checkpoint(configuration["DATABASE_URL"])
    after = checkpoint_as_spotify_after(checkpoint)
    items = fetch_recently_played(configuration, args.limit, after)

    events = []
    rejected = 0
    for item in items:
        event = validated_event(item)
        if event is None:
            rejected += 1
        else:
            events.append(event)

    inserted = insert_events(configuration["DATABASE_URL"], events)
    duplicates_skipped = len(events) - inserted

    print(f"mode={'initial' if checkpoint is None else 'incremental'}")
    print(f"fetched={len(items)}")
    print(f"inserted={inserted}")
    print(f"duplicates_skipped={duplicates_skipped}")
    print(f"rejected={rejected}")


if __name__ == "__main__":
    main()
