"""
Analytics Query Module
SQL queries for reporting and business intelligence
"""

# Total bookings count
GET_TOTAL_BOOKINGS = """
    SELECT COUNT(*) as total_bookings
    FROM bookings
"""

# Total passengers count
GET_TOTAL_PASSENGERS = """
    SELECT COUNT(*) as total_passengers
    FROM passengers
"""

# Bookings by status
GET_BOOKINGS_BY_STATUS = """
    SELECT booking_status, COUNT(*) as count
    FROM bookings
    GROUP BY booking_status
"""

# Revenue by train
GET_REVENUE_BY_TRAIN = """
    SELECT t.train_id, t.train_name, t.train_number, 
           SUM(p.payment_amount) as total_revenue,
           COUNT(b.booking_id) as total_bookings
    FROM trains t
    JOIN schedules s ON t.train_id = s.train_id
    JOIN bookings b ON s.schedule_id = b.schedule_id
    JOIN payments p ON b.booking_id = p.booking_id
    WHERE p.payment_status = 'completed' 
    AND p.payment_date >= %s AND p.payment_date <= %s
    GROUP BY t.train_id, t.train_name, t.train_number
    ORDER BY total_revenue DESC
"""

# Revenue by route
GET_REVENUE_BY_ROUTE = """
    SELECT r.route_id, 
           st_src.station_name || ' - ' || st_dst.station_name as route_name,
           SUM(p.payment_amount) as total_revenue,
           COUNT(b.booking_id) as total_bookings
    FROM routes r
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    JOIN schedules s ON r.route_id = s.route_id
    JOIN bookings b ON s.schedule_id = b.schedule_id
    JOIN payments p ON b.booking_id = p.booking_id
    WHERE p.payment_status = 'completed'
    AND p.payment_date >= %s AND p.payment_date <= %s
    GROUP BY r.route_id, st_src.station_name, st_dst.station_name
    ORDER BY total_revenue DESC
"""

# Occupancy rate by train
GET_OCCUPANCY_BY_TRAIN = """
    SELECT t.train_id, t.train_name, 
           AVG(occupancy_percent.occupancy) as average_occupancy_rate
    FROM trains t
    JOIN schedules s ON t.train_id = s.train_id
    CROSS JOIN LATERAL (
        SELECT (COUNT(b.booking_id) * 100.0 / t.capacity) as occupancy
        FROM bookings b
        WHERE b.schedule_id = s.schedule_id AND b.booking_status != 'cancelled'
    ) occupancy_percent
    GROUP BY t.train_id, t.train_name
    ORDER BY average_occupancy_rate DESC
"""

# Top passengers by bookings
GET_TOP_PASSENGERS_BY_BOOKINGS = """
    SELECT p.passenger_id, p.first_name, p.last_name, p.email,
           COUNT(b.booking_id) as total_bookings,
           SUM(pa.payment_amount) as total_spent
    FROM passengers p
    JOIN bookings b ON p.passenger_id = b.passenger_id
    LEFT JOIN payments pa ON b.booking_id = pa.booking_id AND pa.payment_status = 'completed'
    GROUP BY p.passenger_id, p.first_name, p.last_name, p.email
    ORDER BY total_bookings DESC
    LIMIT %s
"""

# Top passengers by spending
GET_TOP_PASSENGERS_BY_SPENDING = """
    SELECT p.passenger_id, p.first_name, p.last_name, p.email,
           COUNT(b.booking_id) as total_bookings,
           SUM(pa.payment_amount) as total_spent
    FROM passengers p
    JOIN bookings b ON p.passenger_id = b.passenger_id
    LEFT JOIN payments pa ON b.booking_id = pa.booking_id AND pa.payment_status = 'completed'
    GROUP BY p.passenger_id, p.first_name, p.last_name, p.email
    ORDER BY total_spent DESC
    LIMIT %s
"""

# Daily revenue trends
GET_DAILY_REVENUE_TRENDS = """
    SELECT DATE(payment_date) as date, 
           SUM(payment_amount) as daily_revenue,
           COUNT(*) as transaction_count
    FROM payments
    WHERE payment_status = 'completed'
    AND payment_date >= %s AND payment_date <= %s
    GROUP BY DATE(payment_date)
    ORDER BY date
"""

# Bookings by day of week
GET_BOOKINGS_BY_DAY_OF_WEEK = """
    SELECT EXTRACT(DOW FROM booking_date) as day_of_week,
           TO_CHAR(booking_date, 'Day') as day_name,
           COUNT(*) as booking_count
    FROM bookings
    WHERE booking_date >= %s AND booking_date <= %s
    GROUP BY EXTRACT(DOW FROM booking_date), TO_CHAR(booking_date, 'Day')
    ORDER BY day_of_week
"""

# Cancellation statistics
GET_CANCELLATION_STATISTICS = """
    SELECT COUNT(*) as total_cancellations,
           COUNT(*) * 100.0 / (SELECT COUNT(*) FROM bookings) as cancellation_rate
    FROM bookings
    WHERE booking_status = 'cancelled'
"""

# Seat occupancy by coach type
GET_OCCUPANCY_BY_COACH_TYPE = """
    SELECT c.coach_type,
           COUNT(s.seat_id) as total_seats,
           SUM(CASE WHEN b.booking_id IS NOT NULL THEN 1 ELSE 0 END) as booked_seats,
           (SUM(CASE WHEN b.booking_id IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(s.seat_id)) as occupancy_rate
    FROM coaches c
    JOIN seats s ON c.coach_id = s.coach_id
    LEFT JOIN bookings b ON s.seat_id = b.seat_id AND b.booking_status != 'cancelled'
    GROUP BY c.coach_type
"""

# Revenue comparison by month
GET_REVENUE_BY_MONTH = """
    SELECT DATE_TRUNC('month', payment_date) as month,
           SUM(payment_amount) as monthly_revenue,
           COUNT(*) as transaction_count
    FROM payments
    WHERE payment_status = 'completed'
    AND payment_date >= %s AND payment_date <= %s
    GROUP BY DATE_TRUNC('month', payment_date)
    ORDER BY month DESC
"""
