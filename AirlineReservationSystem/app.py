import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from datetime import datetime
from recommend import get_recommendations
from utils import send_booking_confirmation  # Import from utils

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())
csrf = CSRFProtect(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'airwaysabc@gmail.com'
app.config['MAIL_PASSWORD'] = 'pyef tixk gwkf padm'
app.config['MAIL_DEFAULT_SENDER'] = 'balakumaran2470050@ssn.edu.in'
mail = Mail(app)

# Import routes after creating app to avoid circular imports
from routes import *
from models import User

# Register booking routes
from booking import register_routes
register_routes(app)

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

# Add recommendation route
@app.route("/recommendations", methods=["POST"])
def get_travel_recommendations():
    data = request.form
    country = data.get("country", "India")
    budget = float(data.get("budget", 0))
    travel_date = data.get("travel_date")  # Format: YYYY-MM-DD
    highlights = data.get("highlights", None)
    
    # Get month from travel_date
    travel_month = datetime.strptime(travel_date, "%Y-%m-%d").strftime("%B")
    
    # Get recommendations
    recommendations = get_recommendations(budget, travel_month, highlights, country)
    return jsonify(recommendations)

if __name__ == "__main__":
    app.run(debug=True)