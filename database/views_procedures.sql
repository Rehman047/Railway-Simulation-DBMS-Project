-- ============================================================
-- RAILWAY DBMS - ADVANCED POSTGRESQL FEATURES
-- Run after schema.sql and seed.sql
-- ============================================================

-- ============================================================
-- AUDIT TABLE (required by log_payment_changes trigger)
-- ============================================================

CREATE TABLE IF NOT EXISTS payment_audit_log (
    log_id      SERIAL PRIMARY KEY,
    payment_id  INTEGER     NOT NULL,
    old_status  VARCHAR(20),
    new_status  VARCHAR(20),
    changed_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    changed_by  TEXT        DEFAULT current_user
);


-- ============================================================
-- INDEXES
-- ============================================================

-- Passenger booking history with date-range filter
CREATE INDEX IF NOT EXISTS idx_bookings_passenger_date
    ON bookings(passenger_id, booking_date);

-- Schedule search by departure date + train
CREATE INDEX IF NOT EXISTS idx_schedules_date_train
    ON schedules(departure_date, train_id);

-- Pending refund report filtering
CREATE INDEX IF NOT EXISTS idx_cancellations_refund_status
    ON cancellations(refund_status);

-- Revenue queries filtered by payment status + date
CREATE INDEX IF NOT EXISTS idx_payments_status_date
    ON payments(payment_status, payment_date);


-- ============================================================
-- VIEWS
-- ============================================================

-- 1. passenger_complete_booking_info
--    Full join: passenger → booking → payment → schedule → stations
CREATE OR REPLACE VIEW passenger_complete_booking_info AS
SELECT
    p.passenger_id,
    p.first_name,
    p.last_name,
    p.email,
    p.phone_number,
    b.booking_id,
    b.booking_date,
    b.fare_amount,
    b.booking_status,
    py.payment_id,
    py.payment_amount,
    py.payment_method,
    py.payment_date,
    py.payment_status,
    s.schedule_id,
    s.departure_date,
    s.departure_time,
    s.arrival_time,
    s.schedule_status,
    t.train_name,
    t.train_number,
    st_src.station_name AS source_station,
    st_dst.station_name AS destination_station,
    se.seat_number,
    se.seat_class
FROM bookings b
JOIN passengers  p      ON b.passenger_id = p.passenger_id
JOIN schedules   s      ON b.schedule_id  = s.schedule_id
JOIN trains      t      ON s.train_id     = t.train_id
JOIN routes      r      ON s.route_id     = r.route_id
JOIN stations    st_src ON r.source_station_id      = st_src.station_id
JOIN stations    st_dst ON r.destination_station_id = st_dst.station_id
LEFT JOIN seats  se     ON b.seat_id      = se.seat_id
LEFT JOIN payments py   ON b.booking_id   = py.booking_id;


-- 2. revenue_by_route
CREATE OR REPLACE VIEW revenue_by_route AS
SELECT
    r.route_id,
    st_src.station_name                   AS source_station,
    st_dst.station_name                   AS destination_station,
    COUNT(DISTINCT b.booking_id)          AS total_bookings,
    COALESCE(SUM(py.payment_amount), 0)   AS total_revenue,
    COALESCE(AVG(py.payment_amount), 0)   AS avg_fare
FROM routes r
JOIN stations   st_src ON r.source_station_id      = st_src.station_id
JOIN stations   st_dst ON r.destination_station_id = st_dst.station_id
LEFT JOIN schedules s  ON r.route_id    = s.route_id
LEFT JOIN bookings  b  ON s.schedule_id = b.schedule_id
                       AND LOWER(b.booking_status) != 'cancelled'
LEFT JOIN payments  py ON b.booking_id  = py.booking_id
                       AND LOWER(py.payment_status) = 'completed'
GROUP BY r.route_id, st_src.station_name, st_dst.station_name
ORDER BY total_revenue DESC;


-- 3. train_occupancy_status
CREATE OR REPLACE VIEW train_occupancy_status AS
SELECT
    s.schedule_id,
    s.departure_date,
    t.train_id,
    t.train_name,
    t.train_number,
    t.capacity                                                     AS total_seats,
    COUNT(b.booking_id)                                            AS booked_seats,
    ROUND(COUNT(b.booking_id) * 100.0 / NULLIF(t.capacity, 0), 2) AS occupancy_percent
