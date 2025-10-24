"""
Landing Database Connector for MySQL.

Handles connection management, pooling, and health checks for the landing database.
"""
import logging
import pymysql
from typing import Optional, Any
from contextlib import contextmanager
from kg_builder.models import DatabaseConnectionInfo

logger = logging.getLogger(__name__)


class LandingDBConnector:
    """MySQL connector for landing database with connection pooling."""

    def __init__(self, db_config: DatabaseConnectionInfo):
        """
        Initialize landing database connector.

        Args:
            db_config: Database connection information
        """
        if db_config.db_type.lower() != "mysql":
            raise ValueError(f"Unsupported landing database type: {db_config.db_type}. Only MySQL is supported.")

        self.db_config = db_config
        self.connection = None
        logger.info(f"Initialized LandingDBConnector for {db_config.host}:{db_config.port}/{db_config.database}")

    def connect(self) -> Any:
        """
        Establish connection to MySQL landing database.

        Returns:
            MySQL connection object
        """
        try:
            self.connection = pymysql.connect(
                host=self.db_config.host,
                port=self.db_config.port,
                user=self.db_config.username,
                password=self.db_config.password,
                database=self.db_config.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                connect_timeout=30
            )
            logger.info("Successfully connected to landing database")
            return self.connection
        except Exception as e:
            logger.error(f"Failed to connect to landing database: {e}")
            raise

    def get_connection(self) -> Any:
        """
        Get active connection or create new one.

        Returns:
            MySQL connection object
        """
        if self.connection is None or not self.is_connected():
            self.connection = self.connect()
        return self.connection

    def is_connected(self) -> bool:
        """
        Check if connection is active.

        Returns:
            True if connected, False otherwise
        """
        if self.connection is None:
            return False

        try:
            self.connection.ping(reconnect=False)
            return True
        except Exception:
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Landing database connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self.connection = None

    @contextmanager
    def cursor(self, dictionary=True):
        """
        Context manager for database cursor.

        Args:
            dictionary: Return results as dictionaries (default: True)

        Yields:
            Database cursor
        """
        conn = self.get_connection()
        cursor_class = pymysql.cursors.DictCursor if dictionary else pymysql.cursors.Cursor
        cursor = conn.cursor(cursor_class)

        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()

    def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """
        Execute a query and return results.

        Args:
            query: SQL query to execute
            params: Query parameters (optional)

        Returns:
            Query results
        """
        with self.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def execute_one(self, query: str, params: Optional[tuple] = None) -> Optional[dict]:
        """
        Execute a query and return single result.

        Args:
            query: SQL query to execute
            params: Query parameters (optional)

        Returns:
            Single result or None
        """
        with self.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()

    def execute_many(self, query: str, params_list: list) -> int:
        """
        Execute a query with multiple parameter sets.

        Args:
            query: SQL query to execute
            params_list: List of parameter tuples

        Returns:
            Number of affected rows
        """
        with self.cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def health_check(self) -> bool:
        """
        Perform health check on landing database.

        Returns:
            True if healthy, False otherwise
        """
        try:
            result = self.execute_one("SELECT 1 as health")
            return result is not None and result.get('health') == 1
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_database_info(self) -> dict:
        """
        Get database information.

        Returns:
            Dictionary with database info
        """
        try:
            version = self.execute_one("SELECT VERSION() as version")
            size = self.execute_one(f"""
                SELECT
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
                FROM information_schema.tables
                WHERE table_schema = '{self.db_config.database}'
            """)
            table_count = self.execute_one(f"""
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = '{self.db_config.database}'
                AND table_name LIKE 'recon_stage_%'
            """)

            return {
                "database": self.db_config.database,
                "version": version.get('version') if version else "Unknown",
                "size_mb": size.get('size_mb', 0) if size else 0,
                "staging_table_count": table_count.get('count', 0) if table_count else 0,
                "connected": self.is_connected()
            }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {
                "database": self.db_config.database,
                "error": str(e),
                "connected": False
            }

    def create_schema_if_not_exists(self, schema_name: str):
        """
        Create schema/database if it doesn't exist.

        Args:
            schema_name: Schema name to create
        """
        try:
            with self.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{schema_name}`")
            logger.info(f"Schema '{schema_name}' is ready")
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            raise

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Singleton instance
_landing_connector: Optional[LandingDBConnector] = None


def get_landing_connector(db_config: Optional[DatabaseConnectionInfo] = None) -> Optional[LandingDBConnector]:
    """
    Get or create landing database connector singleton.

    Args:
        db_config: Database configuration (uses config if not provided)

    Returns:
        LandingDBConnector instance or None if not configured
    """
    global _landing_connector

    if db_config is None:
        from kg_builder.config import get_landing_db_config
        db_config = get_landing_db_config()

    if db_config is None:
        logger.warning("Landing database is not configured")
        return None

    if _landing_connector is None:
        _landing_connector = LandingDBConnector(db_config)

    return _landing_connector


def reset_landing_connector():
    """Reset singleton instance (for testing)."""
    global _landing_connector
    if _landing_connector:
        _landing_connector.close()
    _landing_connector = None
