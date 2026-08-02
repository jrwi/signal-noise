from signal_noise_sdk.ingestion.spotify_client import SpotifyClient, SpotifyConfig

config = SpotifyConfig()
client = SpotifyClient(config)

tracks = client.get_recently_played(limit=10)
for track, played_at in tracks:
    print(f"{played_at} — {track.title} by {track.artist}")
