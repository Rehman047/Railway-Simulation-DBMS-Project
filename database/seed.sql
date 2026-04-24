-- ============================================================
-- RAILWAY DBMS - SAMPLE DATA
-- ============================================================

-- Insert Stations
INSERT INTO stations (station_name, city, state, address, contact_number) VALUES
('Central Station', 'Karachi', 'Sindh', '123 Railway Road, Karachi', '0300-1234567'),
('Lahore Junction', 'Lahore', 'Punjab', '456 Station Square, Lahore', '0300-2345678'),
('Peshawar Station', 'Peshawar', 'KP', '789 Main Street, Peshawar', '0300-3456789'),
('Islamabad Central', 'Islamabad', 'Federal', '321 Park Road, Islamabad', '0300-4567890'),
('Multan Junction', 'Multan', 'Punjab', '654 Express Road, Multan', '0300-5678901'),
('Quetta Terminal', 'Quetta', 'Balochistan', '987 Railway Lane, Quetta', '0300-6789012'),
('Rawalpindi Station', 'Rawalpindi', 'Punjab', '159 Station Street, Rawalpindi', '0300-7890123'),
('Faisalabad Central', 'Faisalabad', 'Punjab', '753 Main Junction, Faisalabad', '0300-8901234');

-- Insert Staff
INSERT INTO staff (first_name, last_name, email, phone_number, position, hire_date) VALUES
('Ahmed', 'Khan', 'ahmed.khan@railway.com', '0300-1111111', 'Supervisor', '2022-01-15'),
('Fatima', 'Ali', 'fatima.ali@railway.com', '0300-2222222', 'Agent', '2022-06-20'),
('Hassan', 'Mohammad', 'hassan.m@railway.com', '0300-3333333', 'Agent', '2023-02-10'),
('Zainab', 'Ahmed', 'zainab.ahmed@railway.com', '0300-4444444', 'Supervisor', '2021-11-05'),
('Ali', 'Hussain', 'ali.hussain@railway.com', '0300-5555555', 'Agent', '2023-03-15');

-- Insert Trains
INSERT INTO trains (train_name, train_number, train_type, total_capacity, total_coaches) VALUES
('Express One', 'EX-001', 'Express', 500, 10),
('Local Two', 'LC-002', 'Local', 300, 6),
('Luxury Premium', 'LX-003', 'Luxury', 200, 4),
('Fast Track', 'FT-004', 'Express', 450, 9),
('Comfort Plus', 'CP-005', 'Comfort', 350, 7);

-- Insert Coaches
INSERT INTO coaches (train_id, coach_number, coach_type, total_seats) VALUES
(1, 1, 'Standard', 50),
(1, 2, 'Standard', 50),
(1, 3, 'AC', 50),
(2, 1, 'Standard', 50),
(2, 2, 'Standard', 50),
(3, 1, 'Sleeper', 50),
(4, 1, 'Standard', 50),
(5, 1, 'AC', 50);

-- Insert Seats (simplified - just one coach example)
INSERT INTO seats (coach_id, seat_number, seat_class, seat_type) VALUES
(1, 1, 'Economy', 'Window'),
(1, 2, 'Economy', 'Aisle'),
(1, 3, 'Economy', 'Window'),
(1, 4, 'Economy', 'Aisle'),
(1, 5, 'Business', 'Window'),
(1, 6, 'Business', 'Aisle'),
(1, 7, 'Business', 'Window'),
(1, 8, 'Business', 'Aisle'),
(1, 9, 'Economy', 'Window'),
(1, 10, 'Economy', 'Aisle');

-- Insert Services
INSERT INTO services (service_name, service_description, cost) VALUES
('WiFi', 'High-speed internet service', 50),
('Catering', 'Food and beverage service', 200),
('Baggage', 'Luggage handling and storage', 100),
('Lounge Access', 'Premium lounge entry', 300),
('Parking', 'Station parking facility', 150);

