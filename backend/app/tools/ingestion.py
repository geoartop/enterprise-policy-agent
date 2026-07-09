import os
import sys
import glob
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from dotenv import load_dotenv

load_dotenv()

from loguru import logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from backend.app.core.database import get_db_connection_string
from backend.app.services.document_parser import parse_pdf_to_chunks


from functools import lru_cache

@lru_cache(maxsize=1)
def get_vector_store() -> PGVector:
    """
    Initializes and returns the PGVector store using Gemini Embeddings.
    Uses lru_cache to ensure only one instance is created per process, 
    preventing SQLAlchemy MetaData collisions during parallel tool calling.
    """
    # Uses GOOGLE_API_KEY and EMBEDDING_MODEL from environment
    model_name = os.getenv("EMBEDDING_MODEL")
    key = os.getenv("GOOGLE_API_KEY")

    embeddings = GoogleGenerativeAIEmbeddings(model=model_name, api_key=key)
    connection = get_db_connection_string()

    collection_name = "policy_documents"

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    return vector_store


def ingest_file(file_path: str, vector_store: PGVector, force: bool = False):
    """
    Parses a single PDF and inserts it into the database.
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
                vector_store.delete(filter={"source": {"$eq": filename}})
                logger.success(f"Successfully deleted old records for {filename}.")
            except Exception as e:
                logger.warning(f"Standard filter deletion failed ({e}). Attempting fallback simple filter...")
                try:
                    vector_store.delete(filter={"source": filename})
                    logger.success(f"Successfully deleted old records for {filename}.")
                except Exception as e2:
                    logger.error(f"Could not automatically delete old records. Duplicates may be appended! Error: {e2}")

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


# for testing purposes
def main():
    parser = argparse.ArgumentParser(description="Ingest PDF documents into pgvector.")
    parser.add_argument(
        "path",
        nargs="?",
        default="data/input",
        help="Path to a specific PDF file or a directory of PDFs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force ingestion even if the file seems to already exist.",
    )
    args = parser.parse_args()

    target_path = os.path.abspath(args.path)

    if not os.path.exists(target_path):
        logger.error(f"Path not found: {target_path}")
        return

    logger.info("Connecting to Vector Database...")
    vector_store = get_vector_store()

    if os.path.isfile(target_path):
        if target_path.endswith(".pdf"):
            ingest_file(target_path, vector_store, args.force)
        else:
            logger.error("The provided file is not a PDF.")
    elif os.path.isdir(target_path):
        pdf_files = glob.glob(os.path.join(target_path, "*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {target_path}")
            return

        logger.info(f"Found {len(pdf_files)} PDFs in directory. Starting ingestion...")
        for pdf_file in pdf_files:
            ingest_file(pdf_file, vector_store, args.force)


if __name__ == "__main__":
    main()
