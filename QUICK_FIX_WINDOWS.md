# ⚡ QUICK FIX - Chạy ngay trên Windows

## 🎯 Tình huống của bạn

- ✅ Đã có `.venv` folder
- ✅ Đang dùng Git Bash trên Windows
- ❌ Scripts tìm `venv` thay vì `.venv`

---

## 🚀 GIẢI PHÁP NHANH (1 phút)

### Cách 1: Chạy script đã sửa (Khuyến nghị)

```bash
# Script đã được sửa tự động phát hiện .venv và tạo thư mục logs
./scripts/start-all.sh
```

✅ **Script giờ đã:**
- Tự động tìm cả `.venv` và `venv`
- Tự động tạo thư mục `logs/` nếu chưa có
- Hỗ trợ cả Linux/Mac và Windows

---

### Cách 2: Chạy Backend manually

```bash
# Bước 1: Activate virtual environment
source .venv/Scripts/activate

# Bước 2: Kiểm tra dependencies
pip list | grep fastapi

# Bước 3: Nếu thiếu package, install
pip install -r requirements.txt

# Bước 4: Chạy server
python run_server.py
```

Sau đó mở browser: http://localhost:7860

---

### Cách 3: Dùng PowerShell

```powershell
# Mở PowerShell (không phải Git Bash)

# Enable script execution (chỉ chạy 1 lần)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Chạy script
.\scripts\start-all.ps1
```

---

## 🔍 Verify Script đã sửa

Kiểm tra script đã được update:

```bash
# Xem dòng 48-59 của start-all.sh
sed -n '48,59p' scripts/start-all.sh
```

Phải có đoạn code này:
```bash
# Auto-detect virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "⚠️  Virtual environment not found. Using system Python..."
fi
```

---

## 🧪 Test nhanh

```bash
# Test 1: Kiểm tra .venv tồn tại
ls -la .venv/Scripts/activate
# ✅ Phải thấy file activate

# Test 2: Activate thủ công
source .venv/Scripts/activate
# ✅ Prompt sẽ thay đổi có (.venv) ở đầu

# Test 3: Kiểm tra Python
which python
# ✅ Phải trỏ vào .venv/Scripts/python

# Test 4: Test import
python -c "from app import app; print('✅ OK')"
# ✅ Phải in ra "✅ OK"

# Test 5: Chạy script
./scripts/start-backend.sh
# ✅ Phải start server thành công
```

---

## 🐛 Nếu vẫn lỗi

### Lỗi: Dependencies thiếu

```bash
source .venv/Scripts/activate
pip install -r requirements.txt
```

### Lỗi: .env không tồn tại

```bash
cp .env.example .env
# Sau đó edit .env với settings của bạn
```

### Lỗi: Port 7860 đã được dùng

```powershell
# Tìm process
netstat -ano | findstr :7860

# Kill process (thay <PID>)
taskkill /PID <PID> /F
```

### Lỗi: Redis warning

```bash
# Disable Redis nếu không cần
echo "REDIS_ENABLED=False" >> .env
```

---

## ✅ Success Checklist

Sau khi chạy thành công, bạn sẽ thấy:

```bash
🚀 Starting Toxic Language Detector - Full Stack
==================================================

📦 Starting Redis...
⚠️  Redis not found. Starting with Docker...
ℹ️  Skipping Redis (optional)

🔧 Starting Backend API...
✅ Backend started (PID: 12345)

🖥️  Starting Web Dashboard...
✅ Dashboard started (PID: 12346)

==================================================
✅ All services started!

📍 Access points:
   Backend:   http://localhost:7860
   API Docs:  http://localhost:7860/docs
   Health:    http://localhost:7860/health
   Dashboard: http://localhost:8080

📝 Logs:
   Backend:   logs/backend.log
   Dashboard: logs/dashboard.log

🛑 To stop: ./scripts/stop-all.sh
==================================================
```

---

## 🎯 Next Steps

1. **Test Backend**:
   ```bash
   curl http://localhost:7860/health
   ```

2. **Test API**:
   ```bash
   curl http://localhost:7860/docs
   ```

3. **View Logs**:
   ```bash
   tail -f logs/backend.log
   ```

---

## 📞 Nếu cần thêm help

Xem thêm:
- **Full guide**: `WINDOWS_SETUP.md`
- **Quick reference**: `QUICK_REFERENCE.md`
- **Troubleshooting**: `SETUP_AND_RUN_GUIDE.md`

---

*Quick Fix Guide - Created: 2025-10-19*

