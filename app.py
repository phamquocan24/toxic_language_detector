import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys

# Thêm routes từ backend
try:
    from backend.api.routes import admin, auth, extension
except ImportError:
    print("Cannot import routes from backend")

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các routes
try:
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(extension.router, prefix="/api/extension", tags=["Extension"])
    app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
except NameError:
    pass

@app.get("/")
async def root():
    return {"message": "Toxicity Detector API is running on Hugging Face Spaces", "status": "online"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860)