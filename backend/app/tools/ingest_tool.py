import os
import glob
from langchain_core.tools import tool
from loguru import logger
from backend.app.tools.ingestion import ingest_file
from backend.app.utils import get_vector_store

@tool
def ingest_policy_document(force_files: list[str] = None, clear_remaining: bool = False) -> str:
    """
    Ingests PDF policy documents into the vector database from the data/input directory.
    
    Args:
        force_files (list[str], optional): A list of specific filenames (e.g., ['doc1.pdf']) to force ingest.
                                           If None or empty, the tool will attempt to ingest all new files. Defaults to None.
        clear_remaining (bool, optional): If True, deletes all remaining PDF files in the directory after ingestion. Defaults to False.
        
    Returns:
        str: A string indicating the result of the operation, including any skipped files.
    """
    logger.info(f"Tool 'ingest_policy_document' invoked. force_files={force_files}, clear_remaining={clear_remaining}")
    
    try:
        vector_store = get_vector_store()
    except Exception as e:
        logger.error(f"Failed to connect to vector database: {e}")
        return f"Failed to connect to vector database: {str(e)}"
    
    target_dir = os.path.abspath("data/input")
    
    if not os.path.exists(target_dir):
        return f"Directory not found: {target_dir}."
        
    pdf_files = glob.glob(os.path.join(target_dir, "*.pdf"))
    if not pdf_files:
        return "No PDF files found to ingest."
        
    skipped_files = []
    ingested_files = []
    
    # Decide which files to process
    files_to_process = pdf_files
    force_mode = False
    
    if force_files is not None:
        force_mode = True
        # Filter files to process based on force_files
        files_to_process = [f for f in pdf_files if os.path.basename(f) in force_files]
        
    for pdf in files_to_process:
        try:
            # If we are explicitly forcing these files, set force=True
            was_ingested = ingest_file(pdf, vector_store, force=force_mode)
            if was_ingested:
                ingested_files.append(os.path.basename(pdf))
                # Delete the file upon successful ingestion
                os.remove(pdf)
                logger.info(f"Deleted successfully ingested file: {pdf}")
            else:
                skipped_files.append(os.path.basename(pdf))
        except Exception as e:
            logger.error(f"Failed to ingest {os.path.basename(pdf)}: {str(e)}")
            
    # Clear remaining files if requested
    cleared_files = []
    if clear_remaining:
        remaining_pdfs = glob.glob(os.path.join(target_dir, "*.pdf"))
        for pdf in remaining_pdfs:
            try:
                os.remove(pdf)
                cleared_files.append(os.path.basename(pdf))
                logger.info(f"Cleared remaining file: {pdf}")
            except Exception as e:
                logger.error(f"Failed to clear file {pdf}: {str(e)}")
                
    # Construct response
    response_lines = []
    if ingested_files:
        response_lines.append(f"Successfully ingested and deleted: {', '.join(ingested_files)}.")
    
    if skipped_files and not force_mode:
        response_lines.append(f"The following files already exist and were skipped: {', '.join(skipped_files)}.")
        response_lines.append("Please ask the user which of these they would like to force update.")
        
    if cleared_files:
        response_lines.append(f"Cleared the following remaining files from the folder: {', '.join(cleared_files)}.")
        
    if not response_lines:
        return "No action was taken. The files requested for force ingestion were not found in the directory."
        
    return "\n".join(response_lines)
