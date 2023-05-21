from datetime import datetime
from app.models import User
from app import db


def update_cache(user):
    user_db: User = User.query.filter(User.user_id == user.id).first()
    if not user_db:
        print(f"Registering user '{user.username}' with id '{user.id}'")
        user_db = User(user_id=user.id, date_joined=datetime.utcnow())
        db.session.add(user_db)
    
    user_db.image_url = user.image_url
    user_db.display_name = user.username
    db.session.commit()
