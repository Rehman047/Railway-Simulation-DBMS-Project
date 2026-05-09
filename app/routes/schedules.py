"""
Schedules API Routes
Complete schedule management endpoints
"""
from flask import Blueprint, request, jsonify
from app.services.schedule_service import ScheduleService
from datetime import datetime

schedules_bp = Blueprint('schedules', __name__, url_prefix='/api/schedules')


# ==================== LIST & GET SCHEDULES ====================

@schedules_bp.route('', methods=['GET'])
def list_schedules():
    """
    Get all schedules with pagination
    Query params:
        - page: page number (default: 1)
        - limit: items per page (default: 20)
    """
    try:
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=20, type=int)
        
        # Validate pagination parameters
        if page < 1 or limit < 1 or limit > 500:
            return jsonify({
                'success': False,
                'error': 'Invalid pagination parameters. Page and limit must be positive. Limit max 500.'
            }), 400
        
        result = ScheduleService.list_schedules(page, limit)
        
        return jsonify({
            'success': True,
            'data': result['data'],
            'meta': {
                'page': result['page'],
                'limit': result['limit'],
                'total': result['total'],
                'pages': result['pages']
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch schedules: {str(e)}'
        }), 500


@schedules_bp.route('/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """
    Get a single schedule with full details
    Includes: train info, route info, occupancy, available seats
    """
    try:
        # Get schedule details
        schedule = ScheduleService.get_schedule_with_details(schedule_id)
        
        if not schedule:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': schedule
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch schedule: {str(e)}'
        }), 500


# ==================== CREATE SCHEDULE ====================

@schedules_bp.route('', methods=['POST'])
def create_schedule():
    """
    Create a new schedule
    Request body:
    {
        "train_id": 1,
        "route_id": 2,
        "departure_date": "2024-06-15",
        "departure_time": "10:30",
        "arrival_time": "14:45"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['train_id', 'route_id', 'departure_date', 'departure_time', 'arrival_time']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(required_fields)}'
            }), 400
        
        # Validate data types
        try:
            train_id = int(data['train_id'])
            route_id = int(data['route_id'])
            departure_date = datetime.strptime(data['departure_date'], '%Y-%m-%d').date()
            departure_time = datetime.strptime(data['departure_time'], '%H:%M').time()
            arrival_time = datetime.strptime(data['arrival_time'], '%H:%M').time()
        except (ValueError, TypeError) as e:
            return jsonify({
                'success': False,
                'error': f'Invalid data format: {str(e)}'
            }), 400
        
        # Validate business logic
        if departure_time >= arrival_time:
            return jsonify({
                'success': False,
                'error': 'Departure time must be before arrival time'
            }), 400
        
        if departure_date < datetime.now().date():
            return jsonify({
                'success': False,
                'error': 'Departure date cannot be in the past'
            }), 400
        
        # Create schedule
        schedule_status = data.get('schedule_status', 'scheduled')
        result = ScheduleService.create_schedule(
            train_id,
            route_id,
            departure_date,
            departure_time,
            arrival_time,
            schedule_status
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Schedule created successfully',
                'schedule_id': result['schedule_id']
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create schedule: {str(e)}'
        }), 500


# ==================== UPDATE SCHEDULE ====================

@schedules_bp.route('/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """
    Update schedule times
    Can only update if no bookings exist
    Request body:
    {
        "departure_time": "11:00",
        "arrival_time": "15:30"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is empty'
            }), 400
        
        # Validate schedule exists
        schedule = ScheduleService.get_schedule(schedule_id)
        if not schedule:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
        
        # Parse times if provided
        departure_time = None
        arrival_time = None
        
        if 'departure_time' in data:
            try:
                departure_time = datetime.strptime(data['departure_time'], '%H:%M').time()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid departure_time format (use HH:MM)'
                }), 400
        
        if 'arrival_time' in data:
            try:
                arrival_time = datetime.strptime(data['arrival_time'], '%H:%M').time()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid arrival_time format (use HH:MM)'
                }), 400
        
        # Validate times if both provided
        if departure_time and arrival_time:
            if departure_time >= arrival_time:
                return jsonify({
                    'success': False,
                    'error': 'Departure time must be before arrival time'
                }), 400
        
        # Update schedule
        result = ScheduleService.update_schedule(schedule_id, departure_time, arrival_time)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result.get('message', 'Schedule updated')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update schedule: {str(e)}'
        }), 500


