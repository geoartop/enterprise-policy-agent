import os
from pathlib import Path
from loguru import logger
from functools import lru_cache
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_postgres.vectorstores import PGVector
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from backend.app.core.config import settings
from backend.app.core.database import get_db_connection_string

def load_prompt(filename: str) -> str:
    """
    Loads a prompt from the agents/prompts directory.
    
    Args:
        filename (str): The name of the prompt file to load.
        
    Returns:
        str: The contents of the prompt file.
    """
    prompt_path = Path(__file__).parent / "agents" / "prompts" / filename
    try:
        content = prompt_path.read_text(encoding="utf-8").strip()
        logger.debug(f"Successfully loaded prompt: {filename}")
        return content
    except FileNotFoundError as e:
        logger.error(f"Prompt file not found: {prompt_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading prompt file {prompt_path}: {e}")
        raise

def get_llm() -> ChatGoogleGenerativeAI:
    """
    Returns an instance of the configured LLM.
    
    Returns:
        ChatGoogleGenerativeAI: The initialized LangChain LLM instance.
    """
    try:
        model_name = settings.llm_model
        api_key = settings.google_api_key
        if not api_key:
            logger.warning("GOOGLE_API_KEY is not set in the configuration.")
        
        llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=0,
            google_api_key=api_key
        )
        logger.debug(f"Successfully initialized LLM: {model_name}")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise

@lru_cache(maxsize=1)
def get_vector_store() -> PGVector:
    """
    Initializes and returns the PGVector store using Gemini Embeddings.
    Uses lru_cache to ensure only one instance is created per process, 
    preventing SQLAlchemy MetaData collisions during parallel tool calling.
    
    Returns:
        PGVector: The initialized vector store object.
    """
    model_name = settings.embedding_model
    key = settings.google_api_key

    embeddings = GoogleGenerativeAIEmbeddings(model=model_name, api_key=key)
    connection = get_db_connection_string()

    collection_name = settings.collection_name

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    return vector_store

def create_agent_prompt(system_prompt: str, human_prompt: str, options: list[str], members: list[str]) -> ChatPromptTemplate:
    """
    Creates a chat prompt template for an agent.
    
    Args:
        system_prompt (str): The system prompt text.
        human_prompt (str): The human prompt text.
        options (list[str]): A list of available routing options.
        members (list[str]): A list of agent members.
        
    Returns:
        ChatPromptTemplate: The compiled ChatPromptTemplate object.
    """
    try:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                ("system", human_prompt),
            ]
        ).partial(options=str(options), members=", ".join(members))
        logger.debug("Successfully created agent prompt template.")
        return prompt
    except Exception as e:
        logger.error(f"Failed to create agent prompt template: {e}")
        raise
