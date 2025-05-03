from flask import render_template, redirect, url_for, flash, request, session, jsonify
from data import get_user_by_id, get_flight_by_id
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, mail
from extensions import db
from utils import send_booking_confirmation, generate_booking_reference, format_datetime, format_date, format_time, format_price, calculate_flight_duration
from models import User, Flight, Booking, Passenger, Seat
from forms import LoginForm, RegisterForm, FlightSearchForm, BookingForm, BookingSearchForm, AdminFlightForm
import razorpay
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta, date
import data
import logging
logging.debug("Initializing app.py")

# Load environment variables
load_dotenv()
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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

@app.route('/flights/<int:flight_id>/book', methods=['GET'])
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
    
    form = BookingForm(flight_id=flight_id)
    
    while len(form.passengers) < passengers:
        form.passengers.append_entry()
    
    while len(form.passengers) > passengers:
        form.passengers.pop_entry()
    
    today = date.today()
    max_dob = (today - timedelta(days=1)).isoformat()
    min_dob = (today - timedelta(days=120*365)).isoformat()
    
    total_price = flight.get_current_price() * passengers
    
    return render_template(
        'booking.html', 
        form=form, 
        flight=flight, 
        passengers=passengers,
        total_price=total_price,
        discount=0,
        final_price=total_price,
        get_airport_name=data.get_airport_name,
        format_datetime=format_datetime,
        format_price=format_price,
        seat_map=data.get_seat_map(flight_id),
        max_dob=max_dob,
        min_dob=min_dob
    )

@app.route('/create_booking', methods=['POST'])
@login_required
def create_booking():
    try:
        form = BookingForm()
        logging.debug(f"Form data keys received: {list(request.form.keys())}")
        logging.debug(f"Form data values: {dict(request.form)}")
        if not form.validate_on_submit():
            errors = {}
            for field, errs in form.errors.items():
                errors[field] = errs
            logging.error(f"Form validation failed: {errors}")
            return jsonify({'error': 'Invalid form data', 'details': errors}), 400
        
        flight_id = int(form.flight_id.data)
        flight = data.get_flight_by_id(flight_id)
        if not flight:
            logging.error(f"Flight not found: ID {flight_id}")
            return jsonify({'error': 'Flight not found'}), 404
        
        passengers_count = int(request.form.get('passengers_count', 1))
        if flight.seats_available < passengers_count:
            logging.error(f"Not enough seats: {flight.seats_available} available, {passengers_count} requested")
            return jsonify({'error': f'Not enough seats available. Only {flight.seats_available} seats left.'}), 400
        
        selected_seats = form.selected_seats.data.split(',') if form.selected_seats.data else []
        if len(selected_seats) != passengers_count:
            logging.error(f"Seat count mismatch: {len(selected_seats)} seats selected, {passengers_count} required")
            return jsonify({'error': f'Please select exactly {passengers_count} seat(s)'}), 400
        
        # Calculate total price
        total_price = flight.get_current_price() * passengers_count
        
        # Apply frequent flyer points discount
        points_to_redeem = form.points_to_redeem.data or 0
        available_points = current_user.frequent_flyer_points
        max_points = min(available_points, total_price)  # Can't redeem more than the price or available points
        points_to_redeem = min(points_to_redeem, max_points)
        
        # Calculate discount (1 point = ₹1 discount)
        discount = points_to_redeem
        final_price = total_price - discount
        if final_price < 0:
            final_price = 0  # Ensure price doesn't go negative
        
        # Create passenger list
        passenger_list = []
        for i in range(passengers_count):
            passenger_data = form.passengers[i].data
            logging.debug(f"Passenger {i+1} data: {passenger_data}")
            passenger = Passenger(
                first_name=passenger_data['first_name'],
                last_name=passenger_data['last_name'],
                date_of_birth=passenger_data['date_of_birth'],
                passport_number=passenger_data['passport_number'],
                address=passenger_data['address']
            )
            passenger_list.append(passenger)
        
        # Create the booking
        booking = Booking(
            user_id=current_user.id,
            flight_id=flight_id,
            booking_time=datetime.now(),
            status="Pending",
            price_paid=final_price,
            booking_reference=generate_booking_reference(),
            passengers=passenger_list
        )
        
        for seat in selected_seats:
            booking.seat_numbers.append(Seat(seat_number=seat))
        
        data.add_booking(booking)
        
        # Deduct the points from the user's account
        if points_to_redeem > 0:
            current_user.frequent_flyer_points -= points_to_redeem
            db.session.commit()
        
        logging.debug(f"Booking created: ID {booking.id}, User {current_user.id}, Flight {flight_id}, Final Price: {final_price}")
        return jsonify({
            'booking_id': booking.id,
            'total_price': total_price,
            'discount': discount,
            'final_price': final_price
        })
    except Exception as e:
        logging.error(f"Error creating booking: {str(e)}")
        return jsonify({'error': 'Failed to create booking', 'details': str(e)}), 500

