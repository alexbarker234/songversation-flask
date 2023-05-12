from datetime import datetime
from app.helpers.spotify_helper import SpotifyHelper
from constants import SECONDS_IN_MONTH

from app.models import Track
from app import db

def get_tracks(track_ids: list[str]) -> list[Track]:
    ''' Returns a dictionary with keys of track ids containing track data '''
    track_dict = {}

    # check cache
    uncached_track_ids = []
    for track_id in track_ids:   
        track_cache = get_cached_track(track_id)

        # will be None if not found or out of date
        if not track_cache:
            uncached_track_ids.append(track_id)
        else:
            track_dict[track_id] = track_cache

    if len(uncached_track_ids) > 0: 
        spotify = SpotifyHelper()
        response = spotify.tracks(uncached_track_ids)

        for track in response['tracks']:     
            # track does not exist   
            if track is None:
                continue
            track_cache = Track(id = track['id'], name = track['name'], preview_url = track['preview_url'], image_url = track['album']['images'][0]['url'])
            track_dict[track_id] = track_cache
            db.session.add(track_cache)
        print(f'Caching tracks with ids: {uncached_track_ids}')

    db.session.commit()
    return track_dict
       
def get_cached_track(track_id: str) -> Track:
    track_cache: Track = Track.query.filter(Track.id == track_id).first()
    # check if the track_cache exists
    if not track_cache:
        return None
    
    # check if cache is old
    if (datetime.utcnow() - track_cache.last_cache_date).total_seconds() > SECONDS_IN_MONTH:
        print(f"Cache expired for track with track_id: {track_id}")
        return None
    
    # return just the lyrics 
    return track_cache
