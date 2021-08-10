import json
import boto3
import os

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

    def __init__(self,name, prof, start, finish):
        _name = name
        _profession = prof
        _start_level = start
        _target_level = finish
        _client = boto3.Session(AWS_ACCESS_ID, AWS_ACCESS_KEY, "ap-southeast-2").client("dynamodb")

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
            KeyConditionExpression='tradeskill = :tradeskill AND recipelevel >= :recipelevel',
            ExpressionAttributeValues = {
                ':tradeskill': {'S': self.get_profession()},
                ':recipelevel' : {'N' : self.get_current()}
            }
        )
        return recipes['Items']


    def traverse_recipes(self):
        #for e in self.get_recipes():
        return