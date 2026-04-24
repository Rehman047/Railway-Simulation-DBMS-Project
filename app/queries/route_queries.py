"""
Route Query Module
SQL queries for route operations
"""

# Get single route by ID
GET_ROUTE = """
    SELECT route_id, train_id, source_station_id, destination_station_id, distance, estimated_duration, created_at
    FROM routes
    WHERE route_id = %s
"""

# List all routes with pagination
LIST_ROUTES = """
    SELECT r.route_id, r.train_id, r.source_station_id, r.destination_station_id, r.distance, r.estimated_duration,
           t.train_name, t.train_number,
           st_src.station_name as source_station,
           st_dst.station_name as destination_station
    FROM routes r
    JOIN trains t ON r.train_id = t.train_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    ORDER BY r.route_id
    LIMIT %s OFFSET %s
"""

# Count total routes
COUNT_ROUTES = """
    SELECT COUNT(*) as total
    FROM routes
"""

# Create new route
CREATE_ROUTE = """
    INSERT INTO routes 
    (train_id, source_station_id, destination_station_id, distance, estimated_duration)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING route_id
"""

# Update route
UPDATE_ROUTE = """
    UPDATE routes
    SET distance = %s, estimated_duration = %s
    WHERE route_id = %s
"""

# Delete route
DELETE_ROUTE = """
    DELETE FROM routes
    WHERE route_id = %s
"""

# Find routes between two stations
FIND_ROUTES_BETWEEN_STATIONS = """
    SELECT r.route_id, r.train_id, r.distance, r.estimated_duration,
           t.train_name, t.train_number, t.train_type,
           st_src.station_name as source_station,
           st_dst.station_name as destination_station
    FROM routes r
    JOIN trains t ON r.train_id = t.train_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    WHERE r.source_station_id = %s AND r.destination_station_id = %s
    AND t.status = 'active'
"""

# Get routes for a specific train
GET_ROUTES_FOR_TRAIN = """
    SELECT r.route_id, r.distance, r.estimated_duration,
           st_src.station_name as source_station, st_src.station_id as source_station_id,
           st_dst.station_name as destination_station, st_dst.station_id as destination_station_id
    FROM routes r
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    WHERE r.train_id = %s
    ORDER BY r.route_id
"""

# Get detailed route information
GET_ROUTE_DETAILS = """
    SELECT r.route_id, r.train_id, r.distance, r.estimated_duration, r.created_at,
           t.train_name, t.train_number, t.train_type, t.capacity,
           st_src.station_id as source_station_id, st_src.station_name as source_station, 
           st_src.city as source_city,
           st_dst.station_id as destination_station_id, st_dst.station_name as destination_station,
           st_dst.city as destination_city
    FROM routes r
    JOIN trains t ON r.train_id = t.train_id
    JOIN stations st_src ON r.source_station_id = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    WHERE r.route_id = %s
"""
