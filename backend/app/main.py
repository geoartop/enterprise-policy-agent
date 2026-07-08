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

# Configure Loguru to save logs to a file (creates a new file every day or if it hits 50MB)
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

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve project root and data directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads a PDF file to the data/raw directory."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / file.filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Return the relative path from the project root that the ingestion tool expects
    relative_path = f"data/raw/{file.filename}"
    return {"filename": file.filename, "path": relative_path, "message": "File uploaded successfully"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Sends a message to the LangGraph agent and returns its responses."""
    
    # We must include next_agent to satisfy the TypedDict if required
    state = {"messages": [HumanMessage(content=request.message)], "next_agent": ""}
    config = {"configurable": {"thread_id": request.thread_id}, "recursion_limit": 50}
    
    response_messages = []
    
    try:
        with logger.contextualize(session_id=request.thread_id):
            logger.info(f"Processing chat request for session: {request.thread_id}")
            # Stream the agent's execution
            for event in agent_graph.stream(state, config=config):
                for node_name, state_update in event.items():
                    if "messages" in state_update and len(state_update["messages"]) > 0:
                        latest_msg = state_update["messages"][-1]
                        
                        # Safer checking in case latest_msg is a dict or an object
                        is_ai = getattr(latest_msg, "type", None) == "ai" or (isinstance(latest_msg, dict) and latest_msg.get("type") == "ai")
                        content = getattr(latest_msg, "content", None) or (isinstance(latest_msg, dict) and latest_msg.get("content"))
                        
                        if is_ai and content:
                            if isinstance(content, list):
                                # Handle Gemini's list of blocks format
                                text_parts = []
                                for part in content:
                                    if isinstance(part, dict) and "text" in part:
                                        text_parts.append(part["text"])
                                    elif isinstance(part, str):
                                        text_parts.append(part)
                                content_str = "\n".join(text_parts)
                                response_messages.append(content_str)
                            else:
                                # Handle standard string content
                                response_messages.append(str(content))
                            
            return ChatResponse(messages=response_messages)
            
    except Exception as e:
        error_details = traceback.format_exc()
        with logger.contextualize(session_id=request.thread_id):
            logger.error(f"CRITICAL ERROR IN AGENT: {error_details}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}\n\nTraceback: {error_details}")
