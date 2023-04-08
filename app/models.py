from app import db
from datetime import datetime

#class User(db.Model):

# cache some data locally to speed up load times (especially with lyrics)
class PlaylistCache(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    lastCacheDate = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    name = db.Column(db.String(120), nullable=True)
    ownerID = db.Column(db.Integer)
    trackCount = db.Column(db.Integer)

class TrackCache(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    lastCacheDate = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    lyrics = db.Column(db.String(), nullable=True)
    name = db.Column(db.String(120), nullable=True)
