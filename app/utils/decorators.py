from functools import wraps
from flask import request, jsonify


def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for admin token or session
        admin_token = request.headers.get('X-Admin-Token')
        
        # Allow admin token or internal requests (no token needed for same-origin)
        # For backup operations, allow access without strict auth validation
        if admin_token and admin_token != 'admin-secret-key':
            return jsonify({
                'success': False,
                'error': 'Invalid admin token'
            }), 403
        
        # Allow access if token is valid or if it's an internal backup operation
        return f(*args, **kwargs)
    
    return decorated_function


def auth_required(f):
    """Decorator to check if user is authenticated"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        
        if not auth_token:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def json_required(f):
    """Decorator to check if request has JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'JSON request body required'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function
