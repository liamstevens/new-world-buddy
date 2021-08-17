import boto3
import json
import os
import base64

AWS_ACCESS_ID = os.environ["AWS_ACCESS_ID"]
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]

client = boto3.Session(AWS_ACCESS_ID, AWS_ACCESS_KEY,region_name="ap-southeast-2").client("dynamodb")

def load_json(file):
    with open(file) as f:
        contents = json.load(f)["data"]
    return contents


def upload_recipe(json_obj):
    #json_obj = json.loads(json_obj)
    response = client.put_item(
        TableName='CraftingRecipes',
        Item={
            'tradeskill' : {"S": json_obj["tradeskill"]},
            'recipelevel' : {"N": str(json_obj["recipeLevel"])},
            'ingredients' : {"B": base64.b64encode(bytes(str(json_obj["ingredients"]),'utf-8'))},
            'name' : {"S": json_obj["id"]}
        }
    )
    return response

def upload_all_recipe(path):
    for e in os.listdir(path):
        if e.endswith(".json"):
            upload_recipe(load_json(path+'/'+e))



if __name__ == "__main__":
    #print(load_json("./nwdb.info/db/recipe/Woodworker_ClothWeaveT3.json"))
    #upload_recipe(load_json("./nwdb.info/db/recipe/Woodworker_ClothWeaveT3.json"))
    upload_all_recipe('/Users/ljs/Projects/new-world-buddy/nwdb.info/db/recipe')