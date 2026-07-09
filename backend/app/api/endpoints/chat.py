import traceback
from fastapi import APIRouter, HTTPException
from loguru import logger
from langchain_core.messages import HumanMessage

from backend.app.api.schemas import ChatRequest, ChatResponse
from backend.app.agents.graph import app as agent_graph

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Primary endpoint for routing user messages to the LangGraph agent.
    
    Args:
        request (ChatRequest): The chat request object containing the user message and thread ID.
        
    Returns:
        ChatResponse: An object containing a list of strings representing the AI's response messages.
    """
    state = {"messages": [HumanMessage(content=request.message)], "next_agent": ""}
    config = {"configurable": {"thread_id": request.thread_id}, "recursion_limit": 50}
    
    response_messages = []
    
    try:
        with logger.contextualize(session_id=request.thread_id):
            logger.info(f"Processing chat request for session: {request.thread_id}")
            for event in agent_graph.stream(state, config=config):
                for node_name, state_update in event.items():
                    if "messages" in state_update and len(state_update["messages"]) > 0:
                        latest_msg = state_update["messages"][-1]
                        
                        is_ai = getattr(latest_msg, "type", None) == "ai" or (isinstance(latest_msg, dict) and latest_msg.get("type") == "ai")
                        content = getattr(latest_msg, "content", None) or (isinstance(latest_msg, dict) and latest_msg.get("content"))
                        
                        if is_ai and content:
                            if isinstance(content, list):
                                text_parts = []
                                for part in content:
                                    if isinstance(part, dict) and "text" in part:
                                         text_parts.append(part["text"])
                                    elif isinstance(part, str):
                                         text_parts.append(part)
                                content_str = "\n".join(text_parts)
                                response_messages.append(content_str)
                            else:
                                response_messages.append(str(content))
                            
            return ChatResponse(messages=response_messages)
            
    except Exception as e:
        error_details = traceback.format_exc()
        with logger.contextualize(session_id=request.thread_id):
            logger.error(f"CRITICAL ERROR IN AGENT: {error_details}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}\n\nTraceback: {error_details}")

@router.get("/chat/{thread_id}/history")
def get_chat_history(thread_id: str):
    """
    Reconstructs the message history for a specific agent thread.
    
    Args:
        thread_id (str): The unique identifier for the chat session.
        
    Returns:
        dict: A dictionary containing a list of formatted message objects with 'type' and 'content' keys.
    """
    config = {"configurable": {"thread_id": thread_id}}
    state = agent_graph.get_state(config)
    
    formatted_messages = []
    if state and hasattr(state, "values") and state.values and "messages" in state.values:
        for msg in state.values["messages"]:
            msg_type = getattr(msg, "type", None) or (isinstance(msg, dict) and msg.get("type"))
            
            # Only include human and ai messages (ignore system, tool, etc.)
            if msg_type not in ["human", "ai"]:
                continue
                
            content = getattr(msg, "content", None) or (isinstance(msg, dict) and msg.get("content"))
            
            if content:
                if isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and "text" in part:
                             text_parts.append(part["text"])
                        elif isinstance(part, str):
                             text_parts.append(part)
                    content_str = "\n".join(text_parts)
                else:
                    content_str = str(content)
                
                # Exclude AI messages that are empty after parsing or just contain tool call kwargs
                if content_str.strip():
                    formatted_messages.append({"type": msg_type, "content": content_str})
                
    return {"messages": formatted_messages}
