-- ============================================================
-- RAILWAY DBMS - INDEXES
-- Run after schema.sql. Safe to re-run (uses IF NOT EXISTS).
-- ============================================================


-- ============================================================
-- SECTION 1: PRIMARY LOOKUP INDEXES
-- ============================================================

-- Passengers: fast lookup by email and phone (already in schema.sql,
-- included here for completeness with IF NOT EXISTS guard)
CREATE INDEX IF NOT EXISTS idx_passengers_email
    ON passengers(email);

CREATE INDEX IF NOT EXISTS idx_passengers_phone
    ON passengers(phone_number);

-- Trains: lookup by train_number (unique but index speeds prefix searches)
CREATE INDEX IF NOT EXISTS idx_trains_number
    ON trains(train_number);

-- Trains: filter by status (active / inactive)
CREATE INDEX IF NOT EXISTS idx_trains_status
    ON trains(status);


-- ============================================================
-- SECTION 2: BOOKING INDEXES
-- ============================================================

-- Core booking lookups already in schema.sql — guarded duplicates:
CREATE INDEX IF NOT EXISTS idx_bookings_passenger
    ON bookings(passenger_id);

CREATE INDEX IF NOT EXISTS idx_bookings_schedule
    ON bookings(schedule_id);

CREATE INDEX IF NOT EXISTS idx_bookings_seat
    ON bookings(seat_id);

-- Booking status filter (Confirmed / Pending / Cancelled)
CREATE INDEX IF NOT EXISTS idx_bookings_status
    ON bookings(booking_status);

-- Composite: passenger booking history with date range
CREATE INDEX IF NOT EXISTS idx_bookings_passenger_date
    ON bookings(passenger_id, booking_date);

-- Composite: schedule + status for occupancy queries
CREATE INDEX IF NOT EXISTS idx_bookings_schedule_status
    ON bookings(schedule_id, booking_status);

-- Recent bookings (descending order for dashboard queries)
CREATE INDEX IF NOT EXISTS idx_bookings_date_desc
    ON bookings(booking_date DESC);


-- ============================================================
-- SECTION 3: SCHEDULE INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_schedules_train
    ON schedules(train_id);

CREATE INDEX IF NOT EXISTS idx_schedules_route
    ON schedules(route_id);

-- Date-based schedule search (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_schedules_date
    ON schedules(departure_date);

-- Composite: date + train for schedule search
CREATE INDEX IF NOT EXISTS idx_schedules_date_train
    ON schedules(departure_date, train_id);

-- Status filter (Active / Cancelled / Completed)
CREATE INDEX IF NOT EXISTS idx_schedules_status
    ON schedules(schedule_status);

-- Upcoming schedules only (partial index — far smaller than full table)
CREATE INDEX IF NOT EXISTS idx_schedules_upcoming
    ON schedules(departure_date)
    WHERE schedule_status NOT IN ('cancelled', 'Cancelled');


-- ============================================================
-- SECTION 4: PAYMENT INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_payments_booking
    ON payments(booking_id);

-- Payment status filter
CREATE INDEX IF NOT EXISTS idx_payments_status
    ON payments(payment_status);

-- Date range queries for revenue reports
CREATE INDEX IF NOT EXISTS idx_payments_date
    ON payments(payment_date);

-- Composite: status + date (revenue summary with status filter)
CREATE INDEX IF NOT EXISTS idx_payments_status_date
    ON payments(payment_status, payment_date);

-- Payment method breakdown queries
CREATE INDEX IF NOT EXISTS idx_payments_method
    ON payments(payment_method);


-- ============================================================
-- SECTION 5: CANCELLATION INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_cancellations_booking
    ON cancellations(booking_id);

-- Staff performance queries
CREATE INDEX IF NOT EXISTS idx_cancellations_staff
    ON cancellations(cancelled_by_staff_id);

-- Refund status (pending_refunds_report view)
CREATE INDEX IF NOT EXISTS idx_cancellations_refund_status
    ON cancellations(refund_status);

-- Date range for cancellation statistics
CREATE INDEX IF NOT EXISTS idx_cancellations_date
    ON cancellations(cancellation_date);

-- Partial index: only pending refunds (very selective, tiny index)
CREATE INDEX IF NOT EXISTS idx_cancellations_pending_refunds
    ON cancellations(cancellation_date)
    WHERE LOWER(refund_status) = 'pending';


-- ============================================================
-- SECTION 6: ROUTE & COACH INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_routes_train
    ON routes(train_id);

-- Route lookup by station pair (available_trains_by_route function)
CREATE INDEX IF NOT EXISTS idx_routes_source_dest
    ON routes(source_station_id, destination_station_id);

-- Coach lookup by train
CREATE INDEX IF NOT EXISTS idx_coaches_train
    ON coaches(train_id);

-- Coach type filter
CREATE INDEX IF NOT EXISTS idx_coaches_type
    ON coaches(train_id, coach_type);

-- Seat lookup by coach
CREATE INDEX IF NOT EXISTS idx_seats_coach
    ON seats(coach_id);

-- Seat availability filter (get_available_seats function)
CREATE INDEX IF NOT EXISTS idx_seats_availability
    ON seats(availability);

-- Composite: coach + availability (most common seat query)
CREATE INDEX IF NOT EXISTS idx_seats_coach_availability
    ON seats(coach_id, availability);


-- ============================================================
-- SECTION 7: AUDIT LOG INDEX
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_payment_audit_payment
    ON payment_audit_log(payment_id);

CREATE INDEX IF NOT EXISTS idx_payment_audit_changed_at
    ON payment_audit_log(changed_at DESC);
