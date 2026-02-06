#!/bin/bash
set -e

# Define ports
BACKEND_PORT=8000
FRONTEND_PORT=${PORT:-7860}

echo "Starting FastAPI backend on port $BACKEND_PORT..."
uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT &

# Optional: Wait a few seconds for backend to start
sleep 3

echo "Starting Streamlit frontend on port $FRONTEND_PORT..."
# Run Streamlit in foreground so the container stays alive as long as Streamlit is running
streamlit run frontend/app.py \
  --server.port=$FRONTEND_PORT \
  --server.address=0.0.0.0 \
  --server.headless=true
