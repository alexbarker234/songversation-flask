from datetime import datetime
import json
from flask import jsonify, request
from app.api.spotify_api import UNAUTHORISED_MESSAGE

from app.helpers.spotify_helper import SpotifyHelper, SpotifyWebUserData, UnauthorisedException

from app import app, db
from app.models import Friendship, Game, User

@app.route('/api/add-game', methods=['POST'])
def save_game():
    try:
        spotify_helper = SpotifyHelper()     
        user_info = spotify_helper.me()
        user_id = user_info['id']

        score = request.form['score']
        song_failed_on = request.form['last_song']
        game_type = request.form['game_type']
        game_object_id = request.form['game_object_id']

        # Create a new row in the Game table
        new_game = Game(user_id=user_id, score=score, song_failed_on=song_failed_on, game_type=game_type, game_object_id=game_object_id, date_of_game=datetime.utcnow())
        db.session.add(new_game)
        db.session.commit()

        print(f"Succesfully saved game for user: {user_info['display_name']} with score {score}")

        # 201 - Created
        return json.dumps({'success':True}), 201, {'ContentType':'application/json'} 
    except UnauthorisedException:
        return UNAUTHORISED_MESSAGE, 401
    
@app.route('/api/search-users')
def search_users():
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return 'Not authenticated', 401
    search_query = request.args.get('name')

    # get searching user
    current_user = User.query.filter(User.user_id == user_data.id).first()

    users = User.query.filter(User.user_id.ilike(f'%{search_query}%')).all()
    print(users)
    return jsonify([UserResponse.from_db_user(current_user, user).__dict__ for user in users])

@app.route('/api/add-friend')
def add_friend():
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return 'Not authenticated', 401
    
    friend_id = request.args.get('id')

    # stop user adding themselves
    if friend_id == user_data.id:
        return 'Cannot add self as friend', 400

    # verify friend user exist
    friend_user = User.query.filter(User.user_id == friend_id).one_or_none()
    if not friend_user:
        return 'User does not exist', 404

    # verify not already friend
    existing = Friendship.query.filter(Friendship.user_id == user_data.id and Friendship.friend_id == friend_id).one_or_none()
    if existing:
        return 'Already added as friend', 400
    
    # add friend
    friendship = Friendship(user_id = user_data.id, friend_id = friend_id)
    db.session.add(friendship)

    db.session.commit()
    return 'Success'

class UserResponse:
    @classmethod
    def from_db_user(cls, current_user: User, user: User) :
        self = cls()
        self.username = user.display_name
        self.is_self = current_user.user_id == user.user_id
        self.is_friend = user in current_user.friends
        self.image_url = user.image_url
        return self
