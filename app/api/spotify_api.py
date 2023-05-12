
import asyncio
from datetime import datetime
import time
import aiohttp
from flask import jsonify, redirect, request, session, url_for

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from app.cache_manager.track_lyrics_cache import get_lyrics
from app.helpers.spotify_helper import SpotifyHelper, UnauthorisedException

from app.models import Lyric, TrackLyrics
from config import Config



UNAUTHORISED_MESSAGE = "User Unauthorised"

from app import app, db

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
                results.append(Artist(artist))
            if artists['next']:
                artists = sp.next(artists)
            else:
                artists = None
        return jsonify([ob.__dict__ for ob in results])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401
    

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
                platlistObj = Playlist(playlist)
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
            tracks = request_tracks(sp, playlist["tracks"])

            playlistObj = Playlist(playlist, tracks)
            return jsonify(to_dict(playlistObj))
        except:    
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
        results = request_tracks(sp, tracks)

        return jsonify([ob.__dict__ for ob in results])
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401

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

    return jsonify(return_data)
    
def cache_track_data(track_ids):
    pass




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

