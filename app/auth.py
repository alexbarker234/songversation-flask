
from flask import session, redirect
from app import app
from app.helpers.spotify_helper import SpotifyHelper

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
    return redirect("/")
