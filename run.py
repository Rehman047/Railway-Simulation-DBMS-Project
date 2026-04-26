"""
Railway DBMS - Flask Application Entry Point
Run this file to start the development server
"""
import os
from app import create_app

# Create Flask application
app = create_app()


@app.route('/', methods=['GET'])
def index():
    """Health check endpoint"""
    return {
        'success': True,
        'message': 'Railway DBMS API is running',
        'version': '1.0.0',
        'endpoints': {
            'passengers': '/api/passengers',
            'trains': '/api/trains',
            'stations': '/api/stations',
            'schedules': '/api/schedules',
            'bookings': '/api/bookings',
            'payments': '/api/payments',
            'cancellations': '/api/cancellations',
            'analytics': '/api/analytics'
        }
    }, 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    # Run development server
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug
    )
