# 🚀 HƯỚNG DẪN SETUP VÀ CHẠY TOÀN BỘ HỆ THỐNG

## 📋 MỤC LỤC
1. [Backend (API + Database + AI Model)](#1-backend-api--database--ai-model)
2. [Web Dashboard (Laravel/PHP)](#2-web-dashboard-laravelphp)
3. [Browser Extension (Chrome)](#3-browser-extension-chrome)
4. [Full System Deployment](#4-full-system-deployment)

---

## 1️⃣ BACKEND (API + Database + AI Model)

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Check if pip is installed
pip --version

# Optional: Redis for caching (recommended)
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt install redis-server
# Mac: brew install redis
```

---

### Step 1: Setup Environment

```bash
# Clone repository (if not already)
git clone https://github.com/your-repo/toxic-language-detector.git
cd toxic-language-detector

# Create virtual environment
python -m venv venv

# Activate virtual environment
## Windows:
venv\Scripts\activate
## Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 2: Configure Environment Variables

```bash
# Create .env file from example
cp .env.example .env

# Edit .env file (use notepad, vim, or any editor)
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Cấu hình tối thiểu trong `.env`**:
```bash
# API Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
EXTENSION_API_KEY=your-extension-api-key-change-this

# Database
DATABASE_URL=sqlite:///./toxic_detector.db
# Or PostgreSQL for production:
# DATABASE_URL=postgresql://user:password@localhost:5432/toxic_detector

# Redis (Optional - improves performance 10x)
REDIS_ENABLED=False
# Set to True if Redis is running:
# REDIS_ENABLED=True
# REDIS_URL=redis://localhost:6379/0

# ML Model
MODEL_PATH=model/best_model_LSTM.h5
MODEL_VOCAB_PATH=model/tokenizer.pkl
MODEL_CONFIG_PATH=model/config.json
MODEL_PRELOAD=True

# Admin Account
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-this-password-123
```

---

### Step 3: Download/Setup AI Models

```bash
# Option A: Use existing models (if provided)
# Make sure these files exist:
ls -la model/
# Should see:
# - best_model_LSTM.h5 (or .safetensors)
# - tokenizer.pkl
# - config.json

# Option B: Download from cloud storage (if shared)
# Example with wget:
wget https://your-storage-url/models.zip -O models.zip
unzip models.zip -d model/

# Option C: Use dummy model for testing (automatically created if missing)
# Just start the app and it will create a dummy model
```

---

### Step 4: Initialize Database

```bash
# Run database migrations (add indexes)
python -m backend.db.migrations.add_performance_indexes

# Expected output:
# 🚀 Starting Database Performance Index Migration
# ✅ Created index: idx_users_username
# ✅ Created index: idx_comments_platform
# ...
# ✅ Migration completed successfully!
```

---

### Step 5: Start Redis (Optional but Recommended)

```bash
# Option A: Using Docker (easiest)
docker run -d -p 6379:6379 --name redis redis:alpine

# Option B: Native installation
## Windows: Start Redis server from installation directory
redis-server.exe

## Linux:
sudo systemctl start redis-server
# or
redis-server

## Mac:
brew services start redis

# Test Redis connection
redis-cli ping
# Should return: PONG

# Update .env:
# REDIS_ENABLED=True
# REDIS_URL=redis://localhost:6379/0
```

---

### Step 6: Start Backend Server

```bash
# Development mode (with auto-reload)
python run_server.py

# Or using uvicorn directly:
uvicorn app:app --reload --host 0.0.0.0 --port 7860

# Production mode (with Gunicorn):
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:7860

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:7860
# INFO:     Application startup complete.
# ✅ ML Model loaded successfully
```

---

### Step 7: Verify Backend

```bash
# Open browser and test:
# http://localhost:7860              # API documentation
# http://localhost:7860/health       # Health check
# http://localhost:7860/docs         # Swagger UI
# http://localhost:7860/redoc        # ReDoc

# Or use curl:
curl http://localhost:7860/health

# Expected response:
# {"status":"healthy","model_loaded":true,"database":"connected"}
```

---

### Step 8: Run Tests (Optional)

```bash
# Install test dependencies (if not already)
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest -v

# Run with coverage
pytest --cov=backend --cov-report=html

# Open coverage report
# Windows:
start htmlcov/index.html
# Linux:
xdg-open htmlcov/index.html
# Mac:
open htmlcov/index.html
```

---

## 2️⃣ WEB DASHBOARD (Laravel/PHP)

### Prerequisites
```bash
# PHP 8.1+ required
php --version

# Composer required
composer --version

# Node.js 16+ required
node --version
npm --version

# MySQL/PostgreSQL
mysql --version
# or
psql --version
```

---

### Step 1: Setup Laravel Environment

```bash
# Navigate to dashboard directory
cd webdashboard

# Install PHP dependencies
composer install

# Install Node dependencies
npm install

# Copy environment file
cp .env.example .env

# Generate application key
php artisan key:generate
```

---

### Step 2: Configure Dashboard Environment

```bash
# Edit .env file
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Cấu hình trong `webdashboard/.env`**:
```bash
APP_NAME="Toxic Detector Dashboard"
APP_ENV=local
APP_KEY=base64:...  # Generated by php artisan key:generate
APP_DEBUG=true
APP_URL=http://localhost:8080

# Database Configuration
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=toxic_detector
DB_USERNAME=root
DB_PASSWORD=your_mysql_password

# Or use SQLite for development:
# DB_CONNECTION=sqlite
# DB_DATABASE=database/database.sqlite

# Backend API Configuration
API_BASE_URL=http://localhost:7860/api
API_KEY=your-extension-api-key-same-as-backend
API_TIMEOUT=30

# Cache & Session (Optional - use Redis)
CACHE_DRIVER=file
SESSION_DRIVER=file
# Or with Redis:
# CACHE_DRIVER=redis
# SESSION_DRIVER=redis
# REDIS_HOST=127.0.0.1
# REDIS_PORT=6379
```

---

### Step 3: Setup Database

```bash
# Create database (MySQL example)
mysql -u root -p
# In MySQL prompt:
CREATE DATABASE toxic_detector CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Or create SQLite database
touch database/database.sqlite

# Run migrations
php artisan migrate

# Seed database with sample data (optional)
php artisan db:seed
```

---

### Step 4: Build Frontend Assets

```bash
# Development build (with watch)
npm run dev

# Production build (optimized)
npm run build

# Expected output:
# ✓ built in XXXms
# ✓ Laravel Mix compiled successfully
```

---

### Step 5: Start Dashboard Server

```bash
# Start development server
php artisan serve --host=0.0.0.0 --port=8080

# Expected output:
# INFO  Server running on [http://0.0.0.0:8080].

# Alternative: Using Laravel Valet (Mac)
valet link toxic-detector
valet open

# Alternative: Using Apache/Nginx
# Configure virtual host pointing to webdashboard/public
```

---

### Step 6: Access Dashboard

```bash
# Open browser:
# http://localhost:8080

# Default login (if seeded):
# Username: admin@example.com
# Password: admin123

# Or create admin user:
php artisan tinker
# In tinker:
$user = new App\Models\User();
$user->name = 'Admin';
$user->email = 'admin@example.com';
$user->password = bcrypt('admin123');
$user->save();
```

---

### Step 7: Setup Queue Workers (Optional)

```bash
# Start queue worker for background jobs
php artisan queue:work

# Or use supervisor for production
# Create supervisor config: /etc/supervisor/conf.d/laravel-worker.conf
```

---

## 3️⃣ BROWSER EXTENSION (Chrome)

### Step 1: Configure Extension

```bash
# Navigate to extension directory
cd extension

# Edit configuration (if needed)
notepad background.js  # Windows
nano background.js     # Linux/Mac

# Update API endpoint:
const API_ENDPOINT = "http://localhost:7860";
# For production:
const API_ENDPOINT = "https://your-domain.com";
```

---

### Step 2: Load Extension for Development

```bash
# 1. Open Chrome browser
# 2. Go to: chrome://extensions/
# 3. Enable "Developer mode" (toggle in top-right)
# 4. Click "Load unpacked"
# 5. Select the "extension" folder
# 6. Extension should appear in toolbar

# Verify extension loaded:
# - Icon should appear in Chrome toolbar
# - Click icon to see popup
# - Check console for any errors (F12)
```

---

### Step 3: Test Extension

```bash
# 1. Go to Facebook.com or YouTube.com
# 2. Navigate to a post with comments
# 3. Extension should automatically scan comments
# 4. Toxic comments should be highlighted with colors:
#    - Green: Clean
#    - Orange: Offensive
#    - Red: Hate speech
#    - Gray: Spam
```

---

### Step 4: Package Extension for Production

```bash
# Navigate to extension directory
cd extension

# Option A: Create ZIP manually
## Windows PowerShell:
Compress-Archive -Path * -DestinationPath ../toxic-detector-extension.zip

## Linux/Mac:
zip -r ../toxic-detector-extension.zip ./* -x "*.git*" -x "node_modules/*"

# Option B: Use Chrome Packer
## Open Chrome: chrome://extensions/
## Click "Pack extension"
## Select extension directory
## Click "Pack Extension"
## Creates .crx file and private key

# Verify ZIP contents:
unzip -l toxic-detector-extension.zip
# Should contain:
# - manifest.json
# - background.js
# - content.js
# - popup/ folder
# - icons/ folder
# - utils/ folder
```

---

### Step 5: Publish to Chrome Web Store

```bash
# Prerequisites:
# 1. Google Developer Account ($5 one-time fee)
# 2. Chrome Web Store Developer Dashboard access
#    URL: https://chrome.google.com/webstore/devconsole/

# Publishing Steps:
```

**1. Register Developer Account**:
- Go to: https://chrome.google.com/webstore/devconsole/
- Pay $5 registration fee
- Accept developer agreement

**2. Create New Item**:
```bash
# In Developer Dashboard:
# 1. Click "New Item"
# 2. Upload toxic-detector-extension.zip
# 3. Wait for upload to complete
```

**3. Fill Store Listing**:
```bash
# Required Information:
Product Name: Toxic Language Detector
Description: Automatically detects and highlights toxic comments on social media
Category: Social & Communication
Language: Vietnamese (or English)

# Icon Requirements:
# - 128x128 pixels (main icon)
# - 440x280 pixels (small promo tile)
# - 920x680 pixels (large promo tile)
# - 1400x560 pixels (marquee promo tile)

# Screenshots:
# - At least 1, maximum 5
# - 1280x800 or 640x400 pixels
```

**4. Privacy & Permissions**:
```bash
# Single purpose description:
"This extension detects toxic language in social media comments"

# Permission justifications:
# - storage: "Store user settings and statistics"
# - activeTab: "Scan comments on current tab"
# - scripting: "Inject content scripts to analyze comments"

# Host permissions justification:
# - facebook.com: "Analyze Facebook comments"
# - youtube.com: "Analyze YouTube comments"  
# - twitter.com/x.com: "Analyze Twitter comments"
```

**5. Submit for Review**:
```bash
# 1. Click "Submit for review"
# 2. Review can take 1-3 business days
# 3. You'll receive email notification
# 4. If approved, extension goes live automatically
```

**6. Update Extension**:
```bash
# For updates:
# 1. Increment version in manifest.json
# 2. Create new ZIP
# 3. Upload to same item in dashboard
# 4. Submit for review again
```

---

### Extension Package Script (Automated)

Create `package-extension.sh`:
```bash
#!/bin/bash
# Package extension for Chrome Web Store

echo "🚀 Packaging Toxic Language Detector Extension..."

# Set variables
VERSION=$(grep -oP '"version":\s*"\K[^"]+' extension/manifest.json)
OUTPUT_NAME="toxic-detector-v${VERSION}.zip"

# Navigate to extension directory
cd extension

# Remove old build if exists
rm -f "../${OUTPUT_NAME}"

# Create ZIP excluding unnecessary files
zip -r "../${OUTPUT_NAME}" . \
  -x "*.git*" \
  -x "*.DS_Store" \
  -x "node_modules/*" \
  -x "*.md" \
  -x "*.sh"

# Return to root
cd ..

# Show result
if [ -f "${OUTPUT_NAME}" ]; then
  echo "✅ Extension packaged successfully!"
  echo "📦 File: ${OUTPUT_NAME}"
  echo "📊 Size: $(du -h ${OUTPUT_NAME} | cut -f1)"
  echo ""
  echo "Next steps:"
  echo "1. Go to: https://chrome.google.com/webstore/devconsole/"
  echo "2. Upload ${OUTPUT_NAME}"
  echo "3. Fill in store listing details"
  echo "4. Submit for review"
else
  echo "❌ Packaging failed!"
  exit 1
fi
```

Make it executable:
```bash
chmod +x package-extension.sh
./package-extension.sh
```

Windows PowerShell version (`package-extension.ps1`):
```powershell
# Package extension for Chrome Web Store

Write-Host "🚀 Packaging Toxic Language Detector Extension..." -ForegroundColor Green

# Get version from manifest
$manifest = Get-Content "extension/manifest.json" | ConvertFrom-Json
$version = $manifest.version
$outputName = "toxic-detector-v$version.zip"

# Remove old build
if (Test-Path $outputName) {
    Remove-Item $outputName
}

# Create ZIP
Compress-Archive -Path "extension/*" -DestinationPath $outputName -Force `
    -Exclude "*.git*", "*.DS_Store", "node_modules", "*.md", "*.sh"

# Show result
if (Test-Path $outputName) {
    Write-Host "✅ Extension packaged successfully!" -ForegroundColor Green
    Write-Host "📦 File: $outputName" -ForegroundColor Cyan
    Write-Host "📊 Size: $((Get-Item $outputName).Length / 1KB) KB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://chrome.google.com/webstore/devconsole/"
    Write-Host "2. Upload $outputName"
    Write-Host "3. Fill in store listing details"
    Write-Host "4. Submit for review"
} else {
    Write-Host "❌ Packaging failed!" -ForegroundColor Red
    exit 1
}
```

Run it:
```powershell
.\package-extension.ps1
```

---

## 4️⃣ FULL SYSTEM DEPLOYMENT

### Development Environment (All-in-One)

**Script: `start-dev.sh`** (Linux/Mac):
```bash
#!/bin/bash

echo "🚀 Starting Toxic Language Detector - Development Environment"

# Start Redis
echo "📦 Starting Redis..."
redis-server --daemonize yes

# Start Backend
echo "🔧 Starting Backend API..."
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 7860 &
BACKEND_PID=$!

# Start Dashboard
echo "🖥️  Starting Web Dashboard..."
cd webdashboard
php artisan serve --host=0.0.0.0 --port=8080 &
DASHBOARD_PID=$!

# Wait a bit for services to start
sleep 3

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Services:"
echo "   Backend API:    http://localhost:7860"
echo "   API Docs:       http://localhost:7860/docs"
echo "   Web Dashboard:  http://localhost:8080"
echo "   Redis:          localhost:6379"
echo ""
echo "🔌 Extension:"
echo "   Load from: $(pwd)/../extension"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for interrupt
trap "kill $BACKEND_PID $DASHBOARD_PID; redis-cli shutdown; exit" INT
wait
```

**Script: `start-dev.ps1`** (Windows):
```powershell
Write-Host "🚀 Starting Toxic Language Detector - Development Environment" -ForegroundColor Green

# Start Redis (if Docker is available)
Write-Host "📦 Starting Redis..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "docker run -d -p 6379:6379 --name redis redis:alpine" -WindowStyle Hidden

# Start Backend
Write-Host "🔧 Starting Backend API..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList {
    Set-Location $PSScriptRoot
    .\venv\Scripts\Activate.ps1
    uvicorn app:app --reload --host 0.0.0.0 --port 7860
}

# Start Dashboard
Write-Host "🖥️  Starting Web Dashboard..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList {
    Set-Location "$PSScriptRoot\webdashboard"
    php artisan serve --host=0.0.0.0 --port=8080
}

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Services:" -ForegroundColor Yellow
Write-Host "   Backend API:    http://localhost:7860"
Write-Host "   API Docs:       http://localhost:7860/docs"
Write-Host "   Web Dashboard:  http://localhost:8080"
Write-Host "   Redis:          localhost:6379"
Write-Host ""
Write-Host "🔌 Extension:" -ForegroundColor Yellow
Write-Host "   Load from: $PSScriptRoot\extension"
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop services..."
```

---

### Production Deployment (Docker Compose)

**`docker-compose.yml`**:
```yaml
version: '3.8'

services:
  # Redis Cache
  redis:
    image: redis:alpine
    container_name: toxic-detector-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    container_name: toxic-detector-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: toxic_detector
      POSTGRES_USER: toxic_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Backend API
  backend:
    build: .
    container_name: toxic-detector-backend
    restart: unless-stopped
    ports:
      - "7860:7860"
    environment:
      DATABASE_URL: postgresql://toxic_user:${DB_PASSWORD}@postgres:5432/toxic_detector
      REDIS_ENABLED: "True"
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      EXTENSION_API_KEY: ${EXTENSION_API_KEY}
    volumes:
      - ./model:/app/model:ro
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres

  # Web Dashboard
  dashboard:
    build: ./webdashboard
    container_name: toxic-detector-dashboard
    restart: unless-stopped
    ports:
      - "8080:80"
    environment:
      DB_CONNECTION: pgsql
      DB_HOST: postgres
      DB_PORT: 5432
      DB_DATABASE: toxic_detector
      DB_USERNAME: toxic_user
      DB_PASSWORD: ${DB_PASSWORD}
      API_BASE_URL: http://backend:7860/api
    depends_on:
      - postgres
      - backend

volumes:
  redis_data:
  postgres_data:
```

**Deploy with Docker Compose**:
```bash
# Create .env file for Docker Compose
cat > .env << EOF
DB_PASSWORD=your_secure_password
SECRET_KEY=your-super-secret-key-min-32-chars
EXTENSION_API_KEY=your-extension-api-key
EOF

# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 📊 VERIFICATION CHECKLIST

### Backend ✅
- [ ] `http://localhost:7860/health` returns `{"status":"healthy"}`
- [ ] `http://localhost:7860/docs` shows Swagger UI
- [ ] Redis connection: `redis-cli ping` returns `PONG`
- [ ] Database indexes created: Check migration output
- [ ] Model loaded: Check startup logs

### Dashboard ✅
- [ ] `http://localhost:8080` loads login page
- [ ] Can login with admin credentials
- [ ] Dashboard shows statistics
- [ ] API connection working (check dashboard)

### Extension ✅
- [ ] Extension loads without errors
- [ ] Icon appears in Chrome toolbar
- [ ] Popup opens and shows settings
- [ ] Comments are scanned on Facebook/YouTube
- [ ] Toxic comments are highlighted

---

## 🐛 TROUBLESHOOTING

### Backend Issues

**Port already in use**:
```bash
# Find process using port
## Linux/Mac:
lsof -i :7860
kill -9 <PID>

## Windows:
netstat -ano | findstr :7860
taskkill /PID <PID> /F
```

**Model not loading**:
```bash
# Check model files exist
ls -la model/

# Test with dummy model
# Remove MODEL_PATH from .env
# App will create dummy model automatically
```

**Database connection failed**:
```bash
# SQLite: Check file path and permissions
ls -la toxic_detector.db

# PostgreSQL: Test connection
psql -U toxic_user -d toxic_detector -h localhost
```

### Dashboard Issues

**Laravel error 500**:
```bash
# Check Laravel logs
tail -f webdashboard/storage/logs/laravel.log

# Clear cache
php artisan cache:clear
php artisan config:clear
php artisan view:clear
```

**Assets not loading**:
```bash
# Rebuild assets
npm run build

# Check public/build directory
ls -la webdashboard/public/build/
```

### Extension Issues

**Extension not loading**:
```bash
# Check manifest.json syntax
cat extension/manifest.json | jq .

# View extension errors
# Chrome → Extensions → Details → Errors
```

**API calls failing**:
```bash
# Check CORS settings in backend
# Open browser console (F12)
# Look for CORS errors

# Test API directly
curl http://localhost:7860/health
```

---

## 📚 ADDITIONAL RESOURCES

- **Backend API Docs**: http://localhost:7860/docs
- **System Architecture**: See `SYSTEM_ARCHITECTURE.md`
- **Improvements Guide**: See `IMPROVEMENTS_SUMMARY.md`
- **Quick Start**: See `QUICK_START_IMPROVEMENTS.md`

---

*Last Updated: 2025-10-19*
*Version: 1.0.0*

