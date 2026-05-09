-- ============================================================
-- RAILWAY DBMS - AFTER INSERT BACKUP TRIGGERS
-- Copies every inserted row into the matching *_backup table
-- PostgreSQL version
-- ============================================================

-- Drop trigger function if it already exists
DROP FUNCTION IF EXISTS copy_to_backup() CASCADE;

-- Drop backup tables if they already exist
DROP TABLE IF EXISTS cancellations_backup CASCADE;
DROP TABLE IF EXISTS payments_backup CASCADE;
DROP TABLE IF EXISTS bookings_backup CASCADE;
DROP TABLE IF EXISTS schedules_backup CASCADE;
DROP TABLE IF EXISTS train_amenities_backup CASCADE;
DROP TABLE IF EXISTS station_services_backup CASCADE;
DROP TABLE IF EXISTS routes_backup CASCADE;
DROP TABLE IF EXISTS seats_backup CASCADE;
DROP TABLE IF EXISTS coaches_backup CASCADE;
DROP TABLE IF EXISTS trains_backup CASCADE;
DROP TABLE IF EXISTS amenities_backup CASCADE;
DROP TABLE IF EXISTS services_backup CASCADE;
DROP TABLE IF EXISTS staff_backup CASCADE;
DROP TABLE IF EXISTS passengers_backup CASCADE;
DROP TABLE IF EXISTS stations_backup CASCADE;

-- ============================================================
-- BACKUP TABLES
-- Same column structure as the original tables, but without FK constraints
-- ============================================================

CREATE TABLE stations_backup (LIKE stations INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE passengers_backup (LIKE passengers INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE services_backup (LIKE services INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE amenities_backup (LIKE amenities INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE staff_backup (LIKE staff INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE trains_backup (LIKE trains INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE coaches_backup (LIKE coaches INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE seats_backup (LIKE seats INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE routes_backup (LIKE routes INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE station_services_backup (LIKE station_services INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE train_amenities_backup (LIKE train_amenities INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE schedules_backup (LIKE schedules INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE bookings_backup (LIKE bookings INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE payments_backup (LIKE payments INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);
CREATE TABLE cancellations_backup (LIKE cancellations INCLUDING DEFAULTS INCLUDING IDENTITY INCLUDING GENERATED);

-- ============================================================
-- GENERIC TRIGGER FUNCTION
-- Inserts the NEW row into the corresponding backup table
-- ============================================================

CREATE OR REPLACE FUNCTION copy_to_backup()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('INSERT INTO %I_backup SELECT ($1).*', TG_TABLE_NAME)
    USING NEW;
    RETURN NEW;
END;
$$;

-- ============================================================
-- AFTER INSERT TRIGGERS
-- ============================================================

CREATE TRIGGER trg_stations_after_insert
AFTER INSERT ON stations
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_passengers_after_insert
AFTER INSERT ON passengers
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_services_after_insert
AFTER INSERT ON services
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_amenities_after_insert
AFTER INSERT ON amenities
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_staff_after_insert
AFTER INSERT ON staff
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_trains_after_insert
AFTER INSERT ON trains
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_coaches_after_insert
AFTER INSERT ON coaches
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_seats_after_insert
AFTER INSERT ON seats
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_routes_after_insert
AFTER INSERT ON routes
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_station_services_after_insert
AFTER INSERT ON station_services
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_train_amenities_after_insert
AFTER INSERT ON train_amenities
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_schedules_after_insert
AFTER INSERT ON schedules
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_bookings_after_insert
AFTER INSERT ON bookings
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_payments_after_insert
AFTER INSERT ON payments
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

CREATE TRIGGER trg_cancellations_after_insert
AFTER INSERT ON cancellations
FOR EACH ROW
EXECUTE FUNCTION copy_to_backup();

-- ============================================================
-- OPTIONAL TEST EXAMPLE
-- ============================================================
-- INSERT INTO stations (station_name, city, state, address, contact_number)
-- VALUES ('Central Station', 'Lahore', 'Punjab', 'Main Road', '123456789');
--
-- The inserted row will automatically be copied into stations_backup.
