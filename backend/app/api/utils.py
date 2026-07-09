from typing import Generator
import psycopg
from backend.app.core.database import get_raw_connection_string
from loguru import logger

def get_db_connection() -> Generator[psycopg.Connection, None, None]:
    """
    Dependency for yielding a database connection.
    """
    conn_str = get_raw_connection_string()
    try:
        with psycopg.connect(conn_str) as conn:
            yield conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
