from typing import Annotated, Sequence, TypedDict
from loguru import logger
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage

from backend.app.utils import get_llm, load_prompt
from backend.app.tools.ingest_tool import ingest_policy_document

logger.info("Initializing Ingestion Worker Agent manually using StateGraph...")

llm = get_llm()
tools = [ingest_policy_document]
llm_with_tools = llm.bind_tools(tools)
system_prompt_text = load_prompt("ingestion_worker_system.txt")

class IngestionWorkerState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def call_model(state: IngestionWorkerState):
    messages = state["messages"]
    sys_msg = SystemMessage(content=system_prompt_text)
    response = llm_with_tools.invoke([sys_msg] + list(messages))
    return {"messages": [response]}

def should_continue(state: IngestionWorkerState):
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, 'tool_calls', None):
        return "tools"
    return END

# Build the ReAct graph manually
workflow = StateGraph(IngestionWorkerState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

ingestion_worker_agent = workflow.compile()

def ingestion_worker_node(state: dict) -> dict:
    """
    Executes the Ingestion Worker node logic.
    
    Args:
        state: The current conversation state.
        
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
