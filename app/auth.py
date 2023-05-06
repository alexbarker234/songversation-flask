
from flask import session, redirect
from app import app
from app.helpers.spotify_helper import SpotifyHelper
from spotipy.exceptions import SpotifyException

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

    print("test1")

    SpotifyHelper.authorise()
    print("test2")

    # TEST IF THE USER HAS ACCESS
    try:
        SpotifyHelper().me()      
    except SpotifyException as e:
        if 'User not registered in the Developer Dashboard' in e.msg: 
            for key in list(session.keys()):
                session.pop(key)
            return f"Please ask Alex for access - send email associated with spotify account\nBack to <a href='/'>index</a>"
        
    return redirect("/")
