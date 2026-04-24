"""
Station Query Module
SQL queries for station operations
"""

# Get single station by ID
GET_STATION = """
    SELECT station_id, station_name, city, state, address, contact_number, created_at
    FROM stations
    WHERE station_id = %s
"""

# List all stations with pagination
LIST_STATIONS = """
    SELECT station_id, station_name, city, state, address, contact_number, created_at
    FROM stations
    ORDER BY station_name
    LIMIT %s OFFSET %s
"""

# Count total stations
COUNT_STATIONS = """
    SELECT COUNT(*) as total
    FROM stations
"""

# Create new station
CREATE_STATION = """
    INSERT INTO stations 
    (station_name, city, state, address, contact_number)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING station_id
"""

# Update station
UPDATE_STATION = """
    UPDATE stations
    SET station_name = %s, city = %s, state = %s, address = %s, contact_number = %s
    WHERE station_id = %s
"""

# Delete station
DELETE_STATION = """
    DELETE FROM stations
    WHERE station_id = %s
"""

# Get station by name
GET_STATION_BY_NAME = """
    SELECT station_id, station_name, city, state, address, contact_number, created_at
    FROM stations
    WHERE LOWER(station_name) = LOWER(%s)
"""

# List stations in a city
GET_STATIONS_BY_CITY = """
    SELECT station_id, station_name, city, state, address, contact_number, created_at
    FROM stations
    WHERE city = %s
    ORDER BY station_name
"""

# Get routes starting from a station
GET_ROUTES_FROM_STATION = """
    SELECT r.route_id, r.distance, r.estimated_duration, 
           t.train_name, t.train_number,
           st_dst.station_name as destination_station
    FROM routes r
    JOIN trains t ON r.train_id = t.train_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    WHERE r.source_station_id = %s
"""

# Get routes ending at a station
GET_ROUTES_TO_STATION = """
    SELECT r.route_id, r.distance, r.estimated_duration, 
           t.train_name, t.train_number,
           st_src.station_name as source_station
    FROM routes r
    JOIN trains t ON r.train_id = t.train_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    WHERE r.destination_station_id = %s
"""

# Get services available at a station
GET_STATION_SERVICES = """
    SELECT s.service_id, s.service_name, s.service_description, 
           s.service_cost, ss.available_from, ss.available_till
    FROM services s
    JOIN station_services ss ON s.service_id = ss.service_id
    WHERE ss.station_id = %s
"""
