# DEPLOYMENT & WEB DASHBOARD

## 📋 MỤC LỤC
1. [Deployment Guide](#deployment-guide)
2. [Web Dashboard (Laravel)](#web-dashboard-laravel)
3. [Environment Configuration](#environment-configuration)
4. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🚀 1. DEPLOYMENT GUIDE

### System Requirements

#### Backend (FastAPI)
- **Python**: 3.8+
- **RAM**: 2GB minimum, 4GB recommended
- **CPU**: 2 cores minimum
- **Storage**: 10GB minimum
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS

#### Web Dashboard (Laravel)
- **PHP**: 8.1+
- **Composer**: 2.x
- **Node.js**: 16+
- **MySQL/PostgreSQL**: Latest stable
- **Web Server**: Nginx or Apache

---

### Local Development Setup

#### 1. Clone Repository
```bash
git clone https://github.com/your-org/toxic-language-detector.git
cd toxic-language-detector
```

---

#### 2. Backend Setup

**Install Python Dependencies**:
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Download ML Models**:
```bash
# LSTM model
# Place in model/best_model_LSTM.h5

# PhoBERT model
# Place in model/phobert/

# Tokenizer
# Place in model/tokenizer.pkl
```

**Configure Environment**:
```bash
# Create .env file
cp .env.example .env

# Edit .env
DATABASE_URL=sqlite:///./toxic_detector.db
SECRET_KEY=your-secret-key-here
EXTENSION_API_KEY=your-api-key-here
MODEL_PATH=model/best_model_LSTM.h5
```

**Initialize Database**:
```bash
# Run migrations (if using Alembic)
alembic upgrade head

# Or start app (auto-creates tables)
python run_server.py
```

**Start Server**:
```bash
# Development
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or use helper script
python run_server.py
```

---

#### 3. Extension Setup

**Load Unpacked Extension**:
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `extension` folder
5. Extension should appear in toolbar

**Configure API Endpoint**:
```javascript
// extension/background.js
const API_ENDPOINT = "http://localhost:8000/api";
const AUTH_CREDENTIALS = "extension_key_here";
```

---

#### 4. Web Dashboard Setup

**Install PHP Dependencies**:
```bash
cd webdashboard

# Install Composer dependencies
composer install

# Install Node dependencies
npm install
```

**Configure Environment**:
```bash
# Copy environment file
cp env.example .env

# Generate app key
php artisan key:generate

# Configure database in .env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=toxic_detector
DB_USERNAME=root
DB_PASSWORD=your_password

# Configure API endpoint
API_BASE_URL=http://localhost:8000/api
API_KEY=your-api-key-here
```

**Run Migrations**:
```bash
php artisan migrate --seed
```

**Build Assets**:
```bash
npm run dev
# Or for production
npm run build
```

**Start Server**:
```bash
php artisan serve --host=0.0.0.0 --port=8080
```

**Access Dashboard**:
```
http://localhost:8080
```

---

### Production Deployment

#### Option 1: VPS (Ubuntu)

**1. Server Setup**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx supervisor postgresql redis-server

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# Install Composer
curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer
```

---

**2. Backend Deployment**:

**Create Application Directory**:
```bash
sudo mkdir -p /var/www/toxic-detector
sudo chown $USER:$USER /var/www/toxic-detector
cd /var/www/toxic-detector
```

**Clone and Setup**:
```bash
git clone https://github.com/your-org/toxic-language-detector.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

**Configure Gunicorn**:
```bash
# Create gunicorn config
sudo nano /etc/supervisor/conf.d/toxic-detector.conf
```

```ini
[program:toxic-detector]
directory=/var/www/toxic-detector
command=/var/www/toxic-detector/venv/bin/gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/toxic-detector/gunicorn.log
stderr_logfile=/var/log/toxic-detector/gunicorn_error.log
environment=PATH="/var/www/toxic-detector/venv/bin"
```

**Start Service**:
```bash
sudo mkdir -p /var/log/toxic-detector
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start toxic-detector
```

---

**3. Nginx Configuration**:

```bash
sudo nano /etc/nginx/sites-available/toxic-detector
```

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for ML predictions
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # File upload size
    client_max_body_size 10M;
}

# Web Dashboard
server {
    listen 80;
    server_name dashboard.yourdomain.com;
    root /var/www/toxic-detector/webdashboard/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

**Enable Sites**:
```bash
sudo ln -s /etc/nginx/sites-available/toxic-detector /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

**4. SSL with Let's Encrypt**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com -d dashboard.yourdomain.com
```

---

#### Option 2: Docker Deployment

**Docker Compose Configuration**:

```yaml
# docker-compose.yml
version: '3.8'

services:
  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: toxic-detector-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/toxic_detector
      - SECRET_KEY=${SECRET_KEY}
      - EXTENSION_API_KEY=${EXTENSION_API_KEY}
      - MODEL_PATH=/app/model/best_model_LSTM.h5
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./model:/app/model:ro
      - ./data:/app/data:ro
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    restart: unless-stopped

  # PostgreSQL Database
  db:
    image: postgres:14-alpine
    container_name: toxic-detector-db
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=toxic_detector
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: toxic-detector-redis
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: toxic-detector-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    restart: unless-stopped

  # Web Dashboard (Laravel)
  dashboard:
    build:
      context: ./webdashboard
      dockerfile: Dockerfile
    container_name: toxic-detector-dashboard
    ports:
      - "8080:80"
    environment:
      - DB_CONNECTION=pgsql
      - DB_HOST=db
      - DB_PORT=5432
      - DB_DATABASE=toxic_detector
      - DB_USERNAME=user
      - DB_PASSWORD=password
      - API_BASE_URL=http://backend:8000/api
    volumes:
      - ./webdashboard:/var/www/html
    depends_on:
      - db
    restart: unless-stopped

volumes:
  postgres_data:
```

**Dockerfile (Backend)**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
```

**Deploy**:
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

#### Option 3: Heroku Deployment

**Procfile**:
```
web: gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**runtime.txt**:
```
python-3.10.12
```

**Deploy**:
```bash
# Login to Heroku
heroku login

# Create app
heroku create toxic-detector-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set EXTENSION_API_KEY=your-api-key
heroku config:set MODEL_PATH=model/best_model_LSTM.h5

# Deploy
git push heroku main

# Run migrations
heroku run python -c "from backend.db.models import init_db; init_db()"

# View logs
heroku logs --tail
```

---

## 🖥️ 2. WEB DASHBOARD (LARAVEL)

### Architecture Overview

```
webdashboard/
├── app/
│   ├── Http/
│   │   ├── Controllers/
│   │   │   ├── Auth/          # Authentication
│   │   │   ├── API/           # API controllers
│   │   │   └── Web/           # Web controllers
│   │   └── Middleware/
│   └── Services/
│       └── ApiService.php     # Backend API client
├── modules/
│   ├── Admin/                 # Admin module
│   │   ├── Http/Controllers/
│   │   ├── Resources/views/
│   │   └── Routes/
│   ├── User/                  # User management
│   ├── Statistics/            # Analytics
│   ├── Prediction/            # ML predictions
│   ├── Log/                   # Activity logs
│   └── Comment/               # Comment management
├── resources/
│   ├── views/                 # Blade templates
│   └── js/                    # Frontend JS
├── routes/
│   ├── web.php               # Web routes
│   └── api.php               # API routes
└── public/
    └── build/                # Compiled assets
```

---

### Key Features

#### 1. Dashboard Home
- **Statistics Cards**: Total comments, users, accuracy
- **Charts**: 
  - Comments by category (pie chart)
  - Comments by platform (bar chart)
  - Timeline chart (daily/weekly/monthly trends)
- **Recent Activity**: Latest comments and user actions

---

#### 2. User Management (Admin Module)

**Routes**:
```php
// routes/web.php
Route::prefix('admin')->middleware(['auth', 'admin'])->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index']);
    Route::resource('users', UserController::class);
    Route::post('users/{id}/toggle-status', [UserController::class, 'toggleStatus']);
    Route::get('users/{id}/activity', [UserController::class, 'activityLog']);
});
```

**Controller Example**:
```php
// modules/Admin/Http/Controllers/UserController.php
class UserController extends Controller
{
    protected $apiService;

    public function __construct(ApiService $apiService)
    {
        $this->apiService = $apiService;
    }

    public function index(Request $request)
    {
        $filters = [
            'skip' => $request->get('page', 0) * 20,
            'limit' => 20,
            'role' => $request->get('role'),
            'active' => $request->get('active'),
            'search' => $request->get('search')
        ];

        $response = $this->apiService->get('/admin/users', $filters);
        $users = $response['users'] ?? [];
        $total = $response['total'] ?? 0;

        return view('Admin::users.index', compact('users', 'total'));
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'username' => 'required|min:3|max:50',
            'email' => 'required|email',
            'password' => 'required|min:8',
            'role_name' => 'required|in:admin,user,service'
        ]);

        $response = $this->apiService->post('/admin/users', $validated);

        return redirect()->route('admin.users.index')
            ->with('success', 'User created successfully');
    }

    public function update(Request $request, $id)
    {
        $validated = $request->validate([
            'email' => 'email',
            'role_name' => 'in:admin,user,service',
            'is_active' => 'boolean'
        ]);

        $response = $this->apiService->put("/admin/users/{$id}", $validated);

        return redirect()->back()
            ->with('success', 'User updated successfully');
    }

    public function destroy($id)
    {
        $this->apiService->delete("/admin/users/{$id}");

        return redirect()->route('admin.users.index')
            ->with('success', 'User deleted successfully');
    }
}
```

---

#### 3. Comment Management

**Features**:
- View all analyzed comments
- Filter by:
  - Platform (Facebook, YouTube, Twitter)
  - Category (Clean, Offensive, Hate, Spam)
  - Date range
  - Confidence threshold
  - User
- Search by content
- Bulk actions (delete, export)
- Manual review and correction

**Blade View Example**:
```blade
{{-- modules/Comment/Resources/views/index.blade.php --}}
@extends('layouts.app')

@section('content')
<div class="container">
    <h1>Comment Management</h1>

    <!-- Filters -->
    <form method="GET" class="filters">
        <select name="platform">
            <option value="">All Platforms</option>
            <option value="facebook">Facebook</option>
            <option value="youtube">YouTube</option>
            <option value="twitter">Twitter</option>
        </select>

        <select name="prediction">
            <option value="">All Categories</option>
            <option value="0">Clean</option>
            <option value="1">Offensive</option>
            <option value="2">Hate Speech</option>
            <option value="3">Spam</option>
        </select>

        <input type="date" name="start_date" placeholder="Start Date">
        <input type="date" name="end_date" placeholder="End Date">
        <input type="text" name="search" placeholder="Search...">
        <button type="submit">Filter</button>
    </form>

    <!-- Comments Table -->
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Content</th>
                <th>Platform</th>
                <th>Category</th>
                <th>Confidence</th>
                <th>Date</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            @foreach($comments as $comment)
            <tr>
                <td>{{ $comment['id'] }}</td>
                <td>{{ Str::limit($comment['content'], 100) }}</td>
                <td>
                    <span class="badge badge-{{ $comment['platform'] }}">
                        {{ ucfirst($comment['platform']) }}
                    </span>
                </td>
                <td>
                    <span class="badge badge-{{ $comment['prediction_text'] }}">
                        {{ $comment['prediction_text'] }}
                    </span>
                </td>
                <td>{{ number_format($comment['confidence'] * 100, 1) }}%</td>
                <td>{{ Carbon\Carbon::parse($comment['created_at'])->format('Y-m-d H:i') }}</td>
                <td>
                    <button class="btn-view" data-id="{{ $comment['id'] }}">View</button>
                    <button class="btn-delete" data-id="{{ $comment['id'] }}">Delete</button>
                </td>
            </tr>
            @endforeach
        </tbody>
    </table>

    <!-- Pagination -->
    {{ $comments->links() }}
</div>
@endsection
```

---

#### 4. Statistics Module

**Charts Implementation (Chart.js)**:
```javascript
// modules/Statistics/Resources/js/charts.js

// Pie Chart - Comments by Category
const categoryChart = new Chart(document.getElementById('categoryChart'), {
    type: 'pie',
    data: {
        labels: ['Clean', 'Offensive', 'Hate Speech', 'Spam'],
        datasets: [{
            data: [
                {{ $stats['clean_comments'] }},
                {{ $stats['offensive_comments'] }},
                {{ $stats['hate_comments'] }},
                {{ $stats['spam_comments'] }}
            ],
            backgroundColor: [
                '#4CAF50',  // Green
                '#FF9800',  // Orange
                '#F44336',  // Red
                '#9E9E9E'   // Gray
            ]
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom'
            },
            title: {
                display: true,
                text: 'Comments by Category'
            }
        }
    }
});

// Bar Chart - Comments by Platform
const platformChart = new Chart(document.getElementById('platformChart'), {
    type: 'bar',
    data: {
        labels: ['Facebook', 'YouTube', 'Twitter'],
        datasets: [{
            label: 'Comments',
            data: [
                {{ $stats['platforms']['facebook'] ?? 0 }},
                {{ $stats['platforms']['youtube'] ?? 0 }},
                {{ $stats['platforms']['twitter'] ?? 0 }}
            ],
            backgroundColor: '#2196F3'
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Line Chart - Timeline
fetch('/api/statistics/timeline?period=month')
    .then(response => response.json())
    .then(data => {
        const timelineChart = new Chart(document.getElementById('timelineChart'), {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Clean',
                        data: data.clean,
                        borderColor: '#4CAF50',
                        fill: false
                    },
                    {
                        label: 'Offensive',
                        data: data.offensive,
                        borderColor: '#FF9800',
                        fill: false
                    },
                    {
                        label: 'Hate',
                        data: data.hate,
                        borderColor: '#F44336',
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });
    });
```

---

#### 5. API Service (Backend Communication)

```php
// app/Services/ApiService.php
namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ApiService
{
    protected $baseUrl;
    protected $apiKey;
    protected $token;

    public function __construct()
    {
        $this->baseUrl = config('services.api.base_url');
        $this->apiKey = config('services.api.key');
        $this->token = session('api_token');
    }

    protected function headers()
    {
        $headers = [
            'Content-Type' => 'application/json',
            'Accept' => 'application/json'
        ];

        if ($this->token) {
            $headers['Authorization'] = "Bearer {$this->token}";
        } else if ($this->apiKey) {
            $headers['X-API-Key'] = $this->apiKey;
        }

        return $headers;
    }

    public function get(string $endpoint, array $params = [])
    {
        try {
            $response = Http::withHeaders($this->headers())
                ->timeout(30)
                ->get($this->baseUrl . $endpoint, $params);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('API GET Error', [
                'endpoint' => $endpoint,
                'status' => $response->status(),
                'body' => $response->body()
            ]);

            return null;
        } catch (\Exception $e) {
            Log::error('API GET Exception', [
                'endpoint' => $endpoint,
                'message' => $e->getMessage()
            ]);
            return null;
        }
    }

    public function post(string $endpoint, array $data = [])
    {
        try {
            $response = Http::withHeaders($this->headers())
                ->timeout(30)
                ->post($this->baseUrl . $endpoint, $data);

            if ($response->successful()) {
                return $response->json();
            }

            return null;
        } catch (\Exception $e) {
            Log::error('API POST Exception', [
                'endpoint' => $endpoint,
                'message' => $e->getMessage()
            ]);
            return null;
        }
    }

    public function put(string $endpoint, array $data = [])
    {
        try {
            $response = Http::withHeaders($this->headers())
                ->timeout(30)
                ->put($this->baseUrl . $endpoint, $data);

            return $response->successful() ? $response->json() : null;
        } catch (\Exception $e) {
            Log::error('API PUT Exception', [
                'endpoint' => $endpoint,
                'message' => $e->getMessage()
            ]);
            return null;
        }
    }

    public function delete(string $endpoint)
    {
        try {
            $response = Http::withHeaders($this->headers())
                ->timeout(30)
                ->delete($this->baseUrl . $endpoint);

            return $response->successful();
        } catch (\Exception $e) {
            Log::error('API DELETE Exception', [
                'endpoint' => $endpoint,
                'message' => $e->getMessage()
            ]);
            return false;
        }
    }

    // Specific methods
    public function login(string $username, string $password)
    {
        $response = Http::asForm()->post($this->baseUrl . '/auth/token', [
            'username' => $username,
            'password' => $password
        ]);

        if ($response->successful()) {
            $data = $response->json();
            $this->token = $data['access_token'];
            session(['api_token' => $this->token]);
            return $data;
        }

        return null;
    }

    public function logout()
    {
        session()->forget('api_token');
        $this->token = null;
    }
}
```

---

## ⚙️ 3. ENVIRONMENT CONFIGURATION

### Backend (.env)

```bash
# Application
APP_NAME="Toxic Language Detector"
APP_ENV=production
DEBUG=False

# API Keys
SECRET_KEY=your-very-long-secret-key-here-min-32-chars
EXTENSION_API_KEY=your-extension-api-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/toxic_detector
# Or SQLite for development
# DATABASE_URL=sqlite:///./toxic_detector.db

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# ML Model
MODEL_PATH=model/best_model_LSTM.h5
MODEL_VOCAB_PATH=model/tokenizer.pkl
MODEL_CONFIG_PATH=model/config.json
MODEL_PRELOAD=True
MODEL_DEVICE=cpu
MODEL_LABELS=["clean", "offensive", "hate", "spam"]

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME="Toxic Detector"

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log

# Admin Account
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=SecurePassword123!
CREATE_ADMIN_IF_NOT_EXISTS=True
```

---

### Web Dashboard (.env)

```bash
APP_NAME="Toxic Detector Dashboard"
APP_ENV=production
APP_KEY=base64:...  # Generated by php artisan key:generate
APP_DEBUG=false
APP_URL=https://dashboard.yourdomain.com

# Database
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=toxic_detector
DB_USERNAME=root
DB_PASSWORD=your_password

# Backend API
API_BASE_URL=https://api.yourdomain.com/api
API_KEY=your-api-key-here
API_TIMEOUT=30

# Cache
CACHE_DRIVER=redis
QUEUE_CONNECTION=redis
SESSION_DRIVER=redis
REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379

# Mail
MAIL_MAILER=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_ENCRYPTION=tls
MAIL_FROM_ADDRESS=noreply@yourdomain.com
MAIL_FROM_NAME="${APP_NAME}"

# JWT
JWT_SECRET=your-jwt-secret-key
JWT_TTL=1440

# Logging
LOG_CHANNEL=stack
LOG_LEVEL=info
```

---

## 📊 4. MONITORING & MAINTENANCE

### Health Checks

**Backend Health Endpoint**:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": ml_model.loaded,
        "model_type": ml_model.model_type,
        "database": "connected",
        "version": "1.0.0"
    }
```

**Monitoring Script**:
```bash
#!/bin/bash
# monitor.sh

while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    
    if [ $response -ne 200 ]; then
        echo "[$(date)] Backend is down! Status: $response"
        # Send alert (email, SMS, Slack, etc.)
        # Restart service
        sudo supervisorctl restart toxic-detector
    else
        echo "[$(date)] Backend is healthy"
    fi
    
    sleep 60  # Check every minute
done
```

---

### Logging

**Application Logs**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

**Log Rotation** (logrotate):
```bash
# /etc/logrotate.d/toxic-detector
/var/www/toxic-detector/app.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart toxic-detector > /dev/null
    endscript
}
```

---

### Database Backups

**Automated Backup Script**:
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/toxic-detector"
DB_NAME="toxic_detector"

# Create backup directory
mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# SQLite backup (if using SQLite)
# cp /var/www/toxic-detector/toxic_detector.db $BACKUP_DIR/db_backup_$DATE.db

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
```

**Cron Job**:
```bash
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

---

### Performance Monitoring

**System Metrics**:
- CPU usage
- Memory usage
- Disk space
- Network traffic
- API response times
- Database query times

**Tools**:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **New Relic**: APM
- **Datadog**: Full-stack monitoring

**Sample Prometheus Metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Counters
prediction_counter = Counter('predictions_total', 'Total predictions', ['category'])
api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])

# Histograms
prediction_duration = Histogram('prediction_duration_seconds', 'Prediction duration')
api_latency = Histogram('api_latency_seconds', 'API latency', ['endpoint'])

# Gauges
active_users = Gauge('active_users', 'Number of active users')
model_loaded = Gauge('model_loaded', 'Model loaded status')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

### Maintenance Tasks

**Weekly Tasks**:
- Review error logs
- Check disk space
- Monitor API usage
- Review user reports
- Update model if needed

**Monthly Tasks**:
- Database cleanup (old comments)
- Security updates
- Performance optimization
- Backup verification
- User feedback review

**Model Retraining**:
```python
# scripts/retrain_model.py

# 1. Collect feedback data
reports = db.query(Report).filter(Report.status == 'confirmed').all()

# 2. Create training dataset
training_data = []
for report in reports:
    training_data.append({
        'text': report.content,
        'label': report.suggested_category
    })

# 3. Retrain model
# ... ML training code ...

# 4. Evaluate new model
# ... evaluation code ...

# 5. Deploy if better
if new_accuracy > current_accuracy:
    shutil.copy('new_model.h5', 'model/best_model_LSTM.h5')
    print("Model updated successfully")
```

---

*Tài liệu được tạo tự động bởi AI Assistant*
*Ngày tạo: 2025-10-19*

