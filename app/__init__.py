"""
Flask Application Factory
Initializes the Flask app with configuration and routes
"""
from flask import Flask
from app.config import get_config
from app.db import DatabaseConnection


def create_app():
    """
    Create and configure Flask application
    """
    # Get configuration based on environment
    config = get_config()
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Initialize database connection pool
    DatabaseConnection.init_pool(config)
    
    # Register blueprints (routes)
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_blueprints(app):
    """Register all Flask blueprints"""
    from app.routes.passengers import passengers_bp
    from app.routes.trains import trains_bp
    from app.routes.stations import stations_bp
    from app.routes.schedules import schedules_bp
    from app.routes.bookings import bookings_bp
    from app.routes.payments import payments_bp
    from app.routes.cancellations import cancellations_bp
    from app.routes.analytics import analytics_bp
    
    app.register_blueprint(passengers_bp)
    app.register_blueprint(trains_bp)
    app.register_blueprint(stations_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(cancellations_bp)
    app.register_blueprint(analytics_bp)


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            'success': False,
            'error': 'Resource not found'
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'success': False,
            'error': 'Internal server error'
        }, 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {
            'success': False,
            'error': 'Method not allowed'
        }, 405
