from signal_noise_sdk.models.track import Track
from signal_noise_sdk.models.spotify_track import SpotifyTrack

# normal creation
song = Track(title="Alright", artist="Kendrick Lamar", duration_ms=234000)
print(song)
song.describe()

# alternative constructor
spotify_song = Track.from_spotify("Money Trees", "Kendrick Lamar", 386000)
spotify_song.describe()

# test validation — this should fail
# bad_song = Track(title="Bad", artist="Test", duration_ms=-1000)
# print(bad_song)

spotify = SpotifyTrack(
    title="Alright",
    artist="Kendrick Lamar",
    duration_ms=234000,
    spotify_id="6KPhPTBEsBhMHsJkEkJ4BJ"
)
spotify.describe()
print(spotify)
