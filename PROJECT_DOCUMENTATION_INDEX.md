# 📚 TÀI LIỆU DỰ ÁN - TOXIC LANGUAGE DETECTOR

## 🎯 GIỚI THIỆU

Hệ thống **Toxic Language Detector** là một nền tảng toàn diện để phát hiện và phân loại ngôn ngữ độc hại trên các nền tảng mạng xã hội (Facebook, YouTube, Twitter). Hệ thống bao gồm:

- **Backend API** (FastAPI/Python): Xử lý ML predictions và quản lý dữ liệu
- **Browser Extension** (Chrome): Tự động quét và highlight comments độc hại
- **Web Dashboard** (Laravel/PHP): Quản trị và phân tích dữ liệu

---

## 📖 TÀI LIỆU CHI TIẾT

### Core Documentation

### 1. [README.md](./README.md) ⭐ **START HERE**
**Production-Ready Overview & Quick Start**

**Nội dung chính**:
- ✅ Badges và project status
- ✅ 4 quick start options
- ✅ Complete feature list
- ✅ Performance metrics
- ✅ System architecture diagram
- ✅ Testing & deployment guide
- ✅ Links to all documentation

**Đọc tài liệu này nếu bạn muốn**:
- Hiểu tổng quan nhanh về project
- Chạy hệ thống trong 5 phút
- Xem thống kê performance improvements
- Tìm links tới tất cả tài liệu khác

---

### 2. [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)
**Tổng quan kiến trúc hệ thống**

**Nội dung chính**:
- ✅ Sơ đồ kiến trúc tổng thể
- ✅ Mô tả chi tiết các thành phần:
  - Backend API (FastAPI)
  - Browser Extension (Chrome)
  - Web Dashboard (Laravel)
  - Machine Learning Models
  - Database Schema
- ✅ Công nghệ sử dụng
- ✅ Luồng dữ liệu (Data Flow)
- ✅ Cấu trúc thư mục

**Đọc tài liệu này nếu bạn muốn**:
- Hiểu tổng quan về hệ thống
- Nắm được cách các thành phần tương tác
- Xem sơ đồ kiến trúc
- Tìm hiểu về tech stack

---

### 2. [WORKFLOW_ANALYSIS.md](./WORKFLOW_ANALYSIS.md)
**Phân tích chi tiết các luồng hoạt động**

**Nội dung chính**:
- ✅ **Luồng Extension Scanning**: 
  - Platform detection
  - Comment observation (MutationObserver)
  - Batch processing
  - Visual indicators
- ✅ **Luồng Batch Processing**:
  - Chunking strategy
  - Progress tracking
  - Result display
- ✅ **Luồng Authentication**:
  - Register/Login flow
  - JWT token management
  - Session handling
- ✅ **Luồng ML Prediction**:
  - Text preprocessing
  - Model inference
  - Spam heuristics
- ✅ **Luồng User Feedback**:
  - Report incorrect analysis
  - Feedback storage
- ✅ **Luồng Admin Dashboard**:
  - Statistics aggregation
  - Comment management
  - Data export

**Đọc tài liệu này nếu bạn muốn**:
- Hiểu chi tiết từng quy trình
- Debug hoặc tối ưu workflow
- Implement tính năng mới
- Trace code flow

---

### 3. [DATABASE_AND_API.md](./DATABASE_AND_API.md)
**Database schema và API endpoints**

**Nội dung chính**:
- ✅ **Database Schema**:
  - Entity Relationship Diagram
  - Bảng `users`, `roles`, `permissions`
  - Bảng `comments`, `logs`, `reports`
  - Bảng `user_settings`, `refresh_tokens`
  - Indexes và relationships
- ✅ **API Endpoints**:
  - Authentication (`/auth/*`)
  - Extension (`/extension/*`)
  - Prediction (`/prediction/*`)
  - Admin (`/admin/*`)
