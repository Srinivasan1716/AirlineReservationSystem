import json
from app import app
from extensions import db
from data import initialize_data
from models import User
from datetime import datetime

with app.app_context():
    db.drop_all()
    db.create_all()
    
    # Restore backed-up users
    try:
        with open('users_backup.json', 'r') as f:
            user_data = json.load(f)
        for user_info in user_data:
            user = User(
                id=user_info['id'],
                username=user_info['username'],
                email=user_info['email'],
                password_hash=user_info['password_hash'],
                is_admin=user_info['is_admin'],
                frequent_flyer_points=user_info['frequent_flyer_points'],
                created_at=datetime.utcnow()  # Set created_at for existing users
            )
            db.session.add(user)
        db.session.commit()
        print("Restored users from backup")
    except FileNotFoundError:
        print("No user backup found, initializing with sample data")
    
    initialize_data()
    print("Database initialized with sample data.")