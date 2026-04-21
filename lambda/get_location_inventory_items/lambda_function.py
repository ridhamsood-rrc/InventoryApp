import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


# Convert Decimal to JSON-safe types
def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


def lambda_handler(event, context):

    # Get location_id from path
    try:
        location_id = int(event["pathParameters"]["id"])
    except Exception:
        return {"statusCode": 400, "body": json.dumps("Invalid or missing location_id")}

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("Inventory")

    try:
        response = table.query(
            IndexName="GSI_SK_PK",
            KeyConditionExpression=Key("location_id").eq(location_id),
        )

        items = response.get("Items", [])

        # Convert Decimal safely
        clean_items = convert_decimal(items)

        return {"statusCode": 200, "body": json.dumps(clean_items)}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(str(e))}
