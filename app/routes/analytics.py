"""Analytics API Routes"""
from flask import Blueprint, jsonify, request

from app.services.analytics_service import AnalyticsService
from app.utils.validators import Validators

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_date_range():
    """
    Pull from_date / to_date from query params and validate both.

    Returns:
        (from_date, to_date, None)          on success
        (None, None, error_response_tuple)  on failure
    """
    from_date = request.args.get('from_date', type=str)
    to_date   = request.args.get('to_date',   type=str)

    if not from_date or not to_date:
        err = jsonify({'success': False, 'error': 'from_date and to_date are required'}), 400
        return None, None, err

    if not Validators.validate_date(from_date) or not Validators.validate_date(to_date):
        err = jsonify({'success': False,
                       'error': 'from_date and to_date must be in YYYY-MM-DD format'}), 400
        return None, None, err

    return from_date, to_date, None


# ── Revenue ───────────────────────────────────────────────────────────────────

@analytics_bp.route('/revenue/by-train', methods=['GET'])
def revenue_by_train():
    """Revenue breakdown by train. Query params: from_date, to_date (YYYY-MM-DD)."""
    from_date, to_date, err = _require_date_range()
    if err:
        return err

    data = AnalyticsService.get_revenue_by_train(from_date, to_date)
    return jsonify({'success': True, 'data': data, 'count': len(data)}), 200


@analytics_bp.route('/revenue/by-route', methods=['GET'])
def revenue_by_route():
    """Revenue breakdown by route. Query params: from_date, to_date (YYYY-MM-DD)."""
    from_date, to_date, err = _require_date_range()
    if err:
        return err

    data = AnalyticsService.get_revenue_by_route(from_date, to_date)
    return jsonify({'success': True, 'data': data, 'count': len(data)}), 200


# ── Occupancy ─────────────────────────────────────────────────────────────────

@analytics_bp.route('/occupancy', methods=['GET'])
def occupancy_rate():
    """
    Occupancy rate across schedules.
    Optional query params: from_date, to_date (YYYY-MM-DD), train_id (int).
    """
    from_date = request.args.get('from_date', type=str)
    to_date   = request.args.get('to_date',   type=str)
    train_id  = request.args.get('train_id',  type=int)

    # Validate dates only when supplied
    if from_date and not Validators.validate_date(from_date):
        return jsonify({'success': False,
                        'error': 'from_date must be in YYYY-MM-DD format'}), 400
    if to_date and not Validators.validate_date(to_date):
        return jsonify({'success': False,
                        'error': 'to_date must be in YYYY-MM-DD format'}), 400

    data = AnalyticsService.get_occupancy_rate(
        from_date=from_date,
        to_date=to_date,
        train_id=train_id,
    )
    return jsonify({'success': True, 'data': data, 'count': len(data)}), 200


# ── Booking trends ────────────────────────────────────────────────────────────

@analytics_bp.route('/booking-trends', methods=['GET'])
def booking_trends():
    """Daily booking trends. Query params: from_date, to_date (YYYY-MM-DD)."""
    from_date, to_date, err = _require_date_range()
    if err:
        return err

    data = AnalyticsService.get_booking_trends(from_date, to_date)
    return jsonify({'success': True, 'data': data, 'count': len(data)}), 200


# ── Cancellation stats ────────────────────────────────────────────────────────

@analytics_bp.route('/cancellation-stats', methods=['GET'])
def cancellation_stats():
    """Cancellation statistics. Query params: from_date, to_date (YYYY-MM-DD)."""
    from_date, to_date, err = _require_date_range()
    if err:
        return err

    data = AnalyticsService.get_cancellation_statistics(from_date, to_date)
    return jsonify({'success': True, 'data': data}), 200


# ── Top routes ────────────────────────────────────────────────────────────────

@analytics_bp.route('/top-routes', methods=['GET'])
def top_routes():
    """
    Top routes by number of bookings.
    Optional query param: limit (int, default 10, max 50).
    """
    limit = request.args.get('limit', 10, type=int)

    if limit < 1 or limit > 50:
        return jsonify({'success': False,
                        'error': 'limit must be between 1 and 50'}), 400

    data = AnalyticsService.get_top_routes(limit=limit)
    return jsonify({'success': True, 'data': data, 'count': len(data)}), 200


# ── Passenger stats ───────────────────────────────────────────────────────────

@analytics_bp.route('/passenger-stats', methods=['GET'])
def passenger_stats():
    """Aggregate passenger statistics. No params required."""
    data = AnalyticsService.get_passenger_statistics()
    return jsonify({'success': True, 'data': data}), 200


# ── Staff performance ─────────────────────────────────────────────────────────

@analytics_bp.route('/staff-performance', methods=['GET'])
def staff_performance():
    """Staff performance metrics. Query params: from_date, to_date (YYYY-MM-DD)."""
    from_date, to_date, err = _require_date_range()
    if err:
        return err

    data = AnalyticsService.get_staff_performance(from_date, to_date)
    return jsonify({'success': True, 'data': data, 'count': len(data)}), 200


# ── Dashboard summary ─────────────────────────────────────────────────────────

@analytics_bp.route('/dashboard', methods=['GET'])
def dashboard_summary():
    """High-level summary metrics for the dashboard. No params required."""
    data = AnalyticsService.get_dashboard_summary()
    return jsonify({'success': True, 'data': data}), 200