FROM schedules s
JOIN trains t ON s.train_id = t.train_id
LEFT JOIN bookings b ON s.schedule_id = b.schedule_id
                    AND LOWER(b.booking_status) NOT IN ('cancelled')
GROUP BY s.schedule_id, s.departure_date, t.train_id, t.train_name, t.train_number, t.capacity
ORDER BY s.departure_date DESC;


-- 4. pending_refunds_report
CREATE OR REPLACE VIEW pending_refunds_report AS
SELECT
    c.cancellation_id,
    c.booking_id,
    c.cancellation_date,
    c.cancellation_reason,
    c.refund_amount,
    c.refund_status,
    p.first_name,
    p.last_name,
    p.email,
    b.fare_amount,
    b.booking_status
FROM cancellations c
JOIN bookings   b ON c.booking_id   = b.booking_id
JOIN passengers p ON b.passenger_id = p.passenger_id
WHERE LOWER(c.refund_status) = 'pending'
  AND c.refund_amount IS NOT NULL
  AND c.refund_amount > 0
ORDER BY c.cancellation_date ASC;


-- ============================================================
-- FUNCTIONS
-- ============================================================

-- 1. calculate_fare(route_id, seat_class) → NUMERIC
--    Economy=1.0x  Business=1.5x  First/Luxury=2.0x  Base rate=2.5 PKR/km
CREATE OR REPLACE FUNCTION calculate_fare(
    p_route_id   INTEGER,
    p_seat_class TEXT
) RETURNS NUMERIC
LANGUAGE plpgsql AS $$
DECLARE
    v_distance   NUMERIC;
    v_multiplier NUMERIC;
BEGIN
    SELECT distance INTO v_distance FROM routes WHERE route_id = p_route_id;
    IF v_distance IS NULL THEN
        RAISE EXCEPTION 'Route % not found', p_route_id;
    END IF;
    v_multiplier := CASE LOWER(p_seat_class)
        WHEN 'economy'  THEN 1.0
        WHEN 'business' THEN 1.5
        WHEN 'first'    THEN 2.0
        WHEN 'luxury'   THEN 2.0
        ELSE 1.0
    END;
    RETURN ROUND(v_distance * 2.5 * v_multiplier, 2);
END;
$$;


-- 2. get_available_seats(schedule_id) → INTEGER
CREATE OR REPLACE FUNCTION get_available_seats(
    p_schedule_id INTEGER
) RETURNS INTEGER
LANGUAGE plpgsql AS $$
DECLARE
    v_capacity INTEGER;
    v_booked   INTEGER;
BEGIN
    SELECT t.capacity INTO v_capacity
    FROM schedules s
    JOIN trains t ON s.train_id = t.train_id
    WHERE s.schedule_id = p_schedule_id;

    IF v_capacity IS NULL THEN
        RAISE EXCEPTION 'Schedule % not found', p_schedule_id;
    END IF;

    SELECT COUNT(*) INTO v_booked
    FROM bookings
    WHERE schedule_id = p_schedule_id
      AND LOWER(booking_status) != 'cancelled';

    RETURN GREATEST(v_capacity - v_booked, 0);
END;
$$;


-- 3. calculate_refund_amount(fare, departure_ts) → NUMERIC
--    >24 h → 100%   12–24 h → 50%   <12 h → 0%
CREATE OR REPLACE FUNCTION calculate_refund_amount(
    p_fare         NUMERIC,
    p_departure_ts TIMESTAMP
) RETURNS NUMERIC
LANGUAGE plpgsql AS $$
DECLARE
    v_hours NUMERIC;
BEGIN
    v_hours := EXTRACT(EPOCH FROM (p_departure_ts - NOW())) / 3600.0;
    RETURN CASE
        WHEN v_hours > 24 THEN ROUND(p_fare, 2)
        WHEN v_hours > 12 THEN ROUND(p_fare * 0.5, 2)
        ELSE 0
    END;
