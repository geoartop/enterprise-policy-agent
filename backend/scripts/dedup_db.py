import psycopg
from loguru import logger
from backend.app.core.database import get_raw_connection_string

def deduplicate():
    conn_info = get_raw_connection_string()
    
    try:
        with psycopg.connect(conn_info, autocommit=True) as conn:
            with conn.cursor() as cur:
                logger.info("Cleaning up duplicate chunks from the database...")
                # This SQL query keeps only the first inserted copy of each chunk (by comparing the UUID 'id' or internal ctid)
                # and deletes all subsequent duplicates for the same source and text.
                cur.execute("""
                    DELETE FROM langchain_pg_embedding 
                    WHERE ctid NOT IN (
                        SELECT min(ctid) 
                        FROM langchain_pg_embedding 
                        GROUP BY cmetadata->>'source', document
                    );
                """)
                logger.success(f"Success! Deleted {cur.rowcount} duplicate chunks from the database.")
    except Exception as e:
        logger.error(f"Error while deduplicating: {e}")

if __name__ == "__main__":
    deduplicate()
