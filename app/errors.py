from flask import redirect, render_template
from app import app, db
from app.helpers.spotify_helper import SpotifyWebUserData

@app.errorhandler(404)
def not_found_error(error):
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return redirect("/")

    return render_template('errors/404.html', user_data=user_data), 404

@app.errorhandler(500)
def internal_error(error):
    user_data = SpotifyWebUserData()
    if not user_data.authorised:
        return redirect("/")

    db.session.rollback()
    return render_template('errors/500.html', user_data=user_data), 500