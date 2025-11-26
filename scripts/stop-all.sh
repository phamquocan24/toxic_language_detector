#!/bin/bash
# Stop All Services

echo "🛑 Stopping all services..."

# Stop backend
if [ -f logs/backend.pid ]; then
    kill $(cat logs/backend.pid) 2>/dev/null && echo "✅ Backend stopped"
    rm logs/backend.pid
fi

# Stop dashboard
if [ -f logs/dashboard.pid ]; then
    kill $(cat logs/dashboard.pid) 2>/dev/null && echo "✅ Dashboard stopped"
    rm logs/dashboard.pid
fi

# Stop Redis
redis-cli shutdown 2>/dev/null && echo "✅ Redis stopped" || echo "Redis not running"

# Stop Docker Redis
docker stop toxic-redis 2>/dev/null && docker rm toxic-redis 2>/dev/null

echo "✅ All services stopped"
