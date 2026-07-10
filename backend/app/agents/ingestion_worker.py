from loguru import logger
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from backend.app.utils import get_llm, load_prompt
from backend.app.tools.ingest_tool import ingest_policy_document
from backend.app.agents.state import IngestionWorkerState
from backend.app.agents.utils import create_call_model, should_continue

logger.info("Initializing Ingestion Worker Agent manually using StateGraph...")

llm = get_llm()
tools = [ingest_policy_document]
llm_with_tools = llm.bind_tools(tools)
system_prompt_text = load_prompt("ingestion_worker_system.txt")


# Build the ReAct graph manually
workflow = StateGraph(IngestionWorkerState)
workflow.add_node("agent", create_call_model(llm_with_tools, system_prompt_text))
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

ingestion_worker_agent = workflow.compile()

def ingestion_worker_node(state: dict) -> dict:
    """
    Executes the Ingestion Worker node logic by invoking the ingestion worker agent.
    
    Args:
        state (dict): The current conversation state dictionary.
        
    Returns:
        dict: The updated state containing the agent's response messages.
    """
    logger.info("Ingestion Worker node invoked.")
    try:
        result = ingestion_worker_agent.invoke(state)
        return {"messages": result["messages"]}
    except Exception as e:
        logger.error(f"Error in ingestion_worker_node: {e}")
        raise
