from datetime import datetime
from app.models import Game, User
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


@app.route('/stats')
def stats():
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return redirect("/")
    
    game_info = db.session.query(Game.game_id, Game.score, Game.song_failed_on, Game.date_of_game)\
        .filter(Game.user_id == user_data.id).all()
    return render_template('stats.html', title='My Stats',user_data=user_data, user_name=user_data.username, game_info=game_info)
