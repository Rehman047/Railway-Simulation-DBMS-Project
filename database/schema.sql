-- ============================================================
-- RAILWAY DBMS - DATABASE SCHEMA
-- ============================================================

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS cancellations CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS schedules CASCADE;
DROP TABLE IF EXISTS train_amenities CASCADE;
DROP TABLE IF EXISTS station_services CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS seats CASCADE;
DROP TABLE IF EXISTS coaches CASCADE;
DROP TABLE IF EXISTS trains CASCADE;
DROP TABLE IF EXISTS amenities CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS passengers CASCADE;
DROP TABLE IF EXISTS stations CASCADE;

-- ============================================================
-- INDEPENDENT TABLES (No Foreign Keys)
-- ============================================================

CREATE TABLE stations (
    station_id SERIAL PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    address VARCHAR(255),
    contact_number VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE passengers (
    passenger_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    id_proof_type VARCHAR(30),
    id_proof_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    service_description TEXT,
    service_cost NUMERIC(10, 2) DEFAULT 0,
    availability_status VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE amenities (
    amenity_id SERIAL PRIMARY KEY,
    amenity_name VARCHAR(100) NOT NULL,
    amenity_description TEXT,
    amenity_type VARCHAR(50),
    cost_per_use NUMERIC(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staff (
    staff_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    position VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    hire_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trains (
    train_id SERIAL PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    train_number VARCHAR(50) UNIQUE NOT NULL,
    train_type VARCHAR(50),
    capacity INTEGER NOT NULL,
    total_coaches INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SINGLE FOREIGN KEY TABLES
-- ============================================================

CREATE TABLE coaches (
    coach_id SERIAL PRIMARY KEY,
    train_id INTEGER NOT NULL REFERENCES trains(train_id),
    coach_number VARCHAR(10) NOT NULL,
    coach_type VARCHAR(50),
    total_seats INTEGER NOT NULL,
    coach_status VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(train_id, coach_number)
);

CREATE TABLE seats (
    seat_id SERIAL PRIMARY KEY,
    coach_id INTEGER NOT NULL REFERENCES coaches(coach_id),
    seat_number VARCHAR(10) NOT NULL,
    seat_class VARCHAR(30),
    seat_type VARCHAR(30),
    is_accessible BOOLEAN DEFAULT FALSE,
    availability VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(coach_id, seat_number)
);

CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    train_id INTEGER NOT NULL REFERENCES trains(train_id),
    source_station_id INTEGER NOT NULL REFERENCES stations(station_id),
    destination_station_id INTEGER NOT NULL REFERENCES stations(station_id),
    distance NUMERIC(10, 2),
    estimated_duration NUMERIC(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (source_station_id != destination_station_id)
);

CREATE TABLE station_services (
    station_service_id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(station_id),
    service_id INTEGER NOT NULL REFERENCES services(service_id),
    available_from TIME,
    available_till TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE train_amenities (
    train_amenity_id SERIAL PRIMARY KEY,
    train_id INTEGER NOT NULL REFERENCES trains(train_id),
    amenity_id INTEGER NOT NULL REFERENCES amenities(amenity_id),
    quantity_available INTEGER,
    last_maintenance_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- MULTI FOREIGN KEY TABLES
-- ============================================================

CREATE TABLE schedules (
    schedule_id SERIAL PRIMARY KEY,
    train_id INTEGER NOT NULL REFERENCES trains(train_id),
    route_id INTEGER NOT NULL REFERENCES routes(route_id),
    departure_date DATE NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    schedule_status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    passenger_id INTEGER NOT NULL REFERENCES passengers(passenger_id),
    schedule_id INTEGER NOT NULL REFERENCES schedules(schedule_id),
    seat_id INTEGER NOT NULL REFERENCES seats(seat_id),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fare_amount NUMERIC(10, 2) NOT NULL,
    booking_status VARCHAR(20) DEFAULT 'pending',
    CHECK (fare_amount > 0)
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(booking_id),
    payment_amount NUMERIC(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_id VARCHAR(100) UNIQUE,
    payment_status VARCHAR(20) DEFAULT 'pending',
    verification_date TIMESTAMP,
    CHECK (payment_amount > 0)
);

CREATE TABLE cancellations (
    cancellation_id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(booking_id),
    cancellation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancellation_reason VARCHAR(255),
    cancelled_by_staff_id INTEGER REFERENCES staff(staff_id),
    refund_amount NUMERIC(10, 2),
    refund_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX idx_passengers_email ON passengers(email);
CREATE INDEX idx_passengers_phone ON passengers(phone_number);
CREATE INDEX idx_bookings_passenger ON bookings(passenger_id);
CREATE INDEX idx_bookings_schedule ON bookings(schedule_id);
CREATE INDEX idx_bookings_seat ON bookings(seat_id);
CREATE INDEX idx_schedules_train ON schedules(train_id);
CREATE INDEX idx_schedules_route ON schedules(route_id);
CREATE INDEX idx_schedules_date ON schedules(departure_date);
CREATE INDEX idx_coaches_train ON coaches(train_id);
CREATE INDEX idx_seats_coach ON seats(coach_id);
CREATE INDEX idx_routes_train ON routes(train_id);
CREATE INDEX idx_payments_booking ON payments(booking_id);
CREATE INDEX idx_cancellations_booking ON cancellations(booking_id);
CREATE INDEX idx_trains_number ON trains(train_number);