- ✅ **Request/Response Models**:
  - Pydantic schemas
  - Validation rules
- ✅ **Authentication**:
  - JWT structure
  - API key authentication
- ✅ **Rate Limiting**:
  - Configuration
  - Implementation
- ✅ **Error Responses**:
  - Standard format
  - HTTP status codes

**Đọc tài liệu này nếu bạn muốn**:
- Hiểu database structure
- Xem danh sách API endpoints
- Tích hợp với API
- Thiết kế queries
- Debug authentication issues

---

### 4. [DEPLOYMENT_AND_DASHBOARD.md](./DEPLOYMENT_AND_DASHBOARD.md)
**Hướng dẫn deployment và web dashboard**

**Nội dung chính**:
- ✅ **Deployment Guide**:
  - System requirements
  - Local development setup
  - Production deployment:
    - VPS (Ubuntu + Nginx + Gunicorn)
    - Docker Compose
    - Heroku
  - SSL configuration
- ✅ **Web Dashboard (Laravel)**:
  - Architecture overview
  - Key features:
    - Dashboard home
    - User management
    - Comment management
    - Statistics & charts
  - API service implementation
- ✅ **Environment Configuration**:
  - Backend `.env`
  - Dashboard `.env`
- ✅ **Monitoring & Maintenance**:
  - Health checks
  - Logging & log rotation
  - Database backups
  - Performance monitoring
  - Maintenance tasks

**Đọc tài liệu này nếu bạn muốn**:
- Deploy hệ thống lên production
- Setup local development
- Configure web dashboard
- Monitor system health
- Backup và maintain database

---

## 🗂️ CẤU TRÚC DỰ ÁN

```
toxic-language-detector/
│
├── 📁 backend/                  # FastAPI Backend
│   ├── api/
│   │   ├── routes/             # API endpoints
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── extension.py    # Extension endpoints
│   │   │   ├── prediction.py   # ML predictions
│   │   │   ├── admin.py        # Admin endpoints
│   │   │   └── ...
│   │   └── models/             # Pydantic models
│   ├── db/
│   │   └── models/             # SQLAlchemy models
│   ├── services/
│   │   ├── ml_model.py         # ML model service
│   │   ├── model_adapter.py    # Model loading
│   │   └── ...
│   ├── core/
│   │   ├── middleware.py       # Custom middleware
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   └── security.py         # Auth utilities
│   └── config/
│       ├── settings.py         # Configuration
│       └── security.py         # Security settings
│
├── 📁 extension/                # Chrome Extension
│   ├── background.js           # Service worker
│   ├── content.js              # Content script
│   ├── manifest.json           # Extension manifest
│   └── popup/
│       ├── popup.html          # Extension popup UI
│       ├── popup.js            # Popup logic
│       └── popup.css           # Popup styles
│
├── 📁 webdashboard/             # Laravel Dashboard
│   ├── app/
│   │   ├── Http/Controllers/   # Controllers
│   │   └── Services/
│   │       └── ApiService.php  # Backend API client
│   ├── modules/
│   │   ├── Admin/              # Admin module
│   │   ├── User/               # User management
│   │   ├── Statistics/         # Analytics
│   │   ├── Prediction/         # ML interface
│   │   ├── Log/                # Activity logs
│   │   └── Comment/            # Comment management
│   ├── resources/
│   │   ├── views/              # Blade templates
│   │   └── js/                 # Frontend JS
│   └── routes/
│       ├── web.php             # Web routes
│       └── api.php             # API routes
│
├── 📁 model/                    # ML Models
│   ├── best_model_LSTM.h5      # LSTM model
│   ├── tokenizer.pkl           # Tokenizer
│   ├── config.json             # Model config
│   ├── bert/                   # BERT models
│   ├── phobert/                # PhoBERT models
│   └── ...
│
├── 📁 data/                     # Data files
│   ├── vietnamese_offensive_words.txt
│   └── vietnamese_stopwords.txt
│
├── 📄 app.py                    # FastAPI main app
├── 📄 requirements.txt          # Python dependencies
├── 📄 Dockerfile                # Docker configuration
├── 📄 docker-compose.yml        # Docker Compose
└── 📄 README.md                 # Project README
```

