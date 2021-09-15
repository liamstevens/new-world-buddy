import boto3

def lambda_handler(event, context):
    event = event["queryStringParameters"]
    client = boto3.client("dynamodb")
    client.put_item(
        TableName='WarRoster',
        Item={
            "UserName": {
                "S": event["username"]
            },
            "Level": {
                "N": int(event["level"])
            },
            "Weapon1": {
                "S": event["weapon1"]
            },
            "Weapon2": {
                "S": event["weapon2"]
            },
            "Role": {
                "S": event["role"]
            }
        }
    )