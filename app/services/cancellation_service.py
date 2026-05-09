"""
Cancellation Service Layer
Business logic for booking cancellations and refund processing
"""
from app.db import Database
from app.queries.cancellation_queries import *
from datetime import datetime, timedelta


class CancellationService:
    """Service for managing cancellations and refunds"""
    
    # Refund policy: based on hours until departure
    REFUND_POLICY = {
        'full_refund_hours': 24,      # Full refund if cancelled > 24 hours before
        'partial_refund_hours': 12,   # Partial (50%) if cancelled 12-24 hours before
        'no_refund_hours': 0           # No refund if cancelled < 12 hours before
    }
    
    @staticmethod
    def get_cancellation(cancellation_id):
        """Get a single cancellation by ID"""
        return Database.fetch_one(GET_CANCELLATION, (cancellation_id,))
    
    @staticmethod
    def list_cancellations(page=1, limit=20):
        """List all cancellations with pagination"""
        offset = (page - 1) * limit
        cancellations = Database.fetch_all(LIST_CANCELLATIONS, (limit, offset))
        
        # Serialize time/date objects to strings for JSON compatibility
        serialized_cancellations = []
        for cancellation in cancellations:
            if isinstance(cancellation, dict):
                serialized = cancellation.copy()
                # Convert datetime/time objects to strings
                for dt_field in ['cancellation_date', 'created_at']:
                    if dt_field in serialized and serialized[dt_field] is not None:
                        serialized[dt_field] = str(serialized[dt_field])
                serialized_cancellations.append(serialized)
            else:
                serialized_cancellations.append(cancellation)
        
        total = Database.fetch_scalar(COUNT_CANCELLATIONS)
        
        return {
            'data': serialized_cancellations,
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    
    @staticmethod
    def calculate_refund_amount(fare_amount, departure_datetime):
        """
        Calculate refund amount based on cancellation policy
        Returns (refund_amount, refund_percentage, reason)
        """
        now = datetime.now()
        hours_until_departure = (departure_datetime - now).total_seconds() / 3600
        
        policy = CancellationService.REFUND_POLICY
        
        if hours_until_departure > policy['full_refund_hours']:
            return (fare_amount, 100, 'Full refund - cancelled >24 hours before departure')
        elif hours_until_departure > policy['partial_refund_hours']:
            partial = fare_amount * 0.5  # 50% refund
            return (partial, 50, 'Partial refund (50%) - cancelled 12-24 hours before departure')
        else:
            return (0, 0, 'No refund - cancelled <12 hours before departure')
    
    @staticmethod
    def create_cancellation(booking_id, reason, staff_id=None):
        """
        Create a cancellation record and calculate refund
        Returns cancellation_id and refund details
        """
        try:
            # Get booking details
            booking = Database.fetch_one(
                """SELECT b.booking_id, b.fare_amount, b.booking_status, s.departure_date, s.departure_time
                   FROM bookings b
                   JOIN schedules s ON b.schedule_id = s.schedule_id
                   WHERE b.booking_id = %s""",
                (booking_id,)
            )
            
            if not booking:
                return {'success': False, 'error': 'Booking not found'}
            
            if booking['booking_status'] == 'Cancelled':
                return {'success': False, 'error': 'Booking is already cancelled'}
            
            # Calculate refund
            departure_datetime = datetime.combine(booking['departure_date'], booking['departure_time'])
            refund_amount, refund_percent, refund_reason = CancellationService.calculate_refund_amount(
                booking['fare_amount'],
                departure_datetime
            )
            
            # Create cancellation record in transaction
            def cancellation_transaction(conn):
                cursor = conn.cursor()

                # 1. Create cancellation record
                cursor.execute(
                    CREATE_CANCELLATION,
                    (booking_id, staff_id, datetime.now().date(), reason, 'Processed')
                )
                result = cursor.fetchone()
                cancellation_id = result[0] if result else None

                # 2. Update booking status
                cursor.execute(
                    "UPDATE bookings SET booking_status = 'Cancelled' WHERE booking_id = %s",
                    (booking_id,)
                )

                # 3. Release seat — fetch seat_id from booking then mark available
                cursor.execute(
                    "SELECT seat_id FROM bookings WHERE booking_id = %s",
                    (booking_id,)
                )
                seat_row = cursor.fetchone()
                if seat_row and seat_row[0]:
                    cursor.execute(
                        "UPDATE seats SET availability = 'available' WHERE seat_id = %s",
                        (seat_row[0],)
                    )

                # 4. Create refund payment if applicable
                if refund_amount > 0:
                    cursor.execute(
                        """INSERT INTO payments
                        (booking_id, payment_amount, payment_method, payment_date, payment_status)
                        VALUES (%s, %s, 'Refund', %s, 'Completed')
                        RETURNING payment_id""",
                        (booking_id, refund_amount, datetime.now().date())
                    )

                cursor.close()
                return {
                    'success': True,
                    'cancellation_id': cancellation_id,
                    'refund_amount': refund_amount,
                    'refund_percent': refund_percent,
                    'refund_reason': refund_reason
                }
            
            result = Database.transaction(cancellation_transaction)
            return result if result else {'success': False, 'error': 'Transaction failed'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_staff_cancellations(staff_id, from_date=None, to_date=None):
        """Get cancellations processed by a staff member"""
        if from_date and to_date:
            cancellations = Database.fetch_all(
                GET_STAFF_CANCELLATIONS_BY_DATE,
                (staff_id, from_date, to_date)
            )
        else:
            cancellations = Database.fetch_all(
                GET_STAFF_CANCELLATIONS,
                (staff_id,)
            )
        
        return cancellations
    
    @staticmethod
    def get_cancellation_stats(from_date, to_date):
        """Get cancellation statistics for a date range"""
        stats = Database.fetch_one(
            """SELECT 
                COUNT(*) as total_cancellations,
                COUNT(CASE WHEN status = 'Refunded' THEN 1 END) as refunded_count,
                COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending_count,
                SUM(CASE WHEN status = 'Refunded' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) * 100 as refund_rate
               FROM cancellations
               WHERE cancellation_date BETWEEN %s AND %s""",
            (from_date, to_date)
        )
        
        return stats
    
    @staticmethod
    def get_cancellation_reasons(from_date, to_date):
        """Get breakdown of cancellation reasons"""
        reasons = Database.fetch_all(
            """SELECT reason, COUNT(*) as count
               FROM cancellations
               WHERE cancellation_date BETWEEN %s AND %s
               GROUP BY reason
               ORDER BY count DESC""",
            (from_date, to_date)
        )
        
        return reasons
    
    @staticmethod
    def update_cancellation_status(cancellation_id, status):
        """Update cancellation status"""
        try:
            valid_statuses = ['Pending', 'Processed', 'Refunded']
            
            if status not in valid_statuses:
                return {'success': False, 'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}
            
            affected = Database.execute(
                UPDATE_CANCELLATION_STATUS,
                (status, cancellation_id)
            )
            
            if affected > 0:
                return {'success': True, 'message': 'Cancellation status updated'}
            else:
                return {'success': False, 'error': 'Cancellation not found'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
