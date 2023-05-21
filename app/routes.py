from typing import List
from app.cache_manager.artist_cache import get_artist
from app.cache_manager.track_cache import get_tracks
from app.models import Game, User
from flask import redirect, render_template
from app import app
from app.helpers.spotify_helper import SpotifyHelper, SpotifyWebUserData

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
    return render_template('index.html', title='Songversation', user_data=SpotifyWebUserData())


@app.route('/lyricgame')
def select_screen():
    user_data = SpotifyWebUserData()
    return render_template('game/playlistScreen.html', title='Songversation', user_data=user_data) if user_data.authorised else redirect("/")

@app.route('/lyricgame/artist/<object_id>')
@app.route('/lyricgame/playlist/<object_id>')
def game_page(object_id):
    user_data = SpotifyWebUserData()
    return render_template('game/lyricgame.html', title='Songversation', user_data=user_data) if user_data.authorised else redirect("/")


@app.route('/lyricgame/artist/<artist_id>')
def artist_page(artist_id):
    return "not implemented"

@app.route('/stats')
def stats():
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return redirect("/")

    game_list: list[Game] = Game.query.filter(
        Game.user_id == user_data.id).all()

    track_ids = [game.song_failed_on for game in game_list]
    tracks = get_tracks(track_ids)

    # prevents requesting the same thing many times
    playlist_cache = {}
    artist_cache = {}


    sp = SpotifyHelper()

    for game in game_list:
        track = tracks[game.song_failed_on]
        game.failed_track = {'name': track.name, 'image': track.image_url} 
        try:
            if game.game_type == 'artist':
                artist = artist_cache.get(game.game_object_id, get_artist(game.game_object_id))
                artist_cache[game.game_object_id] = artist
                game.game_object = {'name': artist.name, 'image': artist.image_url}
            else:
                playlist = artist_cache.get(game.game_object_id, sp.playlist(game.game_object_id))
                playlist_cache[game.game_object_id] = playlist
                game.game_object = {'name': playlist['name'], 'image': playlist['images'][0]['url']}
        except:
            game.game_object = {'name': 'error', 'image': ''}

    game_info = {}
    # sort the games & get first 50 elements
    game_info['playlists'] = [game for game in game_list if game.game_type == 'playlist'][:50]
    game_info['artists'] = [game for game in game_list if game.game_type == 'artist'][:50]

    best_score = max(game_list, key=lambda game: game.score).score if len(game_list) > 0 else '-'
    average_score = round(sum(game.score for game in game_list) / len(game_list), 2) if len(game_list) > 0 else '-'

    return render_template('user/stats.html', title='My Stats', user_data=user_data, user_name=user_data.username, game_info=game_info, best_score=best_score, average_score=average_score)

# @app.route('/profile')
# def profile_page():
#     user_data = SpotifyWebUserData()
#     if not user_data.authorised:
#         return redirect("/")
#     return render_template('profile_page.html', title='My Profile', user_data=user_data, user_name=user_data.username, dp=user_data.image_url)

@app.route('/friends')
def friends_page():
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return redirect("/")
    
    friends_list = []
    # TODO: query existing friends
    user: User = User.query.filter(User.user_id == user_data.id).first()
    friends: List[User] = user.friends
    for friend in friends:
        friends_list.append({
            'id': friend.user_id,
            'date_joined': friend.date_joined
        })
    print([friend.user_id for friend in friends])

    return render_template('user/friends.html', title='Friends', user_data=user_data, user_name=user_data.username, friends=friends_list)
