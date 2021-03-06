import boto3
import json
def lambda_handler(event, context):
    event = event["queryStringParameters"]
    client = boto3.client("dynamodb")
    client.put_item(
        TableName='WarRoster',
        Item={
            "username": {
                "S": event["username"]
            },
            "level": {
                "N": (event["level"])
            },
            "weapon1": {
                "S": event["weapon1"]
            },
            "weapon2": {
                "S": event["weapon2"]
            },
            "role": {
                "S": event["role"]
            }
        }
    )
    return {
        'statusCode': 200,
        'body' : json.dumps({
            "status": "OK"})
    }