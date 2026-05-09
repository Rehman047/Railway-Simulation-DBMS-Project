"""
Train Service Layer
Business logic for train operations
"""
from app.db import Database
from app.queries.train_queries import *


class TrainService:
    """Service for managing train operations"""
    
    @staticmethod
    def get_train(train_id):
        """Get a single train by ID"""
        return Database.fetch_one(GET_TRAIN, (train_id,))
    
    @staticmethod
    def list_trains(page=1, limit=20):
        """List all trains with pagination"""
        offset = (page - 1) * limit
        trains = Database.fetch_all(LIST_TRAINS, (limit, offset))
        total = Database.fetch_scalar(COUNT_TRAINS)
        
        return {
            'data': trains,
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    
    @staticmethod
    def create_train(data):
        """Create a new train"""
        required_fields = ['train_name', 'train_number', 'train_type', 'capacity', 'total_coaches']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return {'success': False, 'error': f'Missing required field: {field}'}
        
        try:
            train_id = Database.execute_returning(
                CREATE_TRAIN,
                (
                    data['train_name'],
                    data['train_number'],
                    data['train_type'],
                    data['capacity'],
                    data['total_coaches'],
                    data.get('status', 'active')
                )
            )
            
            if train_id:
                return {'success': True, 'train_id': train_id}
            else:
                return {'success': False, 'error': 'Failed to create train'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_train(train_id, data):
        """Update train information"""
        if 'train_name' not in data or 'train_type' not in data or 'capacity' not in data:
            return {'success': False, 'error': 'Missing required fields'}
        
        affected = Database.execute(
            UPDATE_TRAIN,
            (
                data['train_name'],
                data['train_type'],
                data['capacity'],
                data.get('total_coaches'),
                data.get('status', 'active'),
                train_id
            )
        )
        
        if affected > 0:
            return {'success': True, 'message': 'Train updated'}
        else:
            return {'success': False, 'error': 'Train not found'}
    
    @staticmethod
    def delete_train(train_id):
        """Delete a train (only if no schedules)"""
        schedule_count = Database.fetch_scalar(
            "SELECT COUNT(*) FROM schedules WHERE train_id = %s",
            (train_id,)
        )
        
        if schedule_count and schedule_count > 0:
            return {'success': False, 'error': 'Cannot delete train with existing schedules'}
        
        affected = Database.execute(DELETE_TRAIN, (train_id,))
        
        if affected > 0:
            return {'success': True, 'message': 'Train deleted'}
        else:
            return {'success': False, 'error': 'Train not found'}
    
    @staticmethod
    def get_coaches(train_id):
        """Get all coaches for a train"""
        return Database.fetch_all(GET_TRAIN_WITH_COACHES, (train_id,))
    
    @staticmethod
    def get_amenities(train_id):
        """Get all amenities for a train"""
        return Database.fetch_all(GET_TRAIN_AMENITIES, (train_id,))
    
    @staticmethod
    def get_schedules(train_id):
        """Get upcoming schedules for a train"""
        return Database.fetch_all(GET_TRAIN_SCHEDULES, (train_id,))
    
    @staticmethod
    def get_occupancy(train_id, date):
        """Get occupancy information for a train on a specific date"""
        return Database.fetch_all(GET_TRAIN_WITH_OCCUPANCY, (train_id, date))
