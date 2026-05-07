"""
Request / Response Validators — Service Layer
Business-rule validation for all API route handlers.

Differs from app/utils/validators.py (format/regex checks) in that
these functions enforce domain rules: age thresholds, date constraints,
amount limits, ID proof formats, and composite request validation.

Every public method returns a list of human-readable error strings.
An empty list means the data is valid.
"""
import re
from datetime import date, datetime


# ── Constants ──────────────────────────────────────────────────────────

MINIMUM_PASSENGER_AGE = 5          # youngest allowed traveller
MAXIMUM_PASSENGER_AGE = 120
MINIMUM_BOOKING_FARE  = 1.0        # PKR
MAXIMUM_BOOKING_FARE  = 1_000_000  # PKR
VALID_SEAT_CLASSES    = ['economy', 'business', 'first', 'luxury']
VALID_PAYMENT_METHODS = ['Cash', 'Card', 'Online', 'Cheque']
VALID_TRAIN_STATUSES  = ['active', 'inactive', 'maintenance']
VALID_TRAIN_TYPES     = ['Express', 'Local', 'Freight', 'Passenger', 'High-Speed']
VALID_COACH_STATUSES  = ['available', 'maintenance', 'retired']
VALID_ID_PROOF_TYPES  = ['CNIC', 'Passport', 'Driving License']


# ══════════════════════════════════════════════════════════════════════
# Format helpers (thin wrappers so routes only need one import)
# ══════════════════════════════════════════════════════════════════════

def _valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _valid_phone(phone: str) -> bool:
    """Accepts 03XX-XXXXXXX or 03XXXXXXXXX or +92-3XX-XXXXXXX."""
    cleaned = phone.replace('-', '').replace(' ', '')
    pattern = r'^(?:\+92|0)?3[0-9]{9}$'
    return bool(re.match(pattern, cleaned))


def _valid_cnic(cnic: str) -> bool:
    """CNIC format: 12345-6789012-3"""
    return bool(re.match(r'^\d{5}-\d{7}-\d$', cnic))


