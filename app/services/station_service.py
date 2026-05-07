"""
Station Service Layer
Business logic for station operations
"""
from app.db import Database
from app.queries.station_queries import (
    GET_STATION, LIST_STATIONS, COUNT_STATIONS, CREATE_STATION, UPDATE_STATION,
    DELETE_STATION, GET_STATION_BY_NAME, GET_STATIONS_BY_CITY, 
    GET_ROUTES_FROM_STATION, GET_ROUTES_TO_STATION, GET_STATION_SERVICES
)


class StationService:
    """Service class for station operations"""

    @staticmethod
    def list_stations(page=1, limit=20):
        """List all stations with pagination"""
        offset = (page - 1) * limit
        stations = Database.fetch_all(LIST_STATIONS, (limit, offset))
        total = Database.fetch_scalar(COUNT_STATIONS)
        
        return {
            'data': stations,
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit if total else 0
        }

    @staticmethod
    def get_station(station_id):
        """Get station by ID"""
        return Database.fetch_one(GET_STATION, (station_id,))

    @staticmethod
    def get_station_by_name(station_name):
        """Get station by name"""
        return Database.fetch_one(GET_STATION_BY_NAME, (station_name,))

    @staticmethod
    def get_stations_by_city(city):
        """Get all stations in a city"""
        return Database.fetch_all(GET_STATIONS_BY_CITY, (city,))

    @staticmethod
    def create_station(data):
        """Create a new station"""
        required = ['station_name', 'city', 'state', 'address', 'contact_number']
        for field in required:
            if not data.get(field):
                return {'success': False, 'error': f'Missing required field: {field}'}
        
        existing = StationService.get_station_by_name(data['station_name'])
        if existing:
            return {'success': False, 'error': 'Station with this name already exists'}
        
        try:
            station_id = Database.execute_returning(
                CREATE_STATION,
                (data['station_name'], data['city'], data['state'], 
                 data['address'], data['contact_number'])
            )
            return {
                'success': True,
                'message': 'Station created successfully',
                'station_id': station_id
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def update_station(station_id, data):
        """Update station information"""
        station = StationService.get_station(station_id)
        if not station:
            return {'success': False, 'error': 'Station not found'}
        
        station_name = data.get('station_name', station['station_name'])
        city = data.get('city', station['city'])
        state = data.get('state', station['state'])
        address = data.get('address', station['address'])
        contact_number = data.get('contact_number', station['contact_number'])
        
        try:
            Database.execute(
                UPDATE_STATION,
                (station_name, city, state, address, contact_number, station_id)
            )
            return {
                'success': True,
                'message': 'Station updated successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def delete_station(station_id):
        """Delete a station"""
        station = StationService.get_station(station_id)
        if not station:
            return {'success': False, 'error': 'Station not found'}
        
        try:
            Database.execute(DELETE_STATION, (station_id,))
            return {
                'success': True,
                'message': 'Station deleted successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_routes_from_station(station_id):
        """Get all routes starting from this station"""
        return Database.fetch_all(GET_ROUTES_FROM_STATION, (station_id,))

    @staticmethod
    def get_routes_to_station(station_id):
        """Get all routes ending at this station"""
        return Database.fetch_all(GET_ROUTES_TO_STATION, (station_id,))

    @staticmethod
    def get_station_services(station_id):
        """Get all services available at this station"""
        return Database.fetch_all(GET_STATION_SERVICES, (station_id,))

    @staticmethod
    def search_stations(keyword):
        """Search stations by name or city"""
        query = """
            SELECT station_id, station_name, city, state, address, contact_number, created_at
            FROM stations
            WHERE LOWER(station_name) LIKE LOWER(%s) OR LOWER(city) LIKE LOWER(%s)
            ORDER BY station_name
        """
        search_term = f"%{keyword}%"
        return Database.fetch_all(query, (search_term, search_term))
