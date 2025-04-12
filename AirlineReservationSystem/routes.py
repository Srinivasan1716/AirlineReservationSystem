from flask import render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from models import User, Flight, Booking, Passenger
from forms import LoginForm, RegisterForm, FlightSearchForm, BookingForm, BookingSearchForm, AdminFlightForm
import data
from datetime import datetime, timedelta
from utils import (
    format_datetime, format_date, format_time, format_duration, 
    calculate_flight_duration, generate_booking_reference, format_price
)

# Home page
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = FlightSearchForm()
    
    if form.validate_on_submit():
        origin = form.origin.data
        destination = form.destination.data
        departure_date = form.departure_date.data
        passengers = form.passengers.data
        
        # Store search parameters in session
        session['search_params'] = {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date.isoformat(),
            'passengers': passengers
        }
        
        return redirect(url_for('search_results'))
    
    return render_template('index.html', form=form)

# Search results
@app.route('/flights/search')
def search_results():
    search_params = session.get('search_params')
    
    if not search_params:
        flash('Please enter search criteria', 'warning')
        return redirect(url_for('index'))
    
    origin = search_params.get('origin')
    destination = search_params.get('destination')
    departure_date = datetime.fromisoformat(search_params.get('departure_date')).date()
    passengers = search_params.get('passengers', 1)
    
    # Search for matching flights
    flights = data.search_flights(origin, destination, departure_date, passengers)
    
    return render_template(
        'search.html', 
        flights=flights, 
        origin=origin, 
        destination=destination, 
        departure_date=departure_date, 
        passengers=passengers,
        get_airport_name=data.get_airport_name
    )

# Flight details
@app.route('/flights/<int:flight_id>')
def flight_details(flight_id):
    flight = data.get_flight_by_id(flight_id)
    
    if not flight:
        flash('Flight not found', 'danger')
        return redirect(url_for('index'))
    
    passengers = int(request.args.get('passengers', 1))
    
    return render_template(
        'flight_details.html', 
        flight=flight, 
        passengers=passengers,
        get_airport_name=data.get_airport_name,
        format_datetime=format_datetime,
        format_price=format_price
    )

# Book flight
@app.route('/flights/<int:flight_id>/book', methods=['GET', 'POST'])
@login_required
def book_flight(flight_id):
    flight = data.get_flight_by_id(flight_id)
    
    if not flight:
        flash('Flight not found', 'danger')
        return redirect(url_for('index'))
    
    passengers = int(request.args.get('passengers', 1))
    
    if flight.seats_available < passengers:
        flash(f'Not enough seats available. Only {flight.seats_available} seats left.', 'danger')
        return redirect(url_for('flight_details', flight_id=flight_id))
    
    # Create form with the right number of passenger entries
    form = BookingForm()
    
    # Adjust the number of passenger forms
    while len(form.passengers) < passengers:
        form.passengers.append_entry()
    
    # Remove excess passenger forms
    while len(form.passengers) > passengers:
        form.passengers.pop_entry()
    
    if form.validate_on_submit():
        # Process booking
        passenger_list = []
        
        for i in range(passengers):
            passenger_data = form.passengers[i].data
            passenger = Passenger(
                first_name=passenger_data['first_name'],
                last_name=passenger_data['last_name'],
                date_of_birth=passenger_data['date_of_birth'],
                passport_number=passenger_data['passport_number']
            )
            passenger_list.append(passenger)
        
        # Process selected seats
        selected_seats = form.selected_seats.data.split(',') if form.selected_seats.data else []
        
        # Calculate total price
        price_per_passenger = flight.get_current_price()
        total_price = price_per_passenger * passengers
        
        # Create booking
        booking = Booking(
            id=len(data.bookings) + 1,
            user_id=current_user.id,
            flight_id=flight_id,
            seat_number=selected_seats,
            booking_time=datetime.now(),
            status="Confirmed",
            passengers=passenger_list,
            price_paid=total_price
        )
        
        # Add booking to data
        data.add_booking(booking)
        
        # Add frequent flyer points
        user = data.get_user_by_id(current_user.id)
        if user:
            # Points are 10% of the price paid
            user.frequent_flyer_points += int(total_price * 0.1)
        
        flash('Booking confirmed! Your booking reference is: ' + booking.booking_reference, 'success')
        return redirect(url_for('booking_confirm', booking_id=booking.id))
    
    # Set flight_id in the form
    form.flight_id.data = flight_id
    
    return render_template(
        'booking.html', 
        form=form, 
        flight=flight, 
        passengers=passengers,
        get_airport_name=data.get_airport_name,
        format_datetime=format_datetime,
        format_price=format_price,
        seat_map=data.get_seat_map(flight_id)
    )

# Booking confirmation
@app.route('/booking/<int:booking_id>/confirm')
@login_required
def booking_confirm(booking_id):
    booking = data.get_booking_by_id(booking_id)
    
    if not booking or booking.user_id != current_user.id:
        flash('Booking not found', 'danger')
        return redirect(url_for('my_bookings'))
    
    flight = data.get_flight_by_id(booking.flight_id)
    
    return render_template(
        'booking_confirm.html', 
        booking=booking, 
        flight=flight,
        get_airport_name=data.get_airport_name,
        format_datetime=format_datetime,
        format_price=format_price
    )

