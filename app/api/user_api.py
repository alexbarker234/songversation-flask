from datetime import datetime
import json
from flask import request
from app.api.spotify_api import UNAUTHORISED_MESSAGE

from app.helpers.spotify_helper import SpotifyHelper, UnauthorisedException

from app import app, db
from app.models import Game

@app.route('/api/add-game', methods=['POST'])
def save_game():
    try:
        spotify_helper = SpotifyHelper()     
        user_info = spotify_helper.me()
        user_id = user_info['id']

        print(request.form)

        score = request.form['score']
        song_failed_on = request.form['last_song']
        game_type = request.form['game_type']
        game_object_id = request.form['game_object_id']

        # Create a new row in the Game table
        new_game = Game(user_id=user_id, score=score, song_failed_on=song_failed_on, game_type=game_type, game_object_id=game_object_id, date_of_game=datetime.utcnow())
        db.session.add(new_game)
        db.session.commit()

        print(f"Succesfully saved game for user: {user_info['display_name']} with score {score}")

        # 201 - Created
        return json.dumps({'success':True}), 201, {'ContentType':'application/json'} 
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401