import json
import boto3
import os
import base64
import re


AWS_ACCESS_ID = os.environ["AWS_ACCESS_ID"]
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]

class CraftPath:
    _name = ""
    _profession = ""
    _start_level = 0
    _current_level = 0
    _target_level = 0
    _recipes_to_make = []
    _ingredients_to_collect = []
    _client = None

    def __init__(self,name, prof, start, finish):
        self._name = name
        self._profession = prof
        self._start_level = start
        self._target_level = finish
        self._client = boto3.Session(AWS_ACCESS_ID, AWS_ACCESS_KEY, region_name="ap-southeast-2").client("dynamodb")
       
    def init_client(self):
         self._client = boto3.Session(AWS_ACCESS_ID, AWS_ACCESS_KEY, region_name="ap-southeast-2").client("dynamodb")

    def get_profession(self):
        return self._profession

    def get_start(self):
        return self._start_level

    def get_current(self):
        return self._current_level

    def get_target(self):
        return self._target_level

    def get_recipes(self):
        return self._recipes_to_make

    def add_to_recipes(self,recipes):
        for r in recipes:
            self._recipes_to_make.append(r)
        return self._recipes_to_make

    def get_ingredients(self):
        return self._ingredients_to_collect

    def add_to_ingredients(self, ingredients):
        for i in ingredients:
            self._ingredients_to_collect.append(i)
        return self._ingredients_to_collect

    def get_client(self):
        return self._client

    def get_exp_to_next(self):
        #look up exp to next level
        with open('db_exp.json') as f:
            contents = json.load(f)["crafting"][self.get_profession()]
        cur = self.get_current()
        for e in contents:
            if e["lvl"] == cur:
                required_exp = e["xp"] #sets you at the very start of that level
                break
        return required_exp

    def query_recipes(self):
        #perform lookup for all recipes currently available
        #Returns array of serialised recipe DDB entries
        client = self.get_client()
        recipes = client.query(
            TableName="CraftingRecipes",
            KeyConditionExpression='tradeskill = :tradeskill',
            FilterExpression="recipelevel <= :recipelevel",
            ExpressionAttributeValues = {
                ':tradeskill': {'S': self.get_profession()},
                ':recipelevel' : {'N' : str(self.get_current())}
            }
        )
        return recipes['Items']

    def decode_ingredients(self,recipes):
        #ingredients list
        candidate_ingredients = []
        #Loop through the list of recipes and extract a mapping of ingredients with a total experience gain per recipe
        for e in recipes:
            print(e)
            try:
                num_ingredients = 0
                exp_gain = 0
                ing_list = []
                print((base64.b64decode(e["ingredients"]["B"])).decode('utf-8').replace('\'','\"'))
                ingredients = json.loads((base64.b64decode(e["ingredients"]["B"])).decode('utf-8').replace('\'','\"'))
                for e in ingredients:
                    num_ingredients += e["quantity"]
                    if e["type"] == "item":
                        ing_list.append({"quantity":e["quantity"], "choices": e["name"]})
                    elif e["type"] == "category":
                        ing_list.append({"quantity":e["quantity"], "choices": [f["name"] for f in e["subingredients"]]})
                if "CategoricalProgressionReward" in e["event"].keys():
                    exp_gain += (e["event"]["CategoricalProgressionReward"]*num_ingredients)
                candidate_ingredients.append({"name":e["name"], "ingredients":ing_list,"exp_gain": exp_gain} )
                return candidate_ingredients
            except KeyError as e:
                print(e)
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")

    def traverse_recipes(self):
        #for e in self.get_recipes():
        return
    '''
    Cost definition:
        Cost = ((Tier+Rarity) * Quantity) * Scarcity

        Scarcity is the opinionated component of this. Base scarcity is 1 for a flat value.
        Raw materials such as stone, flint, wood, are all base level scarcity as they are easy to obtain.
        
        Harder to obtain materials such as ingots have scarcity > 1.
        Rarer materials again such as motes have increasingly high scarcity.

    '''
    def optimise_cost(self, recipe_map):
        tier_re = 't\d'
        #Loop through the map and compute the lowest cost of crafting
        recipe_cost = []
        for recipe in recipe_map:
            choice_cost = []
            for ingredients in recipe["ingredients"]:
                #TODO: Create DDB tables with weights - https:///projects/NWB/issues/NWB-1O actual weights to be added to dynamodb tables for each item.
                #in the meantime manually weight stone, flint and wood tier as 1 and the rest as 2.
                for ing in ingredients:
                    choices = ing["choices"]
                    #TODO once DDB tables with weights have been established, consider implementing logic that looks at contents of itemClass member in json blob
                    #TODO add tiebreakers based on item weight
                    for choice in choices:
                        choice["tier"] = int(re.search(tier_re,choice["id"]))[-1]
                        if ["stone", "flint", "wood"] in choice["name"].lower():
                            choice_cost.append({"item":choice["name"], "quantity":choice["quantity"], "cost":((choice["tier"]+choice["rarity"])*choice["quantity"])*1})
                            break
                        else:
                            choice_cost.append({"item":choice["name"], "quantity":choice["quantity"], "cost":((choice["tier"]+choice["rarity"])*choice["quantity"])*2})
                            break
            
            recipe_cost.append({"name": recipe["name"], "ingredients":choice_cost})
        return recipe_cost


if __name__ == "__main__":
    path = CraftPath("lime","Arcana","0","50")
    print("Raw return value:")
    print(path.query_recipes())
    print("Decoded value:")
    print(str(path.decode_ingredients(path.query_recipes())))

