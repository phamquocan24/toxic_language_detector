# 🪟 Windows Setup Guide

Hướng dẫn cài đặt và chạy trên Windows.

---

## 🚀 Quick Start cho Windows

### Option 1: Git Bash (Khuyến nghị cho Windows)

```bash
# Đảm bảo đang ở thư mục gốc của project
cd /d/CMC_NCKH_2/Biểu\ mẫu/EUREKA/System/toxic-language-detector

# Kiểm tra virtual environment
ls -la .venv/Scripts/activate  # Nếu có .venv
ls -la venv/Scripts/activate   # Nếu có venv

# Chạy script
./scripts/start-all.sh
```

### Option 2: PowerShell

```powershell
# Mở PowerShell (Run as Administrator)
cd D:\CMC_NCKH_2\Biểu mẫu\EUREKA\System\toxic-language-detector

# Enable script execution (chỉ cần chạy 1 lần)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Chạy script
.\scripts\start-all.ps1
```

### Option 3: Manual (Nếu scripts không chạy được)

```bash
# Terminal 1 - Backend
.venv/Scripts/activate        # Nếu dùng .venv
# HOẶC
venv/Scripts/activate         # Nếu dùng venv

python run_server.py
```

---

## 🔧 Khắc phục lỗi thường gặp

### 1. `make: command not found`

**Nguyên nhân**: Git Bash trên Windows không có `make` command.

**Giải pháp**: Sử dụng scripts thay vì Makefile

```bash
# Thay vì
make start

# Dùng
./scripts/start-all.sh
```

**Hoặc cài đặt make cho Windows**:
```bash
# Option A: Cài qua Chocolatey
choco install make

# Option B: Cài qua Scoop
scoop install make

# Option C: Dùng MinGW
# Download từ: https://sourceforge.net/projects/mingw/
```

---

### 2. `venv/bin/activate: No such file or directory`

**Nguyên nhân**: Bạn có `.venv` (có dấu chấm) nhưng script tìm `venv`.

**Giải pháp**: Script đã được sửa tự động phát hiện! Chỉ cần chạy lại:

```bash
./scripts/start-all.sh
```

**Nếu vẫn lỗi, tạo lại virtual environment**:
```bash
# Xóa cũ (nếu cần)
rm -rf .venv

# Tạo mới
python -m venv .venv

# Activate
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 3. `.\scripts\start-all.ps1: command not found` (trong Git Bash)

**Nguyên nhân**: Git Bash không chạy PowerShell scripts (`.ps1`).

**Giải pháp A** - Dùng file `.sh`:
```bash
./scripts/start-all.sh
```

**Giải pháp B** - Mở PowerShell:
```powershell
# Mở PowerShell riêng
.\scripts\start-all.ps1
```

---

### 4. Port đã được sử dụng

**Lỗi**: `Port 7860 already in use`

**Giải pháp**:

```powershell
# Tìm process đang dùng port
netstat -ano | findstr :7860

# Kill process (thay <PID> bằng số process ID)
taskkill /PID <PID> /F
```

---

### 5. Redis không chạy

**Lỗi**: `Redis not found`

**Giải pháp A** - Disable Redis:
```bash
# Tạo .env file
cp .env.example .env

# Sửa trong .env
REDIS_ENABLED=False
```

**Giải pháp B** - Cài Redis cho Windows:
```powershell
# Option 1: Dùng Docker
docker run -d -p 6379:6379 --name redis redis:alpine

# Option 2: Dùng Memurai (Redis for Windows)
# Download: https://www.memurai.com/