def _valid_date_format(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


def _parse_date(date_str: str):
    """Return a date object or None."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


# ══════════════════════════════════════════════════════════════════════
# Individual validators
# ══════════════════════════════════════════════════════════════════════

def validate_email(email) -> list:
    """Validate email format."""
    errors = []
    if not email or not isinstance(email, str) or not email.strip():
        errors.append('Email is required')
    elif not _valid_email(email.strip()):
        errors.append('Invalid email format (expected user@domain.com)')
    return errors


def validate_phone(phone) -> list:
    """Validate Pakistani mobile phone number."""
    errors = []
    if not phone or not isinstance(phone, str) or not phone.strip():
        errors.append('Phone number is required')
    elif not _valid_phone(phone.strip()):
        errors.append(
            'Invalid phone number — expected format: 0300-1234567 or +923001234567'
        )
    return errors


def validate_passenger_age(date_of_birth) -> list:
    """
    Validate passenger age.
    - Must be a valid date string (YYYY-MM-DD)
    - Passenger must be at least MINIMUM_PASSENGER_AGE years old
    - Cannot be older than MAXIMUM_PASSENGER_AGE years
    """
    errors = []
    if not date_of_birth:
        errors.append('Date of birth is required')
        return errors

    dob = _parse_date(date_of_birth)
    if dob is None:
        errors.append('Date of birth must be in YYYY-MM-DD format')
        return errors

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if dob > today:
        errors.append('Date of birth cannot be in the future')
    elif age < MINIMUM_PASSENGER_AGE:
        errors.append(
            f'Passenger must be at least {MINIMUM_PASSENGER_AGE} years old'
        )
    elif age > MAXIMUM_PASSENGER_AGE:
        errors.append(f'Age {age} exceeds maximum allowed ({MAXIMUM_PASSENGER_AGE})')

    return errors


def validate_booking_date(booking_date=None) -> list:
    """
    Validate booking date.
    - If provided, must be YYYY-MM-DD format and today or in the future.
    - booking_date is optional (defaults to today at booking time).
    """
    errors = []
    if booking_date is None:
        return errors   # optional field — service defaults to NOW()

    d = _parse_date(booking_date)
    if d is None:
        errors.append('booking_date must be in YYYY-MM-DD format')
    elif d < date.today():
        errors.append('booking_date cannot be in the past')

    return errors


def validate_payment_amount(amount, min_amount=MINIMUM_BOOKING_FARE) -> list:
    """Validate payment / fare amount."""
    errors = []
    if amount is None:
        errors.append('Amount is required')
        return errors
    try:
        value = float(amount)
    except (ValueError, TypeError):
        errors.append('Amount must be a numeric value')
        return errors

    if value < min_amount:
        errors.append(f'Amount must be at least {min_amount}')
    elif value > MAXIMUM_BOOKING_FARE:
        errors.append(f'Amount cannot exceed {MAXIMUM_BOOKING_FARE:,}')
    return errors


def validate_id_proof(id_proof_type, id_proof_number) -> list:
    """Validate identity proof type and number format."""
    errors = []

    if not id_proof_type:
        return errors   # optional field

    if id_proof_type not in VALID_ID_PROOF_TYPES:
        errors.append(
            f'id_proof_type must be one of: {", ".join(VALID_ID_PROOF_TYPES)}'
        )
        return errors

    if not id_proof_number or not str(id_proof_number).strip():
        errors.append('id_proof_number is required when id_proof_type is provided')
        return errors

    if id_proof_type == 'CNIC' and not _valid_cnic(id_proof_number):
        errors.append('CNIC must be in format: 12345-6789012-3')

    return errors


# ══════════════════════════════════════════════════════════════════════
# Composite request validators (used directly by route handlers)
# ══════════════════════════════════════════════════════════════════════

def validate_create_passenger(data: dict) -> list:
    """
    Full validation for POST /api/passengers.
    Returns a list of error strings; empty list = valid.
    """
    errors = []

    # Required string fields
    for field in ['first_name', 'last_name']:
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f'{field} is required')

    errors.extend(validate_email(data.get('email')))
    errors.extend(validate_phone(data.get('phone_number')))
    errors.extend(validate_passenger_age(data.get('date_of_birth')))
    errors.extend(
        validate_id_proof(
            data.get('id_proof_type'),
            data.get('id_proof_number')
        )
    )
    return errors


def validate_update_passenger(data: dict) -> list:
    """
    Validation for PUT /api/passengers/<id>.
    Only validates fields that are present in the payload.
    """
    errors = []
    if 'email' in data:
        errors.extend(validate_email(data['email']))
    if 'phone_number' in data:
        errors.extend(validate_phone(data['phone_number']))
    return errors


def validate_create_booking(data: dict) -> list:
    """Full validation for POST /api/bookings."""
    errors = []

    for field in ['passenger_id', 'schedule_id', 'seat_id']:
        val = data.get(field)
        if val is None:
            errors.append(f'{field} is required')
        elif not isinstance(val, int) or val <= 0:
            errors.append(f'{field} must be a positive integer')

    errors.extend(validate_payment_amount(data.get('fare_amount')))
    errors.extend(validate_booking_date(data.get('booking_date')))
    return errors


def validate_create_payment(data: dict) -> list:
    """Full validation for POST /api/payments."""
    errors = []

    booking_id = data.get('booking_id')
    if booking_id is None:
        errors.append('booking_id is required')
    elif not isinstance(booking_id, int) or booking_id <= 0:
        errors.append('booking_id must be a positive integer')

    errors.extend(validate_payment_amount(data.get('amount')))

    method = data.get('method')
    if not method:
        errors.append('method is required')
    elif method not in VALID_PAYMENT_METHODS:
        errors.append(
            f'method must be one of: {", ".join(VALID_PAYMENT_METHODS)}'
        )
    return errors


def validate_create_train(data: dict) -> list:
    """Full validation for POST /api/trains."""
    errors = []

    for field in ['train_name', 'train_number', 'train_type']:
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f'{field} is required')

    for field in ['capacity', 'total_coaches']:
        val = data.get(field)
        if val is None:
            errors.append(f'{field} is required')
        else:
            try:
                if int(val) <= 0:
                    errors.append(f'{field} must be a positive integer')
            except (ValueError, TypeError):
                errors.append(f'{field} must be a valid integer')

    status = data.get('status', 'active')
    if status not in VALID_TRAIN_STATUSES:
        errors.append(
            f'status must be one of: {", ".join(VALID_TRAIN_STATUSES)}'
        )
    return errors


def validate_create_station(data: dict) -> list:
    """Full validation for POST /api/stations."""
    errors = []

    for field in ['station_name', 'city', 'state']:
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f'{field} is required')

    if data.get('contact_number'):
        errors.extend(validate_phone(data['contact_number']))

    return errors
