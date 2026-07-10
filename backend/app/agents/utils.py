from langgraph.graph import END
from langchain_core.messages import SystemMessage

def create_call_model(llm_with_tools, system_prompt_text):
    """
    Creates a call_model function for an agent that binds the given LLM and system prompt.
    
    Args:
        llm_with_tools: The language model bound with specific tools.
        system_prompt_text: The system prompt text to guide the agent.
        
    Returns:
        Callable: A call_model function that takes a state and returns updated messages.
    """
    def call_model(state: dict):
        messages = state["messages"]
        sys_msg = SystemMessage(content=system_prompt_text)
        # The LLM receives the system message plus the conversation history
        response = llm_with_tools.invoke([sys_msg] + list(messages))
        return {"messages": [response]}
    
    return call_model

def should_continue(state: dict):
    """
    Determines whether the workflow should continue to the tools node or end.
    
    Args:
        state (dict): The current conversation state containing messages.
        
    Returns:
        str: "tools" if the last message contains tool calls, otherwise END.
    """
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, 'tool_calls', None):
        return "tools"
    return END
