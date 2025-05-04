from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, IntegerField, HiddenField, FormField, FieldList, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from datetime import datetime, date, timedelta
import data

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = data.get_user_by_username(username.data)
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = data.get_user_by_email(email.data)
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class FlightSearchForm(FlaskForm):
    origin = SelectField('From', validators=[DataRequired()], choices=[])
    destination = SelectField('To', validators=[DataRequired()], choices=[])
    departure_date = DateField('Departure Date', validators=[DataRequired()], format='%Y-%m-%d')
    passengers = IntegerField('Passengers', validators=[DataRequired()], default=1)
    submit = SubmitField('Search Flights')
    
    def __init__(self, *args, **kwargs):
        super(FlightSearchForm, self).__init__(*args, **kwargs)
        airport_choices = [(code, f"{data.airports[code]['city']} ({code})") for code in data.airports]
        self.origin.choices = airport_choices
        self.destination.choices = airport_choices
    
    def validate_departure_date(self, departure_date):
        if departure_date.data < date.today():
            raise ValidationError('Departure date cannot be in the past.')
    
    def validate_passengers(self, passengers):
        if passengers.data < 1:
            raise ValidationError('There must be at least 1 passenger.')
        if passengers.data > 9:
            raise ValidationError('Maximum 9 passengers per booking.')
    
    def validate(self, **kwargs):
        if not super(FlightSearchForm, self).validate(**kwargs):
            return False
        
        if self.origin.data == self.destination.data:
            self.destination.errors.append('Origin and destination cannot be the same.')
            return False
        
        return True

class PassengerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    passport_number = StringField('Passport Number (Optional)', validators=[Length(max=20)])
    address = StringField('Address (Optional)', validators=[Length(max=200)])
    
    def validate_date_of_birth(self, date_of_birth):
        today = date.today()
        if date_of_birth.data >= today:
            raise ValidationError('Date of birth must be in the past.')
        min_date = today - timedelta(days=120*365)
        if date_of_birth.data < min_date:
            raise ValidationError('Date of birth cannot be more than 120 years in the past.')

class BookingForm(FlaskForm):
    flight_id = HiddenField('Flight ID', validators=[DataRequired()])
    passengers = FieldList(FormField(PassengerForm), min_entries=1)
    selected_seats = HiddenField('Selected Seats')
    points_to_redeem = IntegerField('Frequent Flyer Points to Redeem', default=0, validators=[NumberRange(min=0)])
    submit = SubmitField('Confirm Booking')

class BookingSearchForm(FlaskForm):
    booking_reference = StringField('Booking Reference', validators=[DataRequired(), Length(min=6, max=6)])
    last_name = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Search')

class AdminFlightForm(FlaskForm):
    flight_number = StringField('Flight Number', validators=[DataRequired()])
    origin = SelectField('Origin', validators=[DataRequired()])
    destination = SelectField('Destination', validators=[DataRequired()])
    departure_time = DateTimeField('Departure Time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    arrival_time = DateTimeField('Arrival Time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    aircraft_type = SelectField('Aircraft Type', validators=[DataRequired()])
    seats_total = IntegerField('Total Seats', validators=[DataRequired(), NumberRange(min=1)])
    price = IntegerField('Base Price', validators=[DataRequired(), NumberRange(min=1)])
    status = SelectField('Status', choices=[
        ('Scheduled', 'Scheduled'),
        ('Delayed', 'Delayed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed')
    ])
    submit = SubmitField('Save Flight')
    
    def __init__(self, *args, **kwargs):
        super(AdminFlightForm, self).__init__(*args, **kwargs)
        airport_choices = [(code, f"{data.airports[code]['city']} ({code})") for code in data.airports]
        self.origin.choices = airport_choices
        self.destination.choices = airport_choices
        self.aircraft_type.choices = [(t, t) for t in data.aircraft_types]