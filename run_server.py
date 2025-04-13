#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script khởi động máy chủ FastAPI cho dự án phát hiện ngôn từ tiêu cực
"""

import os
import sys
import subprocess
import platform
import socket

def get_local_ip():
    """Lấy địa chỉ IP của máy tính trên mạng local"""
    try:
        # Tạo socket để xác định địa chỉ IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Kết nối đến server bên ngoài (không cần thực sự gửi dữ liệu)
        s.connect(("8.8.8.8", 80))
        # Lấy địa chỉ IP của máy tính hiện tại
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"  # Fallback nếu không thể xác định IP

def main():
    """Hàm chính để thiết lập môi trường và chạy máy chủ"""
    # Đặt encoding cho môi trường
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
    # Thiết lập console để hiển thị tiếng Việt trên Windows
    if platform.system() == "Windows":
        os.system("chcp 65001")
    
    print("===== Khởi động máy chủ API phát hiện ngôn từ tiêu cực =====")
    print(f"OS: {platform.system()} - {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("=============================================================")
    
    # Chạy ứng dụng FastAPI
    from app import app
    import uvicorn
    
    # Xác định port từ biến môi trường hoặc mặc định
    port = int(os.environ.get("PORT", 7860))
    
    # Lấy địa chỉ IP local để hiển thị thông báo hữu ích
    local_ip = get_local_ip()
    
    print("\nSau khi khởi động, bạn có thể truy cập API qua các địa chỉ sau:")
    print(f"- Local:      http://localhost:{port}")
    print(f"- Loopback:   http://127.0.0.1:{port}")
    print(f"- Mạng LAN:   http://{local_ip}:{port}")
    print("\nĐể xem tài liệu API, truy cập: http://localhost:{port}/docs")
    print("Để sử dụng giao diện Gradio, truy cập: http://localhost:{port}/gradio")
    print("=============================================================\n")
    
    # Khởi động uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main() 