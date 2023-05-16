from datetime import datetime
from typing import Tuple
from app.helpers.spotify_helper import SpotifyHelper
from constants import SECONDS_IN_MONTH

from app.models import Track
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

        for track in response['tracks']:     
            # track does not exist   
            if track is None:
                continue
        
            # create cache object
            track_cache = Track(id = track['id'], name = track['name'], preview_url = track['preview_url'], image_url = track['album']['images'][0]['url'], last_cache_date = datetime.utcnow())
            track_dict[track_id] = track_cache

            # modify existing cache
            existing_cache = to_cache[track['id']]
            if existing_cache:
                existing_cache.name = track_cache.name
                existing_cache.last_cache_date = track_cache.last_cache_date
                existing_cache.preview_url = track_cache.preview_url
                existing_cache.image_url = track_cache.image_url
            # add new cache
            else:
                db.session.add(track_cache)
            
        print(f'Caching tracks with ids: {cache_track_ids}')

    db.session.commit()
    return track_dict
       
def get_cached_track(track_id: str) -> Tuple[bool, Track]:
    track_cache: Track = Track.query.filter(Track.id == track_id).first()
    # check if the track_cache exists
    if not track_cache:
        return False, None
    
    # check if cache is old
    if (datetime.utcnow() - track_cache.last_cache_date).total_seconds() > SECONDS_IN_MONTH:
        #print(f"Cache expired for track with track_id: {track_id}")
        return False, track_cache
    
    # return just the lyrics 
    return True, track_cache
