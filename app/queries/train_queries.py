"""
Train Query Module
SQL queries for train operations
"""

# Get single train by ID
GET_TRAIN = """
    SELECT train_id, train_name, train_number, train_type, capacity, total_coaches, status, created_at
    FROM trains
    WHERE train_id = %s
"""

# List all trains with pagination
LIST_TRAINS = """
    SELECT train_id, train_name, train_number, train_type, capacity, total_coaches, status, created_at
    FROM trains
    ORDER BY train_name
    LIMIT %s OFFSET %s
"""

# Count total trains
COUNT_TRAINS = """
    SELECT COUNT(*) as total
    FROM trains
"""

# Create new train
CREATE_TRAIN = """
    INSERT INTO trains 
    (train_name, train_number, train_type, capacity, total_coaches, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING train_id
"""

# Update train
UPDATE_TRAIN = """
    UPDATE trains
    SET train_name = %s, train_type = %s, capacity = %s, total_coaches = %s, status = %s
    WHERE train_id = %s
"""

# Delete train
DELETE_TRAIN = """
    DELETE FROM trains
    WHERE train_id = %s
"""

# Get train by number
GET_TRAIN_BY_NUMBER = """
    SELECT train_id, train_name, train_number, train_type, capacity, total_coaches, status, created_at
    FROM trains
    WHERE train_number = %s
"""

# Get active trains
GET_ACTIVE_TRAINS = """
    SELECT train_id, train_name, train_number, train_type, capacity, total_coaches, status, created_at
    FROM trains
    WHERE status = 'active'
    ORDER BY train_name
"""

# Get train with coaches
GET_TRAIN_WITH_COACHES = """
    SELECT t.train_id, t.train_name, t.train_number, t.train_type, t.capacity, t.total_coaches,
           c.coach_id, c.coach_number, c.coach_type, c.total_seats, c.coach_status
    FROM trains t
    LEFT JOIN coaches c ON t.train_id = c.train_id
    WHERE t.train_id = %s
    ORDER BY c.coach_number
"""

# Get train with amenities
GET_TRAIN_AMENITIES = """
    SELECT a.amenity_id, a.amenity_name, a.amenity_description, 
           a.amenity_type, a.cost_per_use, ta.quantity_available, ta.last_maintenance_date
    FROM amenities a
    JOIN train_amenities ta ON a.amenity_id = ta.amenity_id
    WHERE ta.train_id = %s
"""

# Get trains by type
GET_TRAINS_BY_TYPE = """
    SELECT train_id, train_name, train_number, train_type, capacity, total_coaches, status, created_at
    FROM trains
    WHERE train_type = %s
    ORDER BY train_name
"""

# Count coaches for a train
COUNT_COACHES_FOR_TRAIN = """
    SELECT COUNT(*) as total_coaches
    FROM coaches
    WHERE train_id = %s
"""

# Count total seats for a train
COUNT_SEATS_FOR_TRAIN = """
    SELECT SUM(c.total_seats) as total_seats
    FROM coaches c
    WHERE c.train_id = %s
"""
