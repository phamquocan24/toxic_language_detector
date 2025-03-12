FROM python:3.9-slim

WORKDIR /app

# Cài đặt các dependencies cần thiết
RUN apt-get update && apt-get install -y \
    postgresql-client \
    sqlite3 \
    gcc \
    python3-dev \
    python3-pip \
    libpq-dev \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cập nhật pip, setuptools, wheel trước
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Sao chép và cài đặt dependencies trước (tối ưu cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ ứng dụng
COPY . .

# Mở port 8000
EXPOSE 8000

# Lệnh chạy ứng dụng
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]