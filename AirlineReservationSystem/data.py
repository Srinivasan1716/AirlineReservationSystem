from models import User, Flight, Booking, Passenger, Seat
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
import random
from extensions import db

# Airport data
airports = {
    "JFK": {"name": "John F. Kennedy International Airport", "city": "New York", "country": "USA"},
    "LAX": {"name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA"},
    "ORD": {"name": "O'Hare International Airport", "city": "Chicago", "country": "USA"},
    "LHR": {"name": "Heathrow Airport", "city": "London", "country": "UK"},
    "CDG": {"name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
    "DXB": {"name": "Dubai International Airport", "city": "Dubai", "country": "UAE"},
    "HND": {"name": "Haneda Airport", "city": "Tokyo", "country": "Japan"},
    "SYD": {"name": "Sydney Airport", "city": "Sydney", "country": "Australia"},
    "SIN": {"name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore"},
    "FRA": {"name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
    "DEL": {"name": "Indira Gandhi International Airport", "city": "Delhi", "country": "India"},
    "BOM": {"name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "country": "India"},
    "MAA": {"name": "Chennai International Airport", "city": "Chennai", "country": "India"},
    "BLR": {"name": "Kempegowda International Airport", "city": "Bengaluru", "country": "India"},
    "HYD": {"name": "Rajiv Gandhi International Airport", "city": "Hyderabad", "country": "India"},
    "CCU": {"name": "Netaji Subhas Chandra Bose International Airport", "city": "Kolkata", "country": "India"},
    "GOI": {"name": "Goa International Airport", "city": "Goa", "country": "India"},
    "AMD": {"name": "Sardar Vallabhbhai Patel International Airport", "city": "Ahmedabad", "country": "India"},
    "COK": {"name": "Cochin International Airport", "city": "Kochi", "country": "India"},
    "TRV": {"name": "Trivandrum International Airport", "city": "Thiruvananthapuram", "country": "India"}
}

# Aircraft types
aircraft_types = [
    "Boeing 737", "Boeing 747", "Boeing 777",
    "Airbus A320", "Airbus A330", "Airbus A380",
    "ATR 72", "De Havilland Canada Dash 8 Q400"
]

def initialize_data():
    """Initialize the database with some data"""
    # Create admin and test user if not exist
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="srinivasan2470047@ssn.edu.in",
            password_hash=generate_password_hash("admin123"),
            is_admin=True
        )
        db.session.add(admin)
    
    if not User.query.filter_by(username="testuser").first():
        test_user = User(
            username="testuser",
            email="user@example.com",
            password_hash=generate_password_hash("password123"),
            is_admin=False
        )
        db.session.add(test_user)
    
    db.session.commit()
    
    # Create sample flights if none exist
    if not Flight.query.first():
        create_flights()

def create_flights():
    """Create sample flights"""
    airport_codes = list(airports.keys())
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day in range(45):
        current_date = today + timedelta(days=day)
        for _ in range(random.randint(10, 30)):
            origin, destination = random.sample(airport_codes, 2)
            departure_hour = random.randint(6, 22)
            departure_minute = random.choice([0, 15, 30, 45])
            departure_time = current_date.replace(hour=departure_hour, minute=departure_minute)
            duration_hours = random.randint(1, 12)
            duration_minutes = random.choice([0, 15, 30, 45])
            arrival_time = departure_time + timedelta(hours=duration_hours, minutes=duration_minutes)
            seats = random.choice([120, 180, 240, 300, 360])
            
            flight = Flight(
                flight_number=f"AR{random.randint(100, 999)}",
                origin=origin,
                destination=destination,
                departure_time=departure_time,
                arrival_time=arrival_time,
                aircraft_type=random.choice(aircraft_types),
                seats_total=seats,
                seats_available=seats,
                price=random.randint(5000, 50000),
                status="Scheduled"
            )
            db.session.add(flight)
    
    db.session.commit()

def get_flight_by_id(flight_id):
    """Get a flight by its ID"""
    return Flight.query.get(flight_id)

def get_user_by_id(user_id):
    """Get a user by their ID"""
    return User.query.get(user_id)

def get_user_by_username(username):
    """Get a user by their username"""
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """Get a user by their email"""
    return User.query.filter_by(email=email).first()

def get_user_bookings(user_id):
    """Get all bookings for a specific user"""
    return Booking.query.filter_by(user_id=user_id).all()

def get_booking_by_id(booking_id):
    """Get a booking by its ID"""
    return Booking.query.get(booking_id)

def get_booking_by_reference(reference):
    """Get a booking by its reference number"""
    return Booking.query.filter_by(booking_reference=reference).first()

def add_booking(booking):
    """Add a new booking"""
    db.session.add(booking)
    flight = get_flight_by_id(booking.flight_id)
    if flight:
        flight.seats_available -= len(booking.passengers)
    db.session.commit()

def search_flights(origin, destination, date, passengers=1):
    """Search for flights based on criteria"""
    search_date = datetime.strptime(date, "%Y-%m-%d").date() if isinstance(date, str) else date
    return Flight.query.filter(
        Flight.origin == origin,
        Flight.destination == destination,
        db.func.date(Flight.departure_time) == search_date,
        Flight.seats_available >= passengers
    ).order_by(Flight.departure_time).all()

def get_airport_name(code):
    """Get full airport name from code"""
    if code in airports:
        return f"{airports[code]['name']} ({code}), {airports[code]['city']}, {airports[code]['country']}"
    return code

def get_airport_city(code):
    """Get city name from airport code"""
    if code in airports:
        return airports[code]['city']
    return code

def get_seat_map(flight_id):
    """Generate a seat map for the given flight"""
    flight = get_flight_by_id(flight_id)
    if not flight:
        return []
    
    booked_seats = [seat.seat_number for seat in Seat.query.join(Booking).filter(
        Booking.flight_id == flight_id, Booking.status != "Cancelled"
    ).all()]
    
    rows = []
    if "Boeing 737" in flight.aircraft_type:
        rows = 30
        columns = "ABCDEF"
    elif "Boeing 747" in flight.aircraft_type or "Boeing 777" in flight.aircraft_type:
        rows = 40
        columns = "ABCDEFGHJK"
    elif "Airbus A320" in flight.aircraft_type:
        rows = 30
        columns = "ABCDEF"
    elif "Airbus A330" in flight.aircraft_type:
        rows = 35
        columns = "ABCDEFGHJ"
    elif "Airbus A380" in flight.aircraft_type:
        rows = 50
        columns = "ABCDEFGHJK"
    else:
        rows = 30
        columns = "ABCDEF"
    
    seat_map = []
    for row in range(1, rows + 1):
        row_seats = []
        for col in columns:
            seat = f"{row}{col}"
            row_seats.append({
                "seat": seat,
                "available": seat not in booked_seats
            })
        seat_map.append(row_seats)
    
    return seat_map

def add_user(user):
    """Add a new user"""
    db.session.add(user)
    db.session.commit()