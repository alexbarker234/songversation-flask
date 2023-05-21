import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import request, url_for, session
import time
from app.cache_manager import user_cache
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

        '''cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
             raise UnauthorisedException("The user is not logged in")
        super(SpotifyHelper, self).__init__(auth_manager=auth_manager)'''

    # FETCHING

    def all_album_tracks(self, album_id: str, limit: int = 50) -> list[dict]:
        '''
        Get Spotify catalog information about an album's tracks

        Parameters:

        - album_id - the album ID, URI or URL
        - limit - the number of items to return
        - offset - the index of the first item to return
        '''

        results = []
        tracks = self.album_tracks(album_id, limit = limit)
        while tracks:
            for album in tracks['items']:
                results.append(album)
            if tracks['next']:
                tracks = self.next(tracks)
            else:
                tracks = None
        return results

    def all_artist_albums(self, artist_id: str, album_types: list[str]|str, limit: int) -> list[dict]:
        '''
        Get Spotify catalog information about an artist's albums

        Parameters:

        - artist_id - the artist ID, URI or URL
        - album_type - 'album', 'single', 'appears_on', 'compilation' or a list of multiple values
        - limit - the number of albums to return
        '''
        results = []

        # spotipy doesn't seem to allow doing all types in one request
        if isinstance(album_types, str):
            album_types = [album_types]

        # request albums for each type
        for album_Type in album_types:
            albums = self.artist_albums(artist_id, limit = limit, album_type=album_Type)
            while albums:
                for album in albums['items']:
                    results.append(album)
                if albums['next']:
                    albums = self.next(albums)
                else:
                    albums = None

        return results

    # AUTHORISATION

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
        is_token_expired = session.get(
            'token_info').get('expires_at') - now < 60

        # Refreshing token if it has expired
        if (is_token_expired):
            sp_oauth = self.create_spotify_oauth()
            token_info = sp_oauth.refresh_access_token(
                session.get('token_info').get('refresh_token'))

        token_valid = True
        return token_info, token_valid

    def tracks(self, track_ids: list[str]):
        # split list
        max_size = 50
        to_request = []
        for i in range(0, len(track_ids), max_size):
            to_request.append(track_ids[i:i + max_size])

        final = {}
        for track_id_list in to_request:
            response = super(SpotifyHelper, self).tracks(track_id_list)
            if 'tracks' not in final:
                final = response
            else:
                final['tracks'] += response['tracks']

        return final

    @staticmethod
    def create_spotify_oauth():
        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        return SpotifyOAuth(
            client_id=Config.SPOTIPY_CLIENT_ID,
            client_secret=Config.SPOTIPY_CLIENT_SECRET,
            redirect_uri=url_for('authorise', _external=True),
            scope="user-library-read user-top-read playlist-read-private user-read-private user-follow-read",
            cache_handler=cache_handler,
            show_dialog=True)

    @staticmethod
    def authorise():
        sp_oauth = SpotifyHelper.create_spotify_oauth()
        session.pop("token_info", None)
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
                payload['images']) > 0 else url_for('static', filename='defaultPfp.png')
            self.id = payload['id']

            # CACHE DATA IN DB
            user_cache.update_cache(self)
        except UnauthorisedException:
            self.authorised = False
