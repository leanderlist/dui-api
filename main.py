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
      password="NathanIstCool"
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
      password="NathanIstCool",
      database="data"
    )
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS userinfo(id BIGINT UNSIGNED PRIMARY KEY, name VARCHAR(64), tag INTEGER, status VARCHAR(15), avatar VARCHAR(255), banner VARCHAR(255), creationdate DATE);")
    cursor.execute("CREATE TABLE IF NOT EXISTS spotifyactivity(trackid VARCHAR(25), userid BIGINT UNSIGNED, songname VARCHAR(255), artists VARCHAR(255), albumcover VARCHAR(255), album VARCHAR(255), songurl VARCHAR(255), startedplaying BIGINT, PRIMARY KEY (trackid, userid), FOREIGN KEY (userid) REFERENCES userinfo(id));")
    cursor.execute("CREATE TABLE IF NOT EXISTS playingactivity(name VARCHAR(255), userid BIGINT UNSIGNED, state VARCHAR(255), details VARCHAR(255), startedplaying BIGINT, large_image_url VARCHAR(255), small_image_url VARCHAR(255), PRIMARY KEY (name, userid), FOREIGN KEY (userid) REFERENCES userinfo(id));")
    cursor.execute("CREATE TABLE IF NOT EXISTS watchingactivity(name VARCHAR(255), userid BIGINT UNSIGNED, state VARCHAR(255), details VARCHAR(255), startedwatching BIGINT, large_image_url VARCHAR(255), small_image_url VARCHAR(255), PRIMARY KEY (name, userid), FOREIGN KEY (userid) REFERENCES userinfo(id));")
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
        cursor.execute("INSERT INTO userinfo (id, name, tag, status, avatar, banner, creationdate) VALUES (?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE id=?,name=?,tag=?,status=?,avatar=?,banner=?,creationdate=?",
          (i.id, i.name, int(i.discriminator), str(i.status), str(i.avatar if i.avatar != None else i.default_avatar), str(user.banner), date, i.id, i.name, int(i.discriminator), str(i.status), str(i.avatar if i.avatar != None else i.default_avatar), str(user.banner), date))
        for a in i.activities:
          if isinstance(a, discord.Spotify):
            artists = a.artists
            for artist in artists:
              save_artists += artist+","
            save_artists = save_artists[:-1]
            cursor.execute("INSERT INTO spotifyactivity (trackid, userid, songname, artists, albumcover, album, songurl, startedplaying) VALUES (?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE trackid=?, userid=?, songname=?, artists=?, albumcover=?, album=?, songurl=?, startedplaying=?",
              (a.track_id, i.id, a.title, save_artists, a.album_cover_url, a.album, a.track_url, a.start, a.track_id, i.id, a.title, save_artists, a.album_cover_url, a.album, a.track_url, a.start))

          if a.type == discord.ActivityType.playing:
            cursor.execute("INSERT INTO playingactivity(name, userid, state, gamedetails, startedplaying, large_image_url, small_image_url) VALUES (?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE name=?, userid=?, state=?, details=?, startedplaying=?, large_image_url=?, small_image_url=?",
              (a.name, i.id, a.state, a.details, a.start, a.large_image_url, a.small_image_url, a.name, i.id, a.state, a.details, a.start, a.large_image_url, a.small_image_url))
          
          if a.type == discord.ActivityType.watching:
            cursor.execute("INSERT INTO watchingactivity(name, userid, state, details, startedwatching, large_image_url, small_image_url) VALUES (?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE name=?, userid=?, state=?, details=?, startedwatching=?, large_image_url=?, small_image_url=?",
              (a.name, i.id, a.state, a.details, a.start, a.large_image_url, a.small_image_url, a.name, i.id, a.state, a.details, a.start, a.large_image_url, a.small_image_url))
      
      cursor.close()
    db.commit()

client.run(config['token'])