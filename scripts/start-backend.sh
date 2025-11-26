#!/bin/bash
# Start Backend Server

set -e

echo "🚀 Starting Toxic Language Detector Backend..."
echo ""

# Create logs directory if not exists
mkdir -p logs

# Check and activate virtual environment
echo "📦 Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Using .venv"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Using venv"
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
    echo "✅ Using .venv (Windows)"
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    echo "✅ Using venv (Windows)"
else
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv .venv"
    echo "Then: pip install -r requirements.txt"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found! Creating from example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your settings."
fi

# Check if Redis is running (optional)
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running (optional, but recommended)"
        echo "   Start with: redis-server"
    fi
else
    echo "ℹ️  Redis not installed (optional)"
fi

# Run migrations if needed
echo ""
echo "🗄️  Checking database migrations..."
python -m backend.db.migrations.add_performance_indexes 2>/dev/null || echo "Migrations already applied"

# Start server
echo ""
echo "🔧 Starting server on http://0.0.0.0:7860"
echo ""
echo "📍 Available endpoints:"
echo "   API:        http://localhost:7860"
echo "   Health:     http://localhost:7860/health"
echo "   Docs:       http://localhost:7860/docs"
echo "   Metrics:    http://localhost:7860/metrics"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start with uvicorn
python run_server.py

# Or use this for production:
# gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:7860

