import os
from loguru import logger
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from backend.app.agents.state import AgentState
from backend.app.utils import load_prompt, get_llm, create_agent_prompt

load_dotenv()

members = ["policy_expert", "ingestion_worker"]
options = ["FINISH"] + members

class RouteResponse(BaseModel):
    next_agent: Literal["FINISH", "policy_expert", "ingestion_worker"] = Field(
        description="The next agent to route the conversation to, or FINISH."
    )

llm = get_llm()

system_prompt = load_prompt("supervisor_system.txt")
human_prompt = load_prompt("supervisor_human.txt")

prompt = create_agent_prompt(system_prompt, human_prompt, options, members)

supervisor_chain = prompt | llm.with_structured_output(RouteResponse)

def supervisor_node(state: AgentState) -> dict:
    """
    Executes the supervisor routing logic.
    
    Evaluates the conversation history in the state and determines the next 
    agent to invoke, or finishes the workflow.
    
    Args:
        state: The current AgentState containing the conversation history.
        
    Returns:
        dict: A dictionary containing the 'next' routing key.
    """
    logger.info("Supervisor node invoked. Evaluating conversation state.")
    try:
        result = supervisor_chain.invoke(state)
        logger.info(f"Supervisor routing decision: {result.next_agent}")
        return {"next_agent": result.next_agent}
    except Exception as e:
        logger.error(f"Error during supervisor routing: {e}")
        raise
