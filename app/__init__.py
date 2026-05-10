"""
Flask Application Factory
Initializes the Flask app with configuration and routes
"""
import os
from flask import Flask
from app.config import get_config
from app.db import DatabaseConnection
from app.services.error_handler import register_error_handlers
from app.services.file_storage_service import FileStorageService
from app.services.firebase_client import FirebaseClient

# Absolute path to the /database folder at project root
_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')


def _split_sql(sql: str):
    """
    Split a SQL script into individual statements.
    Uses character-by-character scanning so PostgreSQL
    $$ dollar-quoted blocks (used by PL/pgSQL functions)
    are never broken mid-body on an inner semicolon.
    """
    statements = []
    buf = []
    i = 0
    in_dollar_quote = False

    while i < len(sql):
        # Detect $$ marker
        if sql[i:i+2] == '$$':
            in_dollar_quote = not in_dollar_quote
            buf.append('$$')
            i += 2
            continue

        # Semicolon outside dollar-quote = end of statement
        if sql[i] == ';' and not in_dollar_quote:
            buf.append(';')
            stmt = ''.join(buf).strip()
            if stmt and stmt != ';':
                statements.append(stmt)
            buf = []
            i += 1
            continue

        buf.append(sql[i])
        i += 1

    # Flush any trailing non-semicolon content
    remaining = ''.join(buf).strip()
    if remaining:
        statements.append(remaining)

    return statements


def _apply_startup_sql(filepath: str) -> None:
    """
    Execute a SQL file against the database at application startup.
    Failures are logged as warnings and never crash the server.
    """
    if not os.path.exists(filepath):
        print(f"[SQL] Skipping (not found): {filepath}")
        return

    try:
        # Force pool initialisation so get_connection() works
        DatabaseConnection.init_pool()
        conn = DatabaseConnection.get_connection()
    except Exception as e:
        print(f"[SQL] Cannot connect to DB — skipping {os.path.basename(filepath)}: {e}")
        return

    try:
        conn.autocommit = True          # DDL statements don't need an explicit transaction
        with open(filepath, 'r', encoding='utf-8') as fh:
            sql = fh.read()
        statements = _split_sql(sql)
        executed = 0
        with conn.cursor() as cur:
            for stmt in statements:
                clean = stmt.strip()
                if not clean or clean.startswith('--'):
                    continue
                try:
                    cur.execute(clean)
                    executed += 1
                except Exception as stmt_err:
                    print(f"[SQL] Warning — statement skipped: {stmt_err}")
        print(f"[SQL] ✓ Applied '{os.path.basename(filepath)}' ({executed} statements)")
    except Exception as e:
        print(f"[SQL] Error applying {os.path.basename(filepath)}: {e}")
    finally:
        conn.autocommit = False
        DatabaseConnection.return_connection(conn)


def create_app():
    """
    Create and configure Flask application
    """
    # Get configuration based on environment
    config = get_config()
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Configure session
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    # Set database configuration for lazy initialization
    DatabaseConnection.set_config(config)

    # Apply backup triggers on every startup
    _apply_startup_sql(os.path.join(_DB_DIR, 'railway_backup_triggers.sql'))

    # Initialize upload folders for file storage
    try:
        FileStorageService.init_upload_folder()
    except Exception as e:
        print(f"Warning: Failed to initialize upload folders: {e}")
    
    # Register blueprints (routes)
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_blueprints(app):
    """Register all Flask blueprints"""
    # Authentication routes
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # HTML view pages (server-side rendered)
    from app.routes.views import views_bp
    app.register_blueprint(views_bp)

    # JSON API blueprints
    from app.routes.passengers import passengers_bp
    from app.routes.trains import trains_bp
    from app.routes.stations import stations_bp
    from app.routes.schedules import schedules_bp
    from app.routes.bookings import bookings_bp
    from app.routes.payments import payments_bp
    from app.routes.cancellations import cancellations_bp
    from app.routes.analytics import analytics_bp
    from app.routes.staff import staff_bp
    from app.routes.route import routes_bp
    from app.routes.backups import backups_bp
    from app.routes.storage import storage_bp
    
    app.register_blueprint(passengers_bp)
    app.register_blueprint(trains_bp)
    app.register_blueprint(stations_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(cancellations_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(backups_bp)
    app.register_blueprint(storage_bp)


