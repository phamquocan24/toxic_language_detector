# ⚡ QUICK REFERENCE - CHEAT SHEET

Tham khảo nhanh các lệnh thường dùng.

---

## 🚀 KHỞI ĐỘNG NHANH (5 PHÚT)

### Option 1: Sử dụng Makefile (Khuyến nghị)
```bash
# Setup lần đầu
make setup

# Chạy tất cả services
make start

# Dừng services
make stop
```

### Option 2: Sử dụng Scripts
```bash
# Linux/Mac
./scripts/start-all.sh
./scripts/stop-all.sh

# Windows
.\scripts\start-all.ps1
.\scripts\stop-all.ps1
```

### Option 3: Docker Compose
```bash
docker-compose up -d
docker-compose down
```

---

## 📦 BACKEND API

### Khởi động
```bash
# Development
make start-backend
# Hoặc
uvicorn app:app --reload --port 7860

# Production
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Endpoints
```
http://localhost:7860              # Root
http://localhost:7860/health       # Health check
http://localhost:7860/docs         # Swagger UI
http://localhost:7860/redoc        # ReDoc
http://localhost:7860/metrics      # Prometheus metrics
```

### Test API
```bash
# Health check
curl http://localhost:7860/health

# Detect toxic text
curl -X POST http://localhost:7860/api/extension/detect \
  -H "Content-Type: application/json" \
  -u "extension:api_key" \
  -d '{"text":"Test comment"}'
```

---

## 🖥️ WEB DASHBOARD

### Khởi động
```bash
# Development
make start-dashboard
# Hoặc
cd webdashboard && php artisan serve --port 8080

# Production (Nginx/Apache)
# Point web server to: webdashboard/public
```

### Laravel Commands
```bash
cd webdashboard

# Migrations
php artisan migrate
php artisan migrate:rollback
php artisan migrate:fresh

# Cache
php artisan cache:clear
php artisan config:clear
php artisan view:clear

# Queue workers
php artisan queue:work

# Generate key
php artisan key:generate
```

### URL
```
http://localhost:8080              # Dashboard
```

---

## 🔌 BROWSER EXTENSION

### Development
```
1. Chrome → chrome://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select: extension/ folder
```

### Package for Publishing
```bash
# Create ZIP
make package
# Hoặc
./scripts/package-extension.sh    # Linux/Mac
.\scripts\package-extension.ps1   # Windows

# Output: dist/toxic-detector-extension-vX.X.X.zip
```

### Publishing
```
1. Go to: https://chrome.google.com/webstore/devconsole/
2. Click "New Item"
3. Upload ZIP
4. Fill store listing
5. Submit for review
```

---

## 🗄️ DATABASE

### Migrations
```bash
# Backend indexes
python -m backend.db.migrations.add_performance_indexes

# Dashboard migrations
cd webdashboard && php artisan migrate

# All migrations
make migrate
```

### Database Tools
```bash
# SQLite
sqlite3 toxic_detector.db

# MySQL
mysql -u root -p toxic_detector

# PostgreSQL
psql -U toxic_user -d toxic_detector
```

---

## 🧪 TESTING

### Run Tests
```bash
# All tests
make test
pytest

# Unit tests only
make test-unit
pytest tests/unit -v

# Integration tests
make test-integration
pytest tests/integration -v

# With coverage
make test-coverage
pytest --cov=backend --cov-report=html

# Specific test
pytest tests/unit/test_cache.py::TestCachedDecorator -v
```

### Coverage Report
```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

---

## 🔍 CODE QUALITY

### Linting
```bash
# Run all linters
make lint

# Individual linters
flake8 backend
black --check backend
isort --check-only backend
mypy backend
```

### Format Code
```bash
# Auto-format
make format

# Individual formatters
black backend
isort backend
```

---

## 💾 REDIS

### Start Redis
```bash
# Native
redis-server

# Docker
docker run -d -p 6379:6379 --name redis redis:alpine

# With Makefile/Scripts
# Automatically started by start-all
```

### Test Redis
```bash
redis-cli ping         # Should return: PONG
redis-cli info         # Server info
redis-cli monitor      # Watch commands
```

### Redis Commands
```bash
# Get value
redis-cli GET key_name

# Set value
redis-cli SET key_name "value" EX 60

# Delete key
redis-cli DEL key_name

# List all keys
redis-cli KEYS "*"

# Flush all data (careful!)
redis-cli FLUSHALL
```

---

## 📊 MONITORING

