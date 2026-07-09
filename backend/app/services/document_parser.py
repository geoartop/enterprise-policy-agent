import os
import re
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def parse_pdf_to_chunks(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Parses a PDF document into text chunks suitable for vector storage.
    
    Args:
        file_path (str): The absolute or relative path to the PDF file.
        chunk_size (int, optional): The maximum size of each text chunk. Defaults to 1000.
        chunk_overlap (int, optional): The overlap between consecutive chunks. Defaults to 200.
        
    Returns:
        list: A list of LangChain Document objects representing the chunks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    # Use LangChain's PyMuPDFLoader to load page-by-page
    loader = PyMuPDFLoader(file_path)
    pages = loader.load()
    
    filename = os.path.basename(file_path)
    
    policy_year = None
    # Use lookarounds instead of \b because underscores are considered word characters
    match = re.search(r'(?<!\d)(19\d{2}|20\d{2})(?!\d)', filename)
    if match:
        policy_year = match.group(0)
    
    # Standardize metadata on the page level
    for page in pages:
        page.metadata["policy_year"] = policy_year
        page.metadata["source"] = filename
        # Convert 0-indexed 'page' to human-readable 1-indexed page number
        page.metadata["page_number"] = page.metadata.get("page", 0) + 1
        
        # Remove the original 'page' key to keep pgvector metadata clean
        page.metadata.pop("page", None)

    # Split the page documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(pages)
    
    # Apply the global sequential index
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = idx

    return chunks