import streamlit as st
import time
import requests
import uuid
import os
from pathlib import Path
import random
import string
from datetime import datetime

from utils import generate_short_id, fetch_sessions, fetch_chat_history, send_chat_message, upload_document

st.set_page_config(page_title="Policy Agent", page_icon="📄", layout="wide")

# Initialize session state variables
if "thread_id" not in st.session_state:
    st.session_state.thread_id = generate_short_id()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = str(uuid.uuid4())

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #D04A02; 
        }
        
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: #000000 !important;
            font-weight: 600; /* Makes typography crisp and readable */
        }

        [data-testid="stSidebar"] code {
            background-color: #FFFFFF !important; /* Crisp white background */
            color: #1E1E1E !important;            /* Dark charcoal text */
            border: 1px solid #000000 !important; /* Clean black border */
            font-weight: 700 !important;          /* Bold code text */
            padding: 4px 8px !important;          /* Extra spacing */
            border-radius: 4px;
        }

        [data-testid="stSidebar"] [data-testid="stAlert"] {
            background-color: #F5F5DC !important; /* Bright beige background */
            border: 1px solid #000000 !important; /* Clean black border */
            border-radius: 8px !important;        /* Rounded edges */
            color: #000000 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar configuration for document uploading and session management
with st.sidebar:
    st.title("Enterprise Policy Agent")
    
    st.header("Upload Policy Document")
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data" / "input"
    pending_files = []
    
    # Check for pending ingestions to lock the uploader
    if DATA_DIR.exists():
        pending_files = list(DATA_DIR.glob("*.pdf"))
        
    is_locked = bool(pending_files)
    
    if is_locked:
        st.warning("Files are pending ingestion. Please ask the agent to process them before uploading more.")
        
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True, disabled=is_locked, key=st.session_state.uploader_key)
        
    if uploaded_files:
        if st.button("Upload to Agent", disabled=is_locked):
            # Handle document upload process
            with st.spinner("Uploading..."):
                all_success = True
                for uploaded_file in uploaded_files:
                    result = upload_document(uploaded_file)
                    if not result:
                        all_success = False
                if all_success:
                    st.success("Files uploaded successfully! Ask the agent to ingest them.")
                    time.sleep(1.5)
                    st.session_state.uploader_key = str(uuid.uuid4())
                    st.rerun()
    
    st.divider()
    
    st.header("Chat Sessions")
    
    if st.button("➕ New Chat Session"):
        # Reset session state for a new chat
        st.session_state.thread_id = generate_short_id()
        st.session_state.messages = []
        st.session_state.uploader_key = str(uuid.uuid4())
        if DATA_DIR.exists():
            for f in DATA_DIR.glob("*.pdf"):
                try:
                    import os
                    os.remove(f)
                except:
                    pass
        st.rerun()
        
    sessions = fetch_sessions()
    if sessions:
        # Render history dropdown and handle session switching
        options = sessions if st.session_state.thread_id in sessions else [st.session_state.thread_id] + sessions
        
        selected_session = st.selectbox(
            "Select a past session:",
            options=options,
            index=options.index(st.session_state.thread_id) if st.session_state.thread_id in options else 0
        )
        
        if selected_session != st.session_state.thread_id:
            st.session_state.thread_id = selected_session
            st.session_state.messages = fetch_chat_history(selected_session)
            st.session_state.uploader_key = str(uuid.uuid4())
            if DATA_DIR.exists():
                for f in DATA_DIR.glob("*.pdf"):
                    try:
                        import os
                        os.remove(f)
                    except:
                        pass
            st.rerun()
            
    st.caption(f"Current Thread ID:\n`{st.session_state.thread_id}`")


st.title("Policy Assistant")
st.markdown("An advanced AI agent for comprehensive document analysis, policy compliance verification, and intelligent querying across your enterprise knowledge base.")

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["type"]):
        st.markdown(msg["content"])

# Process new user input
if prompt := st.chat_input("Ask a question about the enterprise policies..."):
    st.chat_message("human").markdown(prompt)
    st.session_state.messages.append({"type": "human", "content": prompt})

    with st.chat_message("ai"):
        with st.spinner("Agent is thinking..."):
            responses = send_chat_message(st.session_state.thread_id, prompt)
            
            if responses:
                combined_response = "\n\n".join(responses)
                st.session_state.messages.append({"type": "ai", "content": combined_response})
                st.rerun()
