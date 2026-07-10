import psycopg
import argparse
from loguru import logger
from backend.app.core.database import get_raw_connection_string

def delete_checkpoint(thread_id: str):
    conn_info = get_raw_connection_string()
    
    try:
        with psycopg.connect(conn_info, autocommit=True) as conn:
            with conn.cursor() as cur:
                logger.info(f"Deleting checkpoint data for thread_id: '{thread_id}'...")
                
                # The LangGraph PostgresSaver uses 3 tables to store state.
                # We need to delete records from all of them for this specific thread_id.
                
                cur.execute("DELETE FROM checkpoint_writes WHERE thread_id = %s", (thread_id,))
                writes_deleted = cur.rowcount
                
                cur.execute("DELETE FROM checkpoint_blobs WHERE thread_id = %s", (thread_id,))
                blobs_deleted = cur.rowcount
                
                cur.execute("DELETE FROM checkpoints WHERE thread_id = %s", (thread_id,))
                checkpoints_deleted = cur.rowcount
                
                logger.success(f"Success! Deleted {checkpoints_deleted} checkpoints, {blobs_deleted} blobs, and {writes_deleted} writes for '{thread_id}'.")
    except Exception as e:
        logger.error(f"Error while deleting checkpoint: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete a specific LangGraph checkpoint session.")
    # Default to the one from your screenshot!
    parser.add_argument("thread_id", type=str, nargs="?", default="test-session-manos", help="The thread_id to delete.")
    args = parser.parse_args()
    
    delete_checkpoint(args.thread_id)