@app.route('/create_order', methods=['POST'])
@login_required
def create_order():
    try:
        booking_id = request.form.get('booking_id')
        booking = data.get_booking_by_id(int(booking_id))
        if not booking:
            logging.error(f"Booking not found: ID {booking_id}")
            return jsonify({'error': 'Booking not found'}), 404
        
        final_price = float(request.form.get('final_price'))
        if final_price <= 0:
            # If final price is 0, confirm booking directly
            booking.status = "Confirmed"
            db.session.commit()
            return jsonify({'status': 'confirmed', 'booking_id': booking_id})
        
        amount = int(final_price * 100)  # Convert to paise
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'booking_{booking_id}',
            'payment_capture': 1
        }
        
        order = razorpay_client.order.create(data=order_data)
        logging.debug(f"Order created: ID {order['id']}, Booking {booking_id}")
        return jsonify({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key_id': RAZORPAY_KEY_ID
        })
    except Exception as e:
        logging.error(f"Error creating order: {str(e)}")
        return jsonify({'error': 'Failed to create order', 'details': str(e)}), 500

@app.route('/verify_payment', methods=['POST'])
@login_required
def verify_payment():
    try:
        payment_id = request.form.get('razorpay_payment_id')
        order_id = request.form.get('razorpay_order_id')
        signature = request.form.get('razorpay_signature')
        booking_id = request.form.get('booking_id')
        
        booking = data.get_booking_by_id(int(booking_id))
        if not booking:
            logging.error(f"Booking not found: ID {booking_id}")
            return jsonify({'error': 'Booking not found'}), 404
        
        params_dict = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        booking.status = "Confirmed"
        booking.payment_id = payment_id
        
        user = data.get_user_by_id(current_user.id)
        if user:
            user.frequent_flyer_points += int(booking.price_paid * 0.1)
        
        db.session.commit()
        
        if send_booking_confirmation(current_user, booking, mail):
            flash('Booking confirmed! A confirmation email has been sent.', 'success')
        else:
            flash('Booking confirmed! Email sending failed.', 'warning')
        
        logging.debug(f"Payment verified: Booking {booking_id}, Payment ID {payment_id}")
        return jsonify({'status': 'success'})
    except razorpay.errors.SignatureVerificationError:
        logging.error("Payment signature verification failed")
        booking = data.get_booking_by_id(int(booking_id))
        if booking:
            booking.status = "Failed"
            db.session.commit()
        return render_template('payment_failed.html', error_message="Payment verification failed")
    except Exception as e:
        logging.error(f"Error verifying payment: {str(e)}")
        booking = data.get_booking_by_id(int(booking_id))
        if booking:
            booking.status = "Failed"
            db.session.commit()
        return render_template('payment_failed.html', error_message="Payment processing failed")

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
    
    booking.status = "Cancelled"
    flight = data.get_flight_by_id(booking.flight_id)
    if flight:
        flight.seats_available += len(booking.passengers)
    
    db.session.commit()
    
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
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = data.get_user_by_username(username)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Logged in successfully', 'success')
            return redirect(next_page or url_for('index'))
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
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=False
        )
        
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
    
    total_flights = Flight.query.count()
    active_flights = Flight.query.filter(Flight.status.notin_(["Completed", "Cancelled"])).count()
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter_by(status="Confirmed").count()
    total_users = User.query.count()
    
    today = datetime.now()
    upcoming_flights = Flight.query.filter(
        Flight.departure_time > today,
        Flight.status != "Cancelled"
    ).order_by(Flight.departure_time).limit(10).all()
    
    recent_bookings = Booking.query.order_by(Booking.booking_time.desc()).limit(10).all()
    
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
    
    query = Flight.query
    
    if search:
        search = search.upper()
        query = query.filter(
            db.or_(
                Flight.flight_number.contains(search),
                Flight.origin.contains(search),
                Flight.destination.contains(search)
            )
        )
    
    if status:
        query = query.filter_by(status=status)
    
    filtered_flights = query.order_by(Flight.departure_time).all()
    
    return render_template(
        'admin/flights.html',
        flights=filtered_flights,
        get_airport_name=data.get_airport_name,
        format_datetime=format_datetime,
        search=search,
        status=status
    )

