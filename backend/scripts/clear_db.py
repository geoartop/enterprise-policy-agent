import os
import sys

# Ensure we can import the backend package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from loguru import logger
from backend.app.utils import get_vector_store

def clear_database():
    """
    Clears the entire PGVector database by dropping the internal tables.
    """
    logger.info("Connecting to PGVector Database to perform a full wipe...")
    try:
        vector_store = get_vector_store()
        
        # This completely drops the internal tables used by LangChain Postgres
        vector_store.drop_tables()
        
        logger.success("Success! The database has been completely wiped.")
        logger.info("You can now run 'python backend/app/tools/ingestion.py' to cleanly ingest your files from scratch.")
        
    except Exception as e:
        logger.error(f"Failed to wipe database: {e}")

if __name__ == "__main__":
    clear_database()
