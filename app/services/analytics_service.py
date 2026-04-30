"""
Analytics Service Layer
Business logic for reporting and data analytics
"""
from app.db import Database
from app.queries.analytics_queries import *


class AnalyticsService:
    """Service for analytics and reporting operations"""
    
    @staticmethod
    def get_revenue_by_train(from_date, to_date):
        """Get revenue breakdown by train"""
        data = Database.fetch_all(
            """SELECT t.train_id, t.train_name, t.train_number,
                      COUNT(DISTINCT b.booking_id) as total_bookings,
                      SUM(p.payment_amount) as revenue,
                      AVG(p.payment_amount) as avg_payment
               FROM trains t
               LEFT JOIN schedules s ON t.train_id = s.train_id
               LEFT JOIN bookings b ON s.schedule_id = b.schedule_id
               LEFT JOIN payments p ON b.booking_id = p.booking_id
               WHERE p.payment_date BETWEEN %s AND %s
               AND p.status = 'Completed'
               GROUP BY t.train_id, t.train_name, t.train_number
               ORDER BY revenue DESC""",
            (from_date, to_date)
        )
        
        return data
    
    @staticmethod
    def get_revenue_by_route(from_date, to_date):
        """Get revenue breakdown by route"""
        data = Database.fetch_all(
            """SELECT r.route_id, 
                      st_src.station_name as source, st_dst.station_name as destination,
                      COUNT(DISTINCT b.booking_id) as total_bookings,
                      SUM(p.payment_amount) as revenue,
                      AVG(p.payment_amount) as avg_fare
               FROM routes r
               JOIN stations st_src ON r.source_station_id = st_src.station_id
               JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
               LEFT JOIN schedules s ON r.route_id = s.route_id
               LEFT JOIN bookings b ON s.schedule_id = b.schedule_id
               LEFT JOIN payments p ON b.booking_id = p.booking_id
               WHERE p.payment_date BETWEEN %s AND %s
               AND p.status = 'Completed'
               GROUP BY r.route_id, st_src.station_name, st_dst.station_name
               ORDER BY revenue DESC""",
            (from_date, to_date)
        )
        
        return data
    
    @staticmethod
    def get_occupancy_rate(from_date=None, to_date=None, train_id=None):
        """Get average occupancy rate"""
        if train_id and from_date and to_date:
            data = Database.fetch_all(
                """SELECT s.schedule_id, s.departure_date,
                          COUNT(b.booking_id) as booked_seats,
                          t.total_capacity as total_seats,
                          ROUND(COUNT(b.booking_id) * 100.0 / t.total_capacity, 2) as occupancy_percent
                   FROM schedules s
                   JOIN trains t ON s.train_id = t.train_id
                   LEFT JOIN bookings b ON s.schedule_id = b.schedule_id AND b.booking_status != 'Cancelled'
                   WHERE t.train_id = %s
                   AND s.departure_date BETWEEN %s AND %s
                   GROUP BY s.schedule_id, s.departure_date, t.total_capacity
                   ORDER BY s.departure_date DESC""",
                (train_id, from_date, to_date)
            )
        else:
            data = Database.fetch_all(
                """SELECT s.schedule_id, s.departure_date,
                          COUNT(b.booking_id) as booked_seats,
                          t.total_capacity as total_seats,
                          ROUND(COUNT(b.booking_id) * 100.0 / t.total_capacity, 2) as occupancy_percent
                   FROM schedules s
                   JOIN trains t ON s.train_id = t.train_id
                   LEFT JOIN bookings b ON s.schedule_id = b.schedule_id AND b.booking_status != 'Cancelled'
                   GROUP BY s.schedule_id, s.departure_date, t.total_capacity
                   ORDER BY s.departure_date DESC
                   LIMIT 100"""
            )
        
        return data
    
    @staticmethod
    def get_booking_trends(from_date, to_date):
        """Get booking trends over time"""
        trends = Database.fetch_all(
            """SELECT DATE(booking_date) as date,
                      COUNT(*) as total_bookings,
                      SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END) as confirmed,
                      SUM(CASE WHEN booking_status = 'Pending' THEN 1 ELSE 0 END) as pending,
                      SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled,
                      SUM(fare_amount) as daily_revenue
               FROM bookings
               WHERE booking_date BETWEEN %s AND %s
               GROUP BY DATE(booking_date)
               ORDER BY date DESC""",
            (from_date, to_date)
        )
        
        return trends
    
    @staticmethod
    def get_cancellation_statistics(from_date, to_date):
        """Get cancellation statistics"""
        stats = Database.fetch_one(
            """SELECT COUNT(*) as total_cancellations,
                      COUNT(CASE WHEN status = 'Refunded' THEN 1 END) as refunded_count,
                      SUM(CASE WHEN status = 'Refunded' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) * 100 as refund_rate,
                      (SELECT COUNT(*) FROM bookings WHERE booking_date BETWEEN %s AND %s) as total_bookings
               FROM cancellations
               WHERE cancellation_date BETWEEN %s AND %s""",
            (from_date, to_date, from_date, to_date)
        )
        
        # Calculate cancellation rate
        if stats and stats['total_bookings']:
            stats['cancellation_rate'] = (stats['total_cancellations'] / stats['total_bookings']) * 100
        
        return stats
    
    @staticmethod
    def get_top_routes(limit=10):
        """Get top routes by number of bookings"""
        routes = Database.fetch_all(
            """SELECT r.route_id,
                      st_src.station_name as source_station,
                      st_dst.station_name as destination_station,
                      COUNT(b.booking_id) as total_bookings,
                      SUM(b.fare_amount) as total_revenue,
                      AVG(b.fare_amount) as avg_fare
               FROM routes r
               JOIN stations st_src ON r.source_station_id = st_src.station_id
               JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
               LEFT JOIN schedules s ON r.route_id = s.route_id
               LEFT JOIN bookings b ON s.schedule_id = b.schedule_id
               WHERE b.booking_id IS NOT NULL
               GROUP BY r.route_id, st_src.station_name, st_dst.station_name
               ORDER BY total_bookings DESC
               LIMIT %s""",
            (limit,)
        )
        
        return routes
    
    @staticmethod
    def get_passenger_statistics():
        """Get passenger statistics"""
        stats = Database.fetch_one(
            """SELECT COUNT(*) as total_passengers,
                      (SELECT COUNT(DISTINCT passenger_id) FROM bookings) as passengers_with_bookings,
                      (SELECT AVG(booking_count) FROM (
                          SELECT COUNT(*) as booking_count 
                          FROM bookings 
                          GROUP BY passenger_id
                      ) subquery) as avg_bookings_per_passenger,
                      (SELECT COUNT(*) FROM bookings) as total_bookings
               FROM passengers"""
        )
        
        return stats
    
    @staticmethod
    def get_staff_performance(from_date, to_date):
        """Get staff performance metrics"""
        performance = Database.fetch_all(
            """SELECT s.staff_id, s.first_name, s.last_name, s.position,
                      COUNT(c.cancellation_id) as cancellations_handled,
                      SUM(CASE WHEN c.status = 'Refunded' THEN 1 ELSE 0 END) as refunds_processed
               FROM staff s
               LEFT JOIN cancellations c ON s.staff_id = c.cancelled_by_staff_id
               AND c.cancellation_date BETWEEN %s AND %s
               GROUP BY s.staff_id, s.first_name, s.last_name, s.position
               ORDER BY cancellations_handled DESC""",
            (from_date, to_date)
        )
        
        return performance
    
    @staticmethod
    def get_dashboard_summary():
        """Get summary metrics for dashboard"""
        summary = {
            'total_passengers': Database.fetch_scalar("SELECT COUNT(*) FROM passengers"),
            'total_bookings': Database.fetch_scalar("SELECT COUNT(*) FROM bookings"),
            'confirmed_bookings': Database.fetch_scalar(
                "SELECT COUNT(*) FROM bookings WHERE booking_status = 'Confirmed'"
            ),
            'cancelled_bookings': Database.fetch_scalar(
                "SELECT COUNT(*) FROM bookings WHERE booking_status = 'Cancelled'"
            ),
            'total_revenue': Database.fetch_scalar(
                "SELECT COALESCE(SUM(payment_amount), 0) FROM payments WHERE status = 'Completed'"
            ),
            'pending_payments': Database.fetch_scalar(
                "SELECT COUNT(*) FROM bookings WHERE booking_status = 'Pending'"
            ),
            'active_schedules': Database.fetch_scalar(
                "SELECT COUNT(*) FROM schedules WHERE status = 'Active'"
            ),
            'total_trains': Database.fetch_scalar("SELECT COUNT(*) FROM trains"),
            'total_stations': Database.fetch_scalar("SELECT COUNT(*) FROM stations")
        }
        
        return summary
