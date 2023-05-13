# Songversation - CITS3403 Project

A lyric guessing game - powered by Flask with [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/) and [Spotify Lyrics API](https://github.com/akashrchandran/spotify-lyrics-api)

## Group Members
- Alex Barker (23152009)
- Gihad Coorey (2309188)
- Daniel Lindsay (23164864)

## Hosted on [Render.com](https://render.com)
https://songversation.onrender.com/

- As the public app is under a Spotify development plan - You will need to request access from [Alex](https://github.com/alexbarker234) - send the email associated with your Spotify Account

## Purpose
Songversation is a music guessing game that allows users to log into their Spotify account and select an artist or playlist. Once they have made their selection, the game will randomly choose a track from that selection, and the lyrics to that track will appear on the screen one by one. The user's task is to guess which track it is as quickly as possible by selecting the correct title from a list of options after each lyric is displayed. 

The game is designed to test the user's knowledge of the lyrics of their chosen artist or playlist and provide them with a fun and challenging way to engage with their favorite music, compared to Heardle or Lyricle- which use random songs that you may have never heard of.

## Architecture

TODO
Add game mode descriptions to index.html
Maybe make game mode descriptions fade in slowly upon hover rather than an instant transtion upon hover


## Requirements
    Python (confirmed working with 3.10)
    Sqlite3

## Running Locally
1. Clone the repo
2. Create the python virtual environment by running command: 
    ```
    python -m venv venv
    ```
3. Enter the venv by running command:
    
    **Windows:**
    ```
    ./venv/Scripts/activate
    ```
    **MacOS/Linux**
    ```
    source venv/bin/activate
    ```
    
4. Install the requirements through 
    ```
    pip install -r requirements.txt
    ```
5. Create the .env file in the structure of 
    ```
    SECRET_KEY=<anything>
    SPOTIPY_CLIENT_ID=<YOUR-SPOTIFY-CLIENT-ID>
    SPOTIPY_CLIENT_SECRET=<YOUR-SPOTIFY-CLIENT-ID>
    SPOTIPY_REDIRECT_URI=<anything>
    ```
    - Creating the Spotify App in [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
        - You will need to get the Spotify Client ID & Secret to fill out the .env
        - The SPOTIPY_REDIRECT_URI is required by spotipy - the actual redirect is dynamically determined in the code so can be anything in the env 
        - You need to configure the Redirect URIs to include
            - http://127.0.0.1:5000/authorise
            - http://localhost:5000/authorise
6. Initialise the database
    ```
    flask db upgrade
    ```

7. Start the app through
    ```
    flask run
    ```

## Unit Tests
TODO