---

## 🚀 QUICK START

### Khởi động Backend
```bash
# Clone repository
git clone https://github.com/your-org/toxic-language-detector.git
cd toxic-language-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env với cấu hình của bạn

# Run server
python run_server.py
# Backend running at: http://localhost:8000
```

### Khởi động Extension
```bash
1. Mở Chrome → chrome://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Chọn thư mục `extension`
5. Extension sẽ xuất hiện trong toolbar
```

### Khởi động Dashboard
```bash
cd webdashboard

# Install dependencies
composer install
npm install

# Setup environment
cp env.example .env
php artisan key:generate

# Configure database trong .env
# DB_DATABASE=toxic_detector
# DB_USERNAME=root
# DB_PASSWORD=your_password

# Run migrations
php artisan migrate --seed

# Build assets
npm run dev

# Start server
php artisan serve
# Dashboard running at: http://localhost:8000
```

---

## 📊 DASHBOARD OVERVIEW

### Admin Login
- **URL**: `http://localhost:8000/admin/login`
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin123` (hoặc theo cấu hình trong `.env`)

### Dashboard Features

#### 🏠 Home Dashboard
- Tổng số comments phân tích
- Số lượng users
- Thống kê theo category (Clean, Offensive, Hate, Spam)
- Biểu đồ phân bố
- Hoạt động gần đây

#### 👥 User Management
- Xem danh sách users
- Tạo/sửa/xóa users
- Quản lý roles (admin, user, service)
- Xem activity logs của user
- Lock/unlock accounts

#### 💬 Comment Management
- Xem tất cả comments đã phân tích
- Filter theo:
  - Platform (Facebook, YouTube, Twitter)
  - Category (Clean, Offensive, Hate, Spam)
  - Date range
  - Confidence threshold
- Search trong content
- Review và correct predictions
- Export data (CSV, Excel, PDF)

#### 📈 Statistics & Analytics
- Biểu đồ theo thời gian
- Phân tích theo platform
- Accuracy metrics
- User engagement stats
- Top toxic users/sources

#### 📋 Activity Logs
- User login/logout
- API access logs
- Prediction history
- Admin actions
- Error logs

#### ⚙️ Settings
- System configuration
- Email settings
- ML model settings
- Rate limiting
- Extension defaults

---

## 🔗 LIÊN KẾT HỮU ÍCH

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Model Information
- **Model Type**: LSTM, CNN, BERT, PhoBERT, BERT4News
- **Input**: Vietnamese text (max 5000 chars)
- **Output**: 4 classes (Clean, Offensive, Hate, Spam)
- **Preprocessing**: Lowercasing, URL removal, Vietnamese tokenization

### Performance Metrics
- **Accuracy**: ~92% (LSTM baseline)
- **Precision**: ~88%
- **Recall**: ~85%
- **API Latency**: <500ms (single prediction)
- **Batch Throughput**: ~100 items/request

---

## 🛠️ TROUBLESHOOTING

### Backend không start được?
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check model files
ls -la model/best_model_LSTM.h5

# Check logs
tail -f app.log
```

### Extension không hoạt động?
```bash
# Check API endpoint
# Mở extension → Settings → API Endpoint
# Phải là: http://localhost:8000/api

# Check console errors
# Mở Developer Tools (F12) → Console tab

# Check network requests
# Developer Tools → Network tab → Filter: Fetch/XHR
```

### Dashboard không connect được API?
```bash
# Check .env configuration
cat webdashboard/.env | grep API_BASE_URL
# Phải là: http://localhost:8000/api

# Test API connection
curl http://localhost:8000/health

# Check Laravel logs
tail -f webdashboard/storage/logs/laravel.log
```

