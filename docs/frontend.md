# Frontend Documentation

The frontend is a lightweight, interactive web application built with **Streamlit**. It is located in `frontend/app.py`.

## Key Features

1. **Chat Interface:**
   The main panel displays the chat history and provides an input box for the user to ask questions. It uses Streamlit's native `st.chat_message` elements.

2. **Sidebar - Document Upload:**
   Allows users to select and upload multiple PDF files. The sidebar automatically checks if there are pending files in the `data/input` directory and temporarily locks the upload button to prevent overlapping ingestion requests. When a file is uploaded, it calls the backend `/api/upload` endpoint.

3. **Sidebar - Session Management:**
   Users can start a new chat session or select a previous one from a dropdown menu. When a session is selected, the frontend queries the `/api/chat/{thread_id}/history` endpoint to reload the conversation context.

## Integration Details
- **State Management:** Uses `st.session_state` to keep track of the current `thread_id`, the active `messages` array, and an `uploader_key` to reset the file uploader widget after a successful upload.
- **API Calls:** The `frontend/utils.py` file contains helper functions that use the `requests` library to communicate with the FastAPI backend.
- **Styling:** Custom CSS is injected to give the sidebar a distinct, branded appearance (e.g., custom background colors, distinct code block styles, and customized alerts).
