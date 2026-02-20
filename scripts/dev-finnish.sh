#!/bin/bash

# Learning Finnish Development Script
# Starts both frontend and backend services

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting Learning Finnish Development Environment..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_service() {
    echo -e "${BLUE}Starting $1...${NC}"
}

print_ready() {
    echo -e "${GREEN}✓ $1 ready at $2${NC}"
}

# Check if already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
    echo "Backend already running on port 8000"
else
    print_service "Backend (Flask)"
    cd "$PROJECT_ROOT/learning_finnish/backend"
    
    # Create venv if needed
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate and run
    source venv/bin/activate
    flask run &
    BACKEND_PID=$!
    print_ready "Backend" "http://localhost:8000"
fi

# Frontend
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null; then
    echo "Frontend already running on port 5173"
else
    print_service "Frontend (Vite + React)"
    cd "$PROJECT_ROOT/learning_finnish"
    npm run dev &
    FRONTEND_PID=$!
    print_ready "Frontend" "http://localhost:5173"
fi

echo ""
echo "================================"
echo "Learning Finnish is running!"
echo "================================"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "API Base: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Wait for processes
if [ ! -z "$BACKEND_PID" ]; then
    wait $BACKEND_PID 2>/dev/null || true
fi

if [ ! -z "$FRONTEND_PID" ]; then
    wait $FRONTEND_PID 2>/dev/null || true
fi