---

## 📚 ADDITIONAL DOCUMENTATION (V1.0.0)

### Quick References

### 6. [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) ⚡
**Command Cheat Sheet - Tham khảo nhanh**

**Nội dung chính**:
- ✅ Quick start trong 5 phút (4 options)
- ✅ Tất cả lệnh thường dùng
- ✅ Backend API commands
- ✅ Dashboard commands
- ✅ Extension packaging
- ✅ Database operations
- ✅ Testing commands
- ✅ Docker commands
- ✅ Redis operations
- ✅ Monitoring & logging
- ✅ Troubleshooting guide

**Đọc tài liệu này nếu bạn muốn**:
- Tra cứu lệnh nhanh
- Copy-paste commands
- Troubleshoot common issues
- Quick reference mọi lúc

---

### 7. [QUICK_START_IMPROVEMENTS.md](./QUICK_START_IMPROVEMENTS.md) 🚀
**5-Minute Quick Start - All Improvements**

**Nội dung chính**:
- ✅ 3 setup options (Makefile, Scripts, Docker)
- ✅ Usage examples
- ✅ Configuration guide
- ✅ Monitoring setup
- ✅ Testing guide
- ✅ Common workflows

**Đọc tài liệu này nếu bạn muốn**:
- Chạy system trong 5 phút
- Hiểu các improvement features
- Setup monitoring
- Quick testing

---

### 8. [IMPROVEMENTS_SUMMARY.md](./IMPROVEMENTS_SUMMARY.md) 📋
**All System Improvements (643 lines)**

**Nội dung chính**:
- ✅ **Phase 1 - CRITICAL**:
  - Redis integration
  - Database indexes
  - Extension retry logic
  - Security enhancements
- ✅ **Phase 2 - MAJOR**:
  - Async model loading
  - API versioning
  - Prometheus metrics
- ✅ **Phase 3 - TESTING & CI/CD**:
  - Unit tests (pytest)
  - Integration tests
  - CI/CD pipeline
- ✅ Code examples
- ✅ Configuration guides
- ✅ Benefits & impact

**Đọc tài liệu này nếu bạn muốn**:
- Hiểu tất cả improvements
- Xem code examples
- Configure features
- Understand benefits

---

### Project Management

### 9. [COMPLETE_SYSTEM_SUMMARY.md](./COMPLETE_SYSTEM_SUMMARY.md) 🎉
**System Summary & Final Status**

**Nội dung chính**:
- ✅ Complete feature list (10 improvements)
- ✅ Performance metrics table
- ✅ Quick start commands (4 options)
- ✅ Service URLs
- ✅ All documentation links
- ✅ Configuration files
- ✅ Dependencies list
- ✅ Security features
- ✅ Monitoring & observability
- ✅ Deployment options
- ✅ Deployment checklist

**Đọc tài liệu này nếu bạn muốn**:
- Xem tổng kết toàn bộ hệ thống
- Performance improvements
- Complete checklist
- Deploy to production

---

### 10. [CHANGELOG.md](./CHANGELOG.md) 📝
**Version History & Release Notes**

**Nội dung chính**:
- ✅ Version 1.0.0 release notes
- ✅ All features added
- ✅ Performance improvements table
- ✅ Bug fixes
- ✅ Dependencies
- ✅ Breaking changes
- ✅ Roadmap for v1.1.0

**Đọc tài liệu này nếu bạn muốn**:
- Xem version history
- Understand what changed
- Plan upgrades
- See roadmap

---

### 11. [CONTRIBUTING.md](./CONTRIBUTING.md) 🤝
**Contribution Guidelines**

**Nội dung chính**:
- ✅ Code of conduct
- ✅ Development setup
- ✅ How to contribute
- ✅ Coding standards (Python, PHP, JS)
- ✅ Testing guidelines
- ✅ Pull request process
- ✅ Issue guidelines
- ✅ Commit message format
- ✅ Development tips

