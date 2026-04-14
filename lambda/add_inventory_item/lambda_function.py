import json
import boto3
import uuid
from decimal import Decimal

def lambda_handler(event, context):
    # Parse incoming JSON data
    try:
        data = json.loads(event['body'])
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps("Invalid or missing request body")
        }

    # Validate required fields
    required_fields = ['name', 'description', 'qty', 'price', 'location_id']
    for field in required_fields:
        if field not in data:
            return {
                'statusCode': 400,
                'body': json.dumps(f"Missing field: {field}")
            }

    # DynamoDB setup
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')

    # Generate ULID
    unique_id = str(uuid.uuid4())

    # Insert data into DynamoDB
    try:
        table.put_item(
            Item={
                'item_id': unique_id,
                'name': data['name'],
                'description': data['description'],
                'qty': int(data['qty']),
                'price': Decimal(str(data['price'])),
                'location_id': int(data['location_id'])
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "Item added successfully",
                "item_id": unique_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error adding item: {str(e)}")
        }