# Admin bookings
@app.route('/admin/bookings', methods=['GET'])
@login_required
def admin_bookings():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    query = Booking.query
    
    if search:
        query = query.filter(Booking.booking_reference.ilike(f'%{search}%'))
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Booking.booking_time.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    bookings = pagination.items
    
    app.logger.debug(f"Retrieved {len(bookings)} bookings (total: {pagination.total})")
    
    return render_template(
        'admin/bookings.html',
        bookings=bookings,
        pagination=pagination,
        search=search,
        status=status,
        get_user_by_id=get_user_by_id,  # Use imported function
        get_flight_by_id=get_flight_by_id,  # Use imported function
        format_datetime=format_datetime
    )

# Admin users
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    search = request.args.get('search', '')
    
    query = User.query
    
    if search:
        search = search.lower()
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    filtered_users = query.all()
    
    return render_template(
        'admin/users.html',
        users=filtered_users,
        search=search
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.context_processor
def utility_processor():
    return {
        'format_datetime': format_datetime,
        'format_date': format_date, 
        'format_time': format_time,
        'format_price': format_price
    }

@app.route('/admin/add_flight', methods=['POST'])
@login_required
def add_flight():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    try:
        flight_number = request.form.get('flight_number')
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        departure_time = datetime.strptime(request.form.get('departure_time'), '%Y-%m-%dT%H:%M')
        arrival_time = datetime.strptime(request.form.get('arrival_time'), '%Y-%m-%dT%H:%M')
        aircraft_type = request.form.get('aircraft_type')
        seats_total = int(request.form.get('seats_total'))
        price = float(request.form.get('price'))
        status = request.form.get('status')

        # Validate inputs
        if origin == destination:
            flash('Origin and destination cannot be the same.', 'danger')
            return redirect(url_for('admin_flights'))
        
        if departure_time >= arrival_time:
            flash('Departure time must be before arrival time.', 'danger')
            return redirect(url_for('admin_flights'))
        
        if seats_total <= 0:
            flash('Total seats must be a positive number.', 'danger')
            return redirect(url_for('admin_flights'))
        
        if price <= 0:
            flash('Price must be a positive number.', 'danger')
            return redirect(url_for('admin_flights'))
        
        # Create a new Flight object
        new_flight = Flight(
            flight_number=flight_number,
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            aircraft_type=aircraft_type,
            seats_total=seats_total,
            seats_available=seats_total,
            price=price,
            status=status
        )

        db.session.add(new_flight)
        db.session.commit()
        app.logger.info(f"Added flight: {new_flight.flight_number}, Total flights: {Flight.query.count()}")

        flash('Flight added successfully!', 'success')
        return redirect(url_for('admin_flights'))
    
    except ValueError as e:
        flash(f'Error adding flight: Invalid data format. {str(e)}', 'danger')
        return redirect(url_for('admin_flights'))
    except Exception as e:
        flash(f'Error adding flight: {str(e)}', 'danger')
        return redirect(url_for('admin_flights'))