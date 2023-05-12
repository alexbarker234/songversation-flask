from datetime import datetime
import json
from flask import request

from app.helpers.spotify_helper import SpotifyHelper

from app import app, db
from app.models import Game

@app.route('/api/add-game', methods=['POST'])
def save_game():
    spotify_helper = SpotifyHelper()     
    user_info = spotify_helper.me()
    user_id = user_info['id']
    score = request.form['score']
    song_loston = request.form['song']

    # Create a new row in the Game table
    new_game = Game(user_id=user_id, score=score, song_loston=song_loston, date_of_game=datetime.utcnow())
    db.session.add(new_game)
    db.session.commit()

    print(f"Succesfully saved game for user: {user_info['display_name']} with score {score}")

    # 201 - Created
    return json.dumps({'success':True}), 201, {'ContentType':'application/json'} 