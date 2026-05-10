"""
Authentication Routes
Handles login, logout, and authentication checks
"""
from flask import Blueprint, request, jsonify, session
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login as admin with password.
    
    Expected JSON:
    {
        "password": "admin_password"
    }
    
    Returns:
    {
        "success": true,
        "message": "Admin authenticated successfully"
    }
    """
    data = request.get_json()
    
    if not data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'Password is required'
        }), 400
    
    password = data['password'].strip()
    
    if not password:
        return jsonify({
            'success': False,
            'error': 'Password cannot be empty'
        }), 400
    
    if AuthService.authenticate_admin(password):
        return jsonify({
            'success': True,
            'message': 'Admin authenticated successfully',
            'role': 'admin'
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid admin password'
        }), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout from admin session.
    
    Returns:
    {
        "success": true,
        "message": "Logged out successfully"
    }
    """
    AuthService.logout_admin()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@auth_bp.route('/status', methods=['GET'])
def status():
    """
    Get current authentication status.
    
    Returns:
    {
        "authenticated": true/false,
        "role": "admin" or "user"
    }
    """
    is_admin = AuthService.is_admin_authenticated()
    return jsonify({
        'authenticated': is_admin,
        'role': AuthService.get_user_role()
    }), 200


@auth_bp.route('/verify-password', methods=['POST'])
def verify_password():
    """
    Verify admin password without setting session.
    Used for UI prompts/dialogs.
    
    Expected JSON:
    {
        "password": "admin_password"
    }
    
    Returns:
    {
        "success": true/false,
        "valid": true/false
    }
    """
    data = request.get_json()
    
    if not data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'Password is required'
        }), 400
    
    password = data['password'].strip()
    is_valid = AuthService.verify_admin_password(password)
    
    return jsonify({
        'success': True,
        'valid': is_valid
    }), 200
