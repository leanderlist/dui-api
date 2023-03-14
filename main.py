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
    db = mariadb.connect(
      host="db",
      port=3306,
      user="root",
      password="mariadb-dui-api",
      database="data"
    )
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS userinfo( id BIGINT UNSIGNED PRIMARY KEY, name VARCHAR(64), tag INTEGER, avatarurl VARCHAR(255));")
    cursor.close()
    userdata.start()

@tasks.loop(seconds=1)
async def userdata():
    global db

    members = client.guilds[0].members
    for i in members:
      cursor = db.cursor()
      if i.id != client.user.id:
        cursor.execute(f"INSERT INTO userinfo (id, name, tag, avatarurl) VALUES (?,?,?,?) ON DUPLICATE KEY UPDATE id=?, name=?, tag=?, avatarurl=?",
        (i.id,i.name,int(i.discriminator),str(i.avatar if i.avatar != None else i.default_avatar)), i.id,i.name,int(i.discriminator),str(i.avatar if i.avatar != None else i.default_avatar))
      cursor.close()
    db.commit()

client.run(config['token'])