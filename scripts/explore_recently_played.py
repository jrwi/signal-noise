"""Read and display a small sample of Spotify listening history."""

import argparse
import os
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth


SCOPE = "user-read-recently-played"
CACHE_PATH = Path(__file__).resolve().parents[1] / ".cache"
REQUIRED_ENVIRONMENT_VARIABLES = (
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
    "SPOTIFY_REDIRECT_URI",
)


def limit_between_1_and_50(value: str) -> int:
    """Convert the command-line limit to an integer accepted by Spotify."""
    try:
        limit = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("--limit must be a whole number from 1 to 50") from error

    if not 1 <= limit <= 50:
        raise argparse.ArgumentTypeError("--limit must be from 1 to 50")
    return limit



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read a small sample of your recently played Spotify tracks."
    )
    # Here we create an argument so that when we run this like:
    # ... python scripts/explore_recently_played.py --limit 10
    parser.add_argument(
        "--limit",
        type=limit_between_1_and_50,
        default=5,
        help="number of plays to request (default: 5; allowed: 1-50)",
    )
    return parser.parse_args()


def spotify_configuration() -> dict[str, str]:
    """Read required Spotify settings without displaying their values."""
    configuration = {
        variable: os.environ.get(variable, "").strip()
        for variable in REQUIRED_ENVIRONMENT_VARIABLES
    }
    missing = [name for name, value in configuration.items() if not value]

    if missing:
        names = ", ".join(missing)
        raise SystemExit(f"Missing required environment configuration: {names}")

    return configuration


def main() -> None:
    args = parse_args()
    configuration = spotify_configuration()

    authentication = SpotifyOAuth(
        client_id=configuration["SPOTIFY_CLIENT_ID"],
        client_secret=configuration["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=configuration["SPOTIFY_REDIRECT_URI"],
        scope=SCOPE,
        cache_path=str(CACHE_PATH),
    )
    spotify = spotipy.Spotify(auth_manager=authentication)

    try:
        response = spotify.current_user_recently_played(limit=args.limit)
    except spotipy.SpotifyException as error:
        status = error.http_status or "unknown"
        raise SystemExit(f"Spotify request failed with HTTP status {status}.") from None

    items = response.get("items", [])
    if not items:
        print("No recently played tracks returned.")
        return

    for item in items:
        track = item.get("track", {})
        artists = ", ".join(
            artist.get("name", "") for artist in track.get("artists", [])
        )
        print(
            f"played_at={item.get('played_at', '')} | "
            f"track_id={track.get('id', '')} | "
            f"name={track.get('name', '')} | "
            f"artists={artists}"
        )


if __name__ == "__main__":
    main()
