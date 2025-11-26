#!/bin/bash
# Start All Services

set -e

echo "🚀 Starting Toxic Language Detector - Full Stack"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Create logs directory if not exists
mkdir -p logs

# Load REDIS_ENABLED from .env if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep REDIS_ENABLED | xargs)
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Start Redis
echo -e "${CYAN}📦 Starting Redis...${NC}"
if command -v redis-server &> /dev/null; then
    if check_port 6379; then
        echo -e "${GREEN}✅ Redis already running${NC}"
    else
        redis-server --daemonize yes
        echo -e "${GREEN}✅ Redis started${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Redis not found. Starting with Docker...${NC}"
    docker run -d -p 6379:6379 --name toxic-redis redis:alpine 2>/dev/null || echo "Docker not available"
fi

sleep 2

# Start Backend
echo ""
echo -e "${CYAN}🔧 Starting Backend API...${NC}"
if check_port 7860; then
    echo -e "${YELLOW}⚠️  Port 7860 already in use. Skipping backend...${NC}"
else
    # Auto-detect virtual environment
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        echo -e "${YELLOW}⚠️  Virtual environment not found. Using system Python...${NC}"
    fi
    
    nohup uvicorn app:app --host 0.0.0.0 --port 7860 > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > logs/backend.pid
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
fi

sleep 3

# Start Dashboard
echo ""
echo -e "${CYAN}🖥️  Starting Web Dashboard...${NC}"
if check_port 8080; then
    echo -e "${YELLOW}⚠️  Port 8080 already in use. Skipping dashboard...${NC}"
else
    cd webdashboard
    nohup php artisan serve --host=0.0.0.0 --port=8080 > ../logs/dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    echo $DASHBOARD_PID > ../logs/dashboard.pid
    cd ..
    echo -e "${GREEN}✅ Dashboard started (PID: $DASHBOARD_PID)${NC}"
fi

sleep 2

# Display status
echo ""
echo "=================================================="
echo -e "${GREEN}✅ All Services Started Successfully!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}📍 Service URLs:${NC}"
echo "   🔧 Backend API:     http://localhost:7860"
echo "   📚 API Docs:        http://localhost:7860/docs"
echo "   ❤️  Health Check:    http://localhost:7860/health"
echo "   🖥️  Web Dashboard:   http://localhost:8080"
if [ "$REDIS_ENABLED" = "True" ] || [ "$REDIS_ENABLED" = "true" ]; then
    echo "   💾 Redis:           localhost:6379 (enabled)"
else
    echo "   💾 Redis:           localhost:6379 (disabled - using in-memory)"
fi
echo ""
echo -e "${YELLOW}🔌 Browser Extension:${NC}"
echo "   📁 Load from:       $(pwd)/extension"
echo "   📖 Guide:           chrome://extensions/"
echo ""
echo -e "${YELLOW}📊 Monitoring:${NC}"
echo "   📈 Metrics:         http://localhost:7860/metrics"
echo "   📝 Backend Log:     tail -f logs/backend.log"
echo "   📝 Dashboard Log:   tail -f logs/dashboard.log"
echo ""
echo -e "${CYAN}To stop all services, run:${NC}"
echo "   ./scripts/stop-all.sh"
echo ""

# Create stop script
cat > scripts/stop-all.sh << 'EOF'
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
EOF

chmod +x scripts/stop-all.sh

