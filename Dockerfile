# Base image có CUDA 11.8, cuDNN 8 và Ubuntu
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Cài Python 3.10
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3-pip python3.10-dev \
    git curl wget unzip \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Dùng Python 3.10 làm mặc định
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements và cài thư viện
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy mã nguồn vào container
COPY . .

# Cài đặt TensorRT (nếu bạn có file .tar.gz, hoặc đang dùng server riêng)
# COPY TensorRT-10.x.x.x.tar.gz /tmp/
# RUN cd /tmp && tar -xvzf TensorRT-*.tar.gz && \
#     cp -r TensorRT-*/python/* /usr/local/lib/python3.10/dist-packages/ && \
#     cp -r TensorRT-*/lib/* /usr/lib/x86_64-linux-gnu/

# Nếu bạn dùng model chuyển đổi sẵn trước khi chạy server
RUN python convert_model.py

# Mở port cho FastAPI
EXPOSE 7860

# Chạy app bằng uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
