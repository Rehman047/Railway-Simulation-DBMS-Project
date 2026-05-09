"""
Views Blueprint
Serves all HTML pages using render_template + real database data.
No JavaScript needed — data is injected server-side via Jinja2.
"""
from flask import Blueprint, render_template
from app.db import Database
from app.services.firebase_client import FirebaseClient


views_bp = Blueprint('views', __name__)


# ── Dashboard ────────────────────────────────────────────────────

@views_bp.route('/')
def dashboard():
    """Main dashboard with live summary stats."""

    # Summary counts
    summary = {
        'total_trains': Database.fetch_scalar("SELECT COUNT(*) FROM trains"),
        'total_stations': Database.fetch_scalar("SELECT COUNT(*) FROM stations"),
        'total_passengers': Database.fetch_scalar("SELECT COUNT(*) FROM passengers"),
        'total_bookings': Database.fetch_scalar("SELECT COUNT(*) FROM bookings"),
        'confirmed_bookings': Database.fetch_scalar(
            "SELECT COUNT(*) FROM bookings WHERE LOWER(booking_status) = 'confirmed'"
        ),
        'cancelled_bookings': Database.fetch_scalar(
            "SELECT COUNT(*) FROM bookings WHERE LOWER(booking_status) = 'cancelled'"
        ),
        'pending_payments': Database.fetch_scalar(
            "SELECT COUNT(*) FROM bookings WHERE LOWER(booking_status) = 'pending'"
        ),
        'active_schedules': Database.fetch_scalar(
            "SELECT COUNT(*) FROM schedules WHERE LOWER(schedule_status) IN ('active', 'scheduled')"
        ),
    }

    # Recent 10 bookings with passenger and route info
    recent_bookings = Database.fetch_all("""
        SELECT b.booking_id,
               p.first_name, p.last_name,
               s.departure_date, s.departure_time,
               st_src.station_name AS source_station,
               st_dst.station_name AS destination_station,
               b.fare_amount,
               b.booking_status
        FROM bookings b
        JOIN passengers p  ON b.passenger_id = p.passenger_id
        JOIN schedules  s  ON b.schedule_id  = s.schedule_id
        JOIN routes     r  ON s.route_id     = r.route_id
        JOIN stations st_src ON r.source_station_id      = st_src.station_id
        JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
        ORDER BY b.booking_id DESC
        LIMIT 10
    """)

    # Top 5 routes by booking count
    top_routes = Database.fetch_all("""
        SELECT st_src.station_name AS source_station,
               st_dst.station_name AS destination_station,
               COUNT(b.booking_id)   AS total_bookings,
               COALESCE(SUM(b.fare_amount), 0) AS total_revenue
        FROM routes r
        JOIN stations st_src ON r.source_station_id      = st_src.station_id
        JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
        LEFT JOIN schedules s ON r.route_id     = s.route_id
        LEFT JOIN bookings  b ON s.schedule_id  = b.schedule_id
        GROUP BY st_src.station_name, st_dst.station_name
        ORDER BY total_bookings DESC
        LIMIT 5
    """)

    return render_template(
        'dashboard.html',
        summary=summary,
        recent_bookings=recent_bookings,
        top_routes=top_routes,
    )


# ── Trains ───────────────────────────────────────────────────────

@views_bp.route('/trains')
def trains():
    """List all trains."""
    trains_list = Database.fetch_all(
        "SELECT * FROM trains ORDER BY train_id"
    )
    return render_template('trains.html', trains=trains_list)


# ── Stations ─────────────────────────────────────────────────────

@views_bp.route('/stations')
def stations():
    """List all stations."""
    stations_list = Database.fetch_all(
        "SELECT * FROM stations ORDER BY station_id"
    )
    return render_template('stations.html', stations=stations_list)


# ── Routes ───────────────────────────────────────────────────────

@views_bp.route('/routes')
def routes():
    """List all routes with train and station info."""
    routes_list = Database.fetch_all("""
        SELECT r.route_id,
               r.train_id,
               r.distance,
               r.estimated_duration,
               r.created_at,
               t.train_name, t.train_number, t.train_type,
               st_src.station_id AS source_station_id,
               st_src.station_name AS source_station,
               st_src.city AS source_city,
               st_dst.station_id AS destination_station_id,
               st_dst.station_name AS destination_station,
               st_dst.city AS destination_city
        FROM routes r
        JOIN trains t ON r.train_id = t.train_id
        JOIN stations st_src ON r.source_station_id = st_src.station_id
        JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
        ORDER BY r.route_id
    """)
    return render_template('routes.html', routes=routes_list)


# ── Schedules ────────────────────────────────────────────────────

