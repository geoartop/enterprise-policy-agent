import os
import shutil
import traceback
from pathlib import Path
from loguru import logger
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from backend.app.api.schemas import ChatRequest, ChatResponse
from backend.app.agents.graph import app as agent_graph

# Configure structured logging with daily rotation and session-based filtering
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
os.makedirs(log_dir, exist_ok=True)
logger.add(
    os.path.join(log_dir, "api_{time:YYYY-MM-DD}.log"),
    rotation="50 MB",
    retention="7 days",
    level="DEBUG",
    filter=lambda record: "session_id" not in record["extra"]
)

session_files = {}

def session_sink(message):
    """Custom log sink to separate agent execution logs by session thread."""
    record = message.record
    session_id = record["extra"].get("session_id")
    if not session_id:
        return
    
    if session_id not in session_files:
        time_str = record["time"].strftime("%Y-%m-%d_%H-%M-%S")
        session_files[session_id] = os.path.join(log_dir, f"session_{session_id}_{time_str}.log")
        
    filepath = session_files[session_id]
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(message)

logger.add(session_sink, filter=lambda record: "session_id" in record["extra"], level="DEBUG")

app = FastAPI(title="Enterprise Policy Agent API")

# Enable cross-origin resource sharing for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "input"

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handles PDF uploads and writes them to the local data directory."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / file.filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    relative_path = f"data/input/{file.filename}"
    return {"filename": file.filename, "path": relative_path, "message": "File uploaded successfully"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Primary endpoint for routing user messages to the LangGraph agent."""
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

from backend.app.core.database import get_raw_connection_string
import psycopg

@app.get("/api/sessions")
def get_sessions():
    """Retrieves a list of distinct historical session IDs from the database."""
    conn_str = get_raw_connection_string()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT thread_id FROM checkpoints;")
                sessions = [row[0] for row in cur.fetchall()]
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return {"sessions": []}

@app.get("/api/chat/{thread_id}/history")
def get_chat_history(thread_id: str):
    """Reconstructs the message history for a specific agent thread."""
    config = {"configurable": {"thread_id": thread_id}}
    state = agent_graph.get_state(config)
    
    formatted_messages = []
    if state and hasattr(state, "values") and state.values and "messages" in state.values:
        for msg in state.values["messages"]:
            is_ai = getattr(msg, "type", None) == "ai" or (isinstance(msg, dict) and msg.get("type") == "ai")
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
                
                formatted_messages.append({"type": "ai" if is_ai else "human", "content": content_str})
                
    return {"messages": formatted_messages}
