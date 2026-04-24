"""
Passenger Service Layer
Business logic for passenger operations
Uses direct database queries via app.db module
"""
from app.db import Database
from app.queries.passenger_queries import *


class PassengerService:
    """Service for managing passenger operations"""
    
    @staticmethod
    def get_passenger(passenger_id):
        """Get a single passenger by ID"""
        return Database.fetch_one(GET_PASSENGER, (passenger_id,))
    
    @staticmethod
    def list_passengers(page=1, limit=20):
        """List all passengers with pagination"""
        offset = (page - 1) * limit
        passengers = Database.fetch_all(LIST_PASSENGERS, (limit, offset))
        
        # Get total count
        total = Database.fetch_scalar(COUNT_PASSENGERS)
        
        return {
            'data': passengers,
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    
    @staticmethod
    def create_passenger(data):
        """Create a new passenger"""
        required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth']
        
        # Validate required fields
        for field in required_fields:
            if field not in data or not data[field]:
                return {'success': False, 'error': f'Missing required field: {field}'}
        
        try:
            passenger_id = Database.execute_returning(
                CREATE_PASSENGER,
                (
                    data['first_name'],
                    data['last_name'],
                    data['email'],
                    data['phone_number'],
                    data['date_of_birth'],
                    data.get('id_proof_type'),
                    data.get('id_proof_number')
                )
            )
            
            if passenger_id:
                return {'success': True, 'passenger_id': passenger_id}
            else:
                return {'success': False, 'error': 'Failed to create passenger'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_passenger(passenger_id, data):
        """Update passenger information"""
        # Only allow updating email and phone
        if 'email' in data and 'phone_number' in data:
            affected = Database.execute(
                UPDATE_PASSENGER,
                (data['email'], data['phone_number'], passenger_id)
            )
            
            if affected > 0:
                return {'success': True, 'message': 'Passenger updated'}
            else:
                return {'success': False, 'error': 'Passenger not found'}
        
        return {'success': False, 'error': 'Only email and phone_number can be updated'}
    
    @staticmethod
    def delete_passenger(passenger_id):
        """Delete a passenger (only if no bookings)"""
        # Check if passenger has bookings
        booking_count = Database.fetch_scalar(COUNT_PASSENGER_BOOKINGS, (passenger_id,))
        
        if booking_count and booking_count > 0:
            return {'success': False, 'error': 'Cannot delete passenger with existing bookings'}
        
        affected = Database.execute(DELETE_PASSENGER, (passenger_id,))
        
        if affected > 0:
            return {'success': True, 'message': 'Passenger deleted'}
        else:
            return {'success': False, 'error': 'Passenger not found'}
    
    @staticmethod
    def get_passenger_bookings(passenger_id):
        """Get all bookings for a passenger"""
        bookings = Database.fetch_all(
            GET_PASSENGER_BOOKINGS,
            (passenger_id,)
        )
        return bookings
