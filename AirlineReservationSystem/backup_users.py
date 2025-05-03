import json
from app import app
from models import User

with app.app_context():
    users = User.query.all()
    user_data = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password_hash': user.password_hash,
            'is_admin': user.is_admin,
            'frequent_flyer_points': user.frequent_flyer_points
        } for user in users
    ]
    with open('users_backup.json', 'w') as f:
        json.dump(user_data, f, indent=2)
    print("Users backed up to users_backup.json")