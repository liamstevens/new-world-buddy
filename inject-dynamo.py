import boto3
import json
import os
import base64

AWS_ACCESS_ID = os.environ["AWS_ACCESS_ID"]
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]

client = boto3.Session(AWS_ACCESS_ID, AWS_ACCESS_KEY,region_name="ap-southeast-2")

def load_json(file):
    with open(file) as f:
        contents = json.load(f)["data"]
    return contents


def upload_recipe(json):
    response = client.put_item(
        TableName='CraftingRecipes',
        Item={
            'tradeskill' : json["tradeskill"],
            'recipelevel' : json["recipelevel"],
            'ingredients' : base64.base64.b64encode(json["ingredients"]),
            'name' : json["id"]
        }
    )
    return response



if __name__ == "__main__":
    print(load_json("./nwdb.info/db/recipe/Woodworker_ClothWeaveT3.json"))