from app.cache_manager.artist_cache import get_artist
from app.cache_manager.track_cache import get_tracks
from app.models import Game
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


@app.route('/lyricgame/artist/<artist_id>')
def artist_page(artist_id):
    return "not implemented"


def calculate_best_score(game_list):
    if not game_list:
        return 0

    # Sort the game_list based on the score in descending order
    sorted_games = sorted(game_list, key=lambda game: game.score, reverse=True)

    # Retrieve the score of the first game in the sorted list (highest score)
    best_score = sorted_games[0].score
    return best_score


def calculate_average_score(game_list):
    if not game_list:
        return 0

    # Calculate the total sum of scores
    total_score = sum(game.score for game in game_list)

    # Calculate the average score by dividing the total score by the number of games
    average_score = total_score / len(game_list)
    return average_score

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

    best_score = calculate_best_score(game_list)
    average_score = round(calculate_average_score(game_list), 2)

    return render_template('stats.html', title='My Stats', user_data=user_data, user_name=user_data.username, game_info=game_list, best_score=best_score, average_score=average_score)


@app.route('/profile')
def profile_page():
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return redirect("/")
    return render_template('profile_page.html', title='My Profile', user_data=user_data, user_name=user_data.username, dp=user_data.image_url)
