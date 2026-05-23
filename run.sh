#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

cleanup() {
  echo "Shutting down..."
  [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null
  exit 0
}
trap cleanup INT TERM

echo "=== AI Essay Detector ==="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 not found." >&2
  exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
  echo "Error: node not found." >&2
  exit 1
fi

# Backend setup
echo "[1/4] Setting up Python virtual environment..."
if [ ! -d "$BACKEND_DIR/venv" ]; then
  python3 -m venv "$BACKEND_DIR/venv"
fi
source "$BACKEND_DIR/venv/bin/activate"

echo "[2/4] Installing Python dependencies..."
pip install -q -r "$BACKEND_DIR/requirements.txt"

echo "[3/4] Downloading spaCy model..."
python3 -m spacy download en_core_web_sm 2>/dev/null || true

echo "[4/4] Starting servers..."
echo ""

# Start backend
cd "$BACKEND_DIR"
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
cd "$PROJECT_DIR"

# Start frontend
cd "$FRONTEND_DIR"
npm install --silent 2>/dev/null
npm run dev &
FRONTEND_PID=$!
cd "$PROJECT_DIR"

echo ""
echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers."
echo ""

wait
