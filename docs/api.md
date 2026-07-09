# API Documentation

The FastAPI backend exposes several REST endpoints to facilitate communication with the frontend UI. All endpoints are grouped under the `/api` prefix.

## 1. Chat Endpoints

### `POST /api/chat`
The primary endpoint for interacting with the LangGraph agent.

- **Request Body:**
  ```json
  {
    "thread_id": "string (unique session ID)",
    "message": "string (user's input)"
  }
  ```
- **Response:**
  ```json
  {
    "messages": [
      "string (AI response paragraph 1)",
      "string (AI response paragraph 2)"
    ]
  }
  ```
- **Description:** Sends the user's message to the LangGraph supervisor, which routes it to the appropriate worker. It streams the execution graph and returns the final AI messages.

### `GET /api/chat/{thread_id}/history`
Retrieves the chat history for a given session.

- **Response:**
  ```json
  {
    "messages": [
      {
        "type": "human",
        "content": "Hello!"
      },
      {
        "type": "ai",
        "content": "Hi there. How can I help you with enterprise policies today?"
      }
    ]
  }
  ```
- **Description:** Accesses the PostgreSQL checkpoint saver to reconstruct the conversation history from the graph's state.

## 2. Session Management

### `GET /api/sessions`
Retrieves a list of all historical session IDs.

- **Response:**
  ```json
  {
    "sessions": ["session_id_1", "session_id_2"]
  }
  ```

## 3. Document Upload

### `POST /api/upload`
Accepts a PDF document upload to be placed in the `data/input` directory.

- **Request Body:** `multipart/form-data` containing the file.
- **Response:**
  ```json
  {
    "message": "File uploaded successfully",
    "filename": "policy.pdf"
  }
  ```
- **Description:** Saves the uploaded PDF locally so that the agent (specifically the Ingestion Worker) can parse and index it into pgvector when requested by the user.
