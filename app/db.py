import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from app.config import Config


class DatabaseConnection:
    """Simple database connection wrapper using psycopg2"""
    
    _pool = None
    
    @classmethod
    def init_pool(cls, config):
        """Initialize connection pool"""
        if cls._pool is None:
            cls._pool = psycopg2.pool.SimpleConnectionPool(
                config.DB_MIN_CONN,
                config.DB_MAX_CONN,
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        if cls._pool is None:
            cls.init_pool(Config)
        return cls._pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Return connection to the pool"""
        if cls._pool is not None:
            cls._pool.putconn(conn)
    
    @classmethod
    def close_all(cls):
        """Close all connections in the pool"""
        if cls._pool is not None:
            cls._pool.closeall()


class Database:
    """Database helper class for common operations"""
    
    @staticmethod
    def fetch_one(query, params=None):
        """Fetch a single row as dictionary"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            DatabaseConnection.return_connection(conn)
    
    @staticmethod
    def fetch_all(query, params=None):
        """Fetch multiple rows as list of dictionaries"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results] if results else []
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            DatabaseConnection.return_connection(conn)
    
    @staticmethod
    def fetch_scalar(query, params=None):
        """Fetch a single scalar value"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            DatabaseConnection.return_connection(conn)
    
    @staticmethod
    def execute(query, params=None):
        """Execute a query (INSERT, UPDATE, DELETE) and commit"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            affected_rows = cursor.rowcount
            conn.commit()
            cursor.close()
            return affected_rows
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            return 0
        finally:
            DatabaseConnection.return_connection(conn)
    
    @staticmethod
    def execute_returning(query, params=None):
        """Execute a query and return the RETURNING value"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            return result[0] if result else None
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            return None
        finally:
            DatabaseConnection.return_connection(conn)
    
    @staticmethod
    def transaction(callback):
        """Execute a transaction with callback"""
        conn = DatabaseConnection.get_connection()
        try:
            result = callback(conn)
            conn.commit()
            return result
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Transaction error: {e}")
            return None
        finally:
            DatabaseConnection.return_connection(conn)
