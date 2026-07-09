import string
import random
from datetime import datetime
import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def generate_short_id():
    """
    Generates a unique 19-character session identifier.
    
    Returns:
        str: A unique session ID string based on random characters and timestamp.
    """
    chars = string.ascii_letters + string.digits
    rand_part = ''.join(random.choices(chars, k=5))
    dt_part = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{rand_part}_{dt_part}"

def fetch_sessions():
    """
    Retrieves historical chat sessions from the backend.
    
    Returns:
        list: A list of session ID strings retrieved from the backend.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/sessions")
        response.raise_for_status()
        return response.json().get("sessions", [])
    except Exception as e:
        st.error(f"Failed to fetch sessions: {e}")
        return []

def fetch_chat_history(thread_id):
    """
    Fetches the message history for a specific session.
    
    Args:
        thread_id (str): The unique identifier for the chat session.
        
    Returns:
        list: A list of message objects representing the conversation history.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/chat/{thread_id}/history")
        response.raise_for_status()
        return response.json().get("messages", [])
    except Exception as e:
        st.error(f"Failed to fetch chat history: {e}")
        return []

def send_chat_message(thread_id, message):
    """
    Sends a user message to the policy agent and retrieves the response.
    
    Args:
        thread_id (str): The unique identifier for the chat session.
        message (str): The text message from the user.
        
    Returns:
        list: A list of string responses from the AI.
    """
    try:
        payload = {"message": message, "thread_id": thread_id}
        response = requests.post(f"{API_BASE_URL}/api/chat", json=payload)
        response.raise_for_status()
        return response.json().get("messages", [])
    except Exception as e:
        st.error(f"Failed to send message: {e}")
        return []

def upload_document(file):
    """
    Uploads a PDF document for policy ingestion.
    
    Args:
        file: The file-like object uploaded by the user via Streamlit.
        
    Returns:
        dict or None: A dictionary containing upload metadata if successful, else None.
    """
    try:
        files = {"file": (file.name, file, "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/api/upload", files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to upload document: {e}")
        return None
