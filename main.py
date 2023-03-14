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

db = mariadb.connect(
      host="db",
      port=3306,
      user="root",
      password="mariadb-dui-api"
)

cursor = db.cursor()



@client.event
async def on_ready():
    global cursor, db
    print(f'{client.user} is now online!')
    
    cursor.execute("CREATE DATABASE IF NOT EXISTS data;")
    cursor.close()

client.run(config['token'])