@views_bp.route('/schedules')
def schedules():
    """List all schedules with train and route info."""
    schedules_list = Database.fetch_all("""
        SELECT s.schedule_id,
               s.departure_date, s.departure_time, s.arrival_time,
               s.schedule_status,
               t.train_name, t.train_number,
               st_src.station_name AS source_station,
               st_dst.station_name AS destination_station
        FROM schedules s
        JOIN trains   t    ON s.train_id = t.train_id
        JOIN routes   r    ON s.route_id = r.route_id
        JOIN stations st_src ON r.source_station_id      = st_src.station_id
        JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
        ORDER BY s.departure_date DESC, s.departure_time
    """)
    return render_template('schedules.html', schedules=schedules_list)


# ── Passengers ───────────────────────────────────────────────────

@views_bp.route('/passengers')
def passengers():
    """List all registered passengers."""
    passengers_list = Database.fetch_all(
        "SELECT * FROM passengers ORDER BY passenger_id"
    )
    return render_template('passengers.html', passengers=passengers_list)


# ── Bookings ─────────────────────────────────────────────────────

@views_bp.route('/bookings')
def bookings():
    """List all bookings with passenger, seat, and route info."""
    bookings_list = Database.fetch_all("""
        SELECT b.booking_id,
               p.first_name, p.last_name,
               s.departure_date,
               st_src.station_name AS source_station,
               st_dst.station_name AS destination_station,
               se.seat_number,
               b.fare_amount,
               b.booking_status
        FROM bookings b
        JOIN passengers p    ON b.passenger_id = p.passenger_id
        JOIN schedules  s    ON b.schedule_id  = s.schedule_id
        JOIN routes     r    ON s.route_id     = r.route_id
        JOIN stations st_src ON r.source_station_id      = st_src.station_id
        JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
        LEFT JOIN seats se   ON b.seat_id      = se.seat_id
        ORDER BY b.booking_id DESC
    """)
    return render_template('bookings.html', bookings=bookings_list)


# ── DBMS Features Demo ───────────────────────────────────────────

