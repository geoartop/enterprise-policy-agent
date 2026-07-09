import psycopg
from loguru import logger
from backend.app.core.config import settings

def get_db_connection_string() -> str:
    """
    Constructs the database connection string from the application settings.
    
    Returns:
        str: The full database connection string including psycopg adapter hint.
    """
    return f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

def get_raw_connection_string() -> str:
    """
    Returns the standard postgresql connection string without the psycopg adapter hint.
    Used by libraries like psycopg_pool and langgraph-checkpoint-postgres.
    
    Returns:
        str: The standard database connection string without the adapter hint.
    """
    return get_db_connection_string().replace("postgresql+psycopg://", "postgresql://")

def setup_database():
    """
    Initializes the database by enabling the pgvector extension.
    LangChain and LangGraph will automatically handle creating their specific tables
    when they are first instantiated.
    """
    conn_info = get_db_connection_string()
    
    try:
        # Use autocommit to execute CREATE EXTENSION
        with psycopg.connect(conn_info, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Enable the pgvector extension
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                logger.info("Successfully enabled pgvector extension.")
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

if __name__ == "__main__":
    logger.info("Testing database connection...")
    try:
        setup_database()
        logger.success("Success! The application connected to the database and pgvector is ready.")
    except Exception as e:
        logger.error(f"Connection failed: {e}")
