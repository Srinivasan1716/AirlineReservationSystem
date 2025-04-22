from flask_login import UserMixin
from datetime import datetime
import uuid

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.frequent_flyer_points = 0
        self.created_at = datetime.now()

class Flight:
    def __init__(self, id, flight_number, origin, destination, departure_time, arrival_time, 
                 aircraft_type, seats_total, seats_available, price, status="Scheduled"):
        self.id = id
        self.flight_number = flight_number
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.aircraft_type = aircraft_type
        self.seats_total = seats_total
        self.seats_available = seats_available
        self.base_price = price
        self.status = status
        
    def get_duration(self):
        """Calculate flight duration in hours and minutes"""
        duration = self.arrival_time - self.departure_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"
    
    def get_current_price(self):
        """Calculate current price based on seat availability"""
        availability_percentage = self.seats_available / self.seats_total
        if availability_percentage < 0.2:
            return self.base_price * 1.5  # 50% markup for low availability
        elif availability_percentage < 0.5:
            return self.base_price * 1.2  # 20% markup for medium availability
        else:
            return self.base_price

class Booking:
    def __init__(self, id, user_id, flight_id, seat_number, booking_time, status, passengers, price_paid):
        self.id = id
        self.user_id = user_id
        self.flight_id = flight_id
        self.booking_reference = self._generate_booking_reference()
        self.seat_number = seat_number
        self.booking_time = booking_time
        self.status = status  # 'Confirmed', 'Cancelled', 'Checked-in'
        self.passengers = passengers  # List of passenger details
        self.price_paid = price_paid
    
    def _generate_booking_reference(self):
        """Generate a unique booking reference"""
        return uuid.uuid4().hex[:6].upper()

class Passenger:
    def __init__(self, first_name, last_name, date_of_birth, passport_number=None, address=None):
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.passport_number = passport_number
        self.address = address