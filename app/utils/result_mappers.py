"""
Result Mappers
Maps database results to API response formats
"""
from datetime import datetime, date


class ResultMapper:
    """Maps database query results to API-friendly formats"""
    
    @staticmethod
    def map_passenger(row):
        """Map passenger row to API response"""
        if not row:
            return None
        return {
            'passenger_id': row.get('passenger_id'),
            'first_name': row.get('first_name'),
            'last_name': row.get('last_name'),
            'email': row.get('email'),
            'phone_number': row.get('phone_number'),
            'date_of_birth': str(row.get('date_of_birth')) if row.get('date_of_birth') else None,
            'id_proof_type': row.get('id_proof_type'),
            'id_proof_number': row.get('id_proof_number'),
            'profile_image': row.get('profile_image'),
            'created_at': row.get('created_at').isoformat() if row.get('created_at') else None
        }
    
    @staticmethod
    def map_booking(row):
        """Map booking row to API response"""
        if not row:
            return None
        return {
            'booking_id': row.get('booking_id'),
            'passenger_id': row.get('passenger_id'),
            'schedule_id': row.get('schedule_id'),
            'seat_id': row.get('seat_id'),
            'booking_date': row.get('booking_date').isoformat() if row.get('booking_date') else None,
            'fare_amount': float(row.get('fare_amount')) if row.get('fare_amount') else 0,
            'booking_status': row.get('booking_status')
        }
    
    @staticmethod
    def map_train(row):
        """Map train row to API response"""
        if not row:
            return None
        return {
            'train_id': row.get('train_id'),
            'train_name': row.get('train_name'),
            'train_number': row.get('train_number'),
            'train_type': row.get('train_type'),
            'capacity': row.get('capacity'),
            'total_coaches': row.get('total_coaches'),
            'status': row.get('status'),
            'photo': row.get('photo'),
            'created_at': row.get('created_at').isoformat() if row.get('created_at') else None
        }
    
    @staticmethod
    def map_schedule(row):
        """Map schedule row to API response"""
        if not row:
            return None
        return {
            'schedule_id': row.get('schedule_id'),
            'train_id': row.get('train_id'),
            'route_id': row.get('route_id'),
            'departure_date': str(row.get('departure_date')) if row.get('departure_date') else None,
            'departure_time': str(row.get('departure_time')) if row.get('departure_time') else None,
            'arrival_time': str(row.get('arrival_time')) if row.get('arrival_time') else None,
            'schedule_status': row.get('schedule_status')
        }
    
    @staticmethod
    def map_payment(row):
        """Map payment row to API response"""
        if not row:
            return None
        return {
            'payment_id': row.get('payment_id'),
            'booking_id': row.get('booking_id'),
            'payment_amount': float(row.get('payment_amount')) if row.get('payment_amount') else 0,
            'payment_method': row.get('payment_method'),
            'payment_date': row.get('payment_date').isoformat() if row.get('payment_date') else None,
            'transaction_id': row.get('transaction_id'),
            'payment_status': row.get('payment_status')
        }
    
    @staticmethod
    def map_station(row):
        """Map station row to API response"""
        if not row:
            return None
        return {
            'station_id': row.get('station_id'),
            'station_name': row.get('station_name'),
            'city': row.get('city'),
            'state': row.get('state'),
            'address': row.get('address'),
            'contact_number': row.get('contact_number'),
            'photo': row.get('photo'),
            'created_at': row.get('created_at').isoformat() if row.get('created_at') else None
        }
    
    @staticmethod
    def format_timestamp(timestamp):
        """Format timestamp to ISO format"""
        if isinstance(timestamp, (datetime, date)):
            return timestamp.isoformat()
        return str(timestamp) if timestamp else None
    
    @staticmethod
    def format_numeric(value):
        """Format numeric value to float"""
        if value is None:
            return 0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0
