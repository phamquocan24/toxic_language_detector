#!/bin/bash
# Stop Dashboard Server

echo "🛑 Stopping Web Dashboard..."
echo ""

# Stop by PID file
if [ -f "logs/dashboard.pid" ]; then
    PID=$(cat logs/dashboard.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✅ Dashboard stopped (PID: $PID)"
        rm logs/dashboard.pid
    else
        echo "⚠️  Dashboard not running"
        rm logs/dashboard.pid
    fi
else
    # Try to find by port
    PID=$(lsof -ti:8080 2>/dev/null)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo "✅ Dashboard stopped (Port 8080)"
    else
        echo "⚠️  Dashboard not running"
    fi
fi

