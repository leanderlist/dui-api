from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash
)

import time
import mariadb
from flask_cors import CORS

time.sleep(15)
db = mariadb.connect(
      host="db",
      port=3306,
      user="root",
      password="schueler",
      database="data"
)

cursor = db.cursor()
app = Flask(__name__)
app.secret_key = 'Test'


def custom_sort_key(key):
    if key == "userinfo":
        return 0
    elif key == "spotifyactivity":
        return 1
    elif key == "playingactivity":
        return 2
    elif key == "watchingactivity":
        return 3
    elif key == "customactivity":
        return 4
    else:
        return key


def dataobject(id):
    db = mariadb.connect(
        host="db",
        port=3306,
        user="root",
        password="schueler",
        database="data"
    )   
    cursor = db.cursor()

    cursor.execute(f"SELECT * FROM userinfo WHERE id={id}")
    userinfo = cursor.fetchall()
    cursor.execute(f"SELECT * FROM spotifyactivity WHERE userid={id}")
    spotifyactivity = cursor.fetchall()
    cursor.execute(f"SELECT * FROM playingactivity WHERE userid={id}")
    playingactivity = cursor.fetchall()
    cursor.execute(f"SELECT * FROM watchingactivity WHERE userid={id}")
    watchingactivity = cursor.fetchall()
    cursor.execute(f"SELECT * FROM customactivity WHERE userid={id}")
    customactivity = cursor.fetchall()
    cursor.close()

    response = {}

    if len(userinfo) > 0:
        response["userinfo"] = {
            "name": userinfo[0][1],
            "tag": userinfo[0][2],
            "status": userinfo[0][3],
            "avatar_url": userinfo[0][4],
            "banner_url": userinfo[0][5],
            "creation_date": userinfo[0][6]
        }
    else:
        response["userinfo"]: "None"
    if len(spotifyactivity) > 0:
        response["spotifyactivity"] = {
            "trackid": spotifyactivity[0][0],
            "songname": spotifyactivity[0][2],
            "artist(s)": spotifyactivity[0][3],
            "albumcover": spotifyactivity[0][4],
            "album": spotifyactivity[0][5],
            "songurl": spotifyactivity[0][6],
            "startedplaying": spotifyactivity[0][7]
        }
    else:
        response["spotifyactivity"] = None
    if len(playingactivity) > 0:
        count = 0
        response["playingactivity"] = {}
        for activity in playingactivity:
            response["playingactivity"][str(count)] = {
                "name": activity[0],
                "state": activity[2],
                "details": activity[3],
                "startedplaying": activity[4],
                "large_image_url": activity[5],
                "small_image_url": activity[6]
            }
            count += 1
    else:
        response["playingactivity"] = None
    if len(watchingactivity) > 0:
        response["watchingactivity"] = {
            "name": playingactivity[0][0],
            "state": playingactivity[0][2],
            "details": playingactivity[0][3],
            "startedwatching": playingactivity[0][4],
            "large_image_url": playingactivity[0][5],
            "small_image_url": playingactivity[0][6]
        }
    else:
        response["watchingactivity"] = None
    if len(customactivity) > 0:
        response["customactivity"] = {
            "name": customactivity[0][0],
            "emoji": customactivity[0][2]
        }
    else:
        response["customactivity"] = None
    
    alle__None = (userinfo == spotifyactivity == playingactivity == watchingactivity == customactivity)
    if alle__None:
        return False
    else:
        return response
        
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api/<id>', methods=['GET'])
def getuser(id):
    speichern = dataobject(id)
    if speichern == False:
        return "To get information about your Discord Profile, the bot of this API needs to be in the same server as you!"
    else:
        return {"data":speichern}

CORS(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7007)
