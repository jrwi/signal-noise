import pytest

from scripts import ingest_recently_played


def test_malformed_spotify_item_is_rejected():
    malformed_item = {
        "played_at": "2026-08-02T12:00:00Z",
        "track": {"id": "", "name": "Incomplete", "artists": []},
    }

    assert ingest_recently_played.validated_event(malformed_item) is None


def test_http_429_retries_once_then_succeeds(monkeypatch):
    attempts = 0
    waits = []

    def request():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ingest_recently_played.spotipy.SpotifyException(429, -1, "hidden")
        return "success"

    monkeypatch.setattr(ingest_recently_played.time, "sleep", waits.append)

    result = ingest_recently_played.spotify_request_with_retry(request)

    assert result == "success"
    assert attempts == 2
    assert waits == [1]


def test_http_401_does_not_retry(monkeypatch):
    attempts = 0

    def request():
        nonlocal attempts
        attempts += 1
        raise ingest_recently_played.spotipy.SpotifyException(401, -1, "hidden")

    def fail_if_sleep_is_called(_seconds):
        pytest.fail("A nonretryable response must not sleep")

    monkeypatch.setattr(
        ingest_recently_played.time,
        "sleep",
        fail_if_sleep_is_called,
    )

    with pytest.raises(ingest_recently_played.spotipy.SpotifyException):
        ingest_recently_played.spotify_request_with_retry(request)

    assert attempts == 1
