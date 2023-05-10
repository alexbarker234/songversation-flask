from datetime import datetime
from app.models import Stats
from flask import redirect, render_template, request
from app import app, db
from app.helpers.spotify_helper import SpotifyWebUserData, SpotifyHelper

'''
TODO:
- caching
 - button for user to delete their cache? 
 -
'''

# all the web pages for Songversation - see api for REST api routes 

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home - Songversation', user_data=SpotifyWebUserData())


@app.route('/lyricgame')
def game_page():
    user_data = SpotifyWebUserData()
    return render_template('game/playlistScreen.html', title='Home', user_data=user_data) if user_data.authorised else redirect("/")


@app.route('/lyricgame/playlist/<playlist_id>')
def playlist_page(playlist_id):
    user_data = SpotifyWebUserData()
    return render_template('game/lyricgame.html', title='Home', user_data=user_data) if user_data.authorised else redirect("/")


@app.route('/lyricgame/artist/<artist_id>')
def artist_page(artist_id):
    return "not implemented"

@app.route('/stats', methods=['POST'])
def save_stats():
    spotify_helper = SpotifyHelper()     
    user_info = spotify_helper.me()
    user_id = user_info['id']
    score = request.form['score']

    # Get the max game_id from the Stats table
    max_game_id = Stats.query.order_by(Stats.game_id.desc()).first()
    if max_game_id is None:
        game_id = 1
    else:
        game_id = max_game_id.game_id + 1

    # Create a new row in the Stats table
    new_stats = Stats(game_id=game_id, user_id=user_id, streaknum=score, date_of_game=datetime.utcnow())
    db.session.add(new_stats)
    db.session.commit()

    return 'Stats saved successfully.'