# Start All Services (Windows PowerShell)

Write-Host "🚀 Starting Toxic Language Detector - Full Stack" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Start Redis
Write-Host "📦 Starting Redis..." -ForegroundColor Cyan
if (Get-Command redis-server -ErrorAction SilentlyContinue) {
    if (Test-Port 6379) {
        Write-Host "✅ Redis already running" -ForegroundColor Green
    } else {
        Start-Process redis-server -WindowStyle Hidden
        Write-Host "✅ Redis started" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Redis not found. Starting with Docker..." -ForegroundColor Yellow
    try {
        docker run -d -p 6379:6379 --name toxic-redis redis:alpine 2>$null
        Write-Host "✅ Redis started in Docker" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Docker not available. Please install Redis or Docker." -ForegroundColor Yellow
    }
}

Start-Sleep -Seconds 2

# Start Backend
Write-Host ""
Write-Host "🔧 Starting Backend API..." -ForegroundColor Cyan
if (Test-Port 7860) {
    Write-Host "⚠️  Port 7860 already in use. Skipping backend..." -ForegroundColor Yellow
} else {
    Start-Process powershell -ArgumentList {
        Set-Location $args[0]
        & ".\venv\Scripts\Activate.ps1"
        uvicorn app:app --host 0.0.0.0 --port 7860
    } -ArgumentList $PSScriptRoot\..
    
    Write-Host "✅ Backend starting..." -ForegroundColor Green
}

Start-Sleep -Seconds 3

# Start Dashboard
Write-Host ""
Write-Host "🖥️  Starting Web Dashboard..." -ForegroundColor Cyan
if (Test-Port 8080) {
    Write-Host "⚠️  Port 8080 already in use. Skipping dashboard..." -ForegroundColor Yellow
} else {
    Start-Process powershell -ArgumentList {
        Set-Location "$($args[0])\webdashboard"
        php artisan serve --host=0.0.0.0 --port=8080
    } -ArgumentList $PSScriptRoot\..
    
    Write-Host "✅ Dashboard starting..." -ForegroundColor Green
}

Start-Sleep -Seconds 2

# Display status
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "✅ All Services Started Successfully!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Service URLs:" -ForegroundColor Yellow
Write-Host "   🔧 Backend API:     http://localhost:7860" -ForegroundColor White
Write-Host "   📚 API Docs:        http://localhost:7860/docs" -ForegroundColor White
Write-Host "   ❤️  Health Check:    http://localhost:7860/health" -ForegroundColor White
Write-Host "   🖥️  Web Dashboard:   http://localhost:8080" -ForegroundColor White
Write-Host "   💾 Redis:           localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "🔌 Browser Extension:" -ForegroundColor Yellow
Write-Host "   📁 Load from:       $PSScriptRoot\..\extension" -ForegroundColor White
Write-Host "   📖 Guide:           chrome://extensions/" -ForegroundColor White
Write-Host ""
Write-Host "📊 Monitoring:" -ForegroundColor Yellow
Write-Host "   📈 Metrics:         http://localhost:7860/metrics" -ForegroundColor White
Write-Host ""
Write-Host "To stop all services:" -ForegroundColor Cyan
Write-Host "   Close all PowerShell windows" -ForegroundColor White
Write-Host "   Or run: .\scripts\stop-all.ps1" -ForegroundColor White
Write-Host ""

# Create stop script
$stopScript = @'
# Stop All Services (Windows PowerShell)

Write-Host "🛑 Stopping all services..." -ForegroundColor Yellow

# Stop processes on specific ports
$ports = @(7860, 8080, 6379)

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Stop-Process -Id $process.Id -Force
                Write-Host "✅ Stopped process on port $port" -ForegroundColor Green
            }
        }
    }
}

# Stop Docker Redis
try {
    docker stop toxic-redis 2>$null
    docker rm toxic-redis 2>$null
    Write-Host "✅ Docker Redis stopped" -ForegroundColor Green
} catch {
    # Ignore if not running
}

Write-Host "✅ All services stopped" -ForegroundColor Green
'@

$stopScript | Out-File -FilePath "$PSScriptRoot\stop-all.ps1" -Encoding UTF8

Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

