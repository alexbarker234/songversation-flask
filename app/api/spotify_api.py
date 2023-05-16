
import re
from flask import jsonify, request, url_for

from app.cache_manager.track_cache import get_tracks
from app.cache_manager.track_lyrics_cache import get_lyrics
from app.helpers.spotify_helper import SpotifyHelper, UnauthorisedException


from app import app
from constants import UNAUTHORISED_MESSAGE

class AlbumResponse:
    def __init__(self, payload):
        self.id = payload['id']
        self.name = payload['name']
        self.image = payload['images'][0]['url']

class ArtistResponse:
    def __init__(self, payload):
        self.id = payload['id']
        self.name = payload['name']
        self.image = payload['images'][0]['url'] if len(payload['images']) > 0 else None

class PlaylistResponse:
    def __init__(self, payload, tracks=[]):
        self.name = payload['name']
        self.id = payload['id']
        self.ownerID = payload['owner']['id']
        self.trackCount = payload['tracks']['total']
        self.tracks = tracks
        if len(payload['images']) > 0:
            self.image = payload['images'][0]['url']
        # default icon
        else:
            self.image = url_for('static', filename='defaultCover.png')

class TrackResponse:
    def __init__(self, payload, album: AlbumResponse = None):
        self.name = payload['name']
        self.id = payload['id']
        self.artists = []
        for artist in payload['artists']:
            self.artists.append(artist['name'])
        # PREVIEW CAN BE NULL
        self.preview_url = payload['preview_url']
        if 'album' in payload:
            self.image_url = payload['album']['images'][0]['url']
        elif album:
            self.image_url = album.image

@app.route('/api/top-artists', methods=['GET'])
def top_artists():
    '''
    returns the current users top 50 artists over the past 4 weeks
    '''
    try:
        sp = SpotifyHelper()
    
        results = []

        artists = sp.current_user_top_artists(limit=50,offset=0, time_range='short_term')
        while artists:
            for i, artist in enumerate(artists['items']):
                results.append(ArtistResponse(artist))
            if artists['next']:
                artists = sp.next(artists)
            else:
                artists = None
        return jsonify([ob.__dict__ for ob in results])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401
    
# ARTISTS

@app.route('/api/get-artists')
def get_artists():
    '''
    returns the current users followed artists
    '''
    try:
        sp = SpotifyHelper()
    
        results = []

        artists = sp.current_user_followed_artists(limit=50)
        while artists:
            for i, artist in enumerate(artists['artists']['items']):
                results.append(ArtistResponse(artist))
            if artists['artists']['next']:
                artists = sp.next(artists['artists'])
            else:
                artists = None
        return jsonify([ob.__dict__ for ob in results])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401

@app.route('/api/get-artist/<artist>')
def get_artist(artist_id):
    try:
        sp = SpotifyHelper()
        
        try:
            playlist = sp.artist(artist_id)
            # TODO
            #tracks = request_tracks(sp, playlist["tracks"])

            #playlistObj = PlaylistResponse(playlist, tracks)
            return 'test' #jsonify(to_dict(playlistObj))
        except Exception as e:  
            return jsonify({'error':True, 'message':'Invalid Playlist ID'})
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401

@app.route('/api/get-artist-tracks/<artist_id>')
def get_artist_tracks(artist_id):
    try:
        sp = SpotifyHelper()
        
        results = []

        print('Fetching Tracks for artist id: ' + artist_id)

        # spotipy doesnt let you do ['album', 'single'] for some reason
        album_request = sp.artist_albums(artist_id, limit = 50, album_type='album')
        albums = request_albums(sp, album_request)
        album_request = sp.artist_albums(artist_id, limit = 50, album_type='single')
        albums.extend(request_albums(sp, album_request))

        # filter remixes, alt versions, acoustics, etc out
        albums = [album for album in albums if not (re.search('[\[\(].* ?(?:Rework|Remix|Version|Acoustic|Acapella|Unplugged|Live|Instrumental)[\]\)]', album.name, re.IGNORECASE))]        
        
        tracks: list[TrackResponse] = []
        print(f'\t{len(albums)} albums found')
        for album in albums:
            track_request = sp.album_tracks(album.id, limit=50)
            print([track.name for track in tracks])
            tracks += request_album_tracks(sp, track_request, album)
            print([track.name for track in tracks])

        # remove duplicate tracks
        unique_tracks = {}
        for track in tracks:
            if track.name not in unique_tracks:
                unique_tracks[track.name] = track

        unique_tracks = list(unique_tracks.values())

        return jsonify([ob.__dict__ for ob in unique_tracks])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401


