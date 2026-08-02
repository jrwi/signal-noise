from signal_noise_sdk.storage.dynamo_client import DynamoClient, DynamoConfig

config = DynamoConfig()
client = DynamoClient(config)

# create the table
client.create_table()
print("table created")

# insert some triage events
client.put_event(track_id=1, action="SAVE", session_id="session_001")
client.put_event(track_id=1, action="SKIP", session_id="session_001")
client.put_event(track_id=2, action="SAVE", session_id="session_001")
print("events inserted")

# fetch events for track 1
events = client.get_events_for_track(track_id=1)
for event in events:
    print(event)
