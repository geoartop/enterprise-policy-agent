import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage

from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The state of our LangGraph application. This state is passed 
    between all nodes (agents) in the graph.
    """
    
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # A string tracking which agent should run next, or 'FINISH' if we are done.
    next_agent: str

class PolicyExpertState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class IngestionWorkerState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
