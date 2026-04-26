"""
Booking Service Layer
Business logic for passenger bookings - critical transaction handling
"""
from app.db import Database
from app.queries.booking_queries import *
from datetime import datetime


class BookingService:
    """Service for managing booking operations with transaction safety"""
    
    @staticmethod
    def get_available_seats(schedule_id):
        """Get available seats for a schedule"""
        available = Database.fetch_all(GET_AVAILABLE_SEATS, (schedule_id,))
        return available
    
    @staticmethod
    def check_seat_availability(schedule_id, seat_id):
        """Check if a specific seat is available for a schedule"""
        result = Database.fetch_one(CHECK_SEAT_BOOKED, (schedule_id, seat_id))
        return result is None  # Available if no booking found
    
    @staticmethod
    def create_booking(passenger_id, schedule_id, seat_id, fare_amount):
        """
        Create a booking - ATOMIC TRANSACTION
        Validates all conditions and creates booking in single transaction
        """
        try:
            # Validation logic wrapped in transaction
            def booking_transaction(conn):
                cursor = conn.cursor()
                
                # 1. Check passenger exists
                cursor.execute("SELECT passenger_id FROM passengers WHERE passenger_id = %s", (passenger_id,))
                if not cursor.fetchone():
                    return {'success': False, 'error': 'Passenger not found'}
                
                # 2. Check schedule exists and is active
                cursor.execute(
                    "SELECT schedule_id FROM schedules WHERE schedule_id = %s AND status = 'Active'",
                    (schedule_id,)
                )
                if not cursor.fetchone():
                    return {'success': False, 'error': 'Schedule not found or inactive'}
                
                # 3. Check seat exists
                cursor.execute("SELECT seat_id FROM seats WHERE seat_id = %s", (seat_id,))
                if not cursor.fetchone():
                    return {'success': False, 'error': 'Seat not found'}
                
                # 4. Check seat NOT already booked (CRITICAL - prevents double booking)
                cursor.execute(
                    "SELECT booking_id FROM bookings WHERE schedule_id = %s AND seat_id = %s",
                    (schedule_id, seat_id)
                )
                if cursor.fetchone():
                    cursor.close()
                    return {'success': False, 'error': 'Seat already booked'}
                
                # 5. Create booking with status 'Pending'
                cursor.execute(
                    CREATE_BOOKING,
                    (passenger_id, schedule_id, seat_id, datetime.now().date(), fare_amount, 'Pending')
                )
                booking_id = cursor.fetchone()[0]
                
                cursor.close()
                return {'success': True, 'booking_id': booking_id}
            
            result = Database.transaction(booking_transaction)
            return result if result else {'success': False, 'error': 'Transaction failed'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_booking(booking_id):
        """Get booking details"""
        return Database.fetch_one(GET_BOOKING, (booking_id,))
    
    @staticmethod
    def list_bookings(page=1, limit=20, status_filter=None):
        """List bookings with pagination and optional status filter"""
        offset = (page - 1) * limit
        
        if status_filter:
            bookings = Database.fetch_all(LIST_BOOKINGS_BY_STATUS, (status_filter, limit, offset))
        else:
            bookings = Database.fetch_all(LIST_BOOKINGS, (limit, offset))
        
        total = Database.fetch_scalar(COUNT_BOOKINGS)
        
        return {
            'data': bookings,
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    
    @staticmethod
    def cancel_booking(booking_id, reason, staff_id):
        """
        Cancel a booking - updates booking status and creates cancellation record
        """
        try:
            def cancel_transaction(conn):
                cursor = conn.cursor()
                
                # 1. Get booking details
                cursor.execute("SELECT booking_id, status FROM bookings WHERE booking_id = %s", (booking_id,))
                booking = cursor.fetchone()
                
                if not booking:
                    return {'success': False, 'error': 'Booking not found'}
                
                if booking[1] == 'Cancelled':
                    cursor.close()
                    return {'success': False, 'error': 'Booking already cancelled'}
                
                # 2. Update booking status to Cancelled
                cursor.execute(
                    "UPDATE bookings SET status = 'Cancelled' WHERE booking_id = %s",
                    (booking_id,)
                )
                
                # 3. Create cancellation record
                cursor.execute(
                    "INSERT INTO cancellations (booking_id, cancelled_by_staff_id, cancellation_date, reason, status) VALUES (%s, %s, %s, %s, %s) RETURNING cancellation_id",
                    (booking_id, staff_id, datetime.now().date(), reason, 'Processed')
                )
                cancellation_id = cursor.fetchone()[0]
                
                cursor.close()
                return {'success': True, 'cancellation_id': cancellation_id, 'message': 'Booking cancelled'}
            
            result = Database.transaction(cancel_transaction)
            return result if result else {'success': False, 'error': 'Transaction failed'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_booking_with_details(booking_id):
        """Get full booking details with passenger, schedule, and seat info"""
        return Database.fetch_one(GET_BOOKING_DETAILS, (booking_id,))
