import discord
import os
import requests
import json

from discord.ext import commands

TOKEN = os.environ['DISCORD_TOKEN']
ENDPOINT = os.environ['API_ENDPOINT']

bot = commands.Bot(command_prefix='!')

@bot.command(name="craft", help="Calculates the best way to craft given a profession, starting level, and finishing level.")
async def get_crafting(ctx, profession: str, start_level: int, finish_level: int):
    #send a request to the configured API gateway. Still setting that up so return a dummy message.
    await ctx.send("Calculating...")
    payload = {'profession': profession.capitalize(), 'startlvl':start_level, 'endlvl':finish_level,'name':ctx.author}
    #get JSON object of recipes to craft.
    r = requests.get(ENDPOINT,params=payload)
    rdict = json.loads(r.text)
    recipes=""
    recipeq=""
    ingr=""
    ingrq=""
    for item in rdict["recipes"]:
        recipes+=f'{item["name"]}\n'
        recipeq+=f'{item["quantity"]}\n'
    
    for item in rdict['ingredients']:
        ingr+=f'{item["item"]}\n'
        ingrq+=f'{item["quantity"]}\n'
    embeddedTable = discord.Embed(title="Recipe Information")
    embeddedTable.add_field(name = "Recipe", value = recipes, inline=True)
    embeddedTable.add_field(name = "Quantity", value = recipeq, inline=True)
    
    await ctx.send(embed=embeddedTable)
    embeddedTable = discord.Embed(title="Ingredient Information")
    embeddedTable.add_field(name = "Ingredient", value = ingr, inline=True)
    embeddedTable.add_field(name = "Quantity", value = ingrq, inline=True)
    
    await ctx.send(embed=embeddedTable)

    



@bot.command(name="stathelp", help="Help us out with resource scarcity definitions. The bot will take input for as long as you will provide it, exit any time by replying with \"STOP\"")
async def stathelp(ctx):
    await ctx.send("Thanks for providing feedback on the resource calculator.")




bot.run(TOKEN)