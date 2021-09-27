import boto3
import json


def lambda_handler(event, context):
    client = boto3.client("dynamodb")

    items = client.scan(
        TableName='WarRoster'
    )['Items']
    #roster = []
    #for e in items:
    #   roster.append({'name':e[''],'level':} 


    return {
        'statusCode': 200,
        'body' : json.dumps(items)
    }