from signal_noise_sdk.storage.postgres_client import PostgresClient, PostgresConfig

config = PostgresConfig()
client = PostgresClient(config)

# fetch the track we inserted earlier
tracks = client.fetch_all("SELECT * FROM tracks")
for track in tracks:
    print(track)

# insert a listening history event
client.execute(
    "INSERT INTO listening_history (track_id, played_at) VALUES (%s, NOW())",
    params=(1,)
)

# fetch it back
history = client.fetch_all("SELECT * FROM listening_history")
for event in history:
    print(event)

client.disconnect()
