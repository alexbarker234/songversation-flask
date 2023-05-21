from datetime import datetime
from app.models import User
from app import db


def update_cache(user):
    user_db: User = User.query.filter(User.user_id == user.id).first()
    if not user_db:
        print("ERROR FINDING USER TO UPDATE CACHE")
        return
    
    user_db.image_url = user.image_url
    user_db.display_name = user.username
    db.session.commit()
