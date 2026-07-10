from loguru import logger
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from backend.app.utils import get_llm, load_prompt
from backend.app.tools.retriever import search_policy_documents
from backend.app.agents.state import PolicyExpertState
from backend.app.agents.utils import create_call_model, should_continue

logger.info("Initializing Policy Expert Agent manually using StateGraph...")

llm = get_llm()
tools = [search_policy_documents]
llm_with_tools = llm.bind_tools(tools)
system_prompt_text = load_prompt("policy_expert_system.txt")

# Build the ReAct graph manually
workflow = StateGraph(PolicyExpertState)
workflow.add_node("agent", create_call_model(llm_with_tools, system_prompt_text))
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

policy_expert_agent = workflow.compile()

def policy_expert_node(state: dict) -> dict:
    """
    Executes the Policy Expert node logic by invoking the policy expert agent.
    
    Args:
        state (dict): The current conversation state dictionary.
        
    Returns:
        dict: The updated state containing the agent's response messages.
    """
    logger.info("Policy Expert node invoked.")
    try:
        result = policy_expert_agent.invoke(state)
        return {"messages": result["messages"]}
    except Exception as e:
        logger.error(f"Error in policy_expert_node: {e}")
        raise
