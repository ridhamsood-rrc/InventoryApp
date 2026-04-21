import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


# Helper function to convert Decimal to float
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
    try:
        print(event)
        item_id = event["pathParameters"]["id"]
    except Exception:
        return {"statusCode": 400, "body": json.dumps("Missing item_id")}

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("Inventory")

    try:
        response = table.query(KeyConditionExpression=Key("item_id").eq(item_id))

        items = response.get("Items", [])

        if not items:
            return {"statusCode": 404, "body": json.dumps("Item not found")}

        # Convert Decimal values
        clean_item = convert_decimal(items[0])

        return {"statusCode": 200, "body": json.dumps(clean_item)}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(str(e))}