# ==================== DELETE SCHEDULE ====================

@schedules_bp.route('/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """
    Delete a schedule (only if no bookings)
    """
    try:
        # Validate schedule exists
        schedule = ScheduleService.get_schedule(schedule_id)
        if not schedule:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
        
        # Check for bookings before deletion
        from app.db import Database
        booking_count = Database.fetch_scalar(
            "SELECT COUNT(*) FROM bookings WHERE schedule_id = %s",
            (schedule_id,)
        )
        
        if booking_count and booking_count > 0:
            return jsonify({
                'success': False,
                'error': f'Cannot delete schedule with {booking_count} existing bookings. Cancel the schedule instead.'
            }), 400
        
        # Delete schedule
        affected = Database.execute(
            "DELETE FROM schedules WHERE schedule_id = %s",
            (schedule_id,)
        )
        
        if affected > 0:
            return jsonify({
                'success': True,
                'message': 'Schedule deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete schedule'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete schedule: {str(e)}'
        }), 500


# ==================== CANCEL SCHEDULE (with cascading) ====================

@schedules_bp.route('/<int:schedule_id>/cancel', methods=['POST'])
def cancel_schedule(schedule_id):
    """
    Cancel a schedule (cascades to all bookings)
    Atomic transaction for data integrity
    Request body:
    {
        "reason": "Maintenance required"
    }
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Schedule cancelled by admin')
        
        if not reason or len(reason.strip()) == 0:
            reason = 'Schedule cancelled by admin'
        
        # Validate schedule exists
        schedule = ScheduleService.get_schedule(schedule_id)
        if not schedule:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
        
        # Check if already cancelled
        if schedule.get('schedule_status') == 'cancelled':
            return jsonify({
                'success': False,
                'error': 'Schedule is already cancelled'
            }), 400
        
        # Cancel schedule (cascades to bookings)
        result = ScheduleService.cancel_schedule(schedule_id, reason)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'cancelled_bookings': result.get('cancelled_bookings', 0)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to cancel schedule: {str(e)}'
        }), 500


# ==================== AVAILABLE SEATS ====================

@schedules_bp.route('/<int:schedule_id>/available-seats', methods=['GET'])
def get_available_seats(schedule_id):
    """
    Get count of available seats for a schedule
    """
    try:
        # Validate schedule exists
        schedule = ScheduleService.get_schedule(schedule_id)
        if not schedule:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
        
        available_seats = ScheduleService.get_available_seats(schedule_id)
        
        return jsonify({
            'success': True,
            'schedule_id': schedule_id,
            'available_seats': available_seats
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch available seats: {str(e)}'
        }), 500


# ==================== OCCUPANCY ====================

@schedules_bp.route('/<int:schedule_id>/occupancy', methods=['GET'])
def get_occupancy(schedule_id):
    """
    Get occupancy details for a schedule
    Returns: total seats, booked seats, available seats, occupancy percentage
    """
    try:
        # Validate schedule exists
        schedule = ScheduleService.get_schedule(schedule_id)
        if not schedule:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
        
        # Get detailed schedule info with occupancy
        schedule_details = ScheduleService.get_schedule_with_details(schedule_id)
        
        if not schedule_details:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch schedule details'
            }), 500
        
        total_seats = schedule_details.get('available_seats', 0) + schedule_details.get('booked_seats', 0)
        booked_seats = schedule_details.get('booked_seats', 0)
        available_seats = schedule_details.get('available_seats', 0)
        
        occupancy_percentage = 0
        if total_seats > 0:
            occupancy_percentage = (booked_seats / total_seats) * 100
        
        return jsonify({
            'success': True,
            'schedule_id': schedule_id,
            'total_seats': total_seats,
            'booked_seats': booked_seats,
            'available_seats': available_seats,
            'occupancy_percentage': round(occupancy_percentage, 2)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch occupancy: {str(e)}'
        }), 500


