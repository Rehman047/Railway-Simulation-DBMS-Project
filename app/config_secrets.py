"""
Secrets Configuration File
Stores sensitive information like admin password
"""
import os
# from dotenv import load_dotenv

# Load environment variables from .env file
# load_dotenv()


class Secrets:
    """Secrets configuration"""
    
    # Admin Password
    # Set via environment variable ADMIN_PASSWORD or use default
    # In production, ALWAYS use environment variables
    ADMIN_PASSWORD = os.getenv('here', 'admin@railway123')
    
    # JWT Secret for session tokens (optional, for future enhancement)
    JWT_SECRET = os.getenv('JWT_SECRET', 'railway-jwt-secret-key-change-in-production')
    
    # Session timeout in seconds (24 hours)
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 86400))


def get_secrets():
    """Get secrets configuration"""
    return Secrets()