END;
$$;


-- 4. validate_passenger_info(dob, id_proof_type, id_proof_number) → BOOLEAN
CREATE OR REPLACE FUNCTION validate_passenger_info(
    p_dob             DATE,
    p_id_proof_type   TEXT,
    p_id_proof_number TEXT
) RETURNS BOOLEAN
LANGUAGE plpgsql AS $$
DECLARE
    v_age INTEGER;
BEGIN
    v_age := DATE_PART('year', AGE(p_dob));
    IF v_age < 18 OR v_age > 120 THEN RETURN FALSE; END IF;

    IF UPPER(p_id_proof_type) = 'CNIC' THEN
        IF p_id_proof_number !~ '^\d{5}-\d{7}-\d$' THEN RETURN FALSE; END IF;
    ELSIF UPPER(p_id_proof_type) = 'PASSPORT' THEN
        IF p_id_proof_number IS NULL OR TRIM(p_id_proof_number) = '' THEN RETURN FALSE; END IF;
    END IF;

    RETURN TRUE;
END;
$$;


-- 5. get_passenger_booking_history(passenger_id) → TABLE
CREATE OR REPLACE FUNCTION get_passenger_booking_history(
    p_passenger_id INTEGER
)
RETURNS TABLE (
    booking_id          INTEGER,
    booking_date        TIMESTAMP,
    fare_amount         NUMERIC,
    booking_status      VARCHAR,
    train_name          VARCHAR,
    departure_date      DATE,
    departure_time      TIME,
    arrival_time        TIME,
    source_station      VARCHAR,
    destination_station VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.booking_id,
        b.booking_date,
        b.fare_amount,
        b.booking_status,
        t.train_name,
        s.departure_date,
        s.departure_time,
        s.arrival_time,
        st_src.station_name AS source_station,
        st_dst.station_name AS destination_station
    FROM bookings b
    JOIN schedules s     ON b.schedule_id = s.schedule_id
    JOIN trains    t     ON s.train_id    = t.train_id
    JOIN routes    r     ON s.route_id    = r.route_id
    JOIN stations st_src ON r.source_station_id      = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    WHERE b.passenger_id = p_passenger_id
    ORDER BY s.departure_date DESC;
END;
$$;


-- 6. available_trains_by_route(source_id, destination_id) → TABLE
--    Replaces the plain view since it needs two station parameters.
CREATE OR REPLACE FUNCTION available_trains_by_route(
    p_source_id      INTEGER,
    p_destination_id INTEGER
)
RETURNS TABLE (
    schedule_id         INTEGER,
    train_id            INTEGER,
    train_name          VARCHAR,
    train_number        VARCHAR,
    departure_date      DATE,
    departure_time      TIME,
    arrival_time        TIME,
    available_seats     INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.schedule_id,
        t.train_id,
        t.train_name,
        t.train_number,
        s.departure_date,
        s.departure_time,
        s.arrival_time,
        get_available_seats(s.schedule_id) AS available_seats
    FROM schedules s
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    WHERE r.source_station_id      = p_source_id
      AND r.destination_station_id = p_destination_id
      AND s.departure_date         >= CURRENT_DATE
      AND LOWER(s.schedule_status) != 'cancelled'
      AND get_available_seats(s.schedule_id) > 0
    ORDER BY s.departure_date, s.departure_time;
END;
$$;


-- ============================================================
-- STORED PROCEDURES
-- ============================================================

-- 1. add_booking
--    Validates seat, checks past-date, prevents double-booking, inserts booking.
--    The after_booking_insert trigger handles seat status update.
CREATE OR REPLACE PROCEDURE add_booking(
    p_passenger_id INTEGER,
    p_schedule_id  INTEGER,
    p_seat_id      INTEGER,
    p_fare_amount  NUMERIC,
    INOUT p_booking_id INTEGER DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    v_departure_date DATE;
    v_existing       INTEGER;
BEGIN
    SELECT departure_date INTO v_departure_date
    FROM schedules WHERE schedule_id = p_schedule_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Schedule % does not exist', p_schedule_id;
    END IF;
    IF v_departure_date < CURRENT_DATE THEN
        RAISE EXCEPTION 'Cannot book a past schedule (departure: %)', v_departure_date;
    END IF;

    PERFORM passenger_id FROM passengers WHERE passenger_id = p_passenger_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Passenger % does not exist', p_passenger_id;
    END IF;

    PERFORM seat_id FROM seats WHERE seat_id = p_seat_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Seat % does not exist', p_seat_id;
    END IF;

    SELECT booking_id INTO v_existing
    FROM bookings
    WHERE schedule_id = p_schedule_id
      AND seat_id     = p_seat_id
      AND LOWER(booking_status) != 'cancelled';
    IF FOUND THEN
        RAISE EXCEPTION 'Seat % is already booked for schedule %', p_seat_id, p_schedule_id;
    END IF;

    INSERT INTO bookings (passenger_id, schedule_id, seat_id, booking_date, fare_amount, booking_status)
    VALUES (p_passenger_id, p_schedule_id, p_seat_id, NOW(), p_fare_amount, 'pending')
    RETURNING booking_id INTO p_booking_id;
END;
$$;


-- 2. process_cancellation
--    Cancels booking, computes refund, releases seat, creates records.
CREATE OR REPLACE PROCEDURE process_cancellation(
    p_booking_id        INTEGER,
    p_staff_id          INTEGER,
    p_reason            TEXT,
    INOUT p_cancellation_id INTEGER DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    v_status         VARCHAR;
    v_fare           NUMERIC;
    v_seat_id        INTEGER;
    v_dep_date       DATE;
    v_dep_time       TIME;
    v_refund         NUMERIC;
BEGIN
    SELECT b.booking_status, b.fare_amount, b.seat_id, s.departure_date, s.departure_time
    INTO   v_status, v_fare, v_seat_id, v_dep_date, v_dep_time
    FROM   bookings b
    JOIN   schedules s ON b.schedule_id = s.schedule_id
    WHERE  b.booking_id = p_booking_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Booking % not found', p_booking_id;
    END IF;
    IF LOWER(v_status) = 'cancelled' THEN
        RAISE EXCEPTION 'Booking % is already cancelled', p_booking_id;
    END IF;

    v_refund := calculate_refund_amount(
        v_fare,
        (v_dep_date::TEXT || ' ' || v_dep_time::TEXT)::TIMESTAMP
    );

    INSERT INTO cancellations (
        booking_id, cancelled_by_staff_id, cancellation_date,
        cancellation_reason, refund_amount, refund_status
    )
    VALUES (
        p_booking_id, p_staff_id, NOW(), p_reason, v_refund,
        CASE WHEN v_refund > 0 THEN 'pending' ELSE 'not_applicable' END
    )
    RETURNING cancellation_id INTO p_cancellation_id;

    UPDATE bookings SET booking_status = 'Cancelled' WHERE booking_id = p_booking_id;
    UPDATE seats    SET availability   = 'available'  WHERE seat_id   = v_seat_id;

    IF v_refund > 0 THEN
        INSERT INTO payments (booking_id, payment_amount, payment_method, payment_date, payment_status)
        VALUES (p_booking_id, v_refund, 'Refund', NOW(), 'Pending');
    END IF;
END;
$$;


-- 3. generate_revenue_report(from_date, to_date) → TABLE
--    Implemented as a FUNCTION so callers can SELECT from it.
CREATE OR REPLACE FUNCTION generate_revenue_report(
    p_from_date DATE,
    p_to_date   DATE
)
RETURNS TABLE (
    route_id            INTEGER,
    source_station      VARCHAR,
    destination_station VARCHAR,
    train_name          VARCHAR,
    train_number        VARCHAR,
    report_date         DATE,
    total_bookings      BIGINT,
    total_revenue       NUMERIC
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.route_id,
        st_src.station_name          AS source_station,
        st_dst.station_name          AS destination_station,
        t.train_name,
        t.train_number,
        py.payment_date::DATE        AS report_date,
        COUNT(DISTINCT b.booking_id) AS total_bookings,
        COALESCE(SUM(py.payment_amount), 0) AS total_revenue
    FROM payments py
    JOIN bookings  b     ON py.booking_id  = b.booking_id
    JOIN schedules s     ON b.schedule_id  = s.schedule_id
    JOIN trains    t     ON s.train_id     = t.train_id
    JOIN routes    r     ON s.route_id     = r.route_id
    JOIN stations st_src ON r.source_station_id      = st_src.station_id
    JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
    WHERE py.payment_date::DATE BETWEEN p_from_date AND p_to_date
      AND LOWER(py.payment_status) = 'completed'
    GROUP BY r.route_id, st_src.station_name, st_dst.station_name,
             t.train_name, t.train_number, py.payment_date::DATE
    ORDER BY py.payment_date::DATE, total_revenue DESC;
END;
$$;


-- 4. update_seat_status(seat_id, new_status)
CREATE OR REPLACE PROCEDURE update_seat_status(
    p_seat_id    INTEGER,
    p_new_status VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_new_status NOT IN ('available', 'booked', 'maintenance') THEN
        RAISE EXCEPTION 'Invalid seat status: %. Must be available, booked, or maintenance', p_new_status;
    END IF;
    UPDATE seats SET availability = p_new_status WHERE seat_id = p_seat_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Seat % not found', p_seat_id;
    END IF;
END;
$$;


-- 5. check_train_availability(schedule_id)
CREATE OR REPLACE PROCEDURE check_train_availability(
    p_schedule_id   INTEGER,
    INOUT p_available INTEGER DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    p_available := get_available_seats(p_schedule_id);
END;
$$;


-- ============================================================
-- TRIGGER FUNCTIONS & TRIGGERS
-- ============================================================

-- ── Trigger 1: after_booking_insert ──────────────────────────
-- Sets seat to 'booked' whenever a new booking row is inserted.
CREATE OR REPLACE FUNCTION trg_after_booking_insert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    UPDATE seats SET availability = 'booked' WHERE seat_id = NEW.seat_id;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS after_booking_insert ON bookings;
CREATE TRIGGER after_booking_insert
    AFTER INSERT ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION trg_after_booking_insert();


-- ── Trigger 2: after_payment_complete ────────────────────────
-- Sets booking_status = 'Confirmed' when payment_status becomes 'Completed'.
CREATE OR REPLACE FUNCTION trg_after_payment_complete()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF LOWER(NEW.payment_status) = 'completed' AND
       (OLD IS NULL OR LOWER(OLD.payment_status) != 'completed') THEN
        UPDATE bookings SET booking_status = 'Confirmed' WHERE booking_id = NEW.booking_id;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS after_payment_complete ON payments;
CREATE TRIGGER after_payment_complete
    AFTER INSERT OR UPDATE OF payment_status ON payments
    FOR EACH ROW
    EXECUTE FUNCTION trg_after_payment_complete();


-- ── Trigger 3: before_cancellation_insert ────────────────────
-- Calculates and stamps refund_amount before the row is written.
CREATE OR REPLACE FUNCTION trg_before_cancellation_insert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_fare   NUMERIC;
    v_dep_ts TIMESTAMP;
BEGIN
    SELECT b.fare_amount,
           (s.departure_date::TEXT || ' ' || s.departure_time::TEXT)::TIMESTAMP
    INTO   v_fare, v_dep_ts
    FROM   bookings  b
    JOIN   schedules s ON b.schedule_id = s.schedule_id
    WHERE  b.booking_id = NEW.booking_id;

    IF FOUND THEN
        NEW.refund_amount := calculate_refund_amount(v_fare, v_dep_ts);
        NEW.refund_status := CASE WHEN NEW.refund_amount > 0 THEN 'pending' ELSE 'not_applicable' END;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS before_cancellation_insert ON cancellations;
CREATE TRIGGER before_cancellation_insert
    BEFORE INSERT ON cancellations
    FOR EACH ROW
    EXECUTE FUNCTION trg_before_cancellation_insert();


-- ── Trigger 4: before_booking_insert (past-date guard) ───────
-- Prevents booking for schedules whose departure date is in the past.
CREATE OR REPLACE FUNCTION trg_before_booking_insert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_dep_date DATE;
BEGIN
    SELECT departure_date INTO v_dep_date FROM schedules WHERE schedule_id = NEW.schedule_id;
    IF v_dep_date < CURRENT_DATE THEN
        RAISE EXCEPTION 'Cannot book schedule %: departure date % is in the past',
            NEW.schedule_id, v_dep_date;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS before_booking_insert ON bookings;
CREATE TRIGGER before_booking_insert
    BEFORE INSERT ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION trg_before_booking_insert();


-- ── Trigger 5: log_payment_changes ───────────────────────────
-- Creates an audit trail row whenever payment_status changes.
CREATE OR REPLACE FUNCTION trg_log_payment_changes()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.payment_status IS DISTINCT FROM NEW.payment_status THEN
        INSERT INTO payment_audit_log (payment_id, old_status, new_status)
        VALUES (NEW.payment_id, OLD.payment_status, NEW.payment_status);
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS log_payment_changes ON payments;
CREATE TRIGGER log_payment_changes
    AFTER UPDATE OF payment_status ON payments
    FOR EACH ROW
    EXECUTE FUNCTION trg_log_payment_changes();


-- ============================================================
-- CURSOR-BASED FUNCTION (for DBMS Demo)
-- Iterates all passengers using an explicit CURSOR and builds
-- per-passenger booking statistics row by row.
-- ============================================================

CREATE OR REPLACE FUNCTION cursor_passenger_booking_summary()
RETURNS TABLE (
    passenger_name    TEXT,
    email             VARCHAR,
    total_bookings    BIGINT,
    total_spent       NUMERIC,
    last_booking_date DATE
)
LANGUAGE plpgsql AS $$
DECLARE
    passenger_cursor CURSOR FOR
        SELECT passenger_id, first_name, last_name, email AS pemail
        FROM passengers
        ORDER BY passenger_id;
    rec          RECORD;
    v_bookings   BIGINT;
    v_spent      NUMERIC;
    v_last_date  DATE;
BEGIN
    OPEN passenger_cursor;
    LOOP
        FETCH passenger_cursor INTO rec;
        EXIT WHEN NOT FOUND;

        SELECT COUNT(*),
               COALESCE(SUM(fare_amount), 0),
               MAX(booking_date::DATE)
        INTO   v_bookings, v_spent, v_last_date
        FROM   bookings
        WHERE  passenger_id = rec.passenger_id;

        passenger_name    := rec.first_name || ' ' || rec.last_name;
        email             := rec.pemail;
        total_bookings    := v_bookings;
        total_spent       := v_spent;
        last_booking_date := v_last_date;
        RETURN NEXT;
    END LOOP;
    CLOSE passenger_cursor;
END;
$$;


-- ============================================================
-- SUBQUERY DEMO FUNCTION (for DBMS Demo)
-- Returns passengers who have spent more than the average
-- fare using a correlated subquery.
-- ============================================================

CREATE OR REPLACE FUNCTION subquery_high_value_passengers()
RETURNS TABLE (
    passenger_id   INTEGER,
    passenger_name TEXT,
    email          VARCHAR,
    total_bookings BIGINT,
    total_spent    NUMERIC,
    avg_all_fares  NUMERIC
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.passenger_id,
        (p.first_name || ' ' || p.last_name)::TEXT  AS passenger_name,
        p.email,
        (SELECT COUNT(*)
         FROM   bookings b
         WHERE  b.passenger_id = p.passenger_id)    AS total_bookings,
        (SELECT COALESCE(SUM(fare_amount), 0)
         FROM   bookings b
         WHERE  b.passenger_id = p.passenger_id)    AS total_spent,
        (SELECT ROUND(AVG(fare_amount), 2) FROM bookings) AS avg_all_fares
    FROM passengers p
    WHERE (
        SELECT COALESCE(SUM(fare_amount), 0)
        FROM   bookings b
        WHERE  b.passenger_id = p.passenger_id
    ) > (SELECT COALESCE(AVG(fare_amount), 0) FROM bookings)
    ORDER BY total_spent DESC;
END;
$$;
