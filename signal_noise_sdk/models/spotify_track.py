from pydantic import field_validator
from .track import Track

class SpotifyTrack(Track):
    spotify_id: str
    preview_url: str = None

    def __repr__(self):
        return f"SpotifyTrack(title={self.title!r}, artist={self.artist!r}, spotify_id={self.spotify_id!r})"

    def describe(self):
        seconds = self.duration_seconds()
        print(f"{self.title} by {self.artist} ({seconds:.1f}s) - spotify_id: {self.spotify_id}")



# class SpotifyTrack(Track):
#     def __init__(self, title, artist, duration_ms, spotify_id, preview_url = None):
#         super().__init__(title, artist, duration_ms)
#         self.spotify_id = spotify_id
#         self.preview_url = preview_url
#         self.source = "spotify"

#     def __repr__(self):
#         return f"SpotifyTrack(title={self.title!r}, artist={self.artist!r}, duration_ms={self.duration_ms}, spotify_id={self.spotify_id!r})"


# super().__init__() means run the parent's class's init first
# then add extra stuff
# so now instances of the SpotifyTrack class have all the Track properties and also have spotify_id and preview_url property.
# instances of just the Track class dont have spotify_ids


