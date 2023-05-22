import asyncio
from datetime import datetime, timedelta
from typing import List
import aiohttp
from app.cache_manager.track_cache import get_tracks
from app.helpers.fetch_helper import fetch

from app.models import Lyric, TrackLyrics

from app import db

from constants import SECONDS_IN_DAY, SECONDS_IN_WEEK


async def get_lyrics(track_ids: list[str]) -> dict:
    ''' Returns a dictionary with keys of track ids containing arrays of lyrics '''
    track_lyrics = {}

    # init
    for track_id in track_ids:
        track_lyrics[track_id] = []

    # check cache
    uncached_track_ids = []
    for track_id in track_ids:
        cached_lyrics = _get_cached_track_lyrics(track_id)

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
                    fetch(
                        session, "https://spotify-lyric-api.herokuapp.com/?trackid=" + track_id, track_id)
                )
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # process responses
            for response in responses:
                track_lyrics[track_id] = _cache_lyrics(response)

        print("Caching lyrics for track_ids:" + str(uncached_track_ids))

    db.session.commit()
    return track_lyrics


def _get_cached_track_lyrics(track_id) -> list[str]:
    lyric_cache: TrackLyrics = TrackLyrics.query.filter(
        TrackLyrics.track_id == track_id).first()
    # check if the lyric_cache exists
    if not lyric_cache:
        return None

    lyric_lines_cache: list[Lyric] = Lyric.query.filter(
        Lyric.track_lyric_id == lyric_cache.id).order_by(Lyric.order.asc()).all()

    # check if cache is old

    # if the song just got relased, cache expires every day, otherwise every week
    cache_time = SECONDS_IN_WEEK
    time_since_release: timedelta = datetime.utcnow(
    ) - get_tracks([track_id])[track_id].release_date
    if time_since_release.total_seconds() < SECONDS_IN_WEEK:
        cache_time = SECONDS_IN_DAY

    if (datetime.utcnow() - lyric_cache.last_cache_date).total_seconds() > cache_time:
        print(f"Cache expired for lyrics with track_id: {track_id}")
        _delete_old_lyrics(lyric_lines_cache)
        return None
    # this case shouldnt happen - failsafe
    if lyric_cache.lyric_count != len(lyric_lines_cache):
        print(
            f"Mismatch between lyric count and lines recieved: count: {lyric_cache.lyric_count}, lines: {len(lyric_lines_cache)}")
        _delete_old_lyrics(lyric_lines_cache)
        return None
    if len(lyric_lines_cache) == 0:
        return None

    # return just the lyrics
    return [lyric_line.lyric for lyric_line in lyric_lines_cache]


def _cache_lyrics(response) -> List[str]:
    track_id = response['data']

    lyric_cache = TrackLyrics.query.filter(
        TrackLyrics.track_id == track_id).first()

    # initialise cache
    if not lyric_cache:
        lyric_cache = TrackLyrics(track_id=track_id)
        db.session.add(lyric_cache)
        # required in order to use lyric_cache.id
        db.session.flush()
        db.session.refresh(lyric_cache)

    lyricCount = 0

    lyric_list = []

    # No lyrics returns 404
    if not response['json']['error']:
        # turn response into list of each lyric
        for line in response['json']['lines']:
            if not line or not line['words'] or line['words'] == '♪':
                continue
            lyric_list.append(line['words'])
            lyric_line = Lyric(
                lyric=line['words'], order=lyricCount, track_lyric_id=lyric_cache.id)
            db.session.add(lyric_line)
            lyricCount += 1

    # update cache
    lyric_cache.lyric_count = lyricCount
    lyric_cache.last_cache_date = datetime.utcnow()

    return lyric_list


def _delete_old_lyrics(lyric_lines_cache):
    '''Does not commit'''
    for lyric in lyric_lines_cache:
        db.session.delete(lyric)

