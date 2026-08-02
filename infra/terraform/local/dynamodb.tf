resource "aws_dynamodb_table" "triage_events" {
  name         = "triage_events"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "track_id"
  range_key    = "timestamp"

  attribute {
    name = "track_id"
    type = "N"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = {
    Project     = "signal-noise"
    Environment = "local"
  }
}
