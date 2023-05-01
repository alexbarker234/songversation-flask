from flask import redirect, render_template

from app import app
from app.helpers.spotify_helper import SpotifyWebUserData

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
    return render_template('index.html', title='Home', user_data=SpotifyWebUserData())


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
