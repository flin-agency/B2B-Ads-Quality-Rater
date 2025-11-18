#!/bin/bash

# ========================================
# Ads Quality Rater - Quickstart Script
# ========================================

set -e  # Exit on error

echo "🎯 Starting Ads Quality Rater..."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and add your GEMINI_API_KEY"
    exit 1
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=AIza" .env; then
    echo "⚠️  Warning: GEMINI_API_KEY might not be set correctly in .env"
    echo "Make sure to add your Gemini API key!"
fi

echo "📦 Installing dependencies..."
echo ""

# Backend dependencies
echo "→ Backend (Python)..."
cd backend
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
cd ..

# Frontend dependencies
echo "→ Frontend (Node.js)..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
cd ..

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "🚀 Starting servers..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

# Start backend
echo "→ Backend: http://localhost:8000"
cd backend
source venv/bin/activate
python3 -m uvicorn src.api.main:app --reload --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "→ Frontend: http://localhost:3000"
cd frontend
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All servers running!"
echo ""
echo "📝 Open http://localhost:3000 in your browser"
echo "📚 API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
wait