# PLAYLISTS
@app.route('/api/get-playlists')
def get_playlists():
    '''
    returns the current users playlists
    '''
    try:
        sp = SpotifyHelper()
    
        results = []

        playlists = sp.current_user_playlists(limit=50,offset=0)
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                platlistObj = PlaylistResponse(playlist)
                if platlistObj.trackCount > 0:
                    results.append(platlistObj)
            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None
        return jsonify([ob.__dict__ for ob in results])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401

@app.route('/api/get-playlist/<playlist_id>')
def get_playlist(playlist_id):
    try:
        sp = SpotifyHelper()
        
        try:
            playlist = sp.playlist(playlist_id=playlist_id)
            tracks = request_playlist_tracks(sp, playlist["tracks"])

            playlistObj = PlaylistResponse(playlist, tracks)
            return jsonify(to_dict(playlistObj))
        except Exception as e:  
            return jsonify({'error':True, 'message':'Invalid Playlist ID'})
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401


@app.route('/api/get-playlist-tracks/<playlist_id>')
def get_playlist_tracks(playlist_id):
    try:
        sp = SpotifyHelper()
        
        results = []

        print('Fetching Tracks for playlist id: ' + playlist_id)

        tracks = sp.playlist_tracks(playlist_id = playlist_id, limit = 50,offset = 0)
        results = request_playlist_tracks(sp, tracks)

        return jsonify([ob.__dict__ for ob in results])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401

def request_playlist_tracks(sp, items):
    '''
    Requests the rest of the tracks given an existing request and turns them into a TrackResponse object for ease of use
    '''
    results = []
    while items:
        for playlist_track in items['items']:
            # dont add local files 
            if playlist_track['track']['is_local'] or playlist_track['track']['id'] != None:
                results.append(TrackResponse(playlist_track['track']))
        if items['next']:
            items = sp.next(items)
        else:
            items = None
    return results

def request_album_tracks(sp, tracks, album) -> list[TrackResponse]:
    '''
    Requests the rest of the tracks given an existing request and turns them into a TrackResponse object for ease of use
    '''
    results = []
    while tracks:
        for track in tracks['items']:
            results.append(TrackResponse(track, album))
        if tracks['next']:
            tracks = sp.next(tracks)
        else:
            tracks = None
    return results

def request_albums(sp, albums) -> list[AlbumResponse]:
    '''
    Requests the rest of the albums given an existing request and turns them into a AlbumResponse object for ease of use
    '''
    results = []
    while albums:
        for i, album in enumerate(albums['items']):
            results.append(AlbumResponse(album))
        if albums['next']:
            albums = sp.next(albums)
        else:
            albums = None
    return results

@app.route('/api/get-track-lyrics', methods=['GET'])
async def get_track_lyrics():
    return_data = {
        'error': False,
        'track_lyrics': {}
    }

    track_ids = request.args.get('track_ids').split(',')
    if len(track_ids) == 0:
        return_data['error'] = True
        return_data['error_message'] = "No track ids entered"

    # fetch lyrics from cache/refresh cache
    return_data['track_lyrics'] = await get_lyrics(track_ids)

    # also add track to cache
    get_tracks(track_ids)

    return jsonify(return_data)

def to_dict(obj):
     # check if the object is a list
    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    # check if the object is a dictionary
    elif isinstance(obj, dict):
        return {key: to_dict(value) for key, value in obj.items()}
    # check if the object has a __dict__ attribute
    elif hasattr(obj, '__dict__'):
        return to_dict(obj.__dict__)
    # check if the object has a vars() function
    elif hasattr(obj, 'vars'):
        return to_dict(vars(obj))
    # base case: return the object as is
    else:
        return obj
