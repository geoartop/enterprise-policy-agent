import psycopg
from loguru import logger
from backend.app.core.database import get_raw_connection_string

def check_db():
    conn_info = get_raw_connection_string()
    
    try:
        # Connect to the database using the raw connection string
        with psycopg.connect(conn_info) as conn:
            # Use dict_row so we can access columns by name easily
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                
                logger.info("--- 1. Checking Parsed Files and Chunk Counts ---")
                cur.execute("""
                    SELECT 
                        cmetadata->>'source' AS file_name, 
                        COUNT(*) AS chunk_count
                    FROM 
                        langchain_pg_embedding
                    WHERE 
                        cmetadata->>'source' IS NOT NULL
                    GROUP BY 
                        cmetadata->>'source'
                    ORDER BY 
                        file_name;
                """)
                files = cur.fetchall()
                if not files:
                    logger.warning("No files found in the database.")
                for f in files:
                    logger.success(f"File: {f['file_name']} | Chunks: {f['chunk_count']}")
                
                print("\n")
                logger.info("--- 2. Checking for Duplicate Chunks ---")
                cur.execute("""
                    SELECT 
                        cmetadata->>'source' AS file_name, 
                        COUNT(*) AS duplicate_count
                    FROM 
                        langchain_pg_embedding
                    WHERE 
                        cmetadata->>'source' IS NOT NULL
                    GROUP BY 
                        cmetadata->>'source', 
                        document
                    HAVING 
                        COUNT(*) > 1;
                """)
                duplicates = cur.fetchall()
                if not duplicates:
                    logger.success("Awesome! No duplicate chunks found.")
                else:
                    logger.warning(f"Found {len(duplicates)} duplicate entries:")
                    for d in duplicates:
                        logger.warning(f"File: {d['file_name']} | Duplicates of chunk: {d['duplicate_count']}")
                        
    except Exception as e:
        logger.error(f"Error checking database: {e}")

if __name__ == "__main__":
    check_db()
