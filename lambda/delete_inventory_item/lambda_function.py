import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


# Convert DynamoDB Decimal to JSON-safe types
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

    # Safe path parameter extraction
    path_params = event.get("pathParameters") or {}
    item_id = path_params.get("id")

    if not item_id:
        return {"statusCode": 400, "body": json.dumps("Missing item_id")}

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("Inventory")

    try:
        # Find item using query
        response = table.query(KeyConditionExpression=Key("item_id").eq(item_id))

        items = response.get("Items", [])

        if not items:
            return {"statusCode": 404, "body": json.dumps("Item not found")}

        item = items[0]

        # Delete using BOTH keys
        table.delete_item(
            Key={"item_id": item["item_id"], "location_id": item["location_id"]}
        )

        # Convert Decimal values before returning
        clean_item = convert_decimal(item)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": f"Item {item_id} deleted successfully",
                    "deleted_item": clean_item,
                }
            ),
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(str(e))}
