from datetime import datetime
from app.cache_manager.track_cache import get_tracks
from app.models import Game, Track, User
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
def select_screen():
    user_data = SpotifyWebUserData()
    return render_template('game/playlistScreen.html', title='Home', user_data=user_data) if user_data.authorised else redirect("/")

@app.route('/lyricgame/artist/<object_id>')
@app.route('/lyricgame/playlist/<object_id>')
def game_page(object_id):
    user_data = SpotifyWebUserData()
    return render_template('game/lyricgame.html', title='Home', user_data=user_data) if user_data.authorised else redirect("/")

@app.route('/stats')
def stats():
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return redirect("/")

    game_list: list[Game] = Game.query.filter(
        Game.user_id == user_data.id).all()

    track_ids = [game.song_failed_on for game in game_list]
    tracks = get_tracks(track_ids)

    for game in game_list:
        game.failed_track = FailedTrack(game, tracks[game.song_failed_on])

    game_info = {}
    game_info['playlists'] = [game for game in game_list if game.game_type == 'playlist']
    game_info['artists'] = [game for game in game_list if game.game_type == 'artist']

    return render_template('stats.html', title='My Stats', user_data=user_data, user_name=user_data.username, game_info=game_info)

@app.route('/profile')
def profile_page():
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return redirect("/")
    return render_template('profile_page.html', title='My Profile', user_data=user_data, user_name=user_data.username, dp=user_data.image_url)


class FailedTrack(object):
    def __init__(self, game: Game, track: Track) -> None:
        self.id = game.song_failed_on
        self.name = track.name
        self.image =  track.image_url
