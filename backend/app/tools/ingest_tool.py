import os
from langchain_core.tools import tool
from loguru import logger
from backend.app.tools.ingestion import get_vector_store, ingest_file

@tool
def ingest_policy_document(file_path: str, force: bool = False) -> str:
    """
    Ingests a PDF policy document into the vector database.
    
    Args:
        file_path: The absolute or relative path to the PDF document to ingest.
        force: If True, forces ingestion even if the document seems to exist in the database.
        
    Returns:
        A string indicating success or the specific error encountered.
    """
    logger.info(f"Tool 'ingest_policy_document' invoked for file: {file_path}, force={force}")
    
    # Resolve absolute path
    target_path = os.path.abspath(file_path)
    
    if not os.path.exists(target_path):
        error_msg = f"File not found: {target_path}. Please check the path and try again."
        logger.error(error_msg)
        return error_msg
        
    if not target_path.lower().endswith(".pdf"):
        error_msg = f"The provided file is not a PDF: {target_path}. Only PDFs are supported."
        logger.error(error_msg)
        return error_msg
        
    try:
        vector_store = get_vector_store()
        # Execute the ingestion function from our existing logic
        was_ingested = ingest_file(target_path, vector_store, force)
        
        if not was_ingested:
            return "The document already exists in the database. Please ask the user if they would like to force an update."
            
        return f"Successfully ingested document {target_path} into the database."
    except Exception as e:
        logger.error(f"Error during ingestion tool execution: {e}")
        return f"Failed to ingest document: {str(e)}"
