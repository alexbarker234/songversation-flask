import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import request, url_for, session
import time
from config import Config

class UnauthorisedException(Exception):
    "Raised when user is not authorised"
    pass

class SpotifyHelper(spotipy.Spotify):
    '''
    Creates a wrapper class of spotipy.Spotify that checks if the user is logged in first 
    '''
    def __init__(self):
        session['token_info'], authorised = self.get_token()
        session.modified = True
        if not authorised:
            raise UnauthorisedException("The user is not logged in")
        super(SpotifyHelper, self).__init__(auth=session.get('token_info').get('access_token'))

    def get_token(self):
        '''
        Checks to see if token is valid and gets a new token if not
        '''
        token_valid = False
        token_info = session.get("token_info", {})

        # Checking if the session already has a token stored
        if not (session.get('token_info', False)):
            token_valid = False
            return token_info, token_valid

        # Checking if token has expired
        now = int(time.time())
        is_token_expired = session.get('token_info').get('expires_at') - now < 60

        # Refreshing token if it has expired
        if (is_token_expired):
            sp_oauth = self.create_spotify_oauth()
            token_info = sp_oauth.refresh_access_token(
                session.get('token_info').get('refresh_token'))

        token_valid = True
        return token_info, token_valid
    
    @staticmethod
    def create_spotify_oauth():
        return SpotifyOAuth(
            client_id=Config.SPOTIPY_CLIENT_ID,
            client_secret=Config.SPOTIPY_CLIENT_SECRET,
            redirect_uri=url_for('authorise', _external=True),
            scope="user-library-read user-top-read playlist-read-private user-read-private")
    
    @staticmethod
    def authorise():
        sp_oauth = SpotifyHelper.create_spotify_oauth()
        session.clear()
        code = request.args.get('code')
        token_info = sp_oauth.get_access_token(code)
        session["token_info"] = token_info

class SpotifyWebUserData: 
    def __init__(self):
        try:
            sp = SpotifyHelper()
            payload = sp.me()
            self.authorised = True
            self.username = payload['display_name']
            self.image_url = payload['images'][0]['url'] if len(
                payload['images']) > 0 else None
            self.id = payload['id']
        except UnauthorisedException:
            self.authorised = False