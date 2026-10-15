"""
HoneyGuard Database Schema Initializer & Inspector
"""

from pathlib import Path
from typing import List, Dict, Any
from honeyguard.database.connection import get_db_connection
from honeyguard.utils.logger import get_logger
from honeyguard.utils.paths import get_database_dir

logger = get_logger("HoneyGuard.Schema")

EXPECTED_TABLES = [
    "protected_directories",
    "decoys",
    "file_events",
    "alerts",
    "incidents",
    "response_actions",
    "benchmark_runs",
    "benchmark_measurements",
    "application_settings",
    "audit_logs"
]


def check_tables_exist() -> List[str]:
    """Return list of existing tables in honeyguard_db."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        rows = cursor.fetchall()
        # In DictCursor rows are like [{'Tables_in_honeyguard_db': 'tableName'}]
        tables = []
        for r in rows:
            for val in r.values():
                tables.append(val)
        return tables


def verify_schema() -> bool:
    """Verify that all 10 expected tables exist."""
    existing = check_tables_exist()
    missing = [t for t in EXPECTED_TABLES if t not in existing]
    if missing:
        logger.warning(f"Missing database tables: {missing}")
        return False
    logger.info("Database schema verified: all 10 tables present.")
    return True


def initialize_schema_if_needed() -> bool:
    """Read database/honeyguard_db.sql and execute schema commands if tables missing."""
    try:
        existing = check_tables_exist()
        missing = [t for t in EXPECTED_TABLES if t not in existing]
        if not missing:
            return True

        sql_file = get_database_dir() / "honeyguard_db.sql"
        if not sql_file.exists():
            logger.error(f"Schema SQL file not found at {sql_file}")
            return False

        logger.info(f"Initializing missing database schema from {sql_file}...")
        conn = get_db_connection()
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Split commands on semicolon while skipping comments
        statements = []
        current = []
        for line in sql_content.splitlines():
            line_str = line.strip()
            if line_str.startswith("--") or line_str.startswith("/*"):
                continue
            current.append(line)
            if line_str.endswith(";"):
                stmt = "\n".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []

        with conn.cursor() as cursor:
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                except Exception as exc:
                    logger.debug(f"Statement execution notice: {exc}")
            conn.commit()

        logger.info("Database schema initialized successfully.")
        return verify_schema()
    except Exception as exc:
        logger.error(f"Failed to initialize schema: {exc}")
        return False
