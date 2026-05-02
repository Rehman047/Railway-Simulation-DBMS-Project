"""Payments API Routes"""
from flask import Blueprint, jsonify, request

from app.services.payment_service import PaymentService
from app.utils.validators import Validators

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')


@payments_bp.route('', methods=['GET'])
def list_payments():
    """List payments with pagination."""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    result = PaymentService.list_payments(page=page, limit=limit)

    return (
        jsonify(
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
        ),
        200,
    )


@payments_bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id: int):
    """Get a single payment by ID."""
    payment = PaymentService.get_payment(payment_id)
    if not payment:
        return jsonify({'success': False, 'error': 'Payment not found'}), 404

    return jsonify({'success': True, 'data': payment}), 200


@payments_bp.route('/pending', methods=['GET'])
def get_pending_payments():
    """Get all pending payments."""
    payments = PaymentService.get_pending_payments()
    return jsonify({'success': True, 'data': payments, 'count': len(payments)}), 200


@payments_bp.route('/booking/<int:booking_id>', methods=['GET'])
def get_booking_payments(booking_id: int):
    """Get all payments for a booking."""
    payments = PaymentService.get_booking_payments(booking_id)
    return jsonify({'success': True, 'data': payments, 'count': len(payments)}), 200


@payments_bp.route('', methods=['POST'])
def record_payment():
    """
    Record a payment for a booking.
    Expected JSON:
    {
      "booking_id": int,
      "amount": number,
      "method": "Cash" | "Card" | "Online" | "Cheque"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    errors = Validators.validate_payment_data(data)
    if errors:
        return jsonify({'success': False, 'error': errors}), 400

    booking_id = data['booking_id']
    amount = data['amount']
    method = data['method']

    result = PaymentService.record_payment(booking_id=booking_id, amount=amount, method=method)
    if result.get('success'):
        return jsonify(result), 201

    return jsonify(result), 400


@payments_bp.route('/<int:payment_id>', methods=['PUT'])
def update_payment_status(payment_id: int):
    """
    Update payment status.
    Expected JSON:
    {
      "status": "Completed" | "Pending" | "Failed" | "Refunded"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    status = data.get('status')
    if not isinstance(status, str) or not status.strip():
        return jsonify({'success': False, 'error': 'status is required'}), 400

    result = PaymentService.update_payment_status(payment_id=payment_id, status=status.strip())
    if result.get('success'):
        return jsonify(result), 200

    return jsonify(result), 400


@payments_bp.route('/refund', methods=['POST'])
def process_refund():
    """
    Process refund for a cancelled booking.
    Expected JSON:
    {
      "cancellation_id": int,
      "refund_amount": number
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    cancellation_id = data.get('cancellation_id')
    refund_amount = data.get('refund_amount')

    if not isinstance(cancellation_id, int) or cancellation_id <= 0:
        return jsonify({'success': False, 'error': 'cancellation_id must be a positive integer'}), 400
    if refund_amount is None or not Validators.validate_fare_amount(refund_amount):
        return jsonify({'success': False, 'error': 'refund_amount must be a positive number'}), 400

    result = PaymentService.process_refund(
        cancellation_id=cancellation_id,
        refund_amount=refund_amount,
    )
    if result.get('success'):
        return jsonify(result), 200

    return jsonify(result), 400


@payments_bp.route('/revenue/summary', methods=['GET'])
def get_revenue_summary():
    """Revenue summary for a date range. Query params: from_date, to_date (YYYY-MM-DD)."""
    from_date = request.args.get('from_date', None, type=str)
    to_date = request.args.get('to_date', None, type=str)

    if not from_date or not to_date:
        return jsonify({'success': False, 'error': 'from_date and to_date are required'}), 400

    if not Validators.validate_date(from_date) or not Validators.validate_date(to_date):
        return jsonify({'success': False, 'error': 'from_date/to_date must be in YYYY-MM-DD format'}), 400

    result = PaymentService.get_revenue_summary(from_date=from_date, to_date=to_date)
    return jsonify({'success': True, 'data': result}), 200


@payments_bp.route('/revenue/by-method', methods=['GET'])
def get_payments_by_method():
    """Revenue breakdown by payment method. Query params: from_date, to_date (YYYY-MM-DD)."""
    from_date = request.args.get('from_date', None, type=str)
    to_date = request.args.get('to_date', None, type=str)

    if not from_date or not to_date:
        return jsonify({'success': False, 'error': 'from_date and to_date are required'}), 400

    if not Validators.validate_date(from_date) or not Validators.validate_date(to_date):
        return jsonify({'success': False, 'error': 'from_date/to_date must be in YYYY-MM-DD format'}), 400

    result = PaymentService.get_payments_by_method(from_date=from_date, to_date=to_date)
    return jsonify({'success': True, 'data': result}), 200