### Prometheus Metrics
```bash
# Enable in .env
PROMETHEUS_ENABLED=True

# View metrics
curl http://localhost:7860/metrics

# Or in browser
open http://localhost:7860/metrics
```

### Logs
```bash
# View logs
make logs

# Tail logs
tail -f logs/backend.log
tail -f logs/dashboard.log
tail -f webdashboard/storage/logs/laravel.log

# Docker logs
docker-compose logs -f
docker-compose logs backend
```

---

## 🐳 DOCKER

### Basic Commands
```bash
# Build images
make docker-build
docker-compose build

# Start containers
make docker-up
docker-compose up -d

# Stop containers
make docker-down
docker-compose down

# View logs
make docker-logs
docker-compose logs -f

# Restart service
docker-compose restart backend
```

### Docker Cleanup
```bash
# Stop and remove containers
docker-compose down -v

# Remove all images
docker rmi $(docker images -q toxic-detector*)

# Full cleanup
docker system prune -a
```

---

## 🔐 ENVIRONMENT VARIABLES

### Critical Variables
```bash
# Backend (.env)
SECRET_KEY=your-secret-key-min-32-chars
EXTENSION_API_KEY=your-extension-api-key
DATABASE_URL=sqlite:///./toxic_detector.db
REDIS_ENABLED=False
PROMETHEUS_ENABLED=False

# Dashboard (webdashboard/.env)
APP_KEY=base64:...
DB_DATABASE=toxic_detector
API_BASE_URL=http://localhost:7860/api
API_KEY=your-extension-api-key
```

### Generate Keys
```bash
# Python secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Laravel app key
cd webdashboard && php artisan key:generate
```

---

## 🐛 TROUBLESHOOTING

### Port Already in Use
```bash
# Find process
lsof -i :7860          # Linux/Mac
netstat -ano | findstr :7860  # Windows

# Kill process
kill -9 <PID>          # Linux/Mac
taskkill /PID <PID> /F # Windows
```

### Clear Caches
```bash
# Backend
rm -rf __pycache__
rm -rf .pytest_cache
rm -f *.pyc

# Dashboard
cd webdashboard
php artisan cache:clear
php artisan config:clear
php artisan view:clear
rm -rf bootstrap/cache/*.php
```

### Reset Database
```bash
# SQLite
rm toxic_detector.db
python -m backend.db.migrations.add_performance_indexes

# Dashboard
cd webdashboard
php artisan migrate:fresh --seed
```

### Extension Not Loading
```bash
# Check manifest
cat extension/manifest.json | jq .

# Check Chrome errors
# Chrome → Extensions → Details → Errors

# Reload extension
# Chrome → Extensions → Reload button
```

---

## 📝 COMMON WORKFLOWS

### First Time Setup
```bash
git clone <repo>
cd toxic-language-detector
make setup
make start
```

### Daily Development
```bash
make start              # Start services
# Do development work
make test               # Run tests
make stop               # Stop services
```

### Before Committing
```bash
make format             # Format code
make lint               # Check code quality
make test               # Run tests
git add .
git commit -m "..."
git push
```

### Deploy to Production
```bash
# Update .env with production settings
make docker-build
make docker-up
# Or use GitHub Actions workflow
```

---

## 📚 DOCUMENTATION

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `SETUP_AND_RUN_GUIDE.md` | Complete setup guide |
| `IMPROVEMENTS_SUMMARY.md` | All improvements documentation |
| `QUICK_START_IMPROVEMENTS.md` | 5-minute setup guide |
| `QUICK_REFERENCE.md` | This cheat sheet |
| `SYSTEM_ARCHITECTURE.md` | Architecture overview |
| `WORKFLOW_ANALYSIS.md` | Detailed workflows |
| `DATABASE_AND_API.md` | API & DB documentation |

---

## 🆘 GETTING HELP

### Check Services Status
```bash
curl http://localhost:7860/health  # Backend
curl http://localhost:8080         # Dashboard
redis-cli ping                     # Redis
```

### View Logs
```bash
tail -f logs/backend.log
tail -f logs/dashboard.log
```

### Common Issues
1. **Port in use**: Stop other services or change port
2. **Permission denied**: `chmod +x scripts/*.sh`
3. **Module not found**: `pip install -r requirements.txt`
4. **Database error**: Check DATABASE_URL in .env
5. **Redis error**: Set REDIS_ENABLED=False or start Redis

---

*Quick Reference v1.0 - Last Updated: 2025-10-19*

