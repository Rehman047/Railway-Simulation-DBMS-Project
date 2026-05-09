"""
Schedule Service Layer
Business logic for train schedule management
"""
from app.db import Database
from app.queries.schedule_queries import *
from datetime import datetime, date


class ScheduleService:
    """Service for managing schedule operations"""
    
    @staticmethod
    def get_schedule(schedule_id):
        """Get a single schedule by ID"""
        return Database.fetch_one(GET_SCHEDULE, (schedule_id,))
    
    @staticmethod
    def list_schedules(page=1, limit=20):
        """List all schedules with pagination"""
        offset = (page - 1) * limit
        schedules = Database.fetch_all(LIST_SCHEDULES, (limit, offset))
        
        # Serialize time objects to strings for JSON compatibility
        serialized_schedules = []
        for schedule in schedules:
            if isinstance(schedule, dict):
                serialized = schedule.copy()
                # Convert time objects to strings
                if 'departure_time' in serialized and serialized['departure_time'] is not None:
                    serialized['departure_time'] = str(serialized['departure_time'])
                if 'arrival_time' in serialized and serialized['arrival_time'] is not None:
                    serialized['arrival_time'] = str(serialized['arrival_time'])
                # Convert date objects to strings
                if 'departure_date' in serialized and serialized['departure_date'] is not None:
                    serialized['departure_date'] = str(serialized['departure_date'])
                # Convert available_seats to int if it's not None
                if 'available_seats' in serialized and serialized['available_seats'] is None:
                    serialized['available_seats'] = 0
                serialized_schedules.append(serialized)
            else:
                serialized_schedules.append(schedule)
        
        total = Database.fetch_scalar(COUNT_SCHEDULES)
        
        return {
            'data': serialized_schedules,
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    
    @staticmethod
    def create_schedule(train_id, route_id, departure_date, departure_time, arrival_time, schedule_status='scheduled'):
        """
        Create a new schedule with validation
        """
        try:
            # Validate inputs
            if not all([train_id, route_id, departure_date, departure_time, arrival_time]):
                return {'success': False, 'error': 'All fields are required'}
            
            # Validate train exists
            train = Database.fetch_one("SELECT train_id FROM trains WHERE train_id = %s", (train_id,))
            if not train:
                return {'success': False, 'error': 'Train not found'}
            
            # Validate route exists
            route = Database.fetch_one("SELECT route_id FROM routes WHERE route_id = %s", (route_id,))
            if not route:
                return {'success': False, 'error': 'Route not found'}
            
            # Create schedule with provided status
            schedule_id = Database.execute_returning(
                CREATE_SCHEDULE,
                (train_id, route_id, departure_date, departure_time, arrival_time, schedule_status)
            )
            
            if schedule_id:
                return {'success': True, 'schedule_id': schedule_id}
            else:
                return {'success': False, 'error': 'Failed to create schedule'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_schedule(schedule_id, departure_time=None, arrival_time=None):
        """
        Update schedule times (only if no bookings exist)
        """
        try:
            # Check if schedule has bookings
            booking_count = Database.fetch_scalar(
                "SELECT COUNT(*) FROM bookings WHERE schedule_id = %s",
                (schedule_id,)
            )
            
            if booking_count and booking_count > 0:
                return {'success': False, 'error': 'Cannot modify schedule with existing bookings'}
            
            # Update times
            if departure_time and arrival_time:
                affected = Database.execute(
                    UPDATE_SCHEDULE,
                    (departure_time, arrival_time, 'scheduled', schedule_id)
                )
                
                if affected > 0:
                    return {'success': True, 'message': 'Schedule updated'}
                else:
                    return {'success': False, 'error': 'Schedule not found'}
            
            return {'success': False, 'error': 'Departure and arrival times are required'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_schedules_for_route(route_id, from_date, to_date):
        """
        Get schedules for a route between dates with occupancy info
        """
        schedules = Database.fetch_all(
            GET_SCHEDULES_FOR_ROUTE,
            (route_id, from_date, to_date)
        )
        
        # Calculate occupancy percentage
        for schedule in schedules:
            if schedule['total_seats']:
                schedule['occupancy_percent'] = (schedule['bookings_count'] / schedule['total_seats']) * 100
                schedule['available_seats'] = schedule['total_seats'] - schedule['bookings_count']
            else:
                schedule['occupancy_percent'] = 0
                schedule['available_seats'] = 0
        
        return schedules
    
    @staticmethod
    def get_available_seats(schedule_id):
        """
        Get count of available seats for a schedule
        """
        result = Database.fetch_one(
            """SELECT
                   t.capacity
                   - COALESCE(
                       (SELECT COUNT(*)
                        FROM bookings b
                        WHERE b.schedule_id = s.schedule_id
                          AND LOWER(b.booking_status) != 'cancelled'),
                       0
                     ) AS available_seats
               FROM schedules s
               JOIN trains t ON s.train_id = t.train_id
               WHERE s.schedule_id = %s""",
            (schedule_id,)
        )
        
        return result['available_seats'] if result else 0
    
    @staticmethod
    def cancel_schedule(schedule_id, reason):
        """
        Cancel a schedule - cascades to all bookings
        Atomic transaction for data integrity
        """
        try:
            def cancel_transaction(conn):
                cursor = conn.cursor()
                
                # 1. Get all bookings for this schedule
                cursor.execute(
                    "SELECT booking_id FROM bookings WHERE schedule_id = %s AND booking_status != 'cancelled'",
                    (schedule_id,)
                )
                bookings = cursor.fetchall()
                
                # 2. Cancel all bookings
                for booking in bookings:
                    booking_id = booking[0]
                    cursor.execute(
                        "UPDATE bookings SET booking_status = 'cancelled' WHERE booking_id = %s",
                        (booking_id,)
                    )
                    
                    # Create cancellation record
                    cursor.execute(
                        """INSERT INTO cancellations 
                        (booking_id, cancellation_date, cancellation_reason, refund_status) 
                        VALUES (%s, %s, %s, 'processed')""",
                        (booking_id, datetime.now().date(), reason)
                    )
                
                # 3. Update schedule status
                cursor.execute(
                    "UPDATE schedules SET schedule_status = 'cancelled' WHERE schedule_id = %s",
                    (schedule_id,)
                )
                
                cursor.close()
                return {'success': True, 'cancelled_bookings': len(bookings), 'message': 'Schedule cancelled'}
            
            result = Database.transaction(cancel_transaction)
            return result if result else {'success': False, 'error': 'Transaction failed'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_schedule_with_details(schedule_id):
        """Get full schedule details with train and route info"""
        return Database.fetch_one(
            """SELECT s.schedule_id, s.departure_date, s.departure_time, s.arrival_time, s.schedule_status,
                      t.train_id, t.train_name, t.train_number, t.train_type, t.capacity,
                      r.route_id, r.distance, r.estimated_duration,
                      st_src.station_id as source_station_id, st_src.station_name as source_station,
                      st_dst.station_id as destination_station_id, st_dst.station_name as destination_station,
                      (SELECT COUNT(*) FROM bookings WHERE schedule_id = %s AND booking_status != 'cancelled') as booked_seats,
                      t.capacity - (SELECT COUNT(*) FROM bookings WHERE schedule_id = %s AND booking_status != 'cancelled') as available_seats
               FROM schedules s
               JOIN trains t ON s.train_id = t.train_id
               JOIN routes r ON s.route_id = r.route_id
               JOIN stations st_src ON r.source_station_id = st_src.station_id
               JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
               WHERE s.schedule_id = %s""",
            (schedule_id, schedule_id, schedule_id)
        )
