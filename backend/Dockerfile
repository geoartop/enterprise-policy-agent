FROM python:3.12-slim

# Install system dependencies (e.g. for building C extensions or interacting with psycopg2)
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install Python dependencies from requirements.txt
COPY backend/requirements.txt /tmp/backend_requirements.txt
COPY frontend/requirements.txt /tmp/frontend_requirements.txt
RUN pip install --no-cache-dir -r /tmp/backend_requirements.txt -r /tmp/frontend_requirements.txt
