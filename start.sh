#!/bin/bash

echo "============================================================"
echo "B2B Data Fusion Engine - Startup Script"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    echo "Then: source venv/bin/activate"
    echo "Then: pip install -r requirements.txt"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "[ERROR] Frontend dependencies not installed!"
    echo "Please run: cd frontend"
    echo "Then: npm install"
    exit 1
fi

echo "[1/2] Starting Flask API Server..."
echo ""

# Activate virtual environment and start backend
source venv/bin/activate
python api_server.py &
BACKEND_PID=$!

sleep 3

echo ""
echo "[2/2] Starting React Frontend..."
echo ""

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "============================================================"
echo "✅ Both servers are running!"
echo "============================================================"
echo ""
echo "Backend API:  http://localhost:5000"
echo "Frontend App: http://localhost:3000"
echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "============================================================"
echo ""

# Wait for user to press Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
