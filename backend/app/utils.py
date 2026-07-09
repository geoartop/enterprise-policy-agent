import os
from pathlib import Path
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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
        model_name = os.getenv("LLM_MODEL")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY is not set in the environment.")
        
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
