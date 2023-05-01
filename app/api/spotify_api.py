
import asyncio
from datetime import datetime
import time
import aiohttp
from flask import jsonify, redirect, request, session, url_for

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from app.helpers.spotify_helper import SpotifyHelper, UnauthorisedException

from app.models import Lyric, TrackLyrics
from config import Config

SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = SECONDS_IN_HOUR * 24

UNAUTHORISED_MESSAGE = "User Unauthorised"

from app import app, db

#TODO: redo this to use code like below
@app.route('/topartists', methods=['GET'])
def topArtists():
    try:
        sp = SpotifyHelper()
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
        
        return jsonify([ob.__dict__ for ob in results])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 501
    

@app.route('/getplaylists')
def get_playlists():
    try:
        sp = SpotifyHelper()
    
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
        return jsonify([ob.__dict__ for ob in results])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 501

@app.route('/getplaylist/<playlist_id>')
def get_playlist(playlist_id):
    try:
        sp = SpotifyHelper()
        
        try:
            playlist = sp.playlist(playlist_id=playlist_id)
            tracks = request_tracks(sp, playlist["tracks"])

            playlistObj = Playlist(playlist, tracks)
            return jsonify(to_dict(playlistObj))
        except:    
            return jsonify({'error':True, 'message':'Invalid Playlist ID'})
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 501


@app.route('/getplaylisttracks/<playlist_id>')
def get_playlist_tracks(playlist_id):
    try:
        sp = SpotifyHelper()
        
        results = []

        print('Fetching Tracks for playlist id: ' + playlist_id)

        tracks = sp.playlist_tracks(playlist_id = playlist_id, limit = 50,offset = 0)
        results = request_tracks(sp, tracks)

        return jsonify([ob.__dict__ for ob in results])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 501

def request_tracks(sp, tracks):
    '''
    Requests the rest of the tracks given an existing request and turns them into a Track object for ease of use
    '''
    results = []
    while tracks:
        for i, playlistTrack in enumerate(tracks['items']):
            # dont add local files 
            if playlistTrack['track']['is_local'] or playlistTrack['track']['id'] != None:
                results.append(Track(playlistTrack['track']))
        if tracks['next']:
            tracks = sp.next(tracks)
        else:
            tracks = None
    return results

@app.route('/gettracklyrics', methods=['GET'])
async def get_track_lyrics():
    return_data = {
        'error': False,
        'track_lyrics': {}
    }

    track_ids = request.args.get('track_ids').split(',')
    if len(track_ids) == 0:
        return_data['error'] = True
        return_data['error_message'] = "No track ids entered"

    # init
    for track_id in track_ids:
        return_data['track_lyrics'][track_id] = []

    # check cache
    uncached_track_ids = []
    for track_id in track_ids:
        lyric_cache = TrackLyrics.query.filter_by(track_id = track_id).first()
        if lyric_cache:
            lyric_lines_cache = Lyric.query.filter_by(track_lyric_id = lyric_cache.id).order_by(Lyric.order.asc()).all()

            # check if cache is old
            needs_refresh = False
            if (datetime.utcnow() - lyric_cache.last_cache_date).total_seconds() > SECONDS_IN_DAY:
                print(f"Cache expired for track_id: {track_id}")
                needs_refresh = True
            elif lyric_cache.lyric_count != len(lyric_lines_cache):
                print(f"Mismatch between lyric count and lines recieved: count: {lyric_cache.lyric_count}, lines: {len(lyric_lines_cache)}")
                needs_refresh = True

            if len(lyric_lines_cache) > 0:      
                for lyric in lyric_lines_cache:
                    # delete all lyric caches if they are old
                    if needs_refresh:
                        db.session.delete(lyric)
                    # add the lyrics to the list
                    else:
                        return_data['track_lyrics'][track_id].append(lyric.lyric)
        if not lyric_cache or needs_refresh:
            uncached_track_ids.append(track_id)

    if len(uncached_track_ids) > 0: 
        # asynchrnously get all uncached lyrics
        async with aiohttp.ClientSession() as session:
            tasks = []
            for track_id in uncached_track_ids:
                    tasks.append(
                        fetch(session, "https://spotify-lyric-api.herokuapp.com/?trackid=" + track_id, track_id)
                    )
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # process responses
            for response in responses:
                track_id = response['data']

                lyric_cache = TrackLyrics.query.filter_by(track_id = track_id).first()

                # initialise cache 
                if not lyric_cache:
                    lyric_cache = TrackLyrics(track_id = track_id)
                    db.session.add(lyric_cache)
                    # required in order to use lyric_cache.id
                    db.session.flush()
                    db.session.refresh(lyric_cache)
                
                lyricCount = 0

                # No lyrics returns 404
                if not response['json']['error']:
                    # turn response into list of each lyric
                    for line in response['json']['lines']:
                        if not line or not line['words']  or line['words'] == '♪': 
                            continue
                        return_data['track_lyrics'][track_id].append(line['words'])
                        lyric_line = Lyric(lyric = line['words'], order = lyricCount, track_lyric_id = lyric_cache.id)
                        db.session.add(lyric_line)
                        lyricCount += 1

                # update cache
                lyric_cache.lyric_count = lyricCount
                lyric_cache.last_cache_date = datetime.utcnow()

                print("Caching lyrics for track_id:" + track_id )

    db.session.commit()
    return jsonify(return_data)

# expanded upon https://dev.to/matteo/async-request-with-python-1hpo
async def fetch(session, url, data):
    """Execute an http call async
    Args:
        session: context for making the http call
        url: URL to call
        data: optional, additional data attached to the call
    Return:
        A dictionary containing 'url', 'json' dictionary of response & additional data attached to the call
    """ 
    async with session.get(url) as response:
            resp = await response.json()
            return { 'url': url, 'json': resp, 'data': data }

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


class Artist:
    def __init__(self, payload):
        self.name = payload['name']
        self.image = payload['images'][0]['url'] if len(payload['images']) > 0 else None

class Playlist:
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

class Track:
    def __init__(self, payload):
        self.name = payload['name']
        self.id = payload['id']
        self.artists = []
        for artist in payload['artists']:
            self.artists.append(artist['name'])
        # PREVIEW CAN BE NULL
        self.preview_url = payload['preview_url']

