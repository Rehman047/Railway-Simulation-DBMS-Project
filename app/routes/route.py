"""
Routes API Endpoints
Flask routes for train route management
"""
from flask import Blueprint, request, jsonify
from app.services.firebase_client import FirebaseClient
from app.services.route_service import RouteService
from app.services.auth_service import require_admin_auth
from app.db import Database

routes_bp = Blueprint('routes', __name__, url_prefix='/api/routes')


# ==================== LIST & GET ROUTES ====================

@routes_bp.route('', methods=['GET'])
def list_routes():
    """
    Get all routes with pagination
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
        
        result = RouteService.list_routes(page, limit)
        
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
            'error': f'Failed to fetch routes: {str(e)}'
        }), 500


@routes_bp.route('/<int:route_id>', methods=['GET'])
def get_route(route_id):
    """
    Get a single route with full details
    Includes: train info, station info, distance, duration
    """
    try:
        route = RouteService.get_route_details(route_id)
        
        if not route:
            return jsonify({
                'success': False,
                'error': 'Route not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': route
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch route: {str(e)}'
        }), 500


# ==================== CREATE ROUTE ====================

@routes_bp.route('', methods=['POST'])
@require_admin_auth
def create_route():
    """
    Create a new route
    Request body:
    {
        "train_id": 1,
        "source_station_id": 5,
        "destination_station_id": 8,
        "distance": 180.5,
        "estimated_duration": 4.5
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['train_id', 'source_station_id', 'destination_station_id', 'distance', 'estimated_duration']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(required_fields)}'
            }), 400
        
        # Validate data types
        try:
            train_id = int(data['train_id'])
            source_station_id = int(data['source_station_id'])
            destination_station_id = int(data['destination_station_id'])
            distance = float(data['distance'])
            estimated_duration = float(data['estimated_duration'])
        except (ValueError, TypeError) as e:
            return jsonify({
                'success': False,
                'error': f'Invalid data type: {str(e)}'
            }), 400
        
        # Create route
        result = RouteService.create_route(
            train_id,
            source_station_id,
            destination_station_id,
            distance,
            estimated_duration
        )
        
        if result['success']:
            try:
                FirebaseClient.backup_data('routes', {
                    str(result['route_id']): {
                        'train_id': train_id,
                        'source_station_id': source_station_id,
                        'destination_station_id': destination_station_id,
                        'distance': distance,
                        'estimated_duration': estimated_duration,
                        'route_id': result['route_id'],
                    }
                })
            except Exception:
                pass
            return jsonify({
                'success': True,
                'message': 'Route created successfully',
                'route_id': result['route_id']
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create route: {str(e)}'
        }), 500


# ==================== UPDATE ROUTE ====================

@routes_bp.route('/<int:route_id>', methods=['PUT'])
@require_admin_auth
def update_route(route_id):
    """
    Update route distance and/or estimated duration
    Can only update if no active schedules exist
    Request body:
    {
        "distance": 190.5,
        "estimated_duration": 4.75
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is empty'
            }), 400
        
        # Validate route exists
        route = RouteService.get_route(route_id)
        if not route:
            return jsonify({
                'success': False,
                'error': 'Route not found'
            }), 404
        
        # Parse values if provided
        distance = None
        estimated_duration = None
        
        if 'distance' in data:
            try:
                distance = float(data['distance'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid distance format (must be a number)'
                }), 400
        
        if 'estimated_duration' in data:
            try:
                estimated_duration = float(data['estimated_duration'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid estimated_duration format (must be a number)'
                }), 400
        
        # Update route
        result = RouteService.update_route(route_id, distance, estimated_duration)
        
        if result['success']:
            try:
                update_data = {}
                if distance is not None: update_data['distance'] = distance
                if estimated_duration is not None: update_data['estimated_duration'] = estimated_duration
                FirebaseClient.backup_data('routes', {str(route_id): {**update_data, 'route_id': route_id}})
            except Exception:
                pass
            return jsonify({
                'success': True,
                'message': result.get('message', 'Route updated')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update route: {str(e)}'
        }), 500


# ==================== DELETE ROUTE ====================

@routes_bp.route('/<int:route_id>', methods=['DELETE'])
@require_admin_auth
def delete_route(route_id):
    """
    Delete a route (only if no schedules exist)
    """
    try:
        # Validate route exists
        route = RouteService.get_route(route_id)
        if not route:
            return jsonify({
                'success': False,
                'error': 'Route not found'
            }), 404
        
        # Delete route
        result = RouteService.delete_route(route_id)
        
        if result['success']:
            try:
                FirebaseClient.delete_document('routes', route_id)
            except Exception:
                pass
            return jsonify({
                'success': True,
                'message': result.get('message', 'Route deleted')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete route: {str(e)}'
        }), 500


# ==================== FIND ROUTES BETWEEN STATIONS ====================

@routes_bp.route('/between', methods=['GET'])
def find_routes_between_stations():
    """
    Find all routes between two stations
    Query params:
        - from_station: source station ID (required)
        - to_station: destination station ID (required)
    """
    try:
        from_station = request.args.get('from_station', type=int)
        to_station = request.args.get('to_station', type=int)
        
        # Validate parameters
        if not from_station or not to_station:
            return jsonify({
                'success': False,
                'error': 'from_station and to_station parameters are required'
            }), 400
        
        if from_station == to_station:
            return jsonify({
                'success': False,
                'error': 'Source and destination stations must be different'
            }), 400
        
        # Find routes
        routes = RouteService.find_routes_between_stations(from_station, to_station)
        
        return jsonify({
            'success': True,
            'from_station': from_station,
            'to_station': to_station,
            'data': routes
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to find routes: {str(e)}'
        }), 500


# ==================== ROUTES FOR SPECIFIC TRAIN ====================

@routes_bp.route('/train/<int:train_id>', methods=['GET'])
def get_routes_for_train(train_id):
    """
    Get all routes assigned to a specific train
    """
    try:
        # Validate train exists
        train = Database.fetch_one(
            "SELECT train_id FROM trains WHERE train_id = %s",
            (train_id,)
        )
        if not train:
            return jsonify({
                'success': False,
                'error': 'Train not found'
            }), 404
        
        # Get routes
        routes = RouteService.get_routes_for_train(train_id)
        
        return jsonify({
            'success': True,
            'train_id': train_id,
            'data': routes
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch routes for train: {str(e)}'
        }), 500


# ==================== ROUTE STATISTICS ====================

@routes_bp.route('/<int:route_id>/statistics', methods=['GET'])
def get_route_statistics(route_id):
    """
    Get statistics for a route
    Returns: schedule count, bookings, revenue, average occupancy
    """
    try:
        # Validate route exists
        route = RouteService.get_route(route_id)
        if not route:
            return jsonify({
                'success': False,
                'error': 'Route not found'
            }), 404
        
        # Get statistics
        stats = RouteService.get_route_statistics(route_id)
        
        return jsonify({
            'success': True,
            'route_id': route_id,
            'data': {
                'route': stats['route'],
                'schedules_count': stats['schedule_count'],
                'total_bookings': stats['total_bookings'],
                'active_bookings': stats['active_bookings'],
                'total_revenue': float(stats['total_revenue']) if stats['total_revenue'] else 0,
                'average_occupancy': round(float(stats['average_occupancy']), 2) if stats['average_occupancy'] else 0
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch route statistics: {str(e)}'
        }), 500


# ==================== SEARCH ROUTES ====================

@routes_bp.route('/search', methods=['GET'])
def search_routes():
    """
    Search routes with optional filters
    Query params:
        - train_id: filter by train ID (optional)
        - from_station: filter by source station ID (optional)
        - to_station: filter by destination station ID (optional)
        - page: pagination (default: 1)
        - limit: items per page (default: 20)
    """
    try:
        # Get filters
        train_id = request.args.get('train_id', type=int)
        from_station = request.args.get('from_station', type=int)
        to_station = request.args.get('to_station', type=int)
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=20, type=int)
        
        # Validate pagination
        if page < 1 or limit < 1 or limit > 100:
            return jsonify({
                'success': False,
                'error': 'Invalid pagination parameters'
            }), 400
        
        # Search routes
        result = RouteService.search_routes(
            train_id=train_id,
            source_station_id=from_station,
            destination_station_id=to_station,
            page=page,
            limit=limit
        )
        
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
            'error': f'Search failed: {str(e)}'
        }), 500


# ==================== ERROR HANDLERS ====================

@routes_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Route endpoint not found'
    }), 404


@routes_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed for this endpoint'
    }), 405