# 🚀 Scripts Documentation

Thư mục này chứa các scripts để setup và chạy toàn bộ hệ thống.

## 📋 Danh sách Scripts

### Backend Scripts
- **`start-backend.sh`** / **`start-backend.ps1`** - Khởi động Backend API ✅
- **`stop-backend.sh`** / **`stop-backend.ps1`** - Dừng Backend API ✅

### Dashboard Scripts  
- **`start-dashboard.sh`** / **`start-dashboard.ps1`** - Khởi động Web Dashboard
- **`stop-dashboard.sh`** / **`stop-dashboard.ps1`** - Dừng Dashboard ✅

### Extension Scripts
- **`package-extension.sh`** / **`package-extension.ps1`** - Đóng gói Extension để upload lên Chrome Web Store

### Full Stack Scripts
- **`start-all.sh`** / **`start-all.ps1`** - Khởi động tất cả services ✅
- **`stop-all.sh`** / **`stop-all.ps1`** - Dừng tất cả services ✅

## 🎯 Quick Start

### Linux/Mac

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start all services
./scripts/start-all.sh

# Or start individually
./scripts/start-backend.sh
./scripts/start-dashboard.sh

# Package extension
./scripts/package-extension.sh

# Stop all services
./scripts/stop-all.sh
```

### Windows

```powershell
# Start all services
.\scripts\start-all.ps1

# Or start individually
.\scripts\start-backend.ps1
.\scripts\start-dashboard.ps1

# Package extension
.\scripts\package-extension.ps1

# Stop all services
.\scripts\stop-all.ps1
```

## 📝 Script Details

### start-backend (.sh / .ps1)
**Chức năng**: Khởi động Backend API server

**Prerequisites**:
- Python 3.8+
- Virtual environment đã setup
- .env file đã cấu hình

**Ports**:
- API: 7860
- Redis: 6379 (optional)

**Output**:
- Backend API: http://localhost:7860
- API Docs: http://localhost:7860/docs
- Health: http://localhost:7860/health

---

### start-dashboard (.sh / .ps1)
**Chức năng**: Khởi động Laravel Dashboard

**Prerequisites**:
- PHP 8.1+
- Composer dependencies installed
- Node.js dependencies installed
- Database configured

**Port**: 8080

**Output**:
- Dashboard: http://localhost:8080

---

### package-extension (.sh / .ps1)
**Chức năng**: Đóng gói extension thành .zip file

**Output**: `dist/toxic-detector-extension-vX.X.X.zip`

**Next Steps**:
1. Go to Chrome Web Store Developer Dashboard
2. Upload ZIP file
3. Fill store listing details
4. Submit for review

---

### start-all (.sh / .ps1)
**Chức năng**: Khởi động toàn bộ stack

**Services Started**:
1. Redis (port 6379)
2. Backend API (port 7860)
3. Web Dashboard (port 8080)

**Logs**:
- Backend: `logs/backend.log`
- Dashboard: `logs/dashboard.log`

---

## 🐛 Troubleshooting

### Port Already In Use

**Linux/Mac**:
```bash
# Find process using port
lsof -i :7860
lsof -i :8080

# Kill process
kill -9 <PID>
```

**Windows**:
```powershell
# Find process using port
Get-NetTCPConnection -LocalPort 7860
Get-NetTCPConnection -LocalPort 8080

# Kill process
Stop-Process -Id <PID> -Force
```

### Permission Denied (Linux/Mac)

```bash
# Make script executable
chmod +x scripts/start-backend.sh

# Or run with bash
bash scripts/start-backend.sh
```

### Script Not Found (Windows)

```powershell
# Run from project root
cd path\to\toxic-language-detector
.\scripts\start-backend.ps1

# Or allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 Service Status Check

```bash
# Check if services are running

# Backend
curl http://localhost:7860/health

# Dashboard
curl http://localhost:8080

# Redis
redis-cli ping
```

## 🔄 Update Scripts

Scripts are version-controlled. To update:

```bash
git pull origin main
chmod +x scripts/*.sh  # Linux/Mac only
```

## 📚 Additional Resources

- **Setup Guide**: See `SETUP_AND_RUN_GUIDE.md`
- **Improvements**: See `IMPROVEMENTS_SUMMARY.md`
- **Quick Start**: See `QUICK_START_IMPROVEMENTS.md`

