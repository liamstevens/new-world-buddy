# new-world-buddy
## Purpose
This tool is designed to provide opinionated advice on optimised pathways to take in order to level crafting professions in New World. 
## Contents
This repository contains the logic that drives the decision making process (currently in Python) as well as the infrastructure definition in Terraform. 
## Usage
The tool was intended to be hosted at a web endpoint, but this has since shifted into a Discord bot. This also marks the pivot of the tool to a more general purpose API + interface via Discord.
To use this repository you will need an AWS account to provision resources into as well as a host to run the bot on. In addition the Terraform backend is configured to use Terraform Cloud, where AWS keypairs will need to be provided to give Terraform access to your desired AWS account.

Once Terraform has been run, you will need to run get_json.sh to scrape nwdb.info for recipe information. Following this, ensure that you have the correct Python dependencies installed either in your base environment or in a `venv` by running `pip install -r requirements.txt` from the base directory of the repository.

Then run inject_dynamo.py with the correct `AWS_ACCESS_KEY` and `AWS_ACCESS_ID` environment variables set to populate the recipe DynamoDB table. This may take a little while

Once this has completed, you can configure your bot in your Discord Developer portal (https://discord.com/developers/applications) and populate the DISCORD_TOKEN environment variable from the value in your portal, as well as the API_ENDPOINT value, which is presented as an output (`base_url`) from the Terraform Workspace. With these vars set you can run the bot using `python bot/buddy-bot.py`.
