from app import db
from datetime import datetime

#each row is a given game done by a given user id, and holds the streak they had, and the date and time of the game
class Game(db.Model): 
    game_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120))
    score = db.Column(db.Integer)

    game_type = db.Column(db.String(120)) # current only supports playlist, but can be expanded to artist later
    game_object_id = db.Column(db.String(120)) # decided how to handle from game_type

    song_failed_on = db.Column(db.String(120))
    date_of_game = db.Column(db.DateTime, default=datetime.utcnow)
    
#user table that has all the user ids and when they joined
class User(db.Model):
    user_id = db.Column(db.String(120), primary_key=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

# cache some data locally to speed up load times (especially with lyrics)
class Playlist(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    last_cache_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    name = db.Column(db.String(120), nullable=True)
    owner_id = db.Column(db.String(120))
    track_count = db.Column(db.Integer)
    image_url = db.Column(db.String(), nullable=True)

class Track(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    last_cache_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    name = db.Column(db.String(120))
    preview_url = db.Column(db.String(), nullable=True)
    image_url = db.Column(db.String(), nullable=True)

    release_date = db.Column(db.DateTime)

class Artist(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    last_cache_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    name = db.Column(db.String(120), nullable=True)
    image_url = db.Column(db.String(), nullable=True)

class TrackArtist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lastCacheDate = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    artist_id = db.Column(db.String(120)) # UNENFORCED FK
    track_id = db.Column(db.String(120)) # UNENFORCED FK

class TrackLyrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_cache_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    lyric_count = db.Column(db.Integer)
    track_id = db.Column(db.String(120)) # UNENFORCED FK

class Lyric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_lyric_id = db.Column(db.Integer) # UNENFORCED FK

    order = db.Column(db.Integer)
    lyric = db.Column(db.String())
