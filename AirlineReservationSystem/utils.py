from datetime import datetime, timedelta
import random
import string
from data import airports, get_airport_city
from flask import current_app
from flask_mail import Message

def format_datetime(dt):
    """Format a datetime object to a user-friendly string"""
    if not dt:
        return ""
    return dt.strftime("%a, %d %b %Y, %H:%M")

def format_date(dt):
    """Format a date to a user-friendly string"""
    if not dt:
        return ""
    if isinstance(dt, datetime):
        dt = dt.date()
    return dt.strftime("%d %b %Y")

def format_time(dt):
    """Format a time to a user-friendly string"""
    if not dt:
        return ""
    return dt.strftime("%H:%M")

def format_duration(minutes):
    """Format duration in minutes to a user-friendly string"""
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins}m"

def calculate_flight_duration(departure, arrival):
    """Calculate the duration between departure and arrival"""
    duration = arrival - departure
    return duration.total_seconds() // 60  # Duration in minutes

def generate_booking_reference(length=6):
    """Generate a random booking reference"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def format_price(price):
    if price is not None:
        return f"\u20B9{price:.2f}"
    return "Not available"

def get_seat_class(seat):
    """Determine the class of a seat based on its row number"""
    if not seat:
        return "Economy"
    
    # Extract row number from seat (e.g., "12A" -> 12)
    try:
        row = int(''.join(filter(str.isdigit, seat)))
    except:
        return "Economy"
    
    if row <= 2:
        return "First Class"
    elif row <= 10:
        return "Business Class"
    else:
        return "Economy"

def get_route_display(origin_code, destination_code):
    """Get a display-friendly route string"""
    origin_city = get_airport_city(origin_code)
    destination_city = get_airport_city(destination_code)
    return f"{origin_city} ({origin_code}) → {destination_city} ({destination_code})"

def get_flight_status_badge_class(status):
    """Return the appropriate Bootstrap badge class for a flight status"""
    status_classes = {
        "Scheduled": "bg-primary",
        "On Time": "bg-success",
        "Delayed": "bg-warning",
        "Cancelled": "bg-danger",
        "Boarding": "bg-info",
        "In Air": "bg-info",
        "Landed": "bg-secondary",
        "Completed": "bg-dark"
    }
    return status_classes.get(status, "bg-secondary")

def get_booking_status_badge_class(status):
    """Return the appropriate Bootstrap badge class for a booking status"""
    status_classes = {
        "Confirmed": "bg-success",
        "Pending": "bg-warning",
        "Cancelled": "bg-danger",
        "Checked-in": "bg-info",
        "Completed": "bg-dark"
    }
    return status_classes.get(status, "bg-secondary")

def send_booking_confirmation(user, booking, mail):
    """Send a booking confirmation email to the user"""
    from data import get_flight_by_id
    flight = get_flight_by_id(booking.flight_id)
    msg = Message(
        'Flight Booking Confirmation',
        recipients=[user.email],
        body=f"Dear {user.username},\nYour flight {flight.flight_number} on {format_datetime(flight.departure_time)} is confirmed. Reference: {booking.booking_reference}\nTotal Price: {format_price(booking.price_paid)}"
    )
    try:
        with current_app.app_context():
            mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {e}")
        return False
'''
def send_flight_cancellation_email(user, booking, flight, mail):
    """Send a flight cancellation email to the user"""
    msg = Message(
        'Flight Cancellation Notification',
        recipients=[user.email],
        body=f"""Dear {user.username},

We regret to inform you that your flight {flight.flight_number} from {get_airport_city(flight.origin)} to {get_airport_city(flight.destination)} scheduled for {format_datetime(flight.departure_time)} has been cancelled.

Booking Reference: {booking.booking_reference}
Status: Cancelled

Please contact our support team at support@airwaysabc.com or call +1-800-555-1234 for assistance with rebooking or refunds.

Thank you for your understanding,
Airways ABC Team"""
    )
    try:
        with current_app.app_context():
            mail.send(msg)
        current_app.logger.info(f"Cancellation email sent to {user.email} for booking {booking.booking_reference}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send cancellation email to {user.email}: {e}")
        return False
   ''' 
def send_booking_cancellation_email(user, booking, flight, mail):
    """Send a booking cancellation email to the user"""
    msg = Message(
        'Booking Cancellation Confirmation',
        recipients=[user.email],
        body=f"""Dear {user.username},

Your booking for flight {flight.flight_number} from {get_airport_city(flight.origin)} to {get_airport_city(flight.destination)} scheduled for {format_datetime(flight.departure_time)} has been cancelled.

Booking Reference: {booking.booking_reference}
Status: Cancelled

If you have any questions, please contact our support team at support@airwaysabc.com or call +1-800-555-1234.

Thank you,
Airways ABC Team""")
   
    try:
        with current_app.app_context():
            mail.send(msg)
        current_app.logger.info(f"Booking cancellation email sent to {user.email} for booking {booking.booking_reference}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send booking cancellation email to {user.email}: {e}")
        return False