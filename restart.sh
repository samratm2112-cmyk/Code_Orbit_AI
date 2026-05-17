#!/bin/bash
# ==============================================================================
# CodeOrbit AI - Restart Script
# Kills existing servers and starts fresh backend + frontend
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=================================================="
echo "  CodeOrbit AI - Restart"
echo "=================================================="
echo ""

# Kill existing processes
echo "Stopping existing servers..."
pkill -f "uvicorn backend.main" 2>/dev/null || true
pkill -f "streamlit run frontend/app" 2>/dev/null || true
sleep 2

# Activate venv
source venv/bin/activate

echo ""
echo "Starting backend (FastAPI)..."
echo "  → http://127.0.0.1:8000"
echo "  → http://127.0.0.1:8000/docs"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

echo ""
echo "Starting frontend (Streamlit)..."
echo "  → http://localhost:8501"
streamlit run frontend/app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "=================================================="
echo "  Both servers running!"
echo "  Backend  : http://127.0.0.1:8000"
echo "  API Docs : http://127.0.0.1:8000/docs"
echo "  Frontend : http://localhost:8501"
echo ""
echo "  Press Ctrl+C to stop both."
echo "=================================================="

# Wait for both
wait $BACKEND_PID $FRONTEND_PID
