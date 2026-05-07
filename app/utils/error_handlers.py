"""
Error Handlers
Global error handling for Flask app
"""
from flask import jsonify


def handle_error(error_code, message, status_code=400):
    """Generic error handler"""
    return jsonify({
        'success': False,
        'error': message,
        'error_code': error_code
    }), status_code


def handle_database_error(error_message):
    """Handle database-related errors"""
    return handle_error('DB_ERROR', f'Database error: {error_message}', 500)


def handle_validation_error(field, message):
    """Handle validation errors"""
    return handle_error('VALIDATION_ERROR', f'{field}: {message}', 400)


def handle_not_found(resource_type, resource_id):
    """Handle not found errors"""
    return handle_error('NOT_FOUND', f'{resource_type} with ID {resource_id} not found', 404)


def handle_unauthorized():
    """Handle unauthorized access"""
    return handle_error('UNAUTHORIZED', 'Unauthorized access', 401)


def handle_forbidden():
    """Handle forbidden access"""
    return handle_error('FORBIDDEN', 'Access forbidden', 403)


def handle_conflict(message):
    """Handle conflict errors (duplicate, etc)"""
    return handle_error('CONFLICT', message, 409)
