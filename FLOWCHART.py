"""
Flowchart generation - creating visual representation of booking flow
"""

FLOWCHART_CONTENT = '''
RAILWAY BOOKING SYSTEM - FLOWCHART
===================================

┌─────────────────────────────────────────────────────────────────────────────┐
│                          PASSENGER BOOKING FLOW                             │
└─────────────────────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌─────────────────────────┐
│ User Login/Register     │
│ (Passenger/Agent)       │
└────────────┬────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Search for Routes                  │
│ (Source, Destination, Date)        │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Query Database Views:              │
│ available_trains_by_route()        │
│ Returns: List of trains/schedules  │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Display Available Options          │
│ (Trains, Fare, Available Seats)    │
└────────────┬───────────────────────┘
             │
        No   │   Yes
    ┌────────┴────────┐
    │                 ▼
    ▼        ┌──────────────────────┐
  [EXIT]     │ User Selects Train   │
             │ & Seats              │
             └────────┬─────────────┘
                      │
                      ▼
             ┌──────────────────────┐
             │ Calculate Fare       │
             │ Function:            │
             │ calculate_fare()     │
             │ (route, seat_class)  │
             └────────┬─────────────┘
                      │
                      ▼
             ┌──────────────────────┐
             │ Display Fare Summary │
             │ & Confirm Booking    │
             └────────┬─────────────┘
                      │
                 No   │   Yes
            ┌─────────┴──────────┐
            │                    ▼
            ▼         ┌────────────────────┐
          [BACK]      │ Passenger Confirms │
                      │ Booking            │
                      └────────┬───────────┘
                               │
                               ▼
                      ┌────────────────────┐
                      │ Call Stored Proc:  │
                      │ add_booking()      │
                      │ (passenger_id,     │
                      │  schedule_id,      │
                      │  seat_id,          │
                      │  fare_amount)      │
                      └────────┬───────────┘
                               │
                               ▼
                      ┌────────────────────┐
                      │ Trigger Fires:     │
                      │ after_booking_     │
                      │ insert             │
                      │ - Updates seat     │
                      │   status to        │
                      │   "booked"         │
                      └────────┬───────────┘
                               │
                               ▼
                      ┌────────────────────┐
                      │ Booking Created    │
                      │ Status: PENDING    │
                      └────────┬───────────┘
                               │
                               ▼
                      ┌────────────────────┐
                      │ Process Payment    │
                      │ (Cash/Card/Online) │
                      └────────┬───────────┘
                               │
                        Paid   │   Not Paid
                    ┌──────────┴──────────┐
                    │                     ▼
                    ▼         ┌────────────────────┐
           ┌────────────────┐ │ Payment Failed     │
           │ INSERT Payment │ │ Send Notification │
           │ status:        │ │ Booking Expired   │
           │ COMPLETED      │ └────────────────────┘
           └────────┬───────┘
                    │
                    ▼
           ┌────────────────────┐
           │ Trigger Fires:     │
           │ after_payment_     │
           │ complete           │
           │ - Updates booking  │
           │   status to        │
           │   "confirmed"      │
           │ - Sends confirmation
           │   email            │
           └────────┬───────────┘
                    │
                    ▼
           ┌────────────────────┐
           │ Generate Ticket    │
           │ Send to Email      │
           └────────┬───────────┘
                    │
                    ▼
           ┌────────────────────┐
           │ Display Ticket &   │
           │ Booking Confirmed  │
           └────────┬───────────┘
                    │
                    ▼
                  [END]


┌─────────────────────────────────────────────────────────────────────────────┐
│                        CANCELLATION FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

START (User requests cancellation)
  │
  ▼
┌─────────────────────────┐
│ Select Booking to       │
│ Cancel                  │
└────────────┬────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Check Days Until Departure         │
│ (Using Triggers)                   │
└────────────┬───────────────────────┘
             │
     Days<2? │ Days>=2?
  ┌──────────┴──────────┐
  ▼                     ▼
No Refund        ┌─────────────────┐
[ALLOWED]        │ Calculate Refund│
  │              │ (80-100%)       │
  │              └────────┬────────┘
  │                       │
  │              ┌────────▼────────┐
  │              │ Call Stored     │
  │              │ Procedure:      │
  │              │ process_        │
  │              │ cancellation()  │
  │              └────────┬────────┘
  │                       │
  │              ┌────────▼────────┐
  │              │ Trigger Fires:  │
  │              │ before_         │
  │              │ cancellation_   │
  │              │ insert          │
  │              │ Validates data  │
  │              └────────┬────────┘
  │                       │
  │              ┌────────▼────────┐
  │              │ Create          │
  │              │ Cancellation    │
  │              │ Record          │
  │              └────────┬────────┘
  │                       │
  │              ┌────────▼────────┐
  │              │ Release Seat    │
  │              │ (Mark as        │
  │              │ available)      │
  │              └────────┬────────┘
  │                       │
  │              ┌────────▼────────┐
  │              │ Process Refund  │
  │              │ (if eligible)   │
  │              └────────┬────────┘
  │                       │
  └───────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ Update Status: │
        │ CANCELLED      │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │ Send SMS/Email │
        │ Confirmation   │
        └────────┬───────┘
                 │
                 ▼
               [END]


┌─────────────────────────────────────────────────────────────────────────────┐
│                      ANALYTICS QUERY FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

START (Admin views analytics)
  │
  ▼
┌──────────────────────┐
│ Select Date Range    │
└────────────┬─────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Query Views:                     │
│ - passenger_revenue_analysis     │
│ - train_occupancy_status         │
│ - pending_refunds_report         │
│ - route_performance_metrics      │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Views Execute SQL WITH JOINS:    │
│ - passengers JOIN bookings       │
│ - bookings JOIN schedules        │
│ - schedules JOIN trains          │
│ - schedules JOIN routes          │
│ - routes JOIN stations           │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Aggregate Data:                  │
│ - Total Revenue                  │
│ - Occupancy %                    │
│ - Refund Pending                 │
│ - Popular Routes                 │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Use INDEX:                       │
│ idx_payments_status_date         │
│ idx_schedules_date_train         │
│ idx_cancellations_refund_status  │
│ idx_bookings_passenger_date      │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Return Results to Dashboard      │
│ Display Charts & Tables          │
└────────────┬─────────────────────┘
             │
             ▼
               [END]


┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

                          FRONTEND
                      (Flask Templates)
                              │
                              ▼
                    ┌─────────────────┐
                    │  Flask Routes   │
                    │  (API Endpoints)│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Services Layer │
                    │  (Business Logic│
                    │   Validation)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Query Objects  │
                    │  (SQL Queries)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Database Layer  │
                    │ Connection Pool │
                    │  (psycopg2)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │   PostgreSQL DBMS    │
                    │  ┌────────────────┐  │
                    │  │ TABLES (20+)   │  │
                    │  │ VIEWS (4)      │  │
                    │  │ FUNCTIONS (12) │  │
                    │  │ PROCEDURES (4) │  │
                    │  │ TRIGGERS (5)   │  │
                    │  │ INDEXES (4)    │  │
                    │  └────────────────┘  │
                    └──────────┬───────────┘
                               │
                               ├─────────────────────┐
                               │                     │
                               ▼                     ▼
                    ┌──────────────────┐  ┌──────────────────┐
                    │  Firebase/Cloud  │  │  Local Storage   │
                    │  Backup Service  │  │  (Images, Files) │
                    └──────────────────┘  └──────────────────┘


TRANSACTION EXAMPLE (Booking Process)
=====================================

BEGIN TRANSACTION
  ├─ Check seat availability ──────────────────────────── SELECT
  ├─ Validate passenger exists ──────────────────────── SELECT
  ├─ Insert booking record ──────────────────────────── INSERT
  │   └─ TRIGGER: after_booking_insert fires
  │       └─ Updates seat status to "booked"
  ├─ Process payment ────────────────────────────────── INSERT
  │   └─ TRIGGER: after_payment_complete fires
  │       └─ Updates booking status to "confirmed"
  └─ Send confirmation email ──────────────────────── APPLICATION LOGIC
  
COMMIT (All operations succeed)
OR
ROLLBACK (Any operation fails - entire transaction reverted)


QUERY EXECUTION FLOW WITH INDEXES
==================================

1. Get Available Trains for Route (uses idx_schedules_date_train)
   SELECT s.*, t.*, COUNT(b.booking_id) as booked_seats
   FROM schedules s
   JOIN trains t ON s.train_id = t.train_id
   LEFT JOIN bookings b ON s.schedule_id = b.schedule_id
   WHERE s.departure_date = ? AND s.route_id = ?
   │
   └─ INDEX USED: idx_schedules_date_train (Fast retrieval)

2. Get Passenger Booking History (uses idx_bookings_passenger_date)
   SELECT b.*, s.*, t.*, p.*
   FROM bookings b
   JOIN schedules s ON b.schedule_id = s.schedule_id
   JOIN trains t ON s.train_id = t.train_id
   JOIN passengers p ON b.passenger_id = p.passenger_id
   WHERE b.passenger_id = ? AND b.booking_date >= ?
   │
   └─ INDEX USED: idx_bookings_passenger_date (Fast filtering)

3. Get Revenue Report (uses idx_payments_status_date)
   SELECT SUM(p.payment_amount), COUNT(*)
   FROM payments p
   WHERE p.payment_status = 'completed' AND p.payment_date >= ?
   │
   └─ INDEX USED: idx_payments_status_date (Aggregate query)

4. Get Pending Refunds (uses idx_cancellations_refund_status)
   SELECT c.*, b.*, p.*
   FROM cancellations c
   JOIN bookings b ON c.booking_id = b.booking_id
   JOIN passengers p ON b.passenger_id = p.passenger_id
   WHERE c.refund_status = 'pending'
   │
   └─ INDEX USED: idx_cancellations_refund_status (Fast filtering)
'''

print(FLOWCHART_CONTENT)
