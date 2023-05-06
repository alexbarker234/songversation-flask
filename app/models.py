from app import db
from datetime import datetime

#class User(db.Model):

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

    order = db.Column(db.Integer)
    lyric = db.Column(db.String())
    track_lyric_id = db.Column(db.String(120)) # UNENFORCED FK
