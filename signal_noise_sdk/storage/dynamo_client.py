import boto3
from pydantic import BaseModel
from datetime import datetime


class DynamoConfig(BaseModel):
    endpoint_url: str = "http://localhost:8000"
    region: str = "us-east-1"
    aws_access_key_id: str = "fake"
    aws_secret_access_key: str = "fake"
    table_name: str = "triage_events"


class DynamoClient:
    def __init__(self, config: DynamoConfig):
        self.config = config
        self.client = boto3.resource(
            "dynamodb",
            endpoint_url=config.endpoint_url,
            region_name=config.region,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key
        )
        self.table = self.client.Table(config.table_name)

    def create_table(self):
        table = self.client.create_table(
            TableName=self.config.table_name,
            KeySchema=[
                {"AttributeName": "track_id", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "track_id", "AttributeType": "N"},
                {"AttributeName": "timestamp", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        table.wait_until_exists()
        return table

    def put_event(self, track_id, action, session_id):
        self.table.put_item(Item={
            "track_id": track_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "session_id": session_id
        })

    def get_events_for_track(self, track_id):
        response = self.table.query(
            KeyConditionExpression="track_id = :tid",
            ExpressionAttributeValues={":tid": track_id}
        )
        return response["Items"]
