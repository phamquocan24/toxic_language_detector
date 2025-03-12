import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Config
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Social Media Toxicity Detector"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "12345")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
        "chrome-extension://*",
        "*"  # Thêm wildcard để cho phép tất cả origins trong môi trường phát triển
    ]
    
    # Database - Đã thay đổi để sử dụng SQLite cho Hugging Face Spaces
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./toxicity_detector.db"
    )
    
    # ML Model
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./model/best_model_LSTM.h5")  # Đường dẫn đơn giản hơn
    HUGGINGFACE_API_URL: str = os.getenv("HUGGINGFACE_API_URL", "https://an24-toxic-language-detector.hf.space/api/predict")
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "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")
    
    # Social Media APIs
    FACEBOOK_API_KEY: str = os.getenv("FACEBOOK_API_KEY", "81da742fd0cc2234df9471509b95a07a")
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "KCAAIYtIgrrlGM80USEOZHBgQ")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "AIzaSyCEFKJNt_leCo246CaMsSaqw7Yj39YijC4")
    
    # Hugging Face Spaces configuration
    PORT: int = os.getenv("PORT", 7860)  # Port mặc định cho Hugging Face Spaces
    
    class Config:
        case_sensitive = True

settings = Settings()