# User reservations
@app.route('/my-bookings')
@login_required
def my_bookings():
    user_bookings = data.get_user_bookings(current_user.id)
    
    # Get flight details for each booking
    booking_details = []
    for booking in user_bookings:
        flight = data.get_flight_by_id(booking.flight_id)
        if flight:
            booking_details.append({
                'booking': booking,
                'flight': flight
            })
    now = datetime.now()
    return render_template(
        'user_reservations.html', 
        booking_details=booking_details,
        get_airport_name=data.get_airport_name,
        format_datetime=format_datetime,
        format_date=format_date,
        format_time=format_time,
        now=now
    )

# Cancel booking
@app.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = data.get_booking_by_id(booking_id)
    
    if not booking or booking.user_id != current_user.id:
        flash('Booking not found', 'danger')
        return redirect(url_for('my_bookings'))
    
    if booking.status == "Cancelled":
        flash('This booking is already cancelled', 'warning')
        return redirect(url_for('my_bookings'))
    
    # Update booking status
    booking.status = "Cancelled"
    
    # Return seats to available inventory
    flight = data.get_flight_by_id(booking.flight_id)
    if flight:
        flight.seats_available += len(booking.passengers)
    
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('my_bookings'))

# User profile
@app.route('/profile')
@login_required
def profile():
    user = data.get_user_by_id(current_user.id)
    bookings_count = len(data.get_user_bookings(current_user.id))
    
    return render_template('user_profile.html', user=user, bookings_count=bookings_count)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Redirect authenticated users to home
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = data.get_user_by_username(username)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Logged in successfully', 'success')
            return redirect(next_page or url_for('index'))  # Ensure redirect to index
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Create new user
        user = User(
            id=len(data.users) + 1,
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=False
        )
        
        # Add user to data
        data.add_user(user)
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Admin dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Count statistics
    total_flights = len(data.flights)
    active_flights = sum(1 for f in data.flights if f.status != "Completed" and f.status != "Cancelled")
    total_bookings = len(data.bookings)
    active_bookings = sum(1 for b in data.bookings if b.status == "Confirmed")
    total_users = len(data.users)
    
    # Get upcoming flights
    today = datetime.now()
    upcoming_flights = [f for f in data.flights if f.departure_time > today and f.status != "Cancelled"]
    upcoming_flights.sort(key=lambda f: f.departure_time)
    upcoming_flights = upcoming_flights[:10]  # Take only the next 10 flights
    
    # Get recent bookings
    recent_bookings = sorted(data.bookings, key=lambda b: b.booking_time, reverse=True)[:10]
    
    return render_template(
        'admin/dashboard.html',
        total_flights=total_flights,
        active_flights=active_flights,
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        total_users=total_users,
        upcoming_flights=upcoming_flights,
        recent_bookings=recent_bookings,
        get_airport_name=data.get_airport_name,
        format_datetime=format_datetime,
        get_user_by_id=data.get_user_by_id,
        get_flight_by_id=data.get_flight_by_id
    )

# Admin flights
@app.route('/admin/flights')
@login_required
def admin_flights():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    # Filter flights
    filtered_flights = data.flights
    
    if search:
        filtered_flights = [
            f for f in filtered_flights 
            if search.upper() in f.flight_number 
            or search.upper() in f.origin 
            or search.upper() in f.destination
        ]
    
    if status:
        filtered_flights = [f for f in filtered_flights if f.status == status]
    
    # Sort by departure time
    filtered_flights.sort(key=lambda f: f.departure_time)
    
    return render_template(
        'admin/flights.html',
        flights=filtered_flights,
        get_airport_name=data.get_airport_name,
        format_datetime=format_datetime,
        search=search,
        status=status
    )

# Admin bookings
@app.route('/admin/bookings')
@login_required
def admin_bookings():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    # Filter bookings
    filtered_bookings = data.bookings
    
    if search:
        filtered_bookings = [
            b for b in filtered_bookings 
            if search.upper() in b.booking_reference
        ]
    
    if status:
        filtered_bookings = [b for b in filtered_bookings if b.status == status]
    
    # Sort by booking time (most recent first)
    filtered_bookings.sort(key=lambda b: b.booking_time, reverse=True)
    
    return render_template(
        'admin/bookings.html',
        bookings=filtered_bookings,
        get_user_by_id=data.get_user_by_id,
        get_flight_by_id=data.get_flight_by_id,
        format_datetime=format_datetime,
        search=search,
        status=status
    )

# Admin users
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    search = request.args.get('search', '')
    
    # Filter users
    filtered_users = data.users
    
    if search:
        filtered_users = [
            u for u in filtered_users 
            if search.lower() in u.username.lower() 
            or search.lower() in u.email.lower()
        ]
    
    return render_template(
        'admin/users.html',
        users=filtered_users,
        search=search
    )

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Add context processors
@app.context_processor
def utility_processor():
    return {
        'format_datetime': format_datetime,
        'format_date': format_date, 
        'format_time': format_time,
        'format_price': format_price
    }
