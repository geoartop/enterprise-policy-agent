import os
import re
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def parse_pdf_to_chunks(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    # Use LangChain's PyMuPDFLoader to load page-by-page
    loader = PyMuPDFLoader(file_path)
    pages = loader.load()
    
    filename = os.path.basename(file_path)
    
    policy_year = None
    match = re.search(r'\b(19\d{2}|20\d{2})\b', filename)
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