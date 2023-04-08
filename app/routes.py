from flask import render_template, request, url_for, session, redirect, jsonify
import time
from app import app

import urllib.request, json

from config import Config

import spotipy
from spotipy.oauth2 import SpotifyOAuth

'''
TODO:
- caching
 - lyric cache: to reduce the amount of API calls for lyrics
'''
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', userdata=UserData())

@app.route('/lyricgame')
def lyricGame():
    return render_template('lyricgame.html', title='Home', userdata=UserData())


@app.route('/login')
def login():    
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/logout')
def logout():    
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/index")

@app.route('/getTracks')
def get_all_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(curGroup):
            track = item['track']
            val = track['name'] + " - " + track['artists'][0]['name']
            results += [val]
        if (len(curGroup) < 50):
            break
    
    return results

@app.route('/topartists', methods=['GET'])
def topArtists():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0

    limit = 20

    while True:
        offset = iter * limit
        iter += 1
        curGroup = sp.current_user_top_artists(limit=limit, offset=offset, time_range='short_term')['items']
        for idx, item in enumerate(curGroup):
            results += [Artist(item)]
        if (len(curGroup) < limit):
            break
    
    return json.dumps([ob.__dict__ for ob in results])

@app.route('/getplaylists')
def get_playlists():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    
    results = []

    playlists = sp.current_user_playlists(limit=50,offset=0)
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            platlistObj = Playlist(playlist)
            if platlistObj.trackCount > 0:
                results.append(platlistObj)
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return json.dumps([ob.__dict__ for ob in results])

@app.route('/getplaylisttracks/<playlist_id>')
def get_playlist_tracks(playlist_id):
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    
    results = []

    print('Fetching Tracks for playlist id: ' + playlist_id)

    tracks = sp.playlist_tracks(playlist_id = playlist_id, limit = 50,offset = 0)
    while tracks:
        for i, playlistTrack in enumerate(tracks['items']):
            # dont add local files 
            if playlistTrack['track']['is_local'] or playlistTrack['track']['id'] != None:
                results.append(Track(playlistTrack['track']))
        if tracks['next']:
            tracks = sp.next(tracks)
        else:
            tracks = None

    return json.dumps([ob.__dict__ for ob in results])

# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

def create_spotify_oauth():
    return SpotifyOAuth(
            client_id = Config.SPOTIPY_CLIENT_ID,
            client_secret = Config.SPOTIPY_CLIENT_SECRET,
            redirect_uri = url_for('authorize', _external=True),
            scope = "user-library-read user-top-read playlist-read-private")


class UserData:
    def __init__(self):
        session['token_info'], self.authorized = get_token()
        session.modified = True
        if self.authorized:
            sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
            payload = sp.me()
            self.username = payload['display_name']     
            self.image_url = payload['images'][0]['url'] if len(payload['images']) > 0 else None
            self.id = payload['id']

class Artist:
    def __init__(self, payload):
        self.name = payload['name']
        self.image = payload['images'][0]['url'] if len(payload['images']) > 0 else None

class Playlist:
    def __init__(self, payload):
        self.name = payload['name']
        self.id = payload['id']
        self.ownerID = payload['owner']['id']
        self.trackCount = payload['tracks']['total']
        if len(payload['images']) > 0:
            self.image = payload['images'][0]['url']
        # default icon
        else:
            self.image = url_for('static', filename='defaultCover.png')

class Track:
    def __init__(self, payload):
        self.name = payload['name']
        self.id = payload['id']
        self.artists = []
        for artist in payload['artists']:
            self.artists.push(artist['name'])
        # PREVIEW CAN BE NULL
        self.preview_url = payload['preview_url']

