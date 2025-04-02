import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
csrf = CSRFProtect(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import routes after creating app to avoid circular imports
from routes import *
from models import User

@login_manager.user_loader
def load_user(user_id):
    from data import users
    for user in users:
        if user.id == int(user_id):
            return user
    return None

# Initialize in-memory data structures
import data
data.initialize_data()
