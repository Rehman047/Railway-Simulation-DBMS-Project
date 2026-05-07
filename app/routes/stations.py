"""Stations API Routes"""
from flask import Blueprint, jsonify, request

from app.db import Database
from app.queries.station_queries import (
    GET_STATION, LIST_STATIONS, COUNT_STATIONS,
    CREATE_STATION, GET_STATION_SERVICES,
)

stations_bp = Blueprint('stations', __name__, url_prefix='/api/stations')


# ── List & Get ────────────────────────────────────────────────

@stations_bp.route('', methods=['GET'])
def list_stations():
    """List all stations with pagination. Optional filter: ?city=Lahore"""
    page  = request.args.get('page',  1,  type=int)
    limit = request.args.get('limit', 20, type=int)
    city  = request.args.get('city',  type=str)
    offset = (page - 1) * limit

    conditions, params = [], []
    if city:
        conditions.append("LOWER(city) = LOWER(%s)")
        params.append(city)

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

    stations = Database.fetch_all(
        f"""SELECT station_id, station_name, city, state, address, contact_number, created_at
            FROM stations {where}
            ORDER BY station_name
            LIMIT %s OFFSET %s""",
        params + [limit, offset]
    )
    total = Database.fetch_scalar(f"SELECT COUNT(*) FROM stations {where}", params)

    return jsonify({
        'success': True,
        'data': stations,
        'meta': {'page': page, 'limit': limit, 'total': total,
                 'pages': (total + limit - 1) // limit if total else 0},
    }), 200


@stations_bp.route('/<int:station_id>', methods=['GET'])
def get_station(station_id: int):
    """Get a station by ID."""
    station = Database.fetch_one(GET_STATION, (station_id,))
    if not station:
        return jsonify({'success': False, 'error': 'Station not found'}), 404
    return jsonify({'success': True, 'data': station}), 200


# ── Create ────────────────────────────────────────────────────

@stations_bp.route('', methods=['POST'])
def create_station():
    """
    Create a new station.
    Required JSON: station_name, city, state.
    Optional: address, contact_number.
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    for field in ['station_name', 'city', 'state']:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

    # Check for duplicate name in same city
    existing = Database.fetch_one(
        "SELECT station_id FROM stations WHERE LOWER(station_name) = LOWER(%s) AND LOWER(city) = LOWER(%s)",
        (data['station_name'], data['city'])
    )
    if existing:
        return jsonify({'success': False, 'error': 'Station already exists in this city'}), 400

    station_id = Database.execute_returning(
        CREATE_STATION,
        (data['station_name'], data['city'], data['state'],
         data.get('address'), data.get('contact_number'))
    )

    if station_id:
        return jsonify({'success': True, 'station_id': station_id}), 201
    return jsonify({'success': False, 'error': 'Failed to create station'}), 500


# ── Sub-resources ─────────────────────────────────────────────

@stations_bp.route('/<int:station_id>/services', methods=['GET'])
def get_station_services(station_id: int):
    """Get all services available at a station."""
    station = Database.fetch_one("SELECT station_id FROM stations WHERE station_id = %s", (station_id,))
    if not station:
        return jsonify({'success': False, 'error': 'Station not found'}), 404

    services = Database.fetch_all(GET_STATION_SERVICES, (station_id,))
    return jsonify({'success': True, 'data': services, 'count': len(services)}), 200


@stations_bp.route('/<int:station_id>', methods=['PUT'])
def update_station(station_id: int):
    """Update station information."""
    station = Database.fetch_one(GET_STATION, (station_id,))
    if not station:
        return jsonify({'success': False, 'error': 'Station not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    station_name = data.get('station_name', station['station_name'])
    city = data.get('city', station['city'])
    state = data.get('state', station['state'])
    address = data.get('address', station['address'])
    contact_number = data.get('contact_number', station['contact_number'])

    try:
        Database.execute(
            "UPDATE stations SET station_name = %s, city = %s, state = %s, address = %s, contact_number = %s WHERE station_id = %s",
            (station_name, city, state, address, contact_number, station_id)
        )
        return jsonify({'success': True, 'message': 'Station updated successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stations_bp.route('/<int:station_id>', methods=['DELETE'])
def delete_station(station_id: int):
    """Delete a station."""
    station = Database.fetch_one(GET_STATION, (station_id,))
    if not station:
        return jsonify({'success': False, 'error': 'Station not found'}), 404

    try:
        Database.execute("DELETE FROM stations WHERE station_id = %s", (station_id,))
        return jsonify({'success': True, 'message': 'Station deleted successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stations_bp.route('/routes/between/<int:source_id>/<int:dest_id>', methods=['GET'])
def routes_between(source_id: int, dest_id: int):
    """
    Find all available trains between two stations using the
    available_trains_by_route() SQL function.
    """
    if source_id == dest_id:
        return jsonify({'success': False, 'error': 'Source and destination must be different'}), 400

    # Verify both stations exist
    src = Database.fetch_one("SELECT station_id FROM stations WHERE station_id = %s", (source_id,))
    dst = Database.fetch_one("SELECT station_id FROM stations WHERE station_id = %s", (dest_id,))
    if not src or not dst:
        return jsonify({'success': False, 'error': 'One or both stations not found'}), 404

    trains = Database.fetch_all(
        "SELECT * FROM available_trains_by_route(%s, %s)",
        (source_id, dest_id)
    )
    return jsonify({
        'success': True,
        'data': trains,
        'count': len(trains),
        'source_station_id': source_id,
        'destination_station_id': dest_id,
    }), 200


@stations_bp.route('/search', methods=['GET'])
def search_stations():
    """Search stations by name or city."""
    keyword = request.args.get('q', type=str)
    
    if not keyword or len(keyword) < 2:
        return jsonify({'success': False, 'error': 'Search keyword must be at least 2 characters'}), 400
    
    stations = Database.fetch_all(
        "SELECT station_id, station_name, city, state, address, contact_number FROM stations WHERE LOWER(station_name) LIKE LOWER(%s) OR LOWER(city) LIKE LOWER(%s) ORDER BY station_name",
        (f"%{keyword}%", f"%{keyword}%")
    )
    return jsonify({'success': True, 'data': stations, 'count': len(stations)}), 200
