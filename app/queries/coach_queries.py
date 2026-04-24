"""
Coach Query Module
SQL queries for coach operations
"""

# Get single coach by ID
GET_COACH = """
    SELECT coach_id, train_id, coach_number, coach_type, total_seats, coach_status, created_at
    FROM coaches
    WHERE coach_id = %s
"""

# List coaches for a train
LIST_COACHES_BY_TRAIN = """
    SELECT coach_id, train_id, coach_number, coach_type, total_seats, coach_status, created_at
    FROM coaches
    WHERE train_id = %s
    ORDER BY coach_number
"""

# Create new coach
CREATE_COACH = """
    INSERT INTO coaches 
    (train_id, coach_number, coach_type, total_seats, coach_status)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING coach_id
"""

# Update coach
UPDATE_COACH = """
    UPDATE coaches
    SET coach_type = %s, total_seats = %s, coach_status = %s
    WHERE coach_id = %s
"""

# Delete coach
DELETE_COACH = """
    DELETE FROM coaches
    WHERE coach_id = %s
"""

# Get coach with all seats
GET_COACH_WITH_SEATS = """
    SELECT c.coach_id, c.train_id, c.coach_number, c.coach_type, c.total_seats, c.coach_status,
           s.seat_id, s.seat_number, s.seat_class, s.seat_type, s.is_accessible, s.availability
    FROM coaches c
    LEFT JOIN seats s ON c.coach_id = s.coach_id
    WHERE c.coach_id = %s
    ORDER BY s.seat_number
"""

# Count available seats in coach
COUNT_AVAILABLE_SEATS_IN_COACH = """
    SELECT COUNT(*) as available_seats
    FROM seats
    WHERE coach_id = %s AND availability = 'available'
"""

# Count booked seats in coach
COUNT_BOOKED_SEATS_IN_COACH = """
    SELECT COUNT(*) as booked_seats
    FROM seats
    WHERE coach_id = %s AND availability = 'booked'
"""

# List coaches by type for a train
LIST_COACHES_BY_TYPE = """
    SELECT coach_id, train_id, coach_number, coach_type, total_seats, coach_status, created_at
    FROM coaches
    WHERE train_id = %s AND coach_type = %s
    ORDER BY coach_number
"""

# Get coach occupancy
GET_COACH_OCCUPANCY = """
    SELECT 
        c.coach_id,
        c.coach_number,
        c.total_seats,
        COUNT(b.booking_id) as booked_seats,
        (COUNT(b.booking_id) * 100.0 / c.total_seats) as occupancy_percentage
    FROM coaches c
    LEFT JOIN seats s ON c.coach_id = s.coach_id
    LEFT JOIN bookings b ON s.seat_id = b.seat_id AND b.booking_status = 'pending'
    WHERE c.coach_id = %s
    GROUP BY c.coach_id, c.coach_number, c.total_seats
"""
