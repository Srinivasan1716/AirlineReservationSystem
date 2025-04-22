import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from datetime import datetime
import razorpay
from dotenv import load_dotenv
from recommend import get_recommendations
from utils import send_booking_confirmation

# Load environment variables from .env file
load_dotenv()

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
app.config['MAIL_USERNAME'] = 'balas07alab@gmail.com'
app.config['MAIL_PASSWORD'] = 'dowm rjvc yxbx gyot'
app.config['MAIL_DEFAULT_SENDER'] = 'balakumaran2470050@ssn.edu.in'
mail = Mail(app)

# Razorpay configuration (Test Mode)
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")  # Loaded from .env
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")  # Loaded from .env
if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    raise ValueError("Razorpay API keys not found in environment variables")
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

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
    
    # Get month from travel_date
    travel_month = datetime.strptime(travel_date, "%Y-%m-%d").strftime("%B")
    
    # Get recommendations
    recommendations = get_recommendations(budget, travel_month, data.get("highlights", None), country)
    return jsonify(recommendations)

# Create temporary booking
@app.route("/create_booking", methods=["POST"])
def create_booking():
    try:
        from data import bookings, Booking
        from models import Passenger
        form_data = request.form
        
        # Extract passenger data
        passengers = []
        for i in range(int(form_data.get("passengers_count", 1))):
            passenger = Passenger(
                first_name=form_data.get(f"passengers[{i}][first_name]"),
                last_name=form_data.get(f"passengers[{i}][last_name]"),
                date_of_birth=form_data.get(f"passengers[{i}][date_of_birth]"),
                passport_number=form_data.get(f"passengers[{i}][passport_number]"),
                address=form_data.get(f"passengers[{i}][address]")
            )
            passengers.append(passenger)
        
        # Create booking
        booking = Booking(
            id=len(bookings) + 1,
            flight_id=int(form_data.get("flight_id")),
            user_id=current_user.id,
            passengers=passengers,
            seat_number=form_data.get("selected_seats").split(","),
            price_paid=float(form_data.get("amount")),
            status="Pending",
            booking_reference="REF" + str(len(bookings) + 1).zfill(6)
        )
        bookings.append(booking)
        return jsonify({"booking_id": booking.id})
    except Exception as e:
        logging.error(f"Error creating booking: {str(e)}")
        return jsonify({"error": "Failed to create booking"}), 500

# Create Razorpay order
@app.route("/create_order", methods=["POST"])
def create_order():
    try:
        data = request.form
        amount = int(float(data.get("amount")) * 100)  # Convert to paise
        currency = "INR"
        order_data = {
            "amount": amount,
            "currency": currency,
            "payment_capture": 1  # Auto-capture payment
        }
        order = razorpay_client.order.create(data=order_data)
        return jsonify({
            "order_id": order["id"],
            "amount": amount,
            "currency": currency,
            "key_id": RAZORPAY_KEY_ID
        })
    except Exception as e:
        logging.error(f"Error creating Razorpay order: {str(e)}")
        return jsonify({"error": "Failed to create order"}), 500

# Verify payment
@app.route("/verify_payment", methods=["POST"])
def verify_payment():
    try:
        payment_id = request.form.get("razorpay_payment_id")
        order_id = request.form.get("razorpay_order_id")
        signature = request.form.get("razorpay_signature")
        
        params_dict = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        }
        
        # Verify signature
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Payment is successful, proceed with booking
        booking_id = request.form.get("booking_id")
        from data import bookings
        for booking in bookings:
            if booking.id == int(booking_id):
                booking.status = "Confirmed"
                booking.payment_id = payment_id  # Store payment ID
                send_booking_confirmation(booking)
                break
        return redirect(url_for("booking_confirm", booking_id=booking_id))
    except razorpay.errors.SignatureVerificationError:
        logging.error("Payment signature verification failed")
        from data import bookings
        booking_id = request.form.get("booking_id")
        for booking in bookings:
            if booking.id == int(booking_id):
                booking.status = "Failed"
                break
        return render_template("payment_failed.html", error_message="Payment verification failed")
    except Exception as e:
        logging.error(f"Error verifying payment: {str(e)}")
        return render_template("payment_failed.html", error_message="Payment processing failed")

if __name__ == "__main__":
    app.run(debug=True)