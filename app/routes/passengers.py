"""
Passenger API Routes
REST endpoints for passenger management
"""
from flask import Blueprint, request, jsonify
from app.services.passenger_service import PassengerService

# Create blueprint for passenger routes
passengers_bp = Blueprint('passengers', __name__, url_prefix='/api/passengers')


@passengers_bp.route('', methods=['GET'])
def list_passengers():
    """List all passengers with pagination"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    result = PassengerService.list_passengers(page, limit)
    
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


@passengers_bp.route('/<int:passenger_id>', methods=['GET'])
def get_passenger(passenger_id):
    """Get a specific passenger by ID"""
    passenger = PassengerService.get_passenger(passenger_id)
    
    if passenger:
        return jsonify({
            'success': True,
            'data': passenger
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Passenger not found'
        }), 404


@passengers_bp.route('', methods=['POST'])
def create_passenger():
    """Create a new passenger"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Request body is required'
        }), 400
    
    result = PassengerService.create_passenger(data)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@passengers_bp.route('/<int:passenger_id>', methods=['PUT'])
def update_passenger(passenger_id):
    """Update passenger information"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Request body is required'
        }), 400
    
    result = PassengerService.update_passenger(passenger_id, data)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@passengers_bp.route('/<int:passenger_id>', methods=['DELETE'])
def delete_passenger(passenger_id):
    """Delete a passenger"""
    result = PassengerService.delete_passenger(passenger_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@passengers_bp.route('/<int:passenger_id>/bookings', methods=['GET'])
def get_passenger_bookings(passenger_id):
    """Get booking history for a passenger"""
    bookings = PassengerService.get_passenger_bookings(passenger_id)
    
    return jsonify({
        'success': True,
        'data': bookings,
        'count': len(bookings)
    }), 200
