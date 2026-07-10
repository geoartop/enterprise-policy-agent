import os
import sys
import glob
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from loguru import logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres.vectorstores import PGVector
import psycopg
from backend.app.core.database import get_raw_connection_string
from backend.app.services.document_parser import parse_pdf_to_chunks
from backend.app.utils import get_vector_store


def ingest_file(file_path: str, vector_store: PGVector, force: bool = False):
    """
    Parses a single PDF and inserts it into the database.
    
    Args:
        file_path (str): The path to the PDF file to ingest.
        vector_store (PGVector): The vector store instance.
        force (bool, optional): If True, overwrites existing documents. Defaults to False.
        
    Returns:
        bool: True if ingestion was successful, False otherwise.
    """
    filename = os.path.basename(file_path)
    logger.info(f"Processing {filename}...")

    # We check if the file exists to determine if we need to skip or delete
    existing = vector_store.similarity_search(
        "dummy query", k=1, filter={"source": filename}
    )
    
    if existing:
        if not force:
            logger.warning(
                f"File {filename} appears to already exist in the database. Skipping. (Use --force to override)"
            )
            return False
        else:
            logger.info(f"File {filename} exists and force=True. Deleting old records to prevent duplicates...")
            try:
                with psycopg.connect(get_raw_connection_string(), autocommit=True) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "DELETE FROM langchain_pg_embedding WHERE cmetadata->>'source' = %s",
                            (filename,)
                        )
                logger.success(f"Successfully deleted old records for {filename}.")
            except Exception as e:
                logger.error(f"Could not automatically delete old records. Duplicates may be appended! Error: {e}")

    try:
        documents = parse_pdf_to_chunks(file_path)
        logger.info(
            f"Extracted {len(documents)} chunks. Embedding and saving to database..."
        )

        vector_store.add_documents(documents)
        logger.success(f"Successfully ingested {filename}")
        return True
    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")
        return False

