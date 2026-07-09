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
        description="The next agent. MUST be 'policy_expert' if the user's latest message is a greeting (e.g., 'hi') or a new question. ONLY use 'FINISH' if an AI worker has already replied to the user's latest message."
    )

llm = get_llm()

def supervisor_node(state: AgentState) -> dict:
    """
    Executes the supervisor routing logic.
    
    Evaluates the conversation history in the state and determines the next 
    agent to invoke, or finishes the workflow.
    
    Args:
        state (AgentState): The current AgentState containing the conversation history.
        
    Returns:
        dict: A dictionary containing the 'next_agent' routing key.
    """
    logger.info("Supervisor node invoked. Evaluating conversation state.")
    try:
        # Load dynamically to catch prompt changes without restart
        sys_prompt = load_prompt("supervisor_system.txt")
        hum_prompt = load_prompt("supervisor_human.txt")
        prompt = create_agent_prompt(sys_prompt, hum_prompt, options, members)
        supervisor_chain = prompt | llm.with_structured_output(RouteResponse)
        
        result = supervisor_chain.invoke(state)
        logger.info(f"Supervisor routing decision: {result.next_agent}")
        return {"next_agent": result.next_agent}
    except Exception as e:
        logger.error(f"Error during supervisor routing: {e}")
        raise
