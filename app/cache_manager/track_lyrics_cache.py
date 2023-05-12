import asyncio
from datetime import datetime
import aiohttp
from app.helpers.fetch_helper import fetch

from app.models import Lyric, TrackLyrics

from app import db

from constants import SECONDS_IN_DAY

async def get_lyrics(track_ids: list[str]) -> dict:
    ''' Returns a dictionary with keys of track ids containing arrays of lyrics '''
    track_lyrics = {}

    # init
    for track_id in track_ids:
        track_lyrics[track_id] = []

    # check cache
    uncached_track_ids = []
    for track_id in track_ids:   
        cached_lyrics = get_cached_track_lyrics(track_id)

        # will be None if not found or out of date
        if not cached_lyrics:
            uncached_track_ids.append(track_id)
        else:
            track_lyrics[track_id] = cached_lyrics

    if len(uncached_track_ids) > 0: 
        # asynchronously get all uncached lyrics
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

                lyric_cache = TrackLyrics.query.filter(TrackLyrics.track_id == track_id).first()

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
                        track_lyrics[track_id].append(line['words'])
                        lyric_line = Lyric(lyric = line['words'], order = lyricCount, track_lyric_id = lyric_cache.id)
                        db.session.add(lyric_line)
                        lyricCount += 1

                # update cache
                lyric_cache.lyric_count = lyricCount
                lyric_cache.last_cache_date = datetime.utcnow()

                print("Caching lyrics for track_id:" + track_id )

    db.session.commit()
    return track_lyrics 

def get_cached_track_lyrics(track_id) -> list[str]:
    lyric_cache: TrackLyrics = TrackLyrics.query.filter(TrackLyrics.track_id == track_id).first()
    # check if the lyric_cache exists
    if not lyric_cache:
        return None
    
    lyric_lines_cache: list[Lyric] = Lyric.query.filter(Lyric.track_lyric_id == lyric_cache.id).order_by(Lyric.order.asc()).all()

    # check if cache is old
    if (datetime.utcnow() - lyric_cache.last_cache_date).total_seconds() > SECONDS_IN_DAY:
        print(f"Cache expired for lyrics with track_id: {track_id}")
        delete_old_lyrics(lyric_lines_cache)
        return None
    # this case shouldnt happen - failsafe
    if lyric_cache.lyric_count != len(lyric_lines_cache):
        print(f"Mismatch between lyric count and lines recieved: count: {lyric_cache.lyric_count}, lines: {len(lyric_lines_cache)}")
        delete_old_lyrics(lyric_lines_cache)
        return None
    if len(lyric_lines_cache) == 0:
        return None

    # return just the lyrics 
    return [lyric_line.lyric for lyric_line in lyric_lines_cache]

def delete_old_lyrics(lyric_lines_cache):
    '''Does not commit'''
    for lyric in lyric_lines_cache:
        db.session.delete(lyric)
