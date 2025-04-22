from models import User, Flight, Booking, Passenger
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# In-memory storage
users = []
flights = []
bookings = []

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

    # Indian Airports
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
    "Boeing 737",
    "Boeing 747",
    "Boeing 777",
    "Airbus A320",
    "Airbus A330",
    "Airbus A380",
    
    # Indian-operated aircraft types
    "ATR 72",               # Used by IndiGo, Alliance Air, SpiceJet (for regional routes)
    "De Havilland Canada Dash 8 Q400"  # Used by SpiceJet for regional connectivity
]


def initialize_data():
    """Initialize the application with some data"""
    # Create admin and test user
    create_users()
    
    # Create sample flights
    create_flights()

def create_users():
    """Create initial users"""
    # Admin user
    admin = User(
        id=1,
        username="admin",
        email="srinivasan2470047@ssn.edu.in",
        password_hash=generate_password_hash("admin123"),
        is_admin=True
    )
    users.append(admin)
    
    # Test user
    test_user = User(
        id=2,
        username="testuser",
        email="user@example.com",
        password_hash=generate_password_hash("password123"),
        is_admin=False
    )
    users.append(test_user)

def create_flights():
    """Create sample flights"""
    airport_codes = list(airports.keys())
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Create flights for next 45 days
    for day in range(45):
        current_date = today + timedelta(days=day)
        
        # Create 10-30 flights per day
        for _ in range(random.randint(10, 30)):
            # Select random origin and destination
            origin, destination = random.sample(airport_codes, 2)
            
            # Random departure time between 6 AM and 10 PM
            departure_hour = random.randint(6, 22)
            departure_minute = random.choice([0, 15, 30, 45])
            departure_time = current_date.replace(hour=departure_hour, minute=departure_minute)
            
            # Flight duration between 1 and 12 hours
            duration_hours = random.randint(1, 12)
            duration_minutes = random.choice([0, 15, 30, 45])
            arrival_time = departure_time + timedelta(hours=duration_hours, minutes=duration_minutes)
            
            # Create flight
            flight = Flight(
                id=len(flights) + 1,
                flight_number=f"AR{random.randint(100, 999)}",
                origin=origin,
                destination=destination,
                departure_time=departure_time,
                arrival_time=arrival_time,
                aircraft_type=random.choice(aircraft_types),
                seats_total=random.choice([120, 180, 240, 300, 360]),
                seats_available=random.choice([120, 180, 240, 300, 360]),  # Initially all seats available
                price=random.randint(200, 2000),  # Base price between $200 and $2000
                status="Scheduled"
            )
            
            flights.append(flight)

def get_flight_by_id(flight_id):
    """Get a flight by its ID"""
    for flight in flights:
        if flight.id == flight_id:
            return flight
    return None

def get_user_by_id(user_id):
    """Get a user by their ID"""
    for user in users:
        if user.id == user_id:
            return user
    return None

def get_user_by_username(username):
    """Get a user by their username"""
    for user in users:
        if user.username == username:
            return user
    return None

def get_user_by_email(email):
    """Get a user by their email"""
    for user in users:
        if user.email == email:
            return user
    return None

def get_user_bookings(user_id):
    """Get all bookings for a specific user"""
    return [booking for booking in bookings if booking.user_id == user_id]

def get_booking_by_id(booking_id):
    """Get a booking by its ID"""
    for booking in bookings:
        if booking.id == booking_id:
            return booking
    return None

def get_booking_by_reference(reference):
    """Get a booking by its reference number"""
    for booking in bookings:
        if booking.booking_reference == reference:
            return booking
    return None

def add_booking(booking):
    """Add a new booking"""
    bookings.append(booking)
    
    # Update flight seat availability
    flight = get_flight_by_id(booking.flight_id)
    if flight:
        flight.seats_available -= len(booking.passengers)

def search_flights(origin, destination, date, passengers=1):
    """Search for flights based on criteria"""
    search_date = datetime.strptime(date, "%Y-%m-%d").date() if isinstance(date, str) else date
    
    results = []
    for flight in flights:
        if (flight.origin == origin and 
            flight.destination == destination and 
            flight.departure_time.date() == search_date and
            flight.seats_available >= passengers):
            results.append(flight)
    
    # Sort by departure time
    return sorted(results, key=lambda x: x.departure_time)

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
    
    # Find all booked seats for this flight
    booked_seats = []
    for booking in bookings:
        if booking.flight_id == flight_id and booking.status != "Cancelled":
            booked_seats.extend(booking.seat_number)
    
    # Generate a seat map based on aircraft type
    rows = []
    if "Boeing 737" in flight.aircraft_type:
        rows = 30
        columns = "ABCDEF"  # 3-3 configuration
    elif "Boeing 747" in flight.aircraft_type or "Boeing 777" in flight.aircraft_type:
        rows = 40
        columns = "ABCDEFGHJK"  # 3-4-3 configuration
    elif "Airbus A320" in flight.aircraft_type:
        rows = 30
        columns = "ABCDEF"  # 3-3 configuration
    elif "Airbus A330" in flight.aircraft_type:
        rows = 35
        columns = "ABCDEFGHJ"  # 2-4-2 configuration
    elif "Airbus A380" in flight.aircraft_type:
        rows = 50
        columns = "ABCDEFGHJK"  # 3-4-3 configuration
    else:
        rows = 30
        columns = "ABCDEF"  # Default 3-3 configuration
    
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
    users.append(user)
