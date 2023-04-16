import json
from datetime import datetime
import discord
import mariadb
from discord.ext import tasks

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

with open('./config.json', 'r') as configreader:
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
    cursor.execute("CREATE TABLE IF NOT EXISTS spotifyactivity(trackid VARCHAR(25) PRIMARY KEY, songname VARCHAR(255), artists VARCHAR(255), albumcover VARCHAR(255), album VARCHAR(255), songurl VARCHAR(255), startedplaying BIGINT);")
    cursor.execute("CREATE TABLE IF NOT EXISTS userinfo(id BIGINT UNSIGNED PRIMARY KEY, name VARCHAR(64), tag INTEGER, status VARCHAR(15), avatar VARCHAR(255), banner VARCHAR(255), creationdate DATE, trackid VARCHAR(25), FOREIGN KEY (trackid) REFERENCES spotifyactivity(trackid));")
    cursor.close()
    userdata.start()

@tasks.loop(seconds=1)
async def userdata():
    global db

    members = client.guilds[0].members
    user_number = 0
    
    for i in members:
      save_artists = ""
      cursor = db.cursor()
      if not i.bot:
        date = datetime.strptime(str(i.created_at)[:10], '%Y-%m-%d')
        user = await client.fetch_user(i.id)
        #print(i.activities)
        cursor.execute("INSERT INTO userinfo (id, name, tag, status, avatar, banner, creationdate) VALUES (?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE id=?,name=?,tag=?,status=?,avatar=?,banner=?,creationdate=?",
          (i.id, i.name, int(i.discriminator), str(i.status), str(i.avatar if i.avatar != None else i.default_avatar), str(user.banner), date, i.id, i.name, int(i.discriminator), str(i.status), str(i.avatar if i.avatar != None else i.default_avatar), str(user.banner), date))
        # PROBLEM wenn mehrere nutzer den selben SONG hören wegen startedplaying
        for a in i.activities:
          if isinstance(a, discord.Spotify):
            artists = a.artists

            for artist in artists:
              save_artists += artist+","
            save_artists = save_artists[:-1]
            
            cursor.execute("INSERT INTO spotifyactivity (trackid, songname, artists, albumcover, album, songurl, startedplaying) VALUES (?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE trackid=?, songname=?, artists=?, albumcover=?, album=?, songurl=?, startedplaying=?",
              (a.track_id, a.title, save_artists, a.album_cover_url, a.album, a.track_url, a.start, a.track_id, a.title, save_artists, a.album_cover_url, a.album, a.track_url, a.start))

            
      
      cursor.close()
    db.commit()

client.run(config['token'])