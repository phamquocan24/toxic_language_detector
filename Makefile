# Makefile for Toxic Language Detector
# Quick shortcuts for common commands

.PHONY: help install setup start stop test clean deploy

# Default target
help:
	@echo "🚀 Toxic Language Detector - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install all dependencies"
	@echo "  make setup            - Complete setup (install + migrate + build)"
	@echo ""
	@echo "Running Services:"
	@echo "  make start            - Start all services"
	@echo "  make start-backend    - Start backend only"
	@echo "  make start-dashboard  - Start dashboard only"
	@echo "  make stop             - Stop all services"
	@echo ""
	@echo "Extension:"
	@echo "  make package          - Package extension for Chrome Web Store"
	@echo "  make extension-dev    - Load extension in development mode"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          - Run database migrations"
	@echo "  make migrate-rollback - Rollback migrations"
	@echo "  make db-seed          - Seed database with sample data"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-coverage    - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Run linters"
	@echo "  make format           - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Clean temporary files"
	@echo "  make logs             - View logs"
	@echo ""

# ===== Setup & Installation =====

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	cd webdashboard && composer install && npm install

setup: install migrate
	@echo "🔧 Running initial setup..."
	cp -n .env.example .env || true
	cd webdashboard && cp -n .env.example .env || true
	cd webdashboard && php artisan key:generate
	cd webdashboard && npm run build
	@echo "✅ Setup complete!"

# ===== Running Services =====

start:
	@echo "🚀 Starting all services..."
	bash scripts/start-all.sh

start-backend:
	@echo "🔧 Starting backend..."
	bash scripts/start-backend.sh

start-dashboard:
	@echo "🖥️  Starting dashboard..."
	bash scripts/start-dashboard.sh

stop:
	@echo "🛑 Stopping all services..."
	bash scripts/stop-all.sh

# ===== Extension =====

package:
	@echo "📦 Packaging extension..."
	bash scripts/package-extension.sh

extension-dev:
	@echo "🔌 Extension location: $(PWD)/extension"
	@echo "📖 Load at: chrome://extensions/"
	@echo "   1. Enable 'Developer mode'"
	@echo "   2. Click 'Load unpacked'"
	@echo "   3. Select extension folder"

# ===== Database =====

migrate:
	@echo "🗄️  Running migrations..."
	python -m backend.db.migrations.add_performance_indexes
	cd webdashboard && php artisan migrate

migrate-rollback:
	@echo "↩️  Rolling back migrations..."
	python -m backend.db.migrations.add_performance_indexes --rollback
	cd webdashboard && php artisan migrate:rollback

db-seed:
	@echo "🌱 Seeding database..."
	cd webdashboard && php artisan db:seed

# ===== Testing =====

test:
	@echo "🧪 Running all tests..."
	pytest -v

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/unit -v

test-integration:
	@echo "🧪 Running integration tests..."
	pytest tests/integration -v

test-coverage:
	@echo "📊 Running tests with coverage..."
	pytest --cov=backend --cov-report=html --cov-report=term
	@echo "📈 Coverage report: htmlcov/index.html"

# ===== Code Quality =====

lint:
	@echo "🔍 Running linters..."
	flake8 backend --count --statistics
	black --check backend
	isort --check-only backend

format:
	@echo "✨ Formatting code..."
	black backend
	isort backend

# ===== Docker =====

docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Containers started!"
	@echo "📍 Backend:   http://localhost:7860"
	@echo "📍 Dashboard: http://localhost:8080"

docker-down:
	@echo "🐳 Stopping Docker containers..."
	docker-compose down

docker-logs:
	@echo "📝 Docker logs..."
	docker-compose logs -f

# ===== Maintenance =====

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f test_toxic_detector.db
	@echo "✅ Cleaned!"

logs:
	@echo "📝 Recent logs:"
	@echo ""
	@echo "=== Backend ==="
	tail -n 20 logs/backend.log 2>/dev/null || echo "No backend logs"
	@echo ""
	@echo "=== Dashboard ==="
	tail -n 20 logs/dashboard.log 2>/dev/null || echo "No dashboard logs"

# ===== Development =====

dev: start
	@echo "🔥 Development environment running"
	@echo "📍 Backend:   http://localhost:7860"
	@echo "📍 Docs:      http://localhost:7860/docs"
	@echo "📍 Dashboard: http://localhost:8080"

# ===== Production =====

deploy:
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Make sure to:"
	@echo "   1. Update .env with production settings"
	@echo "   2. Set SECRET_KEY and API keys"
	@echo "   3. Configure production database"
	@echo "   4. Enable Redis and Prometheus"
	@echo ""
	@echo "Run: make docker-up"

