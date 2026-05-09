"""
Payment Service Layer
Business logic for payment processing and refund management
"""
from app.db import Database
from app.queries.payment_queries import *
from datetime import datetime


class PaymentService:
    """Service for managing payment operations"""
    
    @staticmethod
    def get_payment(payment_id):
        """Get a single payment by ID"""
        return Database.fetch_one(GET_PAYMENT, (payment_id,))
    
    @staticmethod
    def list_payments(page=1, limit=20):
        """List all payments with pagination"""
        offset = (page - 1) * limit
        payments = Database.fetch_all(LIST_PAYMENTS, (limit, offset))
        
        # Serialize time/date objects to strings for JSON compatibility
        serialized_payments = []
        for payment in payments:
            if isinstance(payment, dict):
                serialized = payment.copy()
                # Convert datetime/time objects to strings
                for dt_field in ['payment_date', 'created_at']:
                    if dt_field in serialized and serialized[dt_field] is not None:
                        serialized[dt_field] = str(serialized[dt_field])
                serialized_payments.append(serialized)
            else:
                serialized_payments.append(payment)
        
        total = Database.fetch_scalar(COUNT_PAYMENTS)
        
        return {
            'data': serialized_payments,
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    
    @staticmethod
    def record_payment(booking_id, amount, method):
        """
        Record a payment for a booking — ATOMIC TRANSACTION.
        Both the payment INSERT and the booking status UPDATE
        succeed together or are rolled back together.
        """
        # Pre-transaction validation (read-only, no locks needed)
        booking = Database.fetch_one(
            "SELECT booking_id, fare_amount FROM bookings WHERE booking_id = %s",
            (booking_id,)
        )
        if not booking:
            return {'success': False, 'error': 'Booking not found'}

        if amount < booking['fare_amount']:
            return {'success': False, 'error': f"Amount must be at least {booking['fare_amount']}"}

        valid_methods = ['Cash', 'Card', 'Online', 'Cheque']
        if method not in valid_methods:
            return {'success': False, 'error': f'Invalid payment method. Must be one of: {", ".join(valid_methods)}'}

        # Atomic: insert payment + update booking status
        def payment_transaction(conn):
            cursor = conn.cursor()
            cursor.execute(
                CREATE_PAYMENT,
                (booking_id, amount, method, datetime.now().date(), 'Completed')
            )
            result = cursor.fetchone()
            payment_id = result[0] if result else None

            if not payment_id:
                cursor.close()
                return {'success': False, 'error': 'Failed to record payment'}

            cursor.execute(
                "UPDATE bookings SET booking_status = 'Confirmed' WHERE booking_id = %s",
                (booking_id,)
            )
            cursor.close()
            return {'success': True, 'payment_id': payment_id, 'message': 'Payment recorded'}

        try:
            result = Database.transaction(payment_transaction)
            return result if result else {'success': False, 'error': 'Transaction failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_payment_status(payment_id, status):
        """Update payment status after verification"""
        try:
            valid_statuses = ['Completed', 'Pending', 'Failed', 'Refunded']
            
            if status not in valid_statuses:
                return {'success': False, 'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}
            
            affected = Database.execute(
                UPDATE_PAYMENT_STATUS,
                (status, datetime.now().date(), payment_id)
            )
            
            if affected > 0:
                return {'success': True, 'message': 'Payment status updated'}
            else:
                return {'success': False, 'error': 'Payment not found'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_booking_payments(booking_id):
        """Get all payments for a booking"""
        payments = Database.fetch_all(
            GET_BOOKING_PAYMENTS,
            (booking_id,)
        )
        return payments
    
    @staticmethod
    def get_pending_payments():
        """Get all pending payments"""
        payments = Database.fetch_all(GET_PENDING_PAYMENTS)
        return payments
    
    @staticmethod
    def process_refund(cancellation_id, refund_amount):
        """
        Process refund for a cancelled booking
        Create refund payment record
        """
        try:
            # Get cancellation details
            cancellation = Database.fetch_one(
                "SELECT booking_id FROM cancellations WHERE cancellation_id = %s",
                (cancellation_id,)
            )
            
            if not cancellation:
                return {'success': False, 'error': 'Cancellation not found'}
            
            booking_id = cancellation['booking_id']
            
            # Check if refund already processed
            existing_refund = Database.fetch_one(
                """SELECT payment_id FROM payments 
                   WHERE booking_id = %s AND payment_method LIKE '%refund%' """,
                (booking_id,)
            )
            
            if existing_refund:
                return {'success': False, 'error': 'Refund already processed for this booking'}
            
            # Create refund payment record
            payment_id = Database.execute_returning(
                CREATE_PAYMENT,
                (booking_id, -refund_amount, 'Refund', datetime.now().date(), 'Completed')
            )
            
            if payment_id:
                # Update cancellation status
                Database.execute(
                    "UPDATE cancellations SET status = 'Refunded' WHERE cancellation_id = %s",
                    (cancellation_id,)
                )
                
                return {'success': True, 'payment_id': payment_id, 'refund_amount': refund_amount}
            else:
                return {'success': False, 'error': 'Failed to process refund'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_revenue_summary(from_date, to_date):
        """Get revenue summary for a date range"""
        summary = Database.fetch_one(
            """SELECT 
                COUNT(*) as total_payments,
                SUM(payment_amount) as total_revenue,
                AVG(payment_amount) as avg_payment,
                MIN(payment_amount) as min_payment,
                MAX(payment_amount) as max_payment
               FROM payments
               WHERE payment_date BETWEEN %s AND %s
               AND status = 'Completed'""",
            (from_date, to_date)
        )
        
        return summary if summary else {
            'total_payments': 0,
            'total_revenue': 0,
            'avg_payment': 0,
            'min_payment': 0,
            'max_payment': 0
        }
    
    @staticmethod
    def get_payments_by_method(from_date, to_date):
        """Get payment breakdown by method"""
        payments = Database.fetch_all(
            """SELECT payment_method, COUNT(*) as count, SUM(payment_amount) as total
               FROM payments
               WHERE payment_date BETWEEN %s AND %s
               AND status = 'Completed'
               GROUP BY payment_method
               ORDER BY total DESC""",
            (from_date, to_date)
        )
        
        return payments
