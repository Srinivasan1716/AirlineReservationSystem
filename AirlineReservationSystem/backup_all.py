import json
from app import app
from models import User, Flight, Booking, Passenger, Seat
from extensions import db

with app.app_context():
    # Backup Users
    users = User.query.all()
    user_data = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password_hash': user.password_hash,
            'is_admin': user.is_admin,
            'frequent_flyer_points': user.frequent_flyer_points,
            'created_at': user.created_at.isoformat() if user.created_at else None
        } for user in users
    ]
    with open('backup/users_backup.json', 'w') as f:
        json.dump(user_data, f, indent=2)

    # Backup Flights
    flights = Flight.query.all()
    flight_data = [
        {
            'id': flight.id,
            'flight_number': flight.flight_number,
            'origin': flight.origin,
            'destination': flight.destination,
            'departure_time': flight.departure_time.isoformat(),
            'arrival_time': flight.arrival_time.isoformat(),
            'aircraft_type': flight.aircraft_type,
            'seats_total': flight.seats_total,
            'seats_available': flight.seats_available,
            'price': float(flight.price),
            'status': flight.status
        } for flight in flights
    ]
    with open('backup/flights_backup.json', 'w') as f:
        json.dump(flight_data, f, indent=2)

    # Backup Bookings
    bookings = Booking.query.all()
    booking_data = [
        {
            'id': booking.id,
            'user_id': booking.user_id,
            'flight_id': booking.flight_id,
            'booking_time': booking.booking_time.isoformat(),
            'status': booking.status,
            'price_paid': float(booking.price_paid),
            'booking_reference': booking.booking_reference,
            'payment_id': booking.payment_id
        } for booking in bookings
    ]
    with open('backup/bookings_backup.json', 'w') as f:
        json.dump(booking_data, f, indent=2)

    # Backup Passengers
    passengers = Passenger.query.all()
    passenger_data = [
        {
            'id': passenger.id,
            'booking_id': passenger.booking_id,
            'first_name': passenger.first_name,
            'last_name': passenger.last_name,
            'date_of_birth': passenger.date_of_birth.isoformat(),
            'passport_number': passenger.passport_number,
            'address': passenger.address
        } for passenger in passengers
    ]
    with open('backup/passengers_backup.json', 'w') as f:
        json.dump(passenger_data, f, indent=2)

    # Backup Seats
    seats = Seat.query.all()
    seat_data = [
        {
            'id': seat.id,
            'booking_id': seat.booking_id,
            'seat_number': seat.seat_number
        } for seat in seats
    ]
    with open('backup/seats_backup.json', 'w') as f:
        json.dump(seat_data, f, indent=2)

    print("All data backed up to backup/*.json")