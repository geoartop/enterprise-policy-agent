from typing import Annotated, Sequence, TypedDict
from loguru import logger
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage

from backend.app.utils import get_llm, load_prompt
from backend.app.tools.retriever import search_policy_documents

logger.info("Initializing Policy Expert Agent manually using StateGraph...")

llm = get_llm()
tools = [search_policy_documents]
llm_with_tools = llm.bind_tools(tools)
system_prompt_text = load_prompt("policy_expert_system.txt")

class PolicyExpertState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def call_model(state: PolicyExpertState):
    """
    Invokes the LLM with the provided state messages and tools for the Policy Expert agent.

    Args:
        state (PolicyExpertState): The current conversation state containing messages.

    Returns:
        dict: A dictionary containing the updated messages list with the model's response.
    """
    messages = state["messages"]
    sys_msg = SystemMessage(content=system_prompt_text)
    # The LLM receives the system message plus the conversation history
    response = llm_with_tools.invoke([sys_msg] + list(messages))
    return {"messages": [response]}

def should_continue(state: PolicyExpertState):
    """
    Determines whether the workflow should continue to the tools node or end for the Policy Expert agent.

    Args:
        state (PolicyExpertState): The current conversation state containing messages.

    Returns:
        str: "tools" if the last message contains tool calls, otherwise END.
    """
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, 'tool_calls', None):
        return "tools"
    return END

# Build the ReAct graph manually
workflow = StateGraph(PolicyExpertState)
workflow.add_node("agent", call_model)
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
