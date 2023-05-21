from datetime import datetime
from typing import Tuple
from app.helpers.spotify_helper import SpotifyHelper
from constants import SECONDS_IN_MONTH

from app.models import Track, TrackArtist
from app import db


def get_tracks(track_ids: list[str]) -> dict[str, Track]:
    ''' Returns a dictionary with keys of track ids containing track data '''
    track_dict: dict[str, Track] = {}

    # check cache
    to_cache: dict[str, Track] = {}
    for track_id in track_ids:
        valid_cache, track_cache = get_cached_track(track_id)

        if not valid_cache:
            to_cache[track_id] = track_cache
        else:
            track_dict[track_id] = track_cache

    if len(to_cache) > 0:
        spotify = SpotifyHelper()
        cache_track_ids = list(to_cache.keys())
        response = spotify.tracks(cache_track_ids)
        
        for track_response in response['tracks']:
            # track does not exist
            if track_response is None:
                continue
            
            track_cache = cache_track(track_response, to_cache[track_response['id']])
            track_dict[track_response['id']] = track_cache       

        print(f'Caching tracks with ids: {cache_track_ids}')

    db.session.commit()
    return track_dict

def cache_track(track_response: dict, existing_cache: Track) -> Track:
    # cache the artists
    _cache_track_artists(track_response)

    # create cache object
    release_precision = track_response['album']['release_date_precision']
    date_formats = {'day': '%Y-%m-%d', 'month': '%Y-%m', 'year': '%Y'}
    release_date = datetime.strptime(track_response['album']['release_date'], date_formats[release_precision])
    track_cache = Track(id=track_response['id'],
                        name=track_response['name'],
                        preview_url=track_response['preview_url'],
                        image_url=track_response['album']['images'][0]['url'],
                        release_date=release_date,
                        last_cache_date=datetime.utcnow())
    
    # modify existing cache
    if existing_cache:
        existing_cache.name = track_cache.name
        existing_cache.last_cache_date = track_cache.last_cache_date
        existing_cache.preview_url = track_cache.preview_url
        existing_cache.image_url = track_cache.image_url
        return existing_cache
    # add new cache
    else:
        db.session.add(track_cache)
        return track_cache

def _cache_track_artists(track_response):
    existing: list[TrackArtist] = TrackArtist.query.filter(TrackArtist.id == track_response['id']).all()
    # keys are artist_id for O(1) checks if an element exists
    existing_dict = {track_artist.artist_id:track_artist for track_artist in existing}

    # A track artist can be added or removed - therefore add new ones or delete ones that exist in database

    removed_track_artists = existing_dict
    for artist in track_response['artists']:
        track_artist_cache = TrackArtist(artist_id=artist['id'], track_id=track_response['id'])
        # if the artist for this track is not cached
        if track_artist_cache.artist_id not in existing_dict:
            db.session.add(track_artist_cache)
        # otherwise if its cached, dont include in the removed artists list
        else: 
            removed_track_artists.pop(track_artist_cache.id)

    # delete all artists that are no longer on that track
    for removed_artist in removed_track_artists.values():
        db.session.delete(removed_artist)

def get_cached_track(track_id: str) -> Tuple[bool, Track]:
    track_cache: Track = Track.query.filter(Track.id == track_id).first()
    # check if the track_cache exists
    if not track_cache:
        return False, None

    # check if cache is old
    if (datetime.utcnow() - track_cache.last_cache_date).total_seconds() > SECONDS_IN_MONTH:
        # print(f"Cache expired for track with track_id: {track_id}")
        return False, track_cache

    # return just the lyrics
    return True, track_cache
