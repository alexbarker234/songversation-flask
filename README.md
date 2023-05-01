# Songversation - CITS3403 Project

A lyric guessing game - powered by Flask with [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/) and [Spotify Lyrics API](https://github.com/akashrchandran/spotify-lyrics-api)

## Group Members
- Alex Barker (23152009)
- Gihad Coorey (2309188)
- Daniel Lindsay (23164864)

## Running Locally
1. Clone the repo
2. Create the python virtual environment by running command: 
    ```
    python -m venv <name-of-venv>
    ```
3. Enter the venv by running command:
    
    **Windows:**
    ```
    ./<venv>/Scripts/activate
    ```
    **MacOS/Linux**
    ```
    source <name-of-venv>/bin/activate
    ```
    
4. Install the requirements through 
    ```
    pip install -r requirements.txt
    ```
5. Create the .env file in the structure of 
    ```
    SECRET_KEY=<anything>
    SPOTIPY_CLIENT_ID=x
    SPOTIPY_CLIENT_SECRET=x
    SPOTIPY_REDIRECT_URI=http://localhost:5000/redirect
    ```
    - You will need to get the Spotify Client ID & Secret by going to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and creating a Spotify app

6. Initialise the database
    ```
    flask db init
    flask db upgrade
    ```

7. Start the app through
    ```
    flask run
    ```
