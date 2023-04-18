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
    cursor.execute("CREATE TABLE IF NOT EXISTS userinfo(id BIGINT UNSIGNED PRIMARY KEY, name VARCHAR(64), tag VARCHAR(4), status VARCHAR(15), avatar VARCHAR(255), banner VARCHAR(255), creationdate DATE);")
    cursor.execute("CREATE TABLE IF NOT EXISTS spotifyactivity(trackid VARCHAR(25), userid BIGINT UNSIGNED, songname VARCHAR(255), artists VARCHAR(255), albumcover VARCHAR(255), album VARCHAR(255), songurl VARCHAR(255), startedplaying BIGINT, PRIMARY KEY (userid), FOREIGN KEY (userid) REFERENCES userinfo(id) ON DELETE CASCADE);")
    cursor.execute("CREATE TABLE IF NOT EXISTS playingactivity(name VARCHAR(255), userid BIGINT UNSIGNED, state VARCHAR(255), details VARCHAR(255), startedplaying BIGINT, large_image_url VARCHAR(255), small_image_url VARCHAR(255), PRIMARY KEY (userid, name), FOREIGN KEY (userid) REFERENCES userinfo(id) ON DELETE CASCADE);")
    cursor.execute("CREATE TABLE IF NOT EXISTS watchingactivity(name VARCHAR(255), userid BIGINT UNSIGNED, state VARCHAR(255), details VARCHAR(255), startedwatching BIGINT, large_image_url VARCHAR(255), small_image_url VARCHAR(255), PRIMARY KEY (userid), FOREIGN KEY (userid) REFERENCES userinfo(id) ON DELETE CASCADE);")
    cursor.execute("CREATE TABLE IF NOT EXISTS customactivity(name VARCHAR(255), userid BIGINT UNSIGNED, emoji VARCHAR(255), PRIMARY KEY (userid), FOREIGN KEY (userid) REFERENCES userinfo(id) ON DELETE CASCADE);")
    cursor.close()
    userdata.start()

@client.event
async def on_member_remove(member):
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM userinfo WHERE id = {member.id}")
    db.commit()
    
