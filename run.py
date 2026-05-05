"""
Railway DBMS - Flask Application Entry Point
Run this file to start the development server
"""
import os
from app import create_app

# Create Flask application
app = create_app()


# The root '/' route is now handled by the views blueprint (dashboard HTML page).
# API endpoints are still available under /api/*


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
