
from flask import session, redirect
from app import app, db
from app.cache_manager import user_cache
from app.helpers.spotify_helper import SpotifyHelper, SpotifyWebUserData
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
        spotify_helper = SpotifyHelper()     
        user_info = spotify_helper.me()

        # add user to database on first log in
        SpotifyWebUserData()

    except SpotifyException as e:
        if 'User not registered in the Developer Dashboard' in e.msg: 
            for key in list(session.keys()):
                session.pop(key)
            return f"Please ask Alex for access - send email associated with spotify account\nBack to <a href='/'>index</a>"

        
    return redirect("/")
