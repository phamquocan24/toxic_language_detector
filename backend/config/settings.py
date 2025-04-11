# # config/settings.py
# import os
# from pydantic_settings import BaseSettings
# from typing import List

# class Settings(BaseSettings):
#     # API settings
#     PROJECT_NAME: str = "Toxic Language Detector"
#     API_V1_STR: str = "/api/v1"
#     DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
#     # Security settings
#     SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
#     # Extension API key
#     EXTENSION_API_KEY: str = os.getenv("EXTENSION_API_KEY", "extension-api-key")
    
#     # Database settings
#     DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./toxic_detector.db")
    
#     # CORS settings
#     CORS_ORIGINS: List[str] = [
#         "http://localhost",
#         "http://localhost:3000",  # Frontend development
#         "http://localhost:8000",  # Backend development
#         "chrome-extension://*",   # Chrome extension
#     ]
    
#     # ML Model settings
#     MODEL_PATH: str = os.getenv("MODEL_PATH", "model/model.safetensors")
    
#     # Hugging Face settings
#     HUGGINGFACE_API_URL: str = os.getenv("HUGGINGFACE_API_URL", "https://api-inference.huggingface.co/models/")
#     HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
#     # Social Media API settings
#     FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
#     TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
#     YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    
#     class Config:
#         env_file = ".env"

# settings = Settings()
# config/settings.py
import os
from pydantic_settings import BaseSettings, validator, EmailStr, Field
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    # API settings
    PROJECT_NAME: str = "Vietnamese Toxic Language Detector"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for Vietnamese Toxic Language Detection on Social Media"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days
    
    # Extension API key
    EXTENSION_API_KEY: str = os.getenv("EXTENSION_API_KEY", "extension-api-key")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./toxic_detector.db")
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",  # Frontend development
        "http://localhost:8000",  # Backend development
        "chrome-extension://*",   # Chrome extension
    ]
    
    # ML Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "model/model.safetensors")
    MODEL_VOCAB_PATH: str = os.getenv("MODEL_VOCAB_PATH", "model/vocab.txt")
    MODEL_CONFIG_PATH: str = os.getenv("MODEL_CONFIG_PATH", "model/config.json")
    MODEL_PRELOAD: bool = os.getenv("MODEL_PRELOAD", "True").lower() == "true"
    MODEL_DEVICE: str = os.getenv("MODEL_DEVICE", "cpu")  # "cpu" or "cuda"
    MODEL_LABELS: List[str] = ["clean", "offensive", "hate", "spam"]
    
    # Vector database settings
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "sqlite")  # sqlite, postgres, milvus
    VECTOR_DB_DIMENSION: int = int(os.getenv("VECTOR_DB_DIMENSION", "768"))
    
    # Hugging Face settings
    HUGGINGFACE_API_URL: str = os.getenv("HUGGINGFACE_API_URL", "https://api-inference.huggingface.co/models/")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL_ID: str = os.getenv("HUGGINGFACE_MODEL_ID", "")
    USE_HUGGINGFACE_API: bool = os.getenv("USE_HUGGINGFACE_API", "False").lower() == "true"
    
    # Social Media API settings
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    FACEBOOK_APP_ID: str = os.getenv("FACEBOOK_APP_ID", "")
    FACEBOOK_APP_SECRET: str = os.getenv("FACEBOOK_APP_SECRET", "")
    
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    
    TIKTOK_API_KEY: str = os.getenv("TIKTOK_API_KEY", "")
    
    # Email settings
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: EmailStr = os.getenv("MAIL_FROM", "noreply@example.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Toxic Language Detector")
    MAIL_TLS: bool = os.getenv("MAIL_TLS", "True").lower() == "true"
    MAIL_SSL: bool = os.getenv("MAIL_SSL", "False").lower() == "true"
    MAIL_DEBUG: bool = os.getenv("MAIL_DEBUG", "False").lower() == "true"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # In seconds
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "False").lower() == "true"
    LOG_FILENAME: str = os.getenv("LOG_FILENAME", "app.log")
    
    # Text preprocessing
    TEXT_PREPROCESSING: Dict[str, bool] = {
        "lowercase": os.getenv("TEXT_LOWERCASE", "True").lower() == "true",
        "remove_urls": os.getenv("TEXT_REMOVE_URLS", "True").lower() == "true",
        "remove_mentions": os.getenv("TEXT_REMOVE_MENTIONS", "True").lower() == "true",
        "remove_hashtags": os.getenv("TEXT_REMOVE_HASHTAGS", "False").lower() == "true",
        "remove_punctuation": os.getenv("TEXT_REMOVE_PUNCTUATION", "False").lower() == "true",
        "remove_emojis": os.getenv("TEXT_REMOVE_EMOJIS", "False").lower() == "true",
        "remove_numbers": os.getenv("TEXT_REMOVE_NUMBERS", "False").lower() == "true",
    }
    
    # Admin default account
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL: EmailStr = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "password")
    CREATE_ADMIN_IF_NOT_EXISTS: bool = os.getenv("CREATE_ADMIN_IF_NOT_EXISTS", "True").lower() == "true"
    
    # Extension settings
    EXTENSION_DEFAULT_SETTINGS: Dict[str, Any] = {
        "enabled_platforms": ["facebook", "youtube", "twitter", "tiktok"],
        "auto_analyze": True,
        "highlight_comments": True,
        "notification": True,
        "store_clean": False,
        "threshold": 0.7
    }
    
    # Vietnamese language specific settings
    VIETNAMESE_STOPWORDS_FILE: Optional[str] = os.getenv("VIETNAMESE_STOPWORDS_FILE", "data/vietnamese_stopwords.txt")
    VIETNAMESE_OFFENSIVE_WORDLIST_FILE: Optional[str] = os.getenv("VIETNAMESE_OFFENSIVE_WORDLIST_FILE", "data/vietnamese_offensive_words.txt")
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "supersecretkey" and os.getenv("ENVIRONMENT", "development") == "production":
            raise ValueError("SECRET_KEY must be changed in production")
        return v
    
    @validator("EXTENSION_API_KEY")
    def validate_extension_api_key(cls, v):
        if v == "extension-api-key" and os.getenv("ENVIRONMENT", "development") == "production":
            raise ValueError("EXTENSION_API_KEY must be changed in production")
        return v
    
    @validator("ADMIN_PASSWORD")
    def validate_admin_password(cls, v):
        if v == "password" and os.getenv("ENVIRONMENT", "development") == "production":
            raise ValueError("ADMIN_PASSWORD must be changed in production")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def get_model_labels_dict(self) -> Dict[int, str]:
        """Get mapping from prediction integers to label strings"""
        return {i: label for i, label in enumerate(self.MODEL_LABELS)}

settings = Settings()