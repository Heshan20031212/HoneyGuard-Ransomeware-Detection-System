"""
HoneyGuard Database Connection Manager
Provides safe, parameterized MySQL connection pooling, reconnection, and health checks.
"""

import os
from contextlib import contextmanager
from typing import Optional, Dict, Any
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

from honeyguard.utils.logger import get_logger
from honeyguard.utils.paths import get_project_root

logger = get_logger("HoneyGuard.DB")

# Load environment configuration
load_dotenv(get_project_root() / ".env")


class DatabaseConfig:
    """Encapsulates MySQL database configuration parameters."""

    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "root")
        self.database = os.getenv("DB_NAME", "honeyguard_db")
        self.charset = "utf8mb4"
        self.connect_timeout = 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "charset": self.charset,
            "connect_timeout": self.connect_timeout,
            "cursorclass": DictCursor,
            "autocommit": False
        }


class DatabaseManager:
    """Singleton connection manager for HoneyGuard MySQL database."""

    _instance: Optional["DatabaseManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = DatabaseConfig()
            cls._instance._connection = None
        return cls._instance

    def get_connection(self) -> pymysql.Connection:
        """Obtain an active MySQL database connection, reconnecting if disconnected."""
        try:
            if self._connection is None or not self._connection.open:
                logger.info(f"Connecting to MySQL server at {self._config.host}:{self._config.port}...")
                self._connection = pymysql.connect(**self._config.to_dict())
                logger.info(f"Connected to database '{self._config.database}' successfully.")
            else:
                try:
                    self._connection.ping()
                except Exception:
                    self._connection = pymysql.connect(**self._config.to_dict())
            return self._connection
        except pymysql.MySQLError as exc:
            logger.error(f"MySQL connection error ({self._config.host}:{self._config.port}): {exc}")
            raise

    def is_connected(self) -> bool:
        """Check if MySQL connection is alive and healthy."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                res = cursor.fetchone()
                return res is not None
        except Exception:
            return False

    def close(self):
        """Close active connection cleanly."""
        if self._connection and self._connection.open:
            try:
                self._connection.close()
                logger.info("MySQL connection closed.")
            except Exception as exc:
                logger.warning(f"Error closing MySQL connection: {exc}")
            finally:
                self._connection = None

    @contextmanager
    def transaction(self):
        """Context manager providing ACID transaction with auto-commit and rollback."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as exc:
            logger.error(f"Transaction failed, rolling back: {exc}")
            conn.rollback()
            raise


# Global helper functions
def get_db_connection() -> pymysql.Connection:
    return DatabaseManager().get_connection()


def is_db_connected() -> bool:
    return DatabaseManager().is_connected()


def db_transaction():
    return DatabaseManager().transaction()
