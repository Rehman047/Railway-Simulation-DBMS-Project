"""
Bookings API Routes
REST endpoints for booking management and seat availability
"""
from flask import Blueprint, jsonify, request

from app.services.booking_service import BookingService
from app.utils.validators import Validators

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')


@bookings_bp.route('', methods=['GET'])
def list_bookings():
    """
    List bookings with pagination.
    Optional query param: status (filters by booking_status)
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    status = request.args.get('status', None, type=str)

    result = BookingService.list_bookings(page=page, limit=limit, status_filter=status)

    return jsonify(
        {
            'success': True,
            'data': result['data'],
            'meta': {
                'page': result['page'],
                'limit': result['limit'],
                'total': result['total'],
                'pages': result['pages'],
            },
        }
    ), 200


@bookings_bp.route('/<int:booking_id>', methods=['GET'])
def get_booking(booking_id: int):
    """Get booking details by booking_id (includes passenger/schedule/seat info)."""
    booking = BookingService.get_booking_with_details(booking_id)

    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'}), 404

    return jsonify({'success': True, 'data': booking}), 200


@bookings_bp.route('', methods=['POST'])
def create_booking():
    """
    Create a new booking.
    Expected JSON:
    {
      "passenger_id": int,
      "schedule_id": int,
      "seat_id": int,
      "fare_amount": number
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    errors = Validators.validate_booking_data(data)
    if errors:
        return jsonify({'success': False, 'error': errors}), 400

    result = BookingService.create_booking(
        passenger_id=data['passenger_id'],
        schedule_id=data['schedule_id'],
        seat_id=data['seat_id'],
        fare_amount=data['fare_amount'],
    )

    if result.get('success'):
        return jsonify(result), 201

    return jsonify(result), 400


@bookings_bp.route('/available-seats', methods=['GET'])
def available_seats():
    """
    Get available seats for a schedule.
    Query param: schedule_id (int)
    """
    schedule_id = request.args.get('schedule_id', type=int)
    if not schedule_id or schedule_id <= 0:
        return jsonify({'success': False, 'error': 'Valid schedule_id is required'}), 400

    seats = BookingService.get_available_seats(schedule_id)
    return jsonify({'success': True, 'data': seats, 'schedule_id': schedule_id}), 200


@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id: int):
    """
    Cancel a booking.
    Expected JSON:
    {
      "reason": string,
      "staff_id": int
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    reason = data.get('reason')
    staff_id = data.get('staff_id')

    if not reason or not isinstance(reason, str):
        return jsonify({'success': False, 'error': 'reason is required'}), 400
    if not isinstance(staff_id, int) or staff_id <= 0:
        return jsonify({'success': False, 'error': 'staff_id must be a positive integer'}), 400

    result = BookingService.cancel_booking(
        booking_id=booking_id,
        reason=reason,
        staff_id=staff_id,
    )

    if result.get('success'):
        return jsonify(result), 200

    # keep service error semantics
    return jsonify(result), 400
