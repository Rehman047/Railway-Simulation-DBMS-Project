"""
Schedule Query Module
SQL queries for schedule operations
"""

# Get single schedule by ID
GET_SCHEDULE = """
    SELECT schedule_id, train_id, route_id, departure_date, departure_time, arrival_time, schedule_status, created_at
    FROM schedules
    WHERE schedule_id = %s
"""

# List schedules with pagination
LIST_SCHEDULES = """
    SELECT s.schedule_id, s.train_id, s.route_id, s.departure_date, s.departure_time, s.arrival_time, s.schedule_status,
           t.train_name, t.train_number,
           st_src.station_name as source_station,
           st_dst.station_name as destination_station
    FROM schedules s
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    ORDER BY s.departure_date DESC, s.departure_time
    LIMIT %s OFFSET %s
"""

# Count total schedules
COUNT_SCHEDULES = """
    SELECT COUNT(*) as total
    FROM schedules
"""

# Create new schedule
CREATE_SCHEDULE = """
    INSERT INTO schedules 
    (train_id, route_id, departure_date, departure_time, arrival_time, schedule_status)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING schedule_id
"""

# Update schedule
UPDATE_SCHEDULE = """
    UPDATE schedules
    SET departure_time = %s, arrival_time = %s, schedule_status = %s
    WHERE schedule_id = %s
"""

# Delete schedule
DELETE_SCHEDULE = """
    DELETE FROM schedules
    WHERE schedule_id = %s
"""

# Get schedules for a specific route between two dates
GET_SCHEDULES_FOR_ROUTE = """
    SELECT s.schedule_id, s.departure_date, s.departure_time, s.arrival_time, s.schedule_status,
           t.train_name, t.train_number, t.train_type,
           COUNT(b.booking_id) as bookings_count,
           t.capacity as total_seats
    FROM schedules s
    JOIN trains t ON s.train_id = t.train_id
    LEFT JOIN bookings b ON s.schedule_id = b.schedule_id AND b.booking_status != 'cancelled'
    WHERE s.route_id = %s
    AND s.departure_date >= %s AND s.departure_date <= %s
    GROUP BY s.schedule_id, t.train_name, t.train_number, t.train_type, t.capacity
    ORDER BY s.departure_date, s.departure_time
"""

# Get future schedules (for a specific date onwards)
GET_FUTURE_SCHEDULES = """
    SELECT s.schedule_id, s.train_id, s.route_id, s.departure_date, s.departure_time, s.arrival_time, s.schedule_status,
           t.train_name, t.train_number,
           st_src.station_name as source_station,
           st_dst.station_name as destination_station
    FROM schedules s
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    WHERE s.departure_date >= %s
    AND s.schedule_status IN ('scheduled', 'confirmed')
    ORDER BY s.departure_date, s.departure_time
"""

# Get schedule occupancy
GET_SCHEDULE_OCCUPANCY = """
    SELECT 
        s.schedule_id,
        s.departure_date,
        s.departure_time,
        t.capacity as total_seats,
        COUNT(b.booking_id) as booked_seats,
        (COUNT(b.booking_id) * 100.0 / t.capacity) as occupancy_percentage
    FROM schedules s
    JOIN trains t ON s.train_id = t.train_id
    LEFT JOIN bookings b ON s.schedule_id = b.schedule_id AND b.booking_status != 'cancelled'
    WHERE s.schedule_id = %s
    GROUP BY s.schedule_id, s.departure_date, s.departure_time, t.capacity
"""

# Get available seats count for schedule
GET_AVAILABLE_SEATS_COUNT_FOR_SCHEDULE = """
    SELECT t.capacity - COUNT(b.booking_id) as available_seats
    FROM schedules s
    JOIN trains t ON s.train_id = t.train_id
    LEFT JOIN bookings b ON s.schedule_id = b.schedule_id AND b.booking_status != 'cancelled'
    WHERE s.schedule_id = %s
    GROUP BY t.capacity
"""

# Get schedule details with route information
GET_SCHEDULE_DETAILS = """
    SELECT s.schedule_id, s.departure_date, s.departure_time, s.arrival_time, s.schedule_status,
           t.train_id, t.train_name, t.train_number, t.train_type, t.capacity,
           r.route_id, r.distance, r.estimated_duration,
           st_src.station_id as source_id, st_src.station_name as source_station,
           st_dst.station_id as destination_id, st_dst.station_name as destination_station
    FROM schedules s
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    WHERE s.schedule_id = %s
"""
