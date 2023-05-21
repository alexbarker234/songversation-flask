from datetime import datetime
import json
from flask import jsonify, request
from app.api.spotify_api import UNAUTHORISED_MESSAGE
from app.exceptions import InvalidFriendException, UserNotFoundException, UnauthorisedException

from app.helpers.spotify_helper import SpotifyHelper, SpotifyWebUserData

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
    return jsonify({'users':[UserResponse.from_db_user(current_user, user).__dict__ for user in users]})

@app.route('/api/add-friend', methods=['POST'])
def add_friend():
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return 'Not authenticated', 401
    
    friend_id = request.json.get('id')
    if not friend_id:
        return 'No user id included', 400

    # get current user
    user: User = User.query.filter(User.user_id == user_data.id).one_or_none()
    try:
        user.add_friend(friend_id)
    except UserNotFoundException as e:
        return str(e), 404
    except InvalidFriendException as e:
        return str(e), 400
    
    return 'Success'

class UserResponse:
    @classmethod
    def from_db_user(cls, current_user: User, user: User) :
        self = cls()
        self.id = user.user_id
        self.username = user.display_name
        self.is_self = current_user.user_id == user.user_id
        self.is_friend = user in current_user.friends
        self.image_url = user.image_url
        return self