@views_bp.route('/demo')
def demo():
    """
    DBMS Features Demonstration page.
    Queries each advanced database feature and passes results to the template.
    """

    # 1. VIEWS ─────────────────────────────────────────────────
    occupancy_view = Database.fetch_all(
        "SELECT * FROM train_occupancy_status LIMIT 10"
    )
    revenue_view = Database.fetch_all(
        "SELECT * FROM revenue_by_route LIMIT 10"
    )
    pending_refunds_view = Database.fetch_all(
        "SELECT * FROM pending_refunds_report LIMIT 10"
    )

    # 2. SQL FUNCTIONS ─────────────────────────────────────────
    # calculate_fare — pick first route and compute fares per class
    fare_demos = []
    first_route = Database.fetch_one("SELECT route_id FROM routes LIMIT 1")
    if first_route:
        rid = first_route['route_id']
        for cls in ['economy', 'business', 'first']:
            row = Database.fetch_one(
                "SELECT calculate_fare(%s, %s) AS fare", (rid, cls)
            )
            fare_demos.append({'seat_class': cls, 'fare': row['fare'] if row else 0})

    # get_available_seats — first active schedule
    avail_demo = None
    first_sched = Database.fetch_one(
        "SELECT schedule_id FROM schedules WHERE LOWER(schedule_status) != 'cancelled' LIMIT 1"
    )
    if first_sched:
        row = Database.fetch_one(
            "SELECT get_available_seats(%s) AS available", (first_sched['schedule_id'],)
        )
        avail_demo = {'schedule_id': first_sched['schedule_id'],
                      'available_seats': row['available'] if row else 0}

    # validate_passenger_info — demo call
    validate_demo = Database.fetch_one(
        "SELECT validate_passenger_info('1990-01-01'::DATE, 'CNIC', '12345-6789012-3') AS is_valid"
    )

    # 3. STORED PROCEDURES ─────────────────────────────────────
    # generate_revenue_report — call the function version
    revenue_report = Database.fetch_all(
        "SELECT * FROM generate_revenue_report('2000-01-01', '2099-12-31') LIMIT 10"
    )

    # check_train_availability — via get_available_seats wrapper
    avail_report = []
    schedules_sample = Database.fetch_all(
        """SELECT s.schedule_id, t.train_name, s.departure_date
           FROM schedules s JOIN trains t ON s.train_id = t.train_id
           WHERE LOWER(s.schedule_status) != 'cancelled'
           ORDER BY s.departure_date LIMIT 5"""
    )
    for s in schedules_sample:
        row = Database.fetch_one(
            "SELECT get_available_seats(%s) AS seats", (s['schedule_id'],)
        )
        avail_report.append({
            'schedule_id': s['schedule_id'],
            'train_name': s['train_name'],
            'departure_date': s['departure_date'],
            'available_seats': row['seats'] if row else 0,
        })

    # 4. CURSOR-BASED FUNCTION ─────────────────────────────────
    cursor_results = Database.fetch_all(
        "SELECT * FROM cursor_passenger_booking_summary() LIMIT 10"
    )

    # 5. SUBQUERIES ────────────────────────────────────────────
    subquery_results = Database.fetch_all(
        "SELECT * FROM subquery_high_value_passengers() LIMIT 10"
    )
    # Also show inline subquery: top routes by booking count (used in dashboard too)
    top_routes_subquery = Database.fetch_all("""
        SELECT
            st_src.station_name AS source_station,
            st_dst.station_name AS destination_station,
            COUNT(b.booking_id) AS total_bookings,
            (SELECT COUNT(*) FROM bookings WHERE booking_status = 'Cancelled'
               AND schedule_id IN (SELECT schedule_id FROM schedules WHERE route_id = r.route_id)
            ) AS cancelled_bookings
        FROM routes r
        JOIN stations st_src ON r.source_station_id      = st_src.station_id
        JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
        LEFT JOIN schedules s ON r.route_id    = s.route_id
        LEFT JOIN bookings  b ON s.schedule_id = b.schedule_id
        GROUP BY r.route_id, st_src.station_name, st_dst.station_name
        ORDER BY total_bookings DESC
        LIMIT 8
    """)

    # 6. COMPLEX JOINS ─────────────────────────────────────────
    join_results = Database.fetch_all("""
        SELECT
            b.booking_id,
            p.first_name || ' ' || p.last_name      AS passenger_name,
            p.email,
            t.train_name,
            t.train_number,
            se.seat_number,
            se.seat_class,
            st_src.station_name                      AS from_station,
            st_dst.station_name                      AS to_station,
            s.departure_date,
            s.departure_time,
            b.fare_amount,
            b.booking_status,
            py.payment_status
        FROM bookings b
        JOIN passengers  p      ON b.passenger_id = p.passenger_id
        JOIN schedules   s      ON b.schedule_id  = s.schedule_id
        JOIN trains      t      ON s.train_id     = t.train_id
        JOIN routes      r      ON s.route_id     = r.route_id
        JOIN stations    st_src ON r.source_station_id      = st_src.station_id
        JOIN stations    st_dst ON r.destination_station_id = st_dst.station_id
        LEFT JOIN seats  se     ON b.seat_id      = se.seat_id
        LEFT JOIN payments py   ON b.booking_id   = py.booking_id
        ORDER BY b.booking_id DESC
        LIMIT 10
    """)

    # 7. TRIGGERS ──────────────────────────────────────────────
    # Show payment audit log (populated by log_payment_changes trigger)
    audit_log = Database.fetch_all(
        "SELECT * FROM payment_audit_log ORDER BY changed_at DESC LIMIT 10"
    )
    # List all triggers in the database for display
    triggers_list = Database.fetch_all("""
        SELECT trigger_name, event_manipulation, event_object_table,
               action_timing, action_statement
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        ORDER BY event_object_table, trigger_name
    """)

    # 8. INDEXES ───────────────────────────────────────────────
    indexes_list = Database.fetch_all("""
        SELECT indexname, tablename, indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND tablename NOT IN ('spatial_ref_sys')
        ORDER BY tablename, indexname
    """)

    # 9. TRANSACTIONS ──────────────────────────────────────────
    # Show recent bookings as evidence of transaction execution
    recent_transactions = Database.fetch_all("""
        SELECT
            b.booking_id,
            b.booking_date,
            p.first_name || ' ' || p.last_name AS passenger_name,
            b.fare_amount,
            b.booking_status,
            py.payment_status,
            py.payment_method
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.passenger_id
        LEFT JOIN payments py ON b.booking_id = py.booking_id
        ORDER BY b.booking_id DESC
        LIMIT 10
    """)

    return render_template(
        'demo.html',
        # Views
        occupancy_view=occupancy_view,
        revenue_view=revenue_view,
        pending_refunds_view=pending_refunds_view,
        # Functions
        fare_demos=fare_demos,
        avail_demo=avail_demo,
        validate_demo=validate_demo,
        # Stored Procedures
        revenue_report=revenue_report,
        avail_report=avail_report,
        # Cursor
        cursor_results=cursor_results,
        # Subqueries
        subquery_results=subquery_results,
        top_routes_subquery=top_routes_subquery,
        # Joins
        join_results=join_results,
        # Triggers
        audit_log=audit_log,
        triggers_list=triggers_list,
        # Indexes
        indexes_list=indexes_list,
        # Transactions
        recent_transactions=recent_transactions,
    )
