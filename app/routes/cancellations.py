"""Cancellations API Routes"""
from datetime import datetime

from flask import Blueprint, jsonify, request

from app.services.cancellation_service import CancellationService
from app.services.firebase_client import FirebaseClient
from app.utils.validators import Validators

cancellations_bp = Blueprint('cancellations', __name__, url_prefix='/api/cancellations')


@cancellations_bp.route('', methods=['GET'])
def list_cancellations():
    """List all cancellations with pagination."""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    result = CancellationService.list_cancellations(page=page, limit=limit)

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


@cancellations_bp.route('/<int:cancellation_id>', methods=['GET'])
def get_cancellation(cancellation_id: int):
    """Get a specific cancellation by ID."""
    cancellation = CancellationService.get_cancellation(cancellation_id)

    if not cancellation:
        return jsonify({'success': False, 'error': 'Cancellation not found'}), 404

    return jsonify({'success': True, 'data': cancellation}), 200


@cancellations_bp.route('', methods=['POST'])
def create_cancellation():
    """
    Create a cancellation for a booking.
    Expected JSON:
    {
      "booking_id": int,
      "reason": string,
      "staff_id": int (optional)
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    booking_id = data.get('booking_id')
    reason = data.get('reason')
    staff_id = data.get('staff_id', None)

    if not isinstance(booking_id, int) or booking_id <= 0:
        return jsonify({'success': False, 'error': 'booking_id must be a positive integer'}), 400
    if not isinstance(reason, str) or not reason.strip():
        return jsonify({'success': False, 'error': 'reason is required'}), 400
    if staff_id is not None and (not isinstance(staff_id, int) or staff_id <= 0):
        return jsonify({'success': False, 'error': 'staff_id must be a positive integer when provided'}), 400

    result = CancellationService.create_cancellation(
        booking_id=booking_id,
        reason=reason.strip(),
        staff_id=staff_id,
    )

    if result.get('success'):
        try:
            FirebaseClient.backup_data('cancellations', {
                str(result.get('cancellation_id', 'new')): {
                    'booking_id': booking_id,
                    'reason': reason,
                    'staff_id': staff_id,
                    'cancellation_id': result.get('cancellation_id'),
                }
            })
        except Exception:
            pass
        return jsonify(result), 201

    return jsonify(result), 400


@cancellations_bp.route('/staff/<int:staff_id>', methods=['GET'])
def get_staff_cancellations(staff_id: int):
    """
    Get cancellations processed by a staff member.
    Optional query params: from_date, to_date (YYYY-MM-DD)
    """
    from_date = request.args.get('from_date', None, type=str)
    to_date = request.args.get('to_date', None, type=str)

    if (from_date and not to_date) or (to_date and not from_date):
        return jsonify({'success': False, 'error': 'from_date and to_date must be provided together'}), 400

    if from_date and to_date:
        if not Validators.validate_date(from_date) or not Validators.validate_date(to_date):
            return jsonify({'success': False, 'error': 'from_date/to_date must be in YYYY-MM-DD format'}), 400

    result = CancellationService.get_staff_cancellations(
        staff_id=staff_id,
        from_date=from_date,
        to_date=to_date,
    )

    return jsonify({'success': True, 'data': result, 'count': len(result)}), 200


@cancellations_bp.route('/stats', methods=['GET'])
def get_cancellation_stats():
    """Get cancellation statistics for a date range."""
    from_date = request.args.get('from_date', None, type=str)
    to_date = request.args.get('to_date', None, type=str)

    if not from_date or not to_date:
        return jsonify({'success': False, 'error': 'from_date and to_date are required'}), 400

    if not Validators.validate_date(from_date) or not Validators.validate_date(to_date):
        return jsonify({'success': False, 'error': 'from_date/to_date must be in YYYY-MM-DD format'}), 400

    result = CancellationService.get_cancellation_stats(from_date, to_date)
    return jsonify({'success': True, 'data': result}), 200


@cancellations_bp.route('/reasons', methods=['GET'])
def get_cancellation_reasons():
    """Get cancellation reasons breakdown for a date range."""
    from_date = request.args.get('from_date', None, type=str)
    to_date = request.args.get('to_date', None, type=str)

    if not from_date or not to_date:
        return jsonify({'success': False, 'error': 'from_date and to_date are required'}), 400

    if not Validators.validate_date(from_date) or not Validators.validate_date(to_date):
        return jsonify({'success': False, 'error': 'from_date/to_date must be in YYYY-MM-DD format'}), 400

    result = CancellationService.get_cancellation_reasons(from_date, to_date)
    return jsonify({'success': True, 'data': result}), 200


@cancellations_bp.route('/<int:cancellation_id>/status', methods=['PUT'])
def update_cancellation_status(cancellation_id: int):
    """
    Update cancellation status.
    Expected JSON:
    {
      "status": "Pending" | "Processed" | "Refunded"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    status = data.get('status')
    if not isinstance(status, str) or not status.strip():
        return jsonify({'success': False, 'error': 'status is required'}), 400

    result = CancellationService.update_cancellation_status(
        cancellation_id=cancellation_id,
        status=status.strip(),
    )

    if result.get('success'):
        return jsonify(result), 200

    return jsonify(result), 400


@cancellations_bp.route('/pending-refunds', methods=['GET'])
def get_pending_refunds():
    """Get all cancellations with a pending refund (queries the pending_refunds_report view)."""
    from app.db import Database
    refunds = Database.fetch_all("SELECT * FROM pending_refunds_report")
    return jsonify({'success': True, 'data': refunds, 'count': len(refunds)}), 200


@cancellations_bp.route('/passenger/<int:passenger_id>', methods=['GET'])
def get_passenger_cancellations(passenger_id: int):
    """Get all cancellations for a specific passenger."""
    from app.db import Database
    cancellations = Database.fetch_all(
        """SELECT c.cancellation_id, c.booking_id, c.cancellation_date,
                  c.cancellation_reason, c.refund_amount, c.refund_status,
                  b.fare_amount, b.booking_status,
                  s.departure_date,
                  st_src.station_name AS source_station,
                  st_dst.station_name AS destination_station
           FROM cancellations c
           JOIN bookings  b    ON c.booking_id   = b.booking_id
           JOIN schedules s    ON b.schedule_id  = s.schedule_id
           JOIN routes    r    ON s.route_id     = r.route_id
           JOIN stations st_src ON r.source_station_id      = st_src.station_id
           JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
           WHERE b.passenger_id = %s
           ORDER BY c.cancellation_date DESC""",
        (passenger_id,)
    )
    return jsonify({'success': True, 'data': cancellations, 'count': len(cancellations)}), 200
