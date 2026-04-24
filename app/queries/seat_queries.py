"""
Seat Query Module
SQL queries for seat operations and availability
"""

# Get single seat by ID
GET_SEAT = """
    SELECT seat_id, coach_id, seat_number, seat_class, seat_type, is_accessible, availability, created_at
    FROM seats
    WHERE seat_id = %s
"""

# Get available seats in a coach
GET_AVAILABLE_SEATS_IN_COACH = """
    SELECT seat_id, coach_id, seat_number, seat_class, seat_type, is_accessible, availability, created_at
    FROM seats
    WHERE coach_id = %s AND availability = 'available'
    ORDER BY seat_number
"""

# Get booked seats in a coach
GET_BOOKED_SEATS_IN_COACH = """
    SELECT seat_id, coach_id, seat_number, seat_class, seat_type, is_accessible, availability, created_at
    FROM seats
    WHERE coach_id = %s AND availability = 'booked'
    ORDER BY seat_number
"""

# Create new seat
CREATE_SEAT = """
    INSERT INTO seats 
    (coach_id, seat_number, seat_class, seat_type, is_accessible, availability)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING seat_id
"""

# Update seat
UPDATE_SEAT = """
    UPDATE seats
    SET seat_class = %s, seat_type = %s, is_accessible = %s, availability = %s
    WHERE seat_id = %s
"""

# Delete seat
DELETE_SEAT = """
    DELETE FROM seats
    WHERE seat_id = %s
"""

# Get available seats for a schedule
GET_AVAILABLE_SEATS_FOR_SCHEDULE = """
    SELECT s.seat_id, s.coach_id, s.seat_number, s.seat_class, s.seat_type, s.is_accessible
    FROM seats s
    JOIN coaches c ON s.coach_id = c.coach_id
    WHERE c.train_id = (
        SELECT train_id FROM schedules WHERE schedule_id = %s
    )
    AND s.seat_id NOT IN (
        SELECT seat_id FROM bookings WHERE schedule_id = %s AND booking_status != 'cancelled'
    )
    ORDER BY s.seat_id
"""

# Check if seat is booked for a specific schedule
CHECK_SEAT_AVAILABILITY = """
    SELECT COUNT(*) as is_booked
    FROM bookings
    WHERE seat_id = %s AND schedule_id = %s AND booking_status != 'cancelled'
"""

# Get seats by class in a coach
GET_SEATS_BY_CLASS_IN_COACH = """
    SELECT seat_id, coach_id, seat_number, seat_class, seat_type, is_accessible, availability, created_at
    FROM seats
    WHERE coach_id = %s AND seat_class = %s
    ORDER BY seat_number
"""

# Get accessible seats in a coach
GET_ACCESSIBLE_SEATS_IN_COACH = """
    SELECT seat_id, coach_id, seat_number, seat_class, seat_type, is_accessible, availability, created_at
    FROM seats
    WHERE coach_id = %s AND is_accessible = TRUE
    ORDER BY seat_number
"""

# Count seats by availability status
COUNT_SEATS_BY_AVAILABILITY = """
    SELECT availability, COUNT(*) as count
    FROM seats
    WHERE coach_id = %s
    GROUP BY availability
"""

# Get seats booked by a passenger on a schedule
GET_PASSENGER_SEATS_ON_SCHEDULE = """
    SELECT s.seat_id, s.seat_number, s.seat_class, s.seat_type
    FROM seats s
    JOIN bookings b ON s.seat_id = b.seat_id
    WHERE b.passenger_id = %s AND b.schedule_id = %s AND b.booking_status != 'cancelled'
"""
