import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from pydantic import BaseModel
from signal_noise_sdk.models.track import Track

load_dotenv()


class SpotifyConfig(BaseModel):
    client_id: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    client_secret: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    redirect_uri: str = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
    scope: str = "user-read-recently-played user-library-modify"


class SpotifyClient:
    def __init__(self, config: SpotifyConfig):
        self.config = config
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config.client_id,
            client_secret=config.client_secret,
            redirect_uri=config.redirect_uri,
            scope=config.scope
        ))

    def get_recently_played(self, limit=50):
        results = self.sp.current_user_recently_played(limit=limit)
        tracks = []
        for item in results["items"]:
            t = item["track"]
            track = Track(
                title=t["name"],
                artist=t["artists"][0]["name"],
                duration_ms=t["duration_ms"],
                source="spotify"
            )
            tracks.append((track, item["played_at"]))
        return tracks