**Đọc tài liệu này nếu bạn muốn**:
- Contribute to project
- Follow coding standards
- Create pull requests
- Report bugs/features

---

### 12. [CONTRIBUTORS.md](./CONTRIBUTORS.md) 🏆
**Contributors & Recognition**

**Nội dung chính**:
- ✅ Core team
- ✅ Code contributors
- ✅ Documentation contributors
- ✅ Bug hunters
- ✅ Contribution statistics
- ✅ Badges & recognition
- ✅ How to get listed

**Đọc tài liệu này nếu bạn muốn**:
- See who contributed
- Earn badges
- Get recognized
- Join the team

---

### Scripts & Automation

### 13. [scripts/README.md](./scripts/README.md) 📜
**Scripts Documentation**

**Nội dung chính**:
- ✅ All scripts overview
- ✅ Backend scripts
- ✅ Dashboard scripts
- ✅ Extension packaging
- ✅ Full stack scripts
- ✅ Troubleshooting
- ✅ Service status checks

**Đọc tài liệu này nếu bạn muốn**:
- Understand automation scripts
- Run scripts correctly
- Troubleshoot script issues
- Check service status

---

### 14. [Makefile](./Makefile) 🔧
**Command Shortcuts (40+ commands)**

**Available commands**:
- `make help` - Show all commands
- `make setup` - Complete setup
- `make start` - Start all services
- `make test` - Run tests
- `make lint` - Check code quality
- `make docker-up` - Docker stack
- And 30+ more...

**Đọc file này nếu bạn muốn**:
- Quick commands
- Automation shortcuts
- Development workflows

---

### Deployment & Production

### 15. [FINAL_DEPLOYMENT_CHECKLIST.md](./FINAL_DEPLOYMENT_CHECKLIST.md) ✅
**Production Deployment Checklist (150+ items)**

**Nội dung chính**:
- ✅ Security (environment, auth, CORS)
- ✅ Database (config, backups, performance)
- ✅ Backend API (config, deployment, testing)
- ✅ Web Dashboard (config, deployment, web server)
- ✅ Browser Extension (testing, publishing)
- ✅ Redis (config, testing)
- ✅ Monitoring (Prometheus, Grafana, logging)
- ✅ Docker (if using)
- ✅ CI/CD (GitHub Actions)
- ✅ Performance verification
- ✅ Backup & recovery
- ✅ Documentation
- ✅ Testing (unit, integration, security)
- ✅ Post-deployment monitoring
- ✅ Rollback plan

**Đọc tài liệu này nếu bạn muốn**:
- Deploy to production safely
- Complete pre-deployment checks
- Verify everything works
- Have rollback plan ready

---

### Configuration Files

### 16. [docker-compose.yml](./docker-compose.yml) 🐳
**Container Orchestration**

**Services**:
- Redis (caching & rate limiting)
- PostgreSQL (database)
- Backend API
- Web Dashboard
- Prometheus (optional)
- Grafana (optional)
- Nginx (optional)

**Profiles**:
- Default: Core services
- `monitoring`: + Prometheus + Grafana
- `production`: + Nginx

---

### 17. [Dockerfile](./Dockerfile) 📦
**Backend Container Image**

**Features**:
- Multi-stage build
- Python 3.10-slim
- Non-root user
- Health check
- Optimized layers

---

### 18. [prometheus.yml](./prometheus.yml) 📊
**Prometheus Configuration**

**Scrape targets**:
- Backend API metrics
- Self-monitoring
- Optional: Redis, PostgreSQL, Node

---

### 19. [pytest.ini](./pytest.ini) 🧪
**Test Configuration**

**Settings**:
- Test markers (integration, slow)
- Coverage settings
- Test discovery paths
- Async support

---