-- Insert Amenities
INSERT INTO amenities (amenity_name, amenity_description, cost) VALUES
('Air Conditioning', 'Climate controlled compartments', 100),
('WiFi Service', 'Internet connectivity', 50),
('Dining Car', 'On-board restaurant service', 200),
('Power Outlets', 'USB and electrical outlets', 25),
('Entertainment', 'Movies, music, games', 75);

-- Insert Train Amenities (linking trains with amenities)
INSERT INTO train_amenities (train_id, amenity_id, last_maintenance_date) VALUES
(1, 1, '2024-04-01'),
(1, 2, '2024-04-05'),
(1, 3, '2024-04-10'),
(2, 1, '2024-03-20'),
(3, 2, '2024-04-08'),
(3, 4, '2024-03-15');

-- Insert Routes
INSERT INTO routes (train_id, source_station_id, destination_station_id, distance_km, estimated_duration_hours) VALUES
(1, 1, 2, 1300, 20),
(2, 1, 3, 1500, 24),
(3, 1, 4, 1400, 18),
(4, 2, 3, 400, 8),
(5, 2, 5, 500, 10);

-- Insert Schedules (sample for different dates)
INSERT INTO schedules (train_id, route_id, departure_date, departure_time, arrival_time, status) VALUES
(1, 1, '2024-05-01', '08:00:00', '04:00:00', 'Active'),
(1, 1, '2024-05-02', '08:00:00', '04:00:00', 'Active'),
(2, 2, '2024-05-01', '10:00:00', '10:00:00', 'Active'),
(3, 3, '2024-05-03', '14:00:00', '08:00:00', 'Active'),
(4, 4, '2024-05-05', '06:00:00', '02:00:00', 'Active');

-- Insert Passengers
INSERT INTO passengers (first_name, last_name, email, phone_number, date_of_birth, id_proof_type, id_proof_number) VALUES
('Muhammad', 'Hassan', 'mhasan@email.com', '0300-9000001', '1990-05-15', 'CNIC', '12345-6789012-3'),
('Ayesha', 'Malik', 'ayesha.malik@email.com', '0300-9000002', '1995-08-22', 'Passport', 'PAK123456'),
('Abdullah', 'Khan', 'abdullah.khan@email.com', '0300-9000003', '1988-03-10', 'CNIC', '98765-4321098-7'),
('Hira', 'Ahmed', 'hira.ahmed@email.com', '0300-9000004', '1992-11-30', 'CNIC', '55555-5555555-5'),
('Omar', 'Farooq', 'omar.farooq@email.com', '0300-9000005', '1999-07-18', 'Passport', 'PAK789012');

-- Insert Bookings (sample bookings for schedules)
INSERT INTO bookings (passenger_id, schedule_id, seat_id, booking_date, fare_amount, status) VALUES
(1, 1, 1, '2024-04-20', 2500, 'Confirmed'),
(2, 1, 2, '2024-04-21', 2500, 'Confirmed'),
(3, 2, 5, '2024-04-19', 3000, 'Pending'),
(4, 3, 6, '2024-04-22', 2800, 'Confirmed'),
(5, 4, 3, '2024-04-23', 2200, 'Confirmed');

-- Insert Payments (corresponding to bookings)
INSERT INTO payments (booking_id, payment_amount, payment_method, payment_date, status) VALUES
(1, 2500, 'Card', '2024-04-20', 'Completed'),
(2, 2500, 'Online', '2024-04-21', 'Completed'),
(3, 3000, 'Cash', '2024-04-21', 'Pending'),
(4, 2800, 'Card', '2024-04-22', 'Completed'),
(5, 2200, 'Online', '2024-04-23', 'Completed');

-- Insert Cancellations (sample cancellations)
INSERT INTO cancellations (booking_id, cancelled_by_staff_id, cancellation_date, reason, status) VALUES
(3, 2, '2024-04-24', 'Passenger changed plans', 'Processed');

-- Insert Station Services (linking stations with services)
INSERT INTO station_services (station_id, service_id) VALUES
(1, 1),
(1, 2),
(1, 4),
(2, 1),
(2, 3),
(3, 2),
(4, 1);
