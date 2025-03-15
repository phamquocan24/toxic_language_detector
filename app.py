# app.py - Main entry point for the FastAPI application

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routes import admin, auth, extension, prediction, toxic_detection
from core.middleware import LogMiddleware
from db.models.base import Base
from db.models.user import engine
import uvicorn

app = FastAPI(
    title="Toxic Language Detector API",
    description="API for detecting toxic language in social media comments",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LogMiddleware)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(extension.router, prefix="/extension", tags=["Extension"])
app.include_router(prediction.router, prefix="/predict", tags=["Prediction"])
app.include_router(toxic_detection.router, prefix="/detect", tags=["Toxic Detection"])

# Create database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)