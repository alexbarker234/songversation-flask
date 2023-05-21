from app import db
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, object_mapper
from typing import List

from app.exceptions import InvalidFriendException, UserNotFoundException

# Type hinting/mapping docs:
# https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html

# each row is a given game done by a given user id, and holds the streak they had, and the date and time of the game


class Game(db.Model):
    game_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120))
    score = db.Column(db.Integer)

    # current only supports playlist, but can be expanded to artist later
    game_type = db.Column(db.String(120))
    # decided how to handle from game_type
    game_object_id = db.Column(db.String(120))

    song_failed_on: str = db.Column(db.String(120))
    date_of_game: datetime = db.Column(db.DateTime, default=datetime.utcnow)

# a one way friendship


class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id: str = db.Column(db.String(120))
    friend_id: str = db.Column(db.String(120))

# user table that has all the user ids and when they joined
class User(db.Model):
    user_id: str = db.Column(db.String(120), primary_key=True)
    date_joined: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    friends = relationship(
        'User', secondary='friendship',
        primaryjoin=(Friendship.user_id == user_id),
        secondaryjoin=(Friendship.friend_id == user_id)
    )

    # CACHED SPOTIFY DATA
    display_name: str = db.Column(db.String(120))
    image_url: str = db.Column(db.String(), nullable=True)

    def add_friend(self, friend_id):
        # stop user adding themselves
        if friend_id == self.user_id:
            raise InvalidFriendException('Cannot add self as friend')

        # verify friend user exist
        friend_user = User.query.filter(User.user_id == friend_id).one_or_none()
        if not friend_user:
            raise UserNotFoundException('User does not exist')

        # verify not already friend
        existing = Friendship.query.filter(Friendship.user_id == self.user_id and Friendship.friend_id == friend_id).one_or_none()
        if existing:
           raise InvalidFriendException('Already added as friend')
        
        # add friend
        friendship = Friendship(user_id = self.user_id, friend_id = friend_id)
        db.session.add(friendship)
        db.session.commit()

    def remove_friend(self, friend_id):
        # stop user removing themselves
        if friend_id == self.user_id:
            raise InvalidFriendException('Cannot remove self as friend')

        # verify friend user exist
        friend_user = User.query.filter(User.user_id == friend_id).one_or_none()
        if not friend_user:
            raise UserNotFoundException('User does not exist')

        # verify not already friend
        existing = Friendship.query.filter(Friendship.user_id == self.user_id and Friendship.friend_id == friend_id).one_or_none()
        if not existing:
           raise InvalidFriendException('User is not friends')
        
        # remove friend
        db.session.delete(existing)
        db.session.commit()

# cache some data locally to speed up load times (especially with lyrics)
class Playlist(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    last_cache_date = db.Column(
        db.DateTime, index=True, default=datetime.utcnow)

    name = db.Column(db.String(120), nullable=True)
    owner_id = db.Column(db.String(120))
    track_count = db.Column(db.Integer)
    image_url = db.Column(db.String(), nullable=True)


class Artist(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    last_cache_date = db.Column(
        db.DateTime, index=True, default=datetime.utcnow)
    tracks_last_cache_date = db.Column(db.DateTime, index=True)

    name = db.Column(db.String(120), nullable=True)
    image_url = db.Column(db.String(), nullable=True)


class TrackArtist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lastCacheDate = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    artist_id = db.Column(db.String(120))  # UNENFORCED FK
    track_id = db.Column(db.String(120))  # UNENFORCED FK

class Track(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    last_cache_date = db.Column(
        db.DateTime, index=True, default=datetime.utcnow)

    name = db.Column(db.String(120))
    preview_url = db.Column(db.String(), nullable=True)
    image_url = db.Column(db.String(), nullable=True)

    release_date = db.Column(db.DateTime)

    artists: Mapped[List[Artist]] = relationship('Artist', secondary="track_artist",
                                                 primaryjoin='Track.id == TrackArtist.track_id',
                                                 secondaryjoin='TrackArtist.artist_id == Artist.id')

class TrackLyrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_cache_date = db.Column(
        db.DateTime, index=True, default=datetime.utcnow)

    lyric_count = db.Column(db.Integer)
    track_id = db.Column(db.String(120))  # UNENFORCED FK


class Lyric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_lyric_id = db.Column(db.Integer)  # UNENFORCED FK

    order = db.Column(db.Integer)
    lyric = db.Column(db.String())
