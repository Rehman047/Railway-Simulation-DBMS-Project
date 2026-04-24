"""
Passenger Query Module
SQL queries for passenger CRUD operations
"""

# Get single passenger by ID
GET_PASSENGER = """
    SELECT passenger_id, first_name, last_name, email, phone_number, 
           date_of_birth, id_proof_type, id_proof_number, created_at
    FROM passengers
    WHERE passenger_id = %s
"""

# List all passengers with pagination
LIST_PASSENGERS = """
    SELECT passenger_id, first_name, last_name, email, phone_number, 
           date_of_birth, id_proof_type, id_proof_number, created_at
    FROM passengers
    ORDER BY first_name, last_name
    LIMIT %s OFFSET %s
"""

# Count total passengers
COUNT_PASSENGERS = """
    SELECT COUNT(*) as total
    FROM passengers
"""

# Create new passenger
CREATE_PASSENGER = """
    INSERT INTO passengers 
    (first_name, last_name, email, phone_number, date_of_birth, id_proof_type, id_proof_number)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING passenger_id
"""

# Update passenger
UPDATE_PASSENGER = """
    UPDATE passengers
    SET first_name = %s, last_name = %s, email = %s, phone_number = %s, id_proof_type = %s
    WHERE passenger_id = %s
"""

# Delete passenger
DELETE_PASSENGER = """
    DELETE FROM passengers
    WHERE passenger_id = %s
"""

# Get passenger by email
GET_PASSENGER_BY_EMAIL = """
    SELECT passenger_id, first_name, last_name, email, phone_number, 
           date_of_birth, id_proof_type, id_proof_number, created_at
    FROM passengers
    WHERE email = %s
"""

# Get passenger by phone
GET_PASSENGER_BY_PHONE = """
    SELECT passenger_id, first_name, last_name, email, phone_number, 
           date_of_birth, id_proof_type, id_proof_number, created_at
    FROM passengers
    WHERE phone_number = %s
"""

# Get passenger booking history
GET_PASSENGER_BOOKINGS = """
    SELECT b.booking_id, b.booking_date, b.fare_amount, b.booking_status,
           t.train_name, s.departure_date, s.departure_time, s.arrival_time,
           st_src.station_name as source_station, st_dst.station_name as destination_station
    FROM bookings b
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    WHERE b.passenger_id = %s
    ORDER BY s.departure_date DESC
"""

# Count bookings for a passenger
COUNT_PASSENGER_BOOKINGS = """
    SELECT COUNT(*) as total
    FROM bookings
    WHERE passenger_id = %s
"""

# Search passengers by name
SEARCH_PASSENGERS_BY_NAME = """
    SELECT passenger_id, first_name, last_name, email, phone_number, 
           date_of_birth, id_proof_type, id_proof_number, created_at
    FROM passengers
    WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE LOWER(%s)
    ORDER BY first_name, last_name
"""
