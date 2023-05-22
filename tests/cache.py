
import os
import unittest
from app import app, db
from app.models import Lyric, TrackLyrics
from app.cache_manager.track_lyrics_cache import _cache_lyrics
from app.cache_manager.artist_cache import _cache_artist, _get_cached_artist
import datetime


class CacheTestCase(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.app = app.test_client()


        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_artist_cache(self):

        artist_id = 00000

        mock_response = {
            "external_urls": {
                "spotify": "string"
            },
            "followers": {
                "href": "string",
                "total": 0
            },
            "genres": [
                "Prog rock",
                "Grunge"
            ],
            "href": "string",
            "id": artist_id,
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
                    "height": 300,
                    "width": 300
                }
            ],
            "name": "Artist 1",
            "popularity": 0,
            "type": "artist",
            "uri": "string"
        }

        # check valid retrieval from db cache
        _cache_artist(mock_response, None)

        valid, cached = _get_cached_artist(artist_id)

        self.assertTrue(valid)
        self.assertTrue(cached.name == "Artist 1")

        # check valid identification of expired cache
        month_ago = subtract_month(datetime.datetime.utcnow())
        cached.last_cache_date = month_ago

        valid, cached = _get_cached_artist(artist_id)

        self.assertFalse(valid)
        self.assertTrue(cached.name == "Artist 1")

    def test_lyric_cache(self):
        track_id = '5f8eCNwTlr0RJopE9vQ6mB'
        lyrics = Lyric.query.filter(Lyric.track_lyric_id == track_id).order_by(Lyric.order.asc()).all()
        self.assertTrue(len(lyrics) == 0)

        cached =_cache_lyrics(MOCK_LYRIC_RESPONSE)
        db.session.commit()

        # get the cached lyrics
        lyric_cache: TrackLyrics = TrackLyrics.query.filter( TrackLyrics.track_id == track_id).first()
        lyrics = Lyric.query.filter(Lyric.track_lyric_id == lyric_cache.id).order_by(Lyric.order.asc()).all()
        for i, lyric in enumerate(lyrics):
            self.assertTrue(cached[i] == lyric.lyric)


def subtract_month(dt):
    year = dt.year - 1 if dt.month == 1 else dt.year
    month = dt.month - 1 if dt.month > 1 else 12

    if dt.month == 3 and dt.day == 29:  # February 29th handling
        day = 28
    else:
        day = dt.day

    return datetime.datetime(year, month, day, dt.hour, dt.minute, dt.second, dt.microsecond)


MOCK_LYRIC_RESPONSE = {
    'data': '5f8eCNwTlr0RJopE9vQ6mB',
    'json': {
        "error": False,
        "syncType": "LINE_SYNCED",
        "lines": [
            {
                "startTimeMs": "950",
                "words": "One, two, three, four",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "4030",
                "words": "Ooh-ooh, ooh-ooh-ooh",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "6520",
                "words": "\u266a",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "10530",
                "words": "Every time you come around, you know I can't say no",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "18080",
                "words": "Every time the sun goes down, I let you take control",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "25650",
                "words": "I can feel the paradise before my world implodes",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "32850",
                "words": "And tonight had something wonderful",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "39270",
                "words": "My bad habits lead to late nights endin' alone",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "43220",
                "words": "Conversations with a stranger I barely know",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "47010",
                "words": "Swearin' this will be the last, but it probably won't",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "50610",
                "words": "I got nothin' left to lose, or use, or do",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "54740",
                "words": "My bad habits lead to wide eyes stare into space",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "58460",
                "words": "And I know I'll lose control of the things that I say",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "62220",
                "words": "Yeah, I was lookin' for a way out, now I can't escape",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "66030",
                "words": "Nothin' happens after two, it's true",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "69130",
                "words": "It's true, my bad habits lead to you",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "72510",
                "words": "Ooh-ooh, ooh-ooh-ooh",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "77470",
                "words": "My bad habits lead to you",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "80220",
                "words": "Ooh-ooh, ooh-ooh-ooh",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "85130",
                "words": "My bad habits lead to you",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "88530",
                "words": "Every pure intention ends when the good times start",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "89800",
                "words": "\u266a",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "96080",
                "words": "Fallin' over everything to reach the first time's spark",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "103850",
                "words": "It started under neon lights, and then it all got dark",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "111290",
                "words": "I only know how to go too far",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "117340",
                "words": "My bad habits lead to late nights endin' alone",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "121390",
                "words": "Conversations with a stranger I barely know",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "125170",
                "words": "Swearin' this will be the last, but it probably won't",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "129080",
                "words": "I got nothin' left to lose, or use, or do",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "132780",
                "words": "My bad habits lead to wide eyes stare into space",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "136700",
                "words": "And I know I'll lose control of the things that I say",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "140130",
                "words": "Yeah, I was lookin' for a way out, now I can't escape",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "144270",
                "words": "Nothin' happens after two, it's true",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "147360",
                "words": "It's true, my bad habits lead to you",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "150670",
                "words": "Ooh-ooh, ooh-ooh-ooh",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "155420",
                "words": "My bad habits lead to you",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "158240",
                "words": "Ooh-ooh, ooh-ooh-ooh",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "164720",
                "words": "We took the long way 'round",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "172170",
                "words": "And burned 'til the fun ran out, now",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "178210",
                "words": "My bad habits lead to late nights endin' alone",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "182350",
                "words": "Conversations with a stranger I barely know",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "186180",
                "words": "Swearin' this will be the last, but it probably won't",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "190030",
                "words": "I got nothin' left to lose, or use, or do",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "193690",
                "words": "My bad habits lead to wide eyes stare into space",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "197550",
                "words": "And I know I'll lose control of the things that I say",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "201060",
                "words": "Yeah, I was lookin' for a way out, now I can't escape",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "205210",
                "words": "Nothin' happens after two, it's true",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "208280",
                "words": "It's true, my bad habits lead to you",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "211670",
                "words": "Ooh-ooh, ooh-ooh-ooh",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "216490",
                "words": "My bad habits lead to you",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "219310",
                "words": "Ooh-ooh, ooh-ooh-ooh",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "224100",
                "words": "My bad habits lead to you",
                "syllables": [

                ],
                "endTimeMs":"0"
            },
            {
                "startTimeMs": "226050",
                "words": "",
                "syllables": [

                ],
                "endTimeMs":"0"
            }
        ]
    }
}
