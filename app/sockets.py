from datetime import datetime
import json
from flask import jsonify, session
from app import socketio
from flask_socketio import join_room, leave_room, send

from app.helpers.spotify_helper import SpotifyWebUserData
from app.models import Message, User

from app import db

rooms = {}


@socketio.on("message")
def message(data):
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return

    content = data['message']
    reciever_id = data['reciever']

    # add message to db
    msg_db = Message(sender_id=user_data.id, reciever_id=reciever_id,
                     content=content, date=datetime.utcnow())
    db.session.add(msg_db)
    db.session.commit()

    send(json.dumps({
        'author': { 'username': user_data.username, 'image': user_data.image_url },
        'message': { 'content': content, 'date': msg_db.date.strftime('%d %b %Y %H:%M')}
    }), room=make_room_name(user_data.id, reciever_id))

@socketio.on("join")
def connect(data):
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return
    
    reciever_id = data['reciever']

    join_room(make_room_name(user_data.id, reciever_id))

@socketio.on("disconnect")
def disconnect():
    print('disconnected')

def make_room_name(sender, reciever):
    return ''.join(sorted([sender, reciever]))