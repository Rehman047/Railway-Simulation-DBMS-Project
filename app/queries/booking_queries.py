"""
Booking Query Module
SQL queries for booking operations and management
"""

# Get single booking by ID
GET_BOOKING = """
    SELECT booking_id, passenger_id, schedule_id, seat_id, booking_date, fare_amount, booking_status
    FROM bookings
    WHERE booking_id = %s
"""

# Create new booking
CREATE_BOOKING = """
    INSERT INTO bookings 
    (passenger_id, schedule_id, seat_id, fare_amount, booking_status)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING booking_id
"""

# Get all bookings with pagination
LIST_BOOKINGS = """
    SELECT b.booking_id, b.passenger_id, b.schedule_id, b.seat_id, b.booking_date, 
           b.fare_amount, b.booking_status,
           p.first_name, p.last_name, p.email,
           t.train_name, t.train_number,
           s.departure_date, s.departure_time,
           st_src.station_name as source_station,
           st_dst.station_name as destination_station
    FROM bookings b
    JOIN passengers p ON b.passenger_id = p.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    ORDER BY b.booking_date DESC
    LIMIT %s OFFSET %s
"""

# Count total bookings
COUNT_BOOKINGS = """
    SELECT COUNT(*) as total
    FROM bookings
"""

# Get bookings for a passenger
GET_PASSENGER_BOOKINGS = """
    SELECT b.booking_id, b.schedule_id, b.seat_id, b.booking_date, b.fare_amount, b.booking_status,
           t.train_name, t.train_number,
           s.departure_date, s.departure_time, s.arrival_time,
           st_src.station_name as source_station,
           st_dst.station_name as destination_station,
           se.seat_number, se.seat_class
    FROM bookings b
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    JOIN seats se ON b.seat_id = se.seat_id
    WHERE b.passenger_id = %s
    ORDER BY s.departure_date DESC
"""

# Get bookings for a schedule
GET_SCHEDULE_BOOKINGS = """
    SELECT b.booking_id, b.passenger_id, b.seat_id, b.booking_date, b.fare_amount, b.booking_status,
           p.first_name, p.last_name, p.email,
           se.seat_number, se.seat_class
    FROM bookings b
    JOIN passengers p ON b.passenger_id = p.passenger_id
    JOIN seats se ON b.seat_id = se.seat_id
    WHERE b.schedule_id = %s AND b.booking_status != 'cancelled'
    ORDER BY se.seat_number
"""

# Get booking with full details
GET_BOOKING_DETAILS = """
    SELECT b.booking_id, b.booking_date, b.fare_amount, b.booking_status,
           p.passenger_id, p.first_name, p.last_name, p.email, p.phone_number,
           s.schedule_id, s.departure_date, s.departure_time, s.arrival_time,
           t.train_name, t.train_number, t.train_type,
           st_src.station_name as source_station, st_src.city as source_city,
           st_dst.station_name as destination_station, st_dst.city as destination_city,
           se.seat_id, se.seat_number, se.seat_class, se.seat_type
    FROM bookings b
    JOIN passengers p ON b.passenger_id = p.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    JOIN seats se ON b.seat_id = se.seat_id
    WHERE b.booking_id = %s
"""

# Update booking status
UPDATE_BOOKING_STATUS = """
    UPDATE bookings
    SET booking_status = %s
    WHERE booking_id = %s
"""

# Count bookings by status
COUNT_BOOKINGS_BY_STATUS = """
    SELECT booking_status, COUNT(*) as count
    FROM bookings
    GROUP BY booking_status
"""

# Check if seat is booked for schedule
CHECK_SEAT_BOOKED = """
    SELECT COUNT(*) as is_booked
    FROM bookings
    WHERE schedule_id = %s AND seat_id = %s AND booking_status != 'cancelled'
"""

# Delete booking (soft delete - update status)
CANCEL_BOOKING = """
    UPDATE bookings
    SET booking_status = 'cancelled'
    WHERE booking_id = %s
"""

# Get pending bookings (for payment)
GET_PENDING_BOOKINGS = """
    SELECT b.booking_id, b.passenger_id, b.schedule_id, b.booking_date, b.fare_amount,
           p.first_name, p.last_name, p.email,
           t.train_name, s.departure_date
    FROM bookings b
    JOIN passengers p ON b.passenger_id = p.passenger_id
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    WHERE b.booking_status = 'pending'
    ORDER BY b.booking_date
"""