# ==================== SCHEDULES FOR ROUTE ====================

@schedules_bp.route('/route/<int:route_id>', methods=['GET'])
def get_schedules_for_route(route_id):
    """
    Get all schedules for a specific route between dates
    Query params:
        - from_date: start date (format: YYYY-MM-DD)
        - to_date: end date (format: YYYY-MM-DD)
    """
    try:
        # Get query parameters
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')
        
        # Validate parameters
        if not from_date_str or not to_date_str:
            return jsonify({
                'success': False,
                'error': 'from_date and to_date parameters are required (format: YYYY-MM-DD)'
            }), 400
        
        # Parse dates
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        if from_date > to_date:
            return jsonify({
                'success': False,
                'error': 'from_date must be before or equal to to_date'
            }), 400
        
        # Validate route exists
        from app.db import Database
        route = Database.fetch_one(
            "SELECT route_id FROM routes WHERE route_id = %s",
            (route_id,)
        )
        if not route:
            return jsonify({
                'success': False,
                'error': 'Route not found'
            }), 404
        
        # Get schedules
        schedules = ScheduleService.get_schedules_for_route(route_id, from_date, to_date)
        
        return jsonify({
            'success': True,
            'route_id': route_id,
            'from_date': from_date_str,
            'to_date': to_date_str,
            'data': schedules
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch schedules for route: {str(e)}'
        }), 500


# ==================== SEARCH SCHEDULES ====================

@schedules_bp.route('/search', methods=['GET'])
def search_schedules():
    """
    Search schedules by various criteria
    Query params:
        - train_id: filter by train (optional)
        - status: filter by status (optional) - 'Active', 'Cancelled', etc.
        - from_date: start date (optional)
        - to_date: end date (optional)
        - page: pagination (default: 1)
        - limit: items per page (default: 20)
    """
    try:
        # Get filters
        train_id = request.args.get('train_id', type=int)
        status = request.args.get('status', type=str)
        from_date = request.args.get('from_date', type=str)
        to_date = request.args.get('to_date', type=str)
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=20, type=int)
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if train_id:
            where_conditions.append("s.train_id = %s")
            params.append(train_id)
        
        if status:
            where_conditions.append("s.schedule_status = %s")
            params.append(status)
        
        if from_date:
            try:
                datetime.strptime(from_date, '%Y-%m-%d')
                where_conditions.append("s.departure_date >= %s")
                params.append(from_date)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid from_date format (use YYYY-MM-DD)'
                }), 400
        
        if to_date:
            try:
                datetime.strptime(to_date, '%Y-%m-%d')
                where_conditions.append("s.departure_date <= %s")
                params.append(to_date)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid to_date format (use YYYY-MM-DD)'
                }), 400
        
        # Build query
        from app.db import Database
        base_query = """
            SELECT s.schedule_id, s.train_id, s.route_id, s.departure_date, 
                   s.departure_time, s.arrival_time, s.schedule_status,
                   t.train_name, t.train_number,
                   st_src.station_name as source_station,
                   st_dst.station_name as destination_station
            FROM schedules s
            JOIN trains t ON s.train_id = t.train_id
            JOIN routes r ON s.route_id = r.route_id
            JOIN stations st_src ON r.source_station_id = st_src.station_id
            JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
        """
        
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        # Add pagination
        base_query += " ORDER BY s.departure_date DESC, s.departure_time LIMIT %s OFFSET %s"
        offset = (page - 1) * limit
        params.extend([limit, offset])
        
        # Execute search
        schedules = Database.fetch_all(base_query, params)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM schedules s"
        if where_conditions:
            count_query += " WHERE " + " AND ".join([c for c in where_conditions[:-2]] if len(where_conditions) > 2 else where_conditions)
        
        total = Database.fetch_scalar(count_query) or 0
        
        return jsonify({
            'success': True,
            'data': schedules,
            'meta': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500


# ==================== ERROR HANDLERS ====================

@schedules_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Schedule endpoint not found'
    }), 404


@schedules_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed for this endpoint'
    }), 405