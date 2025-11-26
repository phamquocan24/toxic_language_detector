#!/bin/bash
# Stop Backend Server

echo "🛑 Stopping Backend API..."
echo ""

# Stop by PID file
if [ -f "logs/backend.pid" ]; then
    PID=$(cat logs/backend.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✅ Backend stopped (PID: $PID)"
        rm logs/backend.pid
    else
        echo "⚠️  Backend not running"
        rm logs/backend.pid
    fi
else
    # Try to find by port
    PID=$(lsof -ti:7860 2>/dev/null)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo "✅ Backend stopped (Port 7860)"
    else
        echo "⚠️  Backend not running"
    fi
fi

