import json
import discord
import mariadb
from discord.ext import tasks

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

with open('./insyBot/config.json', 'r') as configreader:
    config = json.load(configreader)

@client.event
async def on_ready():
    print(f'{client.user} is now online!')

client.run(config['token'])