import os
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.endpoints import chat, sessions, upload

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
    """
    Custom log sink to separate agent execution logs by session thread.
    
    Args:
        message (loguru.Message): The log message object containing record details.
    """
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

app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
