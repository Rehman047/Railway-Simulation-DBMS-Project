"""
Payment Query Module
SQL queries for payment operations and tracking
"""

# Get single payment by ID
GET_PAYMENT = """
    SELECT payment_id, booking_id, payment_amount, payment_method, payment_date, 
           transaction_id, payment_status, verification_date
    FROM payments
    WHERE payment_id = %s
"""

# Create new payment
CREATE_PAYMENT = """
    INSERT INTO payments 
    (booking_id, payment_amount, payment_method, transaction_id, payment_status)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING payment_id
"""

# Get payments for a booking
GET_BOOKING_PAYMENTS = """
    SELECT payment_id, payment_amount, payment_method, payment_date, 
           transaction_id, payment_status, verification_date
    FROM payments
    WHERE booking_id = %s
    ORDER BY payment_date DESC
"""

# List all payments with pagination
LIST_PAYMENTS = """
    SELECT p.payment_id, p.booking_id, p.payment_amount, p.payment_method, p.payment_date,
           p.transaction_id, p.payment_status, p.verification_date,
           b.passenger_id, pa.first_name, pa.last_name, pa.email,
           s.departure_date, t.train_name
    FROM payments p
    JOIN bookings b ON p.booking_id = b.booking_id
    JOIN passengers pa ON b.passenger_id = pa.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    ORDER BY p.payment_date DESC
    LIMIT %s OFFSET %s
"""

# Count total payments
COUNT_PAYMENTS = """
    SELECT COUNT(*) as total
    FROM payments
"""

# Update payment status
UPDATE_PAYMENT_STATUS = """
    UPDATE payments
    SET payment_status = %s, verification_date = CURRENT_TIMESTAMP
    WHERE payment_id = %s
"""

# Get pending payments
GET_PENDING_PAYMENTS = """
    SELECT p.payment_id, p.booking_id, p.payment_amount, p.payment_method, p.payment_date,
           b.passenger_id, pa.first_name, pa.last_name, pa.email,
           b.fare_amount, s.departure_date, t.train_name
    FROM payments p
    JOIN bookings b ON p.booking_id = b.booking_id
    JOIN passengers pa ON b.passenger_id = pa.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    WHERE p.payment_status = 'pending'
    ORDER BY p.payment_date
"""

# Get completed payments
GET_COMPLETED_PAYMENTS = """
    SELECT p.payment_id, p.booking_id, p.payment_amount, p.payment_method, p.payment_date,
           p.verification_date,
           b.passenger_id, pa.first_name, pa.last_name,
           s.departure_date, t.train_name
    FROM payments p
    JOIN bookings b ON p.booking_id = b.booking_id
    JOIN passengers pa ON b.passenger_id = pa.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    WHERE p.payment_status = 'completed'
    ORDER BY p.verification_date DESC
"""

# Get payment by transaction ID
GET_PAYMENT_BY_TRANSACTION = """
    SELECT payment_id, booking_id, payment_amount, payment_method, payment_date, 
           transaction_id, payment_status, verification_date
    FROM payments
    WHERE transaction_id = %s
"""

# Count payments by status
COUNT_PAYMENTS_BY_STATUS = """
    SELECT payment_status, COUNT(*) as count
    FROM payments
    GROUP BY payment_status
"""

# Get total revenue (completed payments)
GET_TOTAL_REVENUE = """
    SELECT COALESCE(SUM(payment_amount), 0) as total_revenue
    FROM payments
    WHERE payment_status = 'completed'
"""

# Get revenue by date range
GET_REVENUE_BY_DATE_RANGE = """
    SELECT SUM(p.payment_amount) as total_revenue
    FROM payments p
    WHERE p.payment_status = 'completed'
    AND p.payment_date >= %s AND p.payment_date <= %s
"""

# Get revenue by payment method
GET_REVENUE_BY_METHOD = """
    SELECT payment_method, COUNT(*) as transaction_count, SUM(payment_amount) as total_revenue
    FROM payments
    WHERE payment_status = 'completed'
    GROUP BY payment_method
"""
