# Enterprise Policy Agent

An advanced AI agent for comprehensive document analysis, policy compliance verification, and intelligent querying across your enterprise knowledge base.

This project is built using **FastAPI** for the backend, **Streamlit** for the frontend, and **LangGraph / LangChain** for the AI agent orchestration. It uses **PostgreSQL with pgvector** for storing embeddings and document data, enabling Retrieval-Augmented Generation (RAG) capabilities to answer questions accurately based on uploaded policy documents.

## Features

- **Conversational AI Interface:** Chat with the agent via a user-friendly Streamlit frontend.
- **Document Ingestion:** Upload PDF policy documents directly through the UI.
- **RAG Architecture:** Leverages LangChain and pgvector to securely store and retrieve policy information.
- **Session Management:** Keep track of past chat sessions and resume conversations seamlessly.
- **Unified Development Environment:** Fully containerized setup using VS Code Dev Containers and Docker Compose.

## Architecture

1. **Frontend (Streamlit):** Located in `frontend/`. Communicates with the backend API via HTTP. Provides UI for uploading PDFs and chatting with the AI.
2. **Backend (FastAPI):** Located in `backend/`. Exposes REST API endpoints (`/api/chat`, `/api/sessions`, `/api/upload`). Orchestrates LangGraph agents, handles RAG operations, and manages logging.
3. **Database (PostgreSQL + pgvector):** Runs in a Docker container (`policy_db`). Stores document embeddings, vectors, and chat history.

## Prerequisites

- **Docker & Docker Compose**
- **VS Code** (with the *Dev Containers* extension installed)
- An API key for the generative AI model (e.g., Google Gemini / OpenAI, depending on your `.env` configuration).

## Local Development Setup

This project uses a unified Docker environment for both the frontend and backend.

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd enterprise-policy-agent
   ```

2. **Set up environment variables:**
   Copy the example environment file and fill in your database credentials and API keys.
   ```bash
   cp .env.example .env
   ```

3. **Open in Dev Container:**
   - Open the project folder in VS Code.
   - When prompted, click **"Reopen in Container"** (or use the Command Palette: `Dev Containers: Reopen in Container`).
   - VS Code will build the Docker image (which includes both backend and frontend dependencies) and start the PostgreSQL database.

4. **Run the Application:**
   Once inside the Dev Container, open two separate terminal windows in VS Code.

   **Terminal 1: Start the Backend**
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0
   ```
   The API will be available at `http://localhost:8000/docs`

   **Terminal 2: Start the Frontend**
   ```bash
   streamlit run frontend/app.py
   ```
   The UI will be available at `http://localhost:8501`

## How to Use

1. Navigate to `http://localhost:8501` in your browser.
2. **Upload Documents:** Use the sidebar to upload PDF policy documents. Wait for the agent to ingest them.
3. **Ask Questions:** Use the chat interface to ask questions about the uploaded policies.
4. **Manage Sessions:** Use the dropdown in the sidebar to switch between different chat sessions.

## Project Structure

```text
enterprise-policy-agent/
├── backend/
│   ├── app/                # FastAPI application code
│   │   ├── agents/         # LangGraph agent definitions
│   │   ├── api/            # API routers (chat, sessions, upload)
│   │   ├── core/           # Core configurations
│   │   ├── services/       # Business logic (e.g., document parsing)
│   │   └── tools/          # Agent tools
│   ├── requirements.txt    # Backend Python dependencies
│   └── scripts/            # Utility scripts
├── frontend/
│   ├── app.py              # Main Streamlit application
│   ├── requirements.txt    # Frontend Python dependencies
│   └── utils.py            # API client and helper functions
├── data/                   # Directory for storing raw/uploaded data
├── docs/                   # Additional documentation
├── logs/                   # API and session logs
├── .devcontainer/          # VS Code Dev Container configuration
├── docker-compose.yml      # Docker Compose configuration (App + DB)
├── Dockerfile              # Unified Dockerfile for the Dev Container
└── README.md               # Project documentation (this file)
```
