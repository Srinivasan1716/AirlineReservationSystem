from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    frequent_flyer_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Add created_at
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), nullable=False)
    origin = db.Column(db.String(3), nullable=False)
    destination = db.Column(db.String(3), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    aircraft_type = db.Column(db.String(50), nullable=False)
    seats_total = db.Column(db.Integer, nullable=False)
    seats_available = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    bookings = db.relationship('Booking', backref='flight', lazy=True)

    def get_duration(self):
        from utils import format_duration, calculate_flight_duration
        return format_duration(calculate_flight_duration(self.departure_time, self.arrival_time))

    def get_current_price(self):
        # Simplified; add dynamic pricing logic if needed
        return self.price

    def __repr__(self):
        return f'<Flight {self.flight_number}>'

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    price_paid = db.Column(db.Float, nullable=False)
    booking_reference = db.Column(db.String(6), unique=True, nullable=False)
    payment_id = db.Column(db.String(100))
    passengers = db.relationship('Passenger', backref='booking', lazy=True)
    seat_numbers = db.relationship('Seat', backref='booking', lazy=True)

    def __repr__(self):
        return f'<Booking {self.booking_reference}>'

class Passenger(db.Model):
    __tablename__ = 'passengers'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    passport_number = db.Column(db.String(20))
    address = db.Column(db.String(200))

    def __repr__(self):
        return f'<Passenger {self.first_name} {self.last_name}>'

class Seat(db.Model):
    __tablename__ = 'seats'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Seat {self.seat_number}>'