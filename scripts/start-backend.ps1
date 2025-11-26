# Start Backend Server (Windows PowerShell)

Write-Host "🚀 Starting Toxic Language Detector Backend..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found! Creating from example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file. Please edit it with your settings." -ForegroundColor Green
}

# Check if Redis is running (optional)
try {
    $redisTest = & redis-cli ping 2>$null
    if ($redisTest -eq "PONG") {
        Write-Host "✅ Redis is running" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Redis is not running (optional, but recommended)" -ForegroundColor Yellow
    Write-Host "   Start with: redis-server or docker run -d -p 6379:6379 redis:alpine" -ForegroundColor Yellow
}

# Run migrations if needed
Write-Host ""
Write-Host "🗄️  Checking database migrations..." -ForegroundColor Cyan
try {
    python -m backend.db.migrations.add_performance_indexes 2>$null
} catch {
    Write-Host "Migrations already applied" -ForegroundColor Gray
}

# Start server
Write-Host ""
Write-Host "🔧 Starting server on http://0.0.0.0:7860" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Available endpoints:" -ForegroundColor Yellow
Write-Host "   API:        http://localhost:7860" -ForegroundColor White
Write-Host "   Health:     http://localhost:7860/health" -ForegroundColor White
Write-Host "   Docs:       http://localhost:7860/docs" -ForegroundColor White
Write-Host "   Metrics:    http://localhost:7860/metrics" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start with uvicorn
python run_server.py

# Or use this for production:
# gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:7860

