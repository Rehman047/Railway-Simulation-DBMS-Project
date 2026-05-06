-- ============================================================
-- RAILWAY DBMS - TRANSACTION PATTERNS
-- This file documents and demonstrates how ACID transactions
-- are used throughout the system. Run examples individually
-- in a psql session against a seeded database.
-- ============================================================
--
-- Pattern overview:
--   T1  Booking Creation           (booking_service.py → create_booking)
--   T2  Payment Processing         (payment_service.py → record_payment)
--   T3  Booking Cancellation       (cancellation_service.py → create_cancellation)
--   T4  Schedule Cancellation      (schedule_service.py → cancel_schedule)
--   T5  Stored-Procedure Booking   (views_procedures.sql → add_booking)
--   T6  Stored-Procedure Cancel    (views_procedures.sql → process_cancellation)
-- ============================================================


-- ============================================================
-- T1: BOOKING CREATION
-- Atomically validates and creates a booking while locking the
-- seat row to prevent double-booking under concurrent load.
-- ============================================================

BEGIN;

    -- Lock the seat row FOR UPDATE so no other transaction can
    -- book the same seat until this transaction commits or rolls back.
    SELECT seat_id, availability
    FROM   seats
    WHERE  seat_id = 1          -- replace with target seat_id
    FOR UPDATE;

    -- Guard 1: seat must not already be booked on this schedule
    DO $$
    DECLARE
        v_conflict INTEGER;
    BEGIN
        SELECT booking_id INTO v_conflict
        FROM   bookings
        WHERE  schedule_id   = 1     -- replace with target schedule_id
          AND  seat_id       = 1     -- replace with target seat_id
          AND  LOWER(booking_status) != 'cancelled';

        IF v_conflict IS NOT NULL THEN
            RAISE EXCEPTION 'Seat is already booked (booking_id: %)', v_conflict;
        END IF;
    END;
    $$;

    -- Guard 2: schedule must not be in the past
    DO $$
    DECLARE
        v_dep_date DATE;
    BEGIN
        SELECT departure_date INTO v_dep_date
        FROM   schedules
        WHERE  schedule_id = 1;     -- replace with target schedule_id

        IF v_dep_date < CURRENT_DATE THEN
            RAISE EXCEPTION 'Cannot book past schedule (departure: %)', v_dep_date;
        END IF;
    END;
    $$;

    -- Insert booking (after_booking_insert trigger updates seat status)
    INSERT INTO bookings (passenger_id, schedule_id, seat_id, booking_date, fare_amount, booking_status)
    VALUES (1, 1, 1, NOW(), 2500.00, 'pending');  -- replace with real values

COMMIT;
-- On any exception PostgreSQL automatically rolls back the transaction.


-- ============================================================
-- T2: PAYMENT PROCESSING
-- Atomically records a payment and confirms the booking.
-- If either statement fails the entire transaction rolls back.
-- ============================================================

BEGIN;

    -- Insert payment record
    INSERT INTO payments (booking_id, payment_amount, payment_method, payment_date, payment_status)
    VALUES (1, 2500.00, 'Card', NOW(), 'Completed')  -- replace with real values
    RETURNING payment_id;

    -- Confirm booking (also handled by after_payment_complete trigger,
    -- but the application layer does it explicitly for safety)
    UPDATE bookings
    SET    booking_status = 'Confirmed'
    WHERE  booking_id = 1;  -- replace with real booking_id

COMMIT;


-- ============================================================
-- T3: BOOKING CANCELLATION WITH REFUND
-- Atomically cancels a booking, calculates the refund using the
-- calculate_refund_amount() function, releases the seat, and
-- creates a refund payment record when applicable.
-- ============================================================

BEGIN;

    -- Step 1: Collect booking details needed for refund calculation
    -- (done inside the DO block to keep everything in one transaction)
    DO $$
    DECLARE
        v_fare        NUMERIC;
        v_seat_id     INTEGER;
        v_dep_date    DATE;
        v_dep_time    TIME;
        v_dep_ts      TIMESTAMP;
        v_refund      NUMERIC;
        v_cancel_id   INTEGER;
        v_booking_id  CONSTANT INTEGER := 1;  -- replace with target booking_id
        v_staff_id    CONSTANT INTEGER := 1;  -- replace with staff_id
        v_reason      CONSTANT TEXT    := 'Passenger requested cancellation';
    BEGIN
        SELECT b.fare_amount, b.seat_id, s.departure_date, s.departure_time
        INTO   v_fare, v_seat_id, v_dep_date, v_dep_time
        FROM   bookings  b
        JOIN   schedules s ON b.schedule_id = s.schedule_id
        WHERE  b.booking_id = v_booking_id
        FOR UPDATE OF b;                 -- lock booking row

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Booking % not found', v_booking_id;
        END IF;

        v_dep_ts := (v_dep_date::TEXT || ' ' || v_dep_time::TEXT)::TIMESTAMP;
        v_refund  := calculate_refund_amount(v_fare, v_dep_ts);

        -- Step 2: Create cancellation record
        INSERT INTO cancellations (
            booking_id, cancelled_by_staff_id, cancellation_date,
            cancellation_reason, refund_amount, refund_status
        )
        VALUES (
            v_booking_id, v_staff_id, NOW(), v_reason, v_refund,
            CASE WHEN v_refund > 0 THEN 'pending' ELSE 'not_applicable' END
        )
        RETURNING cancellation_id INTO v_cancel_id;

        -- Step 3: Mark booking cancelled
        UPDATE bookings SET booking_status = 'Cancelled' WHERE booking_id = v_booking_id;

        -- Step 4: Release seat
        UPDATE seats SET availability = 'available' WHERE seat_id = v_seat_id;

        -- Step 5: Insert refund payment if applicable
        IF v_refund > 0 THEN
            INSERT INTO payments (booking_id, payment_amount, payment_method, payment_date, payment_status)
            VALUES (v_booking_id, v_refund, 'Refund', NOW(), 'Pending');
        END IF;

        RAISE NOTICE 'Cancellation % created. Refund: %', v_cancel_id, v_refund;
    END;
    $$;

