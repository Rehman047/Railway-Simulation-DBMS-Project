"""
Authentication Service
Handles user authentication and authorization
"""
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, jsonify
from app.config_secrets import get_secrets


class AuthService:
    """Authentication and authorization service"""
    
    ADMIN_ROLE = 'admin'
    USER_ROLE = 'user'
    ADMIN_SESSION_KEY = 'admin_authenticated'
    ADMIN_AUTHENTICATED_AT = 'admin_authenticated_at'
    
    @staticmethod
    def verify_admin_password(password: str) -> bool:
        """
        Verify if the provided password matches the admin password.
        
        Args:
            password: Password to verify
            
        Returns:
            True if password is correct, False otherwise
        """
        secrets = get_secrets()
        return password == secrets.ADMIN_PASSWORD
    
    @staticmethod
    def authenticate_admin(password: str) -> bool:
        """
        Authenticate as admin by setting session variables.
        
        Args:
            password: Admin password to verify
            
        Returns:
            True if authentication successful, False otherwise
        """
        if not AuthService.verify_admin_password(password):
            return False
        
        session[AuthService.ADMIN_SESSION_KEY] = True
        session[AuthService.ADMIN_AUTHENTICATED_AT] = datetime.now().isoformat()
        return True
    
    @staticmethod
    def is_admin_authenticated() -> bool:
        """
        Check if current session is authenticated as admin.
        
        Returns:
            True if authenticated as admin, False otherwise
        """
        if AuthService.ADMIN_SESSION_KEY not in session:
            return False
        
        secrets = get_secrets()
        authenticated_at = session.get(AuthService.ADMIN_AUTHENTICATED_AT)
        
        if authenticated_at:
            try:
                auth_time = datetime.fromisoformat(authenticated_at)
                if datetime.now() - auth_time > timedelta(seconds=secrets.SESSION_TIMEOUT):
                    # Session expired
                    session.clear()
                    return False
            except (ValueError, TypeError):
                return False
        
        return session.get(AuthService.ADMIN_SESSION_KEY, False)
    
    @staticmethod
    def logout_admin():
        """Logout admin session"""
        session.pop(AuthService.ADMIN_SESSION_KEY, None)
        session.pop(AuthService.ADMIN_AUTHENTICATED_AT, None)
    
    @staticmethod
    def get_user_role():
        """
        Get current user role.
        
        Returns:
            'admin' if authenticated as admin, 'user' otherwise
        """
        if AuthService.is_admin_authenticated():
            return AuthService.ADMIN_ROLE
        return AuthService.USER_ROLE


def require_admin_auth(f):
    """
    Decorator to require admin authentication for a route.
    Returns 403 Forbidden if not authenticated as admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthService.is_admin_authenticated():
            return jsonify({
                'success': False,
                'error': 'Admin authentication required',
                'requires_auth': True
            }), 403
        return f(*args, **kwargs)
    return decorated_function


def require_admin_auth_html(f):
    """
    Decorator to require admin authentication for HTML routes.
    Redirects to authentication prompt if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthService.is_admin_authenticated():
            return jsonify({
                'success': False,
                'error': 'Admin authentication required',
                'requires_auth': True
            }), 403
        return f(*args, **kwargs)
    return decorated_function
