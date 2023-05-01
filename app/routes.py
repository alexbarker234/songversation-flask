from flask import render_template

from app import app
from app.helpers.spotify_helper import SpotifyWebUserData

'''
TODO:
- caching
 - button for user to delete their cache? 
 -
'''
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', userdata=SpotifyWebUserData())

@app.route('/lyricgame')
def lyricGame():
    return render_template('game/playlistScreen.html', title='Home', userdata=SpotifyWebUserData())

@app.route('/lyricgame/playlist/<playlist_id>')
def lyricGamePlaylist(playlist_id):
    return render_template('game/lyricgame.html', title='Home', userdata=SpotifyWebUserData())

@app.route('/lyricgame/artist/<artist_id>')
def lyricGameArtist(artist_id):
    return "not implemented"
