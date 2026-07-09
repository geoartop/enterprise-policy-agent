# Environment & Setup Guide

This project is fully containerized to ensure consistent development environments across different machines.

## Prerequisites
- **Docker** and **Docker Compose** installed.
- **VS Code** with the **Dev Containers** extension installed.

## Environment Variables

1. Copy the `.env.example` file to create your own `.env` file at the root of the project:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in the required values. Specifically, you will need to provide your generative AI API keys (e.g., Google Gemini or OpenAI) depending on the configuration you are using in the LangChain models. The database credentials usually have sensible defaults for local development.

## Launching the Dev Container

1. Open the project folder in VS Code.
2. A prompt should appear in the bottom right corner suggesting to **"Reopen in Container"**. Click it. Alternatively, open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`) and run `Dev Containers: Reopen in Container`.
3. VS Code will build the Docker image (using the root `Dockerfile`) and start the PostgreSQL database container (using `docker-compose.yml`).
4. Once loaded, you are inside an isolated Linux container with all Python requirements (for both frontend and backend) pre-installed.

## Running the Services

Because the Dev Container configuration uses a `sleep infinity` command, the services are not started automatically. You need to start them manually inside the container's integrated terminal.

1. **Start the Backend API:**
   Open a new terminal in VS Code and run:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0
   ```
   *The API will now be accessible from your host machine at `http://localhost:8000`.*

2. **Start the Frontend UI:**
   Open a second terminal in VS Code and run:
   ```bash
   streamlit run frontend/app.py
   ```
   *The UI will now be accessible from your host machine at `http://localhost:8501`.*
