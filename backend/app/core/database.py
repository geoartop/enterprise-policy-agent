import os
import psycopg
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

def get_db_connection_string() -> str:
    """
    Constructs the database connection string from environment variables.
    Falls back to the default docker-compose values if not set.
    """
    user = os.getenv("POSTGRES_USER", "myuser")
    password = os.getenv("POSTGRES_PASSWORD", "mypassword")
    host = os.getenv("POSTGRES_HOST", "db") 
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "policy_agent")
    
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"

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