@tasks.loop(seconds=1)
async def userdata():
    global db

    members = client.guilds[0].members
    
    for i in members:
      curr_user = [i.id, i.name, i.discriminator, i.status, i.avatar, "", i.created_at, i.default_avatar]
      user = await client.fetch_user(curr_user[0])
      curr_user[5] = user.banner

      curr_user_activities = i.activities
      save_artists = ""
      cursor = db.cursor()
      if not i.bot:
        date = datetime.strptime(str(curr_user[6])[:10], '%Y-%m-%d')
        user = await client.fetch_user(curr_user[0])
        cursor.execute("INSERT INTO userinfo (id, name, tag, status, avatar, banner, creationdate) VALUES (?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE id=?,name=?,tag=?,status=?,avatar=?,banner=?,creationdate=?",
          (curr_user[0], curr_user[1], curr_user[2], str(curr_user[3]), str(curr_user[4] if curr_user[4] != None else curr_user[7]), str(curr_user[5]), date, curr_user[0], curr_user[1], curr_user[2], str(curr_user[3]), str(curr_user[4] if curr_user[4] != None else curr_user[7]), str(curr_user[5]), date))

        nospotify = True
        nogame = True
        nowatching = True
        nocustom = True
        for a in curr_user_activities:
      
          if isinstance(a, discord.Spotify):
            nospotify = False
            artists = a.artists
            for artist in artists:
              save_artists += artist+","
            save_artists = save_artists[:-1]
            cursor.execute("INSERT INTO spotifyactivity (trackid, userid, songname, artists, albumcover, album, songurl, startedplaying) VALUES (?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE trackid=?, userid=?, songname=?, artists=?, albumcover=?, album=?, songurl=?, startedplaying=?",
              (a.track_id, curr_user[0], a.title, save_artists, a.album_cover_url, a.album, a.track_url, a.start, a.track_id, curr_user[0], a.title, save_artists, a.album_cover_url, a.album, a.track_url, a.start))
          
          if a.type == discord.ActivityType.playing:
            try:
              cursor.execute("INSERT INTO playingactivity(name, userid, state, details, startedplaying, large_image_url, small_image_url) VALUES (?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE name=?, userid=?, state=?, details=?, startedplaying=?, large_image_url=?, small_image_url=?",
                (a.name, i.id, a.state, a.details, a.start, a.large_image_url, a.small_image_url, a.name, i.id, a.state, a.details, a.start, a.large_image_url, a.small_image_url))
            except AttributeError:
              cursor.execute("INSERT INTO playingactivity(name, userid, state, details, startedplaying, large_image_url, small_image_url) VALUES (?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE name=?, userid=?, state=?, details=?, startedplaying=?, large_image_url=?, small_image_url=?",
                (a.name, i.id, None, None, a.start, None, None, a.name, i.id, None, None, a.start, None, None))

          if a.type == discord.ActivityType.watching:
            nowatching = False
            cursor.execute("INSERT INTO watchingactivity(name, userid, state, details, startedwatching, large_image_url, small_image_url) VALUES (?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE name=?, userid=?, state=?, details=?, startedwatching=?, large_image_url=?, small_image_url=?",
              (a.name, curr_user[0], a.state, a.details, a.start, a.large_image_url, a.small_image_url, a.name, curr_user[0], a.state, a.details, a.start, a.large_image_url, a.small_image_url))
          
          if a.type == discord.ActivityType.custom:
            nocustom = False
            if a.emoji != None and a.name != None:
              if a.emoji.is_custom_emoji():
                cursor.execute("INSERT INTO customactivity(name, userid, emoji) VALUES (?,?,?) ON DUPLICATE KEY UPDATE name=?, userid=?, emoji=?",
                  (a.name, curr_user[0], a.emoji.url, a.name, curr_user[0], a.emoji.url))
              else:
                cursor.execute("INSERT INTO customactivity(name, userid, emoji) VALUES (?,?,?) ON DUPLICATE KEY UPDATE name=?, userid=?, emoji=?",
                  (a.name, curr_user[0], a.emoji.name, a.name, curr_user[0], a.emoji.name))
            elif a.emoji != None and a.name == None:
              if a.emoji.is_custom_emoji():
                cursor.execute("INSERT INTO customactivity(userid, emoji) VALUES (?,?) ON DUPLICATE KEY UPDATE userid=?, emoji=?",
                  (curr_user[0], a.emoji.url, curr_user[0], a.emoji.url))
              elif not a.emoji.is_custom_emoji():
                cursor.execute("INSERT INTO customactivity(userid, emoji) VALUES (?,?) ON DUPLICATE KEY UPDATE userid=?, emoji=?",
                  (curr_user[0], a.emoji.name, curr_user[0], a.emoji.name))
            else:
              cursor.execute("INSERT INTO customactivity(name, userid) VALUES (?,?) ON DUPLICATE KEY UPDATE name=?, userid=?",
                (a.name, curr_user[0], a.name, curr_user[0]))
                  
        if nospotify:
          cursor.execute(f"DELETE FROM spotifyactivity WHERE userid = {curr_user[0]}")
        if nowatching:
          cursor.execute(f"DELETE FROM watchingactivity WHERE userid = {curr_user[0]}")
        if nocustom:
          cursor.execute(f"DELETE FROM customactivity WHERE userid = {curr_user[0]}")
        
        cursor.execute(f"SELECT * FROM playingactivity WHERE userid = {curr_user[0]}")
        playingactivities = cursor.fetchall()

        dbactivityname = []
        for name in playingactivities:
          dbactivityname.append(name[0])
        
        curractivityname = []
        for activity in curr_user_activities:
          curractivityname.append(activity.name)

        for name in dbactivityname:
          if name not in curractivityname:
            cursor.execute(f"DELETE FROM playingactivity WHERE userid = {curr_user[0]} AND name='{name}';")

        
      cursor.close()
    db.commit()

client.run(config['token'])