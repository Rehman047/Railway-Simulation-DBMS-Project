"""
Cancellation Query Module
SQL queries for cancellation operations and refund management
"""

# Get single cancellation by ID
GET_CANCELLATION = """
    SELECT c.cancellation_id, c.booking_id, c.cancelled_by_staff_id, 
           c.cancellation_date, c.reason, c.status, c.created_at,
           b.passenger_id, b.fare_amount, b.booking_status,
           p.first_name, p.last_name, p.email,
           t.train_name, s.departure_date, s.departure_time
    FROM cancellations c
    JOIN bookings b ON c.booking_id = b.booking_id
    JOIN passengers p ON b.passenger_id = p.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    WHERE c.cancellation_id = %s
"""

# List all cancellations with pagination
LIST_CANCELLATIONS = """
    SELECT c.cancellation_id, c.booking_id, c.cancelled_by_staff_id,
           c.cancellation_date, c.reason, c.status,
           b.passenger_id, b.fare_amount,
           p.first_name, p.last_name, p.email,
           t.train_name, s.departure_date,
           st_src.station_name as source_station,
           st_dst.station_name as destination_station
    FROM cancellations c
    JOIN bookings b ON c.booking_id = b.booking_id
    JOIN passengers p ON b.passenger_id = p.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    ORDER BY c.cancellation_date DESC
    LIMIT %s OFFSET %s
"""

# Count total cancellations
COUNT_CANCELLATIONS = """
    SELECT COUNT(*) as total
    FROM cancellations
"""

# Create new cancellation
CREATE_CANCELLATION = """
    INSERT INTO cancellations 
    (booking_id, cancelled_by_staff_id, cancellation_date, reason, status)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING cancellation_id
"""

# Update cancellation status
UPDATE_CANCELLATION_STATUS = """
    UPDATE cancellations
    SET status = %s
    WHERE cancellation_id = %s
"""

# Get cancellations by staff member
GET_STAFF_CANCELLATIONS = """
    SELECT c.cancellation_id, c.booking_id, c.cancellation_date, c.reason, c.status,
           b.passenger_id, b.fare_amount,
           p.first_name, p.last_name, p.email,
           t.train_name, s.departure_date
    FROM cancellations c
    JOIN bookings b ON c.booking_id = b.booking_id
    JOIN passengers p ON b.passenger_id = p.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    WHERE c.cancelled_by_staff_id = %s
    ORDER BY c.cancellation_date DESC
"""

# Get cancellations by staff member in date range
GET_STAFF_CANCELLATIONS_BY_DATE = """
    SELECT c.cancellation_id, c.booking_id, c.cancellation_date, c.reason, c.status,
           b.passenger_id, b.fare_amount,
           p.first_name, p.last_name, p.email,
           t.train_name, s.departure_date
    FROM cancellations c
    JOIN bookings b ON c.booking_id = b.booking_id
    JOIN passengers p ON b.passenger_id = p.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    WHERE c.cancelled_by_staff_id = %s
    AND c.cancellation_date BETWEEN %s AND %s
    ORDER BY c.cancellation_date DESC
"""

# Get cancellations by reason
GET_CANCELLATIONS_BY_REASON = """
    SELECT reason, COUNT(*) as count,
           SUM(b.fare_amount) as total_refunded
    FROM cancellations c
    JOIN bookings b ON c.booking_id = b.booking_id
    GROUP BY reason
    ORDER BY count DESC
"""

# Get pending refunds
GET_PENDING_REFUNDS = """
    SELECT c.cancellation_id, c.booking_id, b.passenger_id, b.fare_amount,
           p.first_name, p.last_name, p.email,
           c.cancellation_date, s.departure_date
    FROM cancellations c
    JOIN bookings b ON c.booking_id = b.booking_id
    JOIN passengers p ON b.passenger_id = p.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    WHERE c.status = 'Pending'
    ORDER BY c.cancellation_date
"""

# Get cancellations with refund status
GET_CANCELLATIONS_WITH_REFUNDS = """
    SELECT c.cancellation_id, c.booking_id, c.cancellation_date, c.reason, c.status,
           b.passenger_id, b.fare_amount,
           p.first_name, p.last_name,
           COALESCE(pay.payment_amount, 0) as refund_amount,
           COALESCE(pay.status, 'Not Processed') as refund_status
    FROM cancellations c
    JOIN bookings b ON c.booking_id = b.booking_id
    JOIN passengers p ON b.passenger_id = p.passenger_id
    LEFT JOIN payments pay ON b.booking_id = pay.booking_id 
                          AND pay.payment_method = 'Refund'
    ORDER BY c.cancellation_date DESC
"""

# Count cancellations by status
COUNT_CANCELLATIONS_BY_STATUS = """
    SELECT status, COUNT(*) as count
    FROM cancellations
    GROUP BY status
"""

# Get cancellation rate statistics
GET_CANCELLATION_STATISTICS = """
    SELECT COUNT(*) as total_cancellations,
           SUM(CASE WHEN status = 'Refunded' THEN 1 ELSE 0 END) as refunded,
           SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
           SUM(CASE WHEN status = 'Processed' THEN 1 ELSE 0 END) as processed
    FROM cancellations
"""
