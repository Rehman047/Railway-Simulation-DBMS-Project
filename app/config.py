"""
Flask Application Configuration
Loads settings from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration with defaults"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'railway_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Connection Pool Configuration
    DB_POOL_MIN = int(os.getenv('DB_POOL_MIN', 2))
    DB_POOL_MAX = int(os.getenv('DB_POOL_MAX', 10))
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 30))
    
    # Application Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    TIMEZONE = os.getenv('TIMEZONE', 'UTC')


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    DB_NAME = 'railway_db_test'


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False


# Select configuration based on environment
def get_config():
    """Get appropriate config based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig

    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', False)
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'railway_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Connection Pool Settings
    DB_MIN_CONN = int(os.getenv('DB_MIN_CONN', 2))
    DB_MAX_CONN = int(os.getenv('DB_MAX_CONN', 10))
    
    # Database connection string
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_config():
    """Return configuration object"""
    return Config()
