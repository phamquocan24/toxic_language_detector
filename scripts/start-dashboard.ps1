# Start Laravel Dashboard (Windows PowerShell)

Write-Host "🖥️  Starting Toxic Language Detector Dashboard..." -ForegroundColor Green
Write-Host ""

# Navigate to dashboard directory
Set-Location webdashboard

# Check if vendor directory exists
if (-not (Test-Path "vendor")) {
    Write-Host "📦 Installing PHP dependencies..." -ForegroundColor Cyan
    composer install
}

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing Node dependencies..." -ForegroundColor Cyan
    npm install
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found! Creating from example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    php artisan key:generate
    Write-Host "✅ Created .env file. Please configure database settings." -ForegroundColor Green
}

# Build assets if needed
if (-not (Test-Path "public/build")) {
    Write-Host "🎨 Building frontend assets..." -ForegroundColor Cyan
    npm run build
}

# Run migrations
Write-Host ""
Write-Host "🗄️  Running database migrations..." -ForegroundColor Cyan
try {
    php artisan migrate --force 2>$null
} catch {
    Write-Host "Migrations already applied" -ForegroundColor Gray
}

# Clear cache
Write-Host "🧹 Clearing cache..." -ForegroundColor Cyan
php artisan cache:clear
php artisan config:clear

# Start server
Write-Host ""
Write-Host "🚀 Starting Laravel development server..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 Dashboard URL: http://localhost:8080" -ForegroundColor Yellow
Write-Host "📍 Make sure Backend API is running on: http://localhost:7860" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

php artisan serve --host=0.0.0.0 --port=8080

