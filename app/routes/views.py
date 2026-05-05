"""
Views Blueprint
Serves all HTML pages using render_template + real database data.
No JavaScript needed — data is injected server-side via Jinja2.
"""
from flask import Blueprint, render_template
from app.db import Database

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