### 20. [LICENSE](./LICENSE) 📜
**MIT License**

Open source, free to use, modify, and distribute.

---

### Windows-Specific Guides

### 21. [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) 🪟
**Complete Windows Setup Guide**

**Nội dung chính**:
- ✅ 3 quick start options cho Windows
- ✅ Khắc phục 8+ lỗi thường gặp:
  - `make: command not found`
  - `venv/bin/activate: No such file`
  - Port already in use
  - Redis issues
  - Permission denied
  - Module not found
- ✅ Windows-specific workflows
- ✅ Path differences (Scripts vs bin)
- ✅ Git Bash vs PowerShell
- ✅ Docker alternative
- ✅ Debug steps

**Đọc tài liệu này nếu bạn**:
- Đang dùng Windows
- Gặp lỗi với scripts
- Cần troubleshoot Windows issues
- Muốn hiểu Windows-specific setup

---

### 22. [QUICK_FIX_WINDOWS.md](./QUICK_FIX_WINDOWS.md) ⚡
**1-Minute Quick Fix for Windows**

**Nội dung chính**:
- ✅ 3 cách chạy nhanh (1 phút)
- ✅ Verify script đã sửa
- ✅ Test steps (5 tests)
- ✅ Common errors & fixes
- ✅ Success checklist

**Đọc tài liệu này nếu bạn**:
- Gặp lỗi ngay lập tức
- Cần fix nhanh trong 1 phút
- Script tìm `venv` thay vì `.venv`
- Muốn test xem script hoạt động chưa

---

## 📊 DOCUMENTATION STATISTICS

### Total Documentation
- **22 documentation files** (+2 Windows guides)
- **3,500+ lines of documentation**
- **9 comprehensive guides**
- **6 quick references** (including Windows-specific)
- **3 project management docs**
- **4 configuration files**

### Coverage
- ✅ Architecture & Design
- ✅ Setup & Deployment
- ✅ Testing & CI/CD
- ✅ Monitoring & Observability
- ✅ Contributing & Community
- ✅ Quick References
- ✅ Production Checklist

---

## 📞 HỖ TRỢ

### Issues & Bugs
- GitHub Issues: https://github.com/your-org/toxic-language-detector/issues

### Documentation
- **System Architecture**: [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)
- **Workflow Analysis**: [WORKFLOW_ANALYSIS.md](./WORKFLOW_ANALYSIS.md)
- **API & Database**: [DATABASE_AND_API.md](./DATABASE_AND_API.md)
- **Deployment**: [DEPLOYMENT_AND_DASHBOARD.md](./DEPLOYMENT_AND_DASHBOARD.md)

### Contributing
- Fork repository
- Create feature branch
- Commit changes
- Push to branch
- Create Pull Request

---

## 📝 CHANGELOG

### Version 1.0.0 (2024-10-19)
- ✅ Initial release
- ✅ LSTM model implementation
- ✅ Chrome extension
- ✅ FastAPI backend
- ✅ Laravel dashboard
- ✅ Multi-platform support (Facebook, YouTube, Twitter)
- ✅ User authentication & authorization
- ✅ Admin dashboard
- ✅ Statistics & analytics
- ✅ Export functionality

### Version 1.1.0 (Planned)
- 🔄 BERT model integration
- 🔄 Real-time notifications
- 🔄 Mobile app
- 🔄 Advanced analytics
- 🔄 Model retraining pipeline

---

## 📜 LICENSE

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 ACKNOWLEDGMENTS

- **FastAPI**: Modern web framework
- **Laravel**: PHP web framework
- **TensorFlow/Keras**: ML framework
- **Transformers**: Hugging Face library
- **underthesea**: Vietnamese NLP library
- **Chart.js**: Data visualization

---

*Tài liệu được tạo bởi AI Assistant*
*Cập nhật lần cuối: 2025-10-19*
*Phiên bản: 1.0.0*

