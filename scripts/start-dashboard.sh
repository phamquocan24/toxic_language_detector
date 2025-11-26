#!/bin/bash
# Start Laravel Dashboard

set -e

echo "🖥️  Starting Toxic Language Detector Dashboard..."
echo ""

# Navigate to dashboard directory
cd webdashboard

# Check if vendor directory exists
if [ ! -d "vendor" ]; then
    echo "📦 Installing PHP dependencies..."
    composer install
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found! Creating from example..."
    cp .env.example .env
    php artisan key:generate
    echo "✅ Created .env file. Please configure database settings."
fi

# Build assets if needed
if [ ! -d "public/build" ]; then
    echo "🎨 Building frontend assets..."
    npm run build
fi

# Run migrations
echo ""
echo "🗄️  Running database migrations..."
php artisan migrate --force 2>/dev/null || echo "Migrations already applied"

# Clear cache
echo "🧹 Clearing cache..."
php artisan cache:clear
php artisan config:clear

# Start server
echo ""
echo "🚀 Starting Laravel development server..."
echo ""
echo "📍 Dashboard URL: http://localhost:8080"
echo "📍 Make sure Backend API is running on: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop"
echo ""

php artisan serve --host=0.0.0.0 --port=8080

