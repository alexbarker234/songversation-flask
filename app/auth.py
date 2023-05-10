
from flask import session, redirect
from app import app, db
from app.helpers.spotify_helper import SpotifyHelper
from spotipy.exceptions import SpotifyException
from app.models import User
from datetime import datetime

@app.route('/login')
def login():    
    sp_oauth = SpotifyHelper.create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/logout')
def logout():    
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

@app.route('/authorise')
def authorise():

    SpotifyHelper.authorise()
    
    # TEST IF THE USER HAS ACCESS
    try:
        SpotifyHelper().me() 
        spotify_helper = SpotifyHelper()     
        user_info = spotify_helper.me()

        user = User.query.filter(User.user_id == user_info['id']).first()

        if not user:
            # Create new user row if user does not exist in database
            user = User(user_id=user_info['id'], name=user_info['display_name'], date_joined=datetime.utcnow())
            db.session.add(user)
            db.session.commit()

    except SpotifyException as e:
        if 'User not registered in the Developer Dashboard' in e.msg: 
            for key in list(session.keys()):
                session.pop(key)
            return f"Please ask Alex for access - send email associated with spotify account\nBack to <a href='/'>index</a>"

        
    return redirect("/")