# Option 3: Dùng WSL
wsl -d Ubuntu
sudo service redis-server start
```

---

### 6. Permission Denied khi chạy scripts

**Giải pháp**:

```bash
# Thêm quyền thực thi
chmod +x scripts/*.sh

# Hoặc chạy với bash
bash scripts/start-all.sh
```

---

### 7. Python command not found

**Giải pháp**:

```bash
# Kiểm tra Python đã cài chưa
python --version
py --version
python3 --version

# Nếu chưa có, download từ:
# https://www.python.org/downloads/

# Trong quá trình cài, tick vào:
# ✅ Add Python to PATH
```

---

### 8. Module not found errors

**Lỗi**: `ModuleNotFoundError: No module named 'fastapi'`

**Giải pháp**:

```bash
# Activate virtual environment
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

## 📋 Checklist cho Windows

### Kiểm tra môi trường

```bash
# 1. Kiểm tra Python
python --version  # Phải >= 3.8

# 2. Kiểm tra pip
pip --version

# 3. Kiểm tra virtual environment
ls -la .venv/Scripts/activate

# 4. Activate venv
source .venv/Scripts/activate

# 5. Kiểm tra packages
pip list

# 6. Kiểm tra .env file
ls -la .env

# 7. Test backend
python -c "from app import app; print('OK')"
```

---

## 🎯 Recommended Workflow cho Windows

### Setup lần đầu

```bash
# 1. Clone project (đã có rồi)
cd /d/CMC_NCKH_2/Biểu\ mẫu/EUREKA/System/toxic-language-detector

# 2. Tạo virtual environment (nếu chưa có)
python -m venv .venv

# 3. Activate
source .venv/Scripts/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy .env
cp .env.example .env

# 6. Edit .env với settings của bạn
nano .env  # hoặc notepad .env

# 7. Run migrations (optional)
python -m backend.db.migrations.add_performance_indexes

# 8. Start server
./scripts/start-backend.sh
```

### Hàng ngày

```bash
# Mở Git Bash tại thư mục project

# Option A: Chạy all services
./scripts/start-all.sh

# Option B: Chỉ chạy backend
./scripts/start-backend.sh

# Stop services
./scripts/stop-all.sh
```

---

## 🔧 Alternative: Dùng Python trực tiếp

Nếu scripts không hoạt động, bạn có thể chạy trực tiếp:

```bash
# Activate venv
source .venv/Scripts/activate

# Start backend
python run_server.py

# Hoặc dùng uvicorn trực tiếp
uvicorn app:app --reload --port 7860 --host 0.0.0.0
```

---

## 🐳 Docker Alternative

Nếu gặp quá nhiều vấn đề, dùng Docker:

```bash
# Install Docker Desktop for Windows
# Download: https://www.docker.com/products/docker-desktop

# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f
```

---

## 📝 Windows-Specific Notes

### Path Differences

**Linux/Mac**:
```bash
.venv/bin/activate
venv/bin/activate
```

**Windows (Git Bash)**:
```bash
.venv/Scripts/activate
venv/Scripts/activate
```

**Windows (PowerShell)**:
```powershell
.venv\Scripts\Activate.ps1
venv\Scripts\Activate.ps1
```

### Line Endings

Nếu gặp lỗi `$'\r': command not found`:

```bash
# Convert line endings từ CRLF sang LF
dos2unix scripts/*.sh

# Hoặc dùng Git
git config core.autocrlf false
git rm --cached -r .
git reset --hard
```

---

## 🆘 Vẫn gặp lỗi?

### Debug Steps

1. **Kiểm tra cấu trúc thư mục**:
```bash
ls -la
ls -la .venv/Scripts/
```

2. **Kiểm tra Python path**:
```bash
which python
python --version
```

3. **Test import**:
```bash
source .venv/Scripts/activate
python -c "import fastapi; print(fastapi.__version__)"
```

4. **Check logs**:
```bash
cat logs/backend.log
tail -f app.log
```

5. **Manual start từng bước**:
```bash
# Step 1: Activate venv
source .venv/Scripts/activate

# Step 2: Test import
python -c "from app import app"

# Step 3: Start server
python run_server.py
```

---

## 📞 Contact

Nếu vẫn gặp vấn đề:
1. Check logs: `logs/backend.log`
2. Check terminal errors
3. Create GitHub issue với:
   - Output của `python --version`
   - Output của `pip list`
   - Full error message
   - Screenshot nếu có

---

## ✅ Verified Working on Windows

Đã test trên:
- ✅ Windows 10 với Git Bash
- ✅ Windows 11 với PowerShell
- ✅ WSL2 (Ubuntu on Windows)

---

*Last Updated: 2025-10-19*
*Tested on: Windows 10/11, Git Bash 2.x*

