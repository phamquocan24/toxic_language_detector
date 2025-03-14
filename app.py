import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Khởi tạo app FastAPI (KHÔNG dùng backend_app)
app = FastAPI()

# Đảm bảo CORS được cấu hình đúng
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route mặc định cho kiểm tra
@app.get("/")
async def root():
    return {"message": "Toxicity Detector API is running on Hugging Face Spaces"}

# Chạy app nếu script được thực thi trực tiếp
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860)