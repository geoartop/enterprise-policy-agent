from fastapi import APIRouter, Depends
import psycopg
from loguru import logger

from backend.app.api.utils import get_db_connection

router = APIRouter()

@router.get("/sessions")
def get_sessions(conn: psycopg.Connection = Depends(get_db_connection)):
    """
    Retrieves a list of distinct historical session IDs from the database.
    
    Args:
        conn (psycopg.Connection, optional): The database connection object. Defaults to Depends(get_db_connection).
        
    Returns:
        dict: A dictionary containing a 'sessions' key mapped to a list of thread ID strings.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT thread_id FROM checkpoints;")
            sessions = [row[0] for row in cur.fetchall()]
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return {"sessions": []}