COMMIT;


-- ============================================================
-- T4: SCHEDULE CANCELLATION (cascades to bookings)
-- Cancels a schedule and all active bookings under it in one
-- atomic operation, preventing partial state.
-- ============================================================

BEGIN;

    -- Mark all active bookings on this schedule as cancelled
    UPDATE bookings
    SET    booking_status = 'Cancelled'
    WHERE  schedule_id    = 1              -- replace with target schedule_id
      AND  LOWER(booking_status) NOT IN ('cancelled');

    -- Release all seats that were held by those bookings
    UPDATE seats
    SET    availability = 'available'
    WHERE  seat_id IN (
        SELECT seat_id FROM bookings WHERE schedule_id = 1
    );

    -- Mark the schedule itself as cancelled
    UPDATE schedules
    SET    schedule_status = 'cancelled'
    WHERE  schedule_id = 1;

COMMIT;


-- ============================================================
-- T5: USING THE add_booking STORED PROCEDURE
-- Demonstrates calling the procedure within an explicit
-- transaction so the caller can ROLLBACK if needed.
-- ============================================================

BEGIN;

    -- Declare an output variable and call the procedure
    DO $$
    DECLARE
        v_booking_id INTEGER;
    BEGIN
        CALL add_booking(
            p_passenger_id => 1,       -- replace with real IDs
            p_schedule_id  => 1,
            p_seat_id      => 2,
            p_fare_amount  => 2500.00,
            p_booking_id   => v_booking_id
        );
        RAISE NOTICE 'New booking_id: %', v_booking_id;
    END;
    $$;

COMMIT;


-- ============================================================
-- T6: USING THE process_cancellation STORED PROCEDURE
-- ============================================================

BEGIN;

    DO $$
    DECLARE
        v_cancel_id INTEGER;
    BEGIN
        CALL process_cancellation(
            p_booking_id        => 1,              -- replace with real booking_id
            p_staff_id          => 1,              -- replace with real staff_id
            p_reason            => 'Schedule conflict',
            p_cancellation_id   => v_cancel_id
        );
        RAISE NOTICE 'Cancellation created: %', v_cancel_id;
    END;
    $$;

COMMIT;


-- ============================================================
-- ISOLATION LEVEL REFERENCE
-- ============================================================
--
-- PostgreSQL default: READ COMMITTED
--   Each statement sees data committed before it began.
--   Suitable for T2 (payment) and T4 (schedule cancel).
--
-- REPEATABLE READ
--   Snapshot taken at transaction start; prevents non-repeatable reads.
--   Use for T1 (booking) to ensure seat availability check and insert
--   see the same state:
--
--       BEGIN ISOLATION LEVEL REPEATABLE READ;
--       ...booking logic...
--       COMMIT;
--
-- SERIALIZABLE
--   Full isolation; prevents phantom reads.
--   Recommended for high-concurrency booking scenarios:
--
--       BEGIN ISOLATION LEVEL SERIALIZABLE;
--       ...booking logic...
--       COMMIT;
--
-- The application uses psycopg2 with autocommit=False (default),
-- which means every Database.transaction() call runs under
-- READ COMMITTED unless the isolation level is set explicitly.
-- To upgrade, set it on the connection before the first statement:
--
--   conn.set_isolation_level(
--       psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ
--   )
-- ============================================================


-- ============================================================
-- SAVEPOINT PATTERN (partial rollback within a transaction)
-- Useful when one optional step failing should not abort all work.
-- ============================================================

BEGIN;

    INSERT INTO bookings (passenger_id, schedule_id, seat_id, booking_date, fare_amount, booking_status)
    VALUES (1, 1, 3, NOW(), 3000.00, 'pending');

    SAVEPOINT after_booking;

    -- Attempt optional audit action; if it fails, roll back only this part
    BEGIN
        INSERT INTO payment_audit_log (payment_id, old_status, new_status)
        VALUES (-1, NULL, 'pending');   -- intentionally invalid for demo
    EXCEPTION WHEN OTHERS THEN
        ROLLBACK TO SAVEPOINT after_booking;
        RAISE NOTICE 'Audit insert skipped: %', SQLERRM;
    END;

COMMIT;
