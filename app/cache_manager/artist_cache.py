from datetime import datetime
import re
from typing import Tuple
from app.cache_manager.track_cache import get_tracks
from app.helpers.spotify_helper import SpotifyHelper
from constants import SECONDS_IN_DAY, SECONDS_IN_MONTH, SECONDS_IN_WEEK

from app.models import Artist, Track, TrackArtist
from app import db


def get_artist_tracks(artist_id: str) -> dict[str, Track]:
    ''' Returns a dictionary with keys of track ids containing track data '''
    track_dict: dict[str, Track] = {}

    # get artist
    artist = get_artist(artist_id)

    # check cache
    if artist.tracks_last_cache_date and (datetime.utcnow() - artist.tracks_last_cache_date).total_seconds() < SECONDS_IN_DAY:
        track_cache: list[Track] = db.session.query(Track).outerjoin(TrackArtist, Track.id == TrackArtist.track_id).filter(TrackArtist.artist_id == artist_id).all()
        track_dict = {track.id:track for track in track_cache}
    else:
        sp = SpotifyHelper()
        albums = sp.all_artist_albums(artist_id, ['album', 'single'], limit = 50)

        # filter remixes, alt versions, acoustics, etc out
        albums = [album for album in albums if not (re.search('[\[\(].* ?(?:Rework|Remix|Version|Acoustic|Acapella|Unplugged|Live|Instrumental)[\]\)]', album['name'], re.IGNORECASE))]        
        
        tracks: list[dict] = []
        for album in albums:
            tracks += sp.all_album_tracks(album['id'])

        # remove duplicate tracks
        unique_tracks = {}
        for track in tracks:
            if track['name'] not in unique_tracks:
                unique_tracks[track['name']] = track

        unique_tracks = list(unique_tracks.values())
        track_ids = [track['id'] for track in unique_tracks]

        # cache all tracks
        track_dict = get_tracks(track_ids)
        # update last cache date
        artist.tracks_last_cache_date = datetime.utcnow()

    db.session.commit()

    return track_dict

def get_artist(artist_id: str) -> Artist:
    # check cache
    valid_cache, artist_cache = _get_cached_artist(artist_id)

    if not valid_cache:
        spotify = SpotifyHelper()
        response = spotify.artist(artist_id)
        new_artist_cache = _cache_artist(response, artist_cache)
        db.session.commit()
        return new_artist_cache
    else:
        db.session.commit()
        return artist_cache

def _get_cached_artist(artist_id: str) -> Tuple[bool, Artist]:
    artist_cache: Artist = Artist.query.filter(Artist.id == artist_id).first()

    # check if the track_cache exists
    if not artist_cache:
        return False, None

    # check if cache is old
    if (datetime.utcnow() - artist_cache.last_cache_date).total_seconds() > SECONDS_IN_WEEK:
        # print(f"Cache expired for track with track_id: {track_id}")
        return False, artist_cache

    # return just the lyrics
    return True, artist_cache

def _cache_artist(artist_response: dict, existing_cache: Artist) -> Artist:
    # create cache object
    artist_cache = Artist(id=artist_response['id'],
                        name=artist_response['name'],
                        image_url=artist_response['images'][0]['url'],
                        last_cache_date=datetime.utcnow())

    # modify existing cache
    if existing_cache:
        existing_cache.name = artist_cache.name
        existing_cache.last_cache_date = artist_cache.last_cache_date
        existing_cache.image_url = artist_cache.image_url
        return existing_cache
    # add new cache
    else:
        db.session.add(artist_cache)
        return artist_cache