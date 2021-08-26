import json
import boto3
import os
import base64
import re
import math

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
        self._start_level = int(start)
        self._current_level = self._start_level
        self._target_level = int(finish)
        self._client = boto3.client("dynamodb")
       
    def init_client(self):
        #init client using inbuild lambda credentials
        self._client = boto3.client("dynamodb")

    def get_profession(self):
        return self._profession

    def get_start(self):
        return self._start_level

    def get_current(self):
        return self._current_level

    def incr_current(self):
        self._current_level += 1

    def get_target(self):
        return self._target_level

    def get_recipes(self):
        return self._recipes_to_make

    def __str__(self):
        return f"CraftPath object.\n Name:{self._name}. \nStartLevel:{self._start_level}. \nCurrentLevel:{self._current_level}. \nTargetLevel:{self._target_level}. \nProfession:{self._profession}.\n"

    def add_to_recipes(self,recipe):
        if len(self._recipes_to_make) == 0:
            self._recipes_to_make.append(recipe)
        else:
            newrecipe=True
            for r in self._recipes_to_make:
                if r['name'] == recipe['name']:
                    r['quantity']+=recipe['quantity']
                    newrecipe=False
            if newrecipe:
                self._recipes_to_make.append(recipe)
        return self._recipes_to_make

    def get_ingredients(self):
        return self._ingredients_to_collect

    def add_to_ingredients(self, ingredients):
        if len(self._ingredients_to_collect) == 0:
            self._ingredients_to_collect+=ingredients
        else:
            for i in ingredients:
                newitem=True
                for j in self._ingredients_to_collect:
                    if i['item'] == j['item']:
                        j['quantity']+=i['quantity']
                        newitem=False
                        break
                if newitem:
                    self._ingredients_to_collect.append(i)           
        return self._ingredients_to_collect

    def get_client(self):
        return self._client

    def get_exp_to_next(self):
        #look up exp to next level
        cur = self.get_current() 
        client = self.get_client()
        recipes = client.query(
            TableName="CraftingRecipes",
            KeyConditionExpression='tradeskill = :tradeskill',
            FilterExpression="itemtype = :itemtype",
            ExpressionAttributeValues = {
                ':tradeskill': {'S': self.get_profession().lower()},
                ':itemtype' : {'S' : "exp_map"}
            }
        )
        event = json.loads((base64.b64decode(recipes["Items"][0]["value"]['S']).decode('utf-8')))
        for e in event[self.get_profession().lower()]:
            if e['lvl'] == cur:
                required_exp = e['xp'] #sets you at the very start of that level
                break  
        return required_exp

    def query_recipes(self):
        #perform lookup for all recipes currently available
        #Returns array of serialised recipe DDB entries
        #items = []
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
        return recipes["Items"]

    def decode_ingredients(self,recipes):
        #ingredients list
        candidate_ingredients = []
        #Loop through the list of recipes and extract a mapping of ingredients with a total experience gain per recipe
        for e in recipes:
            try:
                num_ingredients = 0
                exp_gain = 0
                ing_list = []
                ingredients = json.loads((base64.b64decode(e["ingredients"]["B"])).decode('utf-8').replace('\'','\"'))
                event = json.loads((base64.b64decode(e["event"]["B"])).decode('utf-8').replace('\'','\"'))
                for ing in ingredients:
                    num_ingredients += ing["quantity"]
                    if ing["type"] == "item":
                        ing_list.append({"quantity":ing["quantity"], "choices": ing["name"]})
                    elif ing["type"] == "category":
                        ing_list.append({"quantity":ing["quantity"], "choices": [f for f in ing["subIngredients"]]})
                if "CategoricalProgressionReward" in event.keys():
                    exp_gain += (event["CategoricalProgressionReward"]*num_ingredients)
                candidate_ingredients.append({"name":e["name"], "ingredients":ing_list,"exp_gain": exp_gain} )
            except KeyError as exc:
                
                continue
            except Exception as exc:
               
                continue

        return candidate_ingredients

    '''
    Cost definition:
        Cost = ((Tier+Rarity) * Quantity) * Scarcity

        Scarcity is the opinionated component of this. Base scarcity is 1 for a flat value.
        Raw materials such as stone, flint, wood, are all base level scarcity as they are easy to obtain.
        
        Harder to obtain materials such as ingots have scarcity > 1.
        Rarer materials again such as motes have increasingly high scarcity.

    '''
    def determine_cost(self, recipe_map):
        tier_re = 't\d'
        #Loop through the map and compute the cost of crafting
        recipe_cost = []
        for recipe in recipe_map:
            recipe["weighted_ings"] = []

            for ing in recipe["ingredients"]:
                choice_cost = []
                #TODO: Create DDB tables with weights - https:///projects/NWB/issues/NWB-1O actual weights to be added to dynamodb tables for each item.
                #in the meantime manually weight stone, flint and wood tier as 1 and the rest as 2.
                choices = ing["choices"]
                #TODO once DDB tables with weights have been established, consider implementing logic that looks at contents of itemClass member in json blob
                #TODO add tiebreakers based on item weight
                for choice in choices:
                    if type(choices) == str:
                        if any(res in choices.lower() for res in ["stone", "flint", "wood", "water"]):
                            if "mote" not in choices.lower():
                                choice_cost.append({"item":choices, "quantity":ing['quantity'], "cost":((1+1)*ing["quantity"])*1})
                                
                        else:
                            #Choice is likely a quest item or raw material, skip this recipe.
                            break
                    else:
                        try:
                            choice["tier"] = int(re.search(tier_re,choice["id"]).group(0)[-1])
                            if any(res in choice["name"].lower() for res in ["stone", "flint", "wood", "water"]):
                                choice_cost.append({"item":choice["name"], "quantity":choice["quantity"], "cost":((choice["tier"]+choice["rarity"])*choice["quantity"])*1})
                            else:
                                choice_cost.append({"item":choice["name"], "quantity":choice["quantity"], "cost":((choice["tier"]+choice["rarity"])*choice["quantity"])*2})
                        except Exception as e:
                            continue
                recipe["weighted_ings"].append(choice_cost)            
            recipe_cost.append({"name": recipe["name"], "ingredients":recipe["weighted_ings"],"exp_gain": recipe["exp_gain"]})
        for rec in recipe_cost:
            if len(rec["ingredients"]) < 1 or any(not ing for ing in rec["ingredients"]):
                recipe_cost.remove(rec)
        return recipe_cost


    def optimise_cost(self,recipe_cost):
        optimised_rec = []
        for rec in recipe_cost:
            o = {}
            o['name'] = rec['name']
            o['ingredients'] = []
            o['exp_gain'] = rec['exp_gain']
            for items in rec['ingredients']:
                try:
                    mincost = items[0]
                    for item in items:
                        if item['cost'] < mincost['cost']:
                            mincost = item
                    o['ingredients'].append(mincost)
                except IndexError:
                    #Somehow a recipe that shouldn't be here has fallen through. Remove it.
                    continue
            optimised_rec.append(o)                    
        return optimised_rec
                    
    def select_best(self, optimised_recipes):
        best = {'total_cost':50,'exp_gain':0}
        for recipe in optimised_recipes:
            if 'ingredients' not in recipe.keys():
                continue
            #compute experience/cost
            try:
                empty_ing = False
                recipe['total_cost'] = 0
                for ing in recipe['ingredients']:
                    if ing == []:
                        empty_ing = True
                        break
                    else:
                        recipe['total_cost']+=ing['cost']
                if empty_ing == True:
                    continue
                ratio = recipe['exp_gain']/recipe['total_cost']
                if ratio > best['exp_gain']/best['total_cost']:
                    best = recipe
            except:
                continue
        return best

    def traverse_levels(self):
        while self.get_current() < self.get_target():
            best = self.select_best(self.optimise_cost(self.determine_cost(self.decode_ingredients(self.query_recipes()))))
            to_next = self.get_exp_to_next()
            try:
                quantity = math.ceil(to_next/best['exp_gain'])
            except ZeroDivisionError:
                print(f"Division by zero error. Best: {best}")
                return
            self.add_to_recipes({'name':best['name']['S'],'quantity':quantity})
            for i in best['ingredients']:
                i['quantity']*=quantity
            self.add_to_ingredients(best['ingredients'])
            self.incr_current()
        print((self.get_recipes(), self.get_ingredients()))
        return (self.get_recipes(), self.get_ingredients())

def lambda_handler(event, context):
    event = event["queryStringParameters"]
    path = CraftPath(event["name"],event["profession"],event["startlvl"],event["endlvl"])
    return {
        'message' : path.traverse_levels()
    }


if __name__ == "__main__":
    path = CraftPath("lime","Arcana","2","50")
    print("Optimal crafting found:")
    print(path.traverse_levels())