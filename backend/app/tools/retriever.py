from typing import Optional
from langchain_core.tools import tool
from loguru import logger
from backend.app.utils import get_vector_store

@tool
def search_policy_documents(query: str, year: Optional[str] = None, page_number: Optional[int] = None) -> str:
    """
    Searches the internal policy documents vector database for relevant information.
    
    Args:
        query (str): The semantic search query based on the user's question.
        year (str, optional): An optional 4-digit year (e.g., "2020", "2024") to restrict the search to a specific policy version. Defaults to None.
        page_number (int, optional): An optional page number to restrict the search to a specific page. Defaults to None.
        
    Returns:
        str: A formatted string containing the matching document chunks, including citations for policy_year, source file, and page number.
    """
    logger.info(f"Executing search_policy_documents: query='{query}', year={year}, page_number={page_number}")
    try:
        vector_store = get_vector_store()
        
        filter_dict = {}
        conditions = []
        if year:
            conditions.append({"policy_year": {"$eq": str(year)}})
        if page_number:
            conditions.append({"page_number": {"$eq": int(page_number)}})
            
        if len(conditions) == 1:
            filter_dict = conditions[0]
        elif len(conditions) > 1:
            filter_dict = {"$and": conditions}
            
        search_kwargs = {"k": 4} # Retrieve top 4 chunks
        if filter_dict:
            search_kwargs["filter"] = filter_dict
            
        docs = vector_store.similarity_search(query, **search_kwargs)
        
        if not docs:
            return "No relevant policy documents found matching the criteria."
            
        formatted_results = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown Document')
            policy_year = doc.metadata.get('policy_year', 'Unknown Year')
            page = doc.metadata.get('page_number', 'Unknown Page')
            content = doc.page_content.replace('\n', ' ').strip()
            
            formatted_results.append(
                f"--- Result {i+1} ---\n"
                f"Source: {source} (Year: {policy_year}, Page: {page})\n"
                f"Content: {content}\n"
            )
            
        return "\n".join(formatted_results)
    except Exception as e:
        logger.error(f"Error in search_policy_documents: {e}")
        return f"Error executing search: {str(e)}"
