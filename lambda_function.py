import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
TABLE = "CropEvents"
BUCKET = "crop-surveillance-logs-balazs"

def lambda_handler(event, context):
    print("RAW EVENT:", json.dumps(event))
    try:
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", {})

        print("PARSED BODY:", body)
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        table = dynamodb.Table(TABLE)
        table.put_item(Item={
            "event_id": event_id,
            "timestamp": timestamp,
            "edge_node": body.get("edge_node"),
            "device_id": body.get("device_id"),
            "parameter": body.get("parameter"),
            "value": body.get("value")
        })

        log_line = json.dumps({
            "event_id": event_id,
            "timestamp": timestamp,
            "data": body
        })

        s3.put_object(
            Bucket=BUCKET,
            Key=f"logs/{event_id}.json",
            Body=log_line.encode("utf-8")
        )

        print("SUCCESS:", event_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"saved": True, "event_id": event_id})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }