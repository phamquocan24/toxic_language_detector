"""
Backend application proxy - Chuyển tiếp từ thư mục backend tới app chính
"""
import sys
import os
import logging

# Đảm bảo thư mục gốc trong sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app từ thư mục gốc
try:
    from app import app
except ImportError as e:
    logging.error(f"Không thể import app từ thư mục gốc: {e}")
    # Tạo một ứng dụng FastAPI đơn giản
    from fastapi import FastAPI, Request
    
    app = FastAPI(
        title="Toxic Language Detector API (Backend)",
        description="Proxy app for the main toxic language detector API",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Backend service proxy - Hãy chạy server từ thư mục gốc với lệnh: python -m uvicorn app:app --reload"
        }

# Thông báo cho người dùng biết rằng server đang chạy từ thư mục backend
print("=" * 50)
print("THÔNG BÁO: Server đang chạy từ thư mục 'backend'")
print("Một số tính năng có thể không hoạt động chính xác.")
print("Khuyến nghị: Chạy server từ thư mục gốc với lệnh:")
print("python -m uvicorn app:app --reload")
print("=" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 