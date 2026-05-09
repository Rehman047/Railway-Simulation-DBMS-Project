"""Staff API Routes"""
from flask import Blueprint, jsonify, request

from app.db import Database
from app.services.cancellation_service import CancellationService
from app.services.firebase_client import FirebaseClient

staff_bp = Blueprint('staff', __name__, url_prefix='/api/staff')

# ── Inline queries (no staff_queries.py exists yet) ───────────

_LIST_STAFF = """
    SELECT staff_id, first_name, last_name, email, phone_number,
           role, hire_date, created_at
    FROM staff
    ORDER BY last_name, first_name
    LIMIT %s OFFSET %s
"""

_COUNT_STAFF = "SELECT COUNT(*) FROM staff"

_GET_STAFF = """
    SELECT staff_id, first_name, last_name, email, phone_number,
           role, hire_date, created_at
    FROM staff
    WHERE staff_id = %s
"""

_CREATE_STAFF = """
    INSERT INTO staff (first_name, last_name, email, phone_number, role, hire_date)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING staff_id
"""

_UPDATE_STAFF = """
    UPDATE staff
    SET first_name = %s, last_name = %s, email = %s,
        phone_number = %s, role = %s
    WHERE staff_id = %s
"""


# ── Endpoints ─────────────────────────────────────────────────

@staff_bp.route('', methods=['GET'])
def list_staff():
    """List all staff members with pagination."""
    page  = request.args.get('page',  1,  type=int)
    limit = request.args.get('limit', 20, type=int)
    offset = (page - 1) * limit

    staff = Database.fetch_all(_LIST_STAFF, (limit, offset))
    total = Database.fetch_scalar(_COUNT_STAFF)

    return jsonify({
        'success': True,
        'data': staff,
        'meta': {
            'page': page, 'limit': limit, 'total': total,
            'pages': (total + limit - 1) // limit if total else 0,
        },
    }), 200


@staff_bp.route('/<int:staff_id>', methods=['GET'])
def get_staff(staff_id: int):
    """Get a staff member by ID."""
    member = Database.fetch_one(_GET_STAFF, (staff_id,))
    if not member:
        return jsonify({'success': False, 'error': 'Staff member not found'}), 404
    return jsonify({'success': True, 'data': member}), 200


@staff_bp.route('', methods=['POST'])
def create_staff():
    """
    Add a new staff member.
    Required JSON: first_name, last_name, email, role.
    Optional: phone_number, hire_date.
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    for field in ['first_name', 'last_name', 'email', 'role']:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

    # Duplicate email check
    existing = Database.fetch_one(
        "SELECT staff_id FROM staff WHERE LOWER(email) = LOWER(%s)", (data['email'],)
    )
    if existing:
        return jsonify({'success': False, 'error': 'Email already registered'}), 400

    from datetime import date
    hire_date = data.get('hire_date', date.today().isoformat())

    staff_id = Database.execute_returning(
        _CREATE_STAFF,
        (data['first_name'], data['last_name'], data['email'],
         data.get('phone_number'), data['role'], hire_date)
    )

    if staff_id:
        try:
            FirebaseClient.backup_data('staff', {
                str(staff_id): {
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'role': data['role'],
                    'staff_id': staff_id,
                }
            })
        except Exception:
            pass
        return jsonify({'success': True, 'staff_id': staff_id}), 201
    return jsonify({'success': False, 'error': 'Failed to create staff member'}), 500


@staff_bp.route('/<int:staff_id>', methods=['PUT'])
def update_staff(staff_id: int):
    """
    Update staff information.
    Updatable fields: first_name, last_name, email, phone_number, role.
    Only supply fields you want to change.
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    member = Database.fetch_one(_GET_STAFF, (staff_id,))
    if not member:
        return jsonify({'success': False, 'error': 'Staff member not found'}), 404

    first_name   = data.get('first_name',   member['first_name'])
    last_name    = data.get('last_name',    member['last_name'])
    email        = data.get('email',        member['email'])
    phone_number = data.get('phone_number', member['phone_number'])
    role         = data.get('role',         member['role'])

    # If email changed, check uniqueness
    if email != member['email']:
        dup = Database.fetch_one(
            "SELECT staff_id FROM staff WHERE LOWER(email) = LOWER(%s) AND staff_id != %s",
            (email, staff_id)
        )
        if dup:
            return jsonify({'success': False, 'error': 'Email already in use'}), 400

    affected = Database.execute(
        _UPDATE_STAFF, (first_name, last_name, email, phone_number, role, staff_id)
    )

    if affected > 0:
        try:
            FirebaseClient.backup_data('staff', {
                str(staff_id): {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone_number': phone_number,
                    'role': role,
                    'staff_id': staff_id,
                }
            })
        except Exception:
            pass
        return jsonify({'success': True, 'message': 'Staff member updated successfully'}), 200
    return jsonify({'success': False, 'error': 'No changes made'}), 400


@staff_bp.route('/<int:staff_id>/cancellations-processed', methods=['GET'])
def staff_cancellations(staff_id: int):
    """
    Get all cancellations processed by a staff member.
    Optional query params: from_date, to_date (YYYY-MM-DD).
    """
    member = Database.fetch_one(_GET_STAFF, (staff_id,))
    if not member:
        return jsonify({'success': False, 'error': 'Staff member not found'}), 404

    from_date = request.args.get('from_date', type=str)
    to_date   = request.args.get('to_date',   type=str)

    if (from_date and not to_date) or (to_date and not from_date):
        return jsonify({'success': False,
                        'error': 'from_date and to_date must be provided together'}), 400

    if from_date and to_date:
        from app.utils.validators import Validators
        if not Validators.validate_date(from_date) or not Validators.validate_date(to_date):
            return jsonify({'success': False,
                            'error': 'Dates must be in YYYY-MM-DD format'}), 400

    cancellations = CancellationService.get_staff_cancellations(
        staff_id=staff_id, from_date=from_date, to_date=to_date
    )
    return jsonify({
        'success': True,
        'data': cancellations,
        'count': len(cancellations),
        'staff_id': staff_id,
    }), 200
