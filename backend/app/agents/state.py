import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    The state of our LangGraph application. This state is passed 
    between all nodes (agents) in the graph.
    """
    
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # A string tracking which agent should run next, or 'FINISH' if we are done.
    next_agent: str
