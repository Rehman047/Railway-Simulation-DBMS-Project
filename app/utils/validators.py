"""
Data Validators
Validation functions for user input and business logic
"""
import re
from datetime import datetime


class Validators:
    """Validation utilities for passenger and booking data"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate Pakistani phone number format"""
        # Format: 0300-1234567 or 03001234567
        pattern = r'^(?:\+92|0)?(?:3[0-9]{2})[0-9]{7}$'
        # Remove dashes for validation
        cleaned = phone.replace('-', '')
        return re.match(pattern, cleaned) is not None
    
    @staticmethod
    def validate_cnic(cnic):
        """Validate CNIC format (Pakistani ID)"""
        # Format: 12345-6789012-3
        pattern = r'^\d{5}-\d{7}-\d$'
        return re.match(pattern, cnic) is not None
    
    @staticmethod
    def validate_date(date_str):
        """Validate date format (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_time(time_str):
        """Validate time format (HH:MM:SS)"""
        try:
            datetime.strptime(time_str, '%H:%M:%S')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_of_birth(dob_str):
        """Validate date of birth (must be adult)"""
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age >= 18 and age <= 120
        except ValueError:
            return False
    
    @staticmethod
    def validate_fare_amount(amount):
        """Validate fare amount (must be positive)"""
        try:
            return float(amount) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_distance(distance):
        """Validate distance (must be positive)"""
        try:
            return float(distance) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_passenger_data(data):
        """Validate complete passenger data"""
        errors = []
        
        if 'first_name' not in data or not data['first_name']:
            errors.append('First name is required')
        
        if 'last_name' not in data or not data['last_name']:
            errors.append('Last name is required')
        
        if 'email' not in data or not data['email']:
            errors.append('Email is required')
        elif not Validators.validate_email(data['email']):
            errors.append('Invalid email format')
        
        if 'phone_number' not in data or not data['phone_number']:
            errors.append('Phone number is required')
        elif not Validators.validate_phone(data['phone_number']):
            errors.append('Invalid phone number format')
        
        if 'date_of_birth' not in data or not data['date_of_birth']:
            errors.append('Date of birth is required')
        elif not Validators.validate_date_of_birth(data['date_of_birth']):
            errors.append('Invalid date of birth (must be adult)')
        
        return errors
    
    @staticmethod
    def validate_booking_data(data):
        """Validate complete booking data"""
        errors = []
        
        if 'passenger_id' not in data or not data['passenger_id']:
            errors.append('Passenger ID is required')
        elif not isinstance(data['passenger_id'], int) or data['passenger_id'] <= 0:
            errors.append('Invalid passenger ID')
        
        if 'schedule_id' not in data or not data['schedule_id']:
            errors.append('Schedule ID is required')
        elif not isinstance(data['schedule_id'], int) or data['schedule_id'] <= 0:
            errors.append('Invalid schedule ID')
        
        if 'seat_id' not in data or not data['seat_id']:
            errors.append('Seat ID is required')
        elif not isinstance(data['seat_id'], int) or data['seat_id'] <= 0:
            errors.append('Invalid seat ID')
        
        if 'fare_amount' not in data or not data['fare_amount']:
            errors.append('Fare amount is required')
        elif not Validators.validate_fare_amount(data['fare_amount']):
            errors.append('Invalid fare amount (must be positive)')
        
        return errors
    
    @staticmethod
    def validate_payment_data(data):
        """Validate payment data"""
        errors = []
        
        if 'booking_id' not in data or not data['booking_id']:
            errors.append('Booking ID is required')
        
        if 'amount' not in data or not data['amount']:
            errors.append('Amount is required')
        elif not Validators.validate_fare_amount(data['amount']):
            errors.append('Invalid amount (must be positive)')
        
        if 'method' not in data or not data['method']:
            errors.append('Payment method is required')
        elif data['method'] not in ['Cash', 'Card', 'Online', 'Cheque']:
            errors.append('Invalid payment method')
        
        return errors
