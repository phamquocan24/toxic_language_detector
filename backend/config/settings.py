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
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pydantic import EmailStr, Field, field_validator
from pydantic_settings import BaseSettings  # Import validator từ pydantic, không phải pydantic_settings

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
    PORT: int = int(os.getenv("PORT", "7860"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"
    
    # URL settings
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:7860")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:7860")
    
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
    
    # ML Model settings (Single model - backward compatible)
    MODEL_PATH: str = os.getenv("MODEL_PATH", "model/model.safetensors")
    MODEL_TYPE: Optional[str] = os.getenv("MODEL_TYPE", None)
    MODEL_VOCAB_PATH: str = os.getenv("MODEL_VOCAB_PATH", "model/vocab.txt")
    MODEL_CONFIG_PATH: str = os.getenv("MODEL_CONFIG_PATH", "model/config.json")
    MODEL_PRELOAD: bool = os.getenv("MODEL_PRELOAD", "True").lower() == "true"
    MODEL_DEVICE: str = os.getenv("MODEL_DEVICE", "cpu")  # "cpu" or "cuda"
    MODEL_LABELS: List[str] = ["clean", "offensive", "hate", "spam"]
    
    # Multi-Model Support (Optional - backward compatible)
    DEFAULT_MODEL: Optional[str] = os.getenv("DEFAULT_MODEL", None)
    MODEL_LOADING_MODE: Optional[str] = os.getenv("MODEL_LOADING_MODE", "single")
    AVAILABLE_MODELS: Optional[str] = os.getenv("AVAILABLE_MODELS", None)
    
    # LSTM Model
    MODEL_LSTM_PATH: Optional[str] = os.getenv("MODEL_LSTM_PATH", None)
    MODEL_LSTM_TYPE: Optional[str] = os.getenv("MODEL_LSTM_TYPE", None)
    MODEL_LSTM_VOCAB: Optional[str] = os.getenv("MODEL_LSTM_VOCAB", None)
    MODEL_LSTM_CONFIG: Optional[str] = os.getenv("MODEL_LSTM_CONFIG", None)
    
    # CNN Model
    MODEL_CNN_PATH: Optional[str] = os.getenv("MODEL_CNN_PATH", None)
    MODEL_CNN_TYPE: Optional[str] = os.getenv("MODEL_CNN_TYPE", None)
    MODEL_CNN_VOCAB: Optional[str] = os.getenv("MODEL_CNN_VOCAB", None)
    MODEL_CNN_CONFIG: Optional[str] = os.getenv("MODEL_CNN_CONFIG", None)
    
    # GRU Model
    MODEL_GRU_PATH: Optional[str] = os.getenv("MODEL_GRU_PATH", None)
    MODEL_GRU_TYPE: Optional[str] = os.getenv("MODEL_GRU_TYPE", None)
    MODEL_GRU_VOCAB: Optional[str] = os.getenv("MODEL_GRU_VOCAB", None)
    MODEL_GRU_CONFIG: Optional[str] = os.getenv("MODEL_GRU_CONFIG", None)
    
    # BERT Model
    MODEL_BERT_PATH: Optional[str] = os.getenv("MODEL_BERT_PATH", None)
    MODEL_BERT_TYPE: Optional[str] = os.getenv("MODEL_BERT_TYPE", None)
    MODEL_BERT_VOCAB: Optional[str] = os.getenv("MODEL_BERT_VOCAB", None)
    MODEL_BERT_CONFIG: Optional[str] = os.getenv("MODEL_BERT_CONFIG", None)
    
    # BERT1800 Model
    MODEL_BERT1800_PATH: Optional[str] = os.getenv("MODEL_BERT1800_PATH", None)
    MODEL_BERT1800_TYPE: Optional[str] = os.getenv("MODEL_BERT1800_TYPE", None)
    MODEL_BERT1800_VOCAB: Optional[str] = os.getenv("MODEL_BERT1800_VOCAB", None)
    MODEL_BERT1800_CONFIG: Optional[str] = os.getenv("MODEL_BERT1800_CONFIG", None)
    
    # BERT4News Model
    MODEL_BERT4NEWS_PATH: Optional[str] = os.getenv("MODEL_BERT4NEWS_PATH", None)
    MODEL_BERT4NEWS_TYPE: Optional[str] = os.getenv("MODEL_BERT4NEWS_TYPE", None)
    MODEL_BERT4NEWS_VOCAB: Optional[str] = os.getenv("MODEL_BERT4NEWS_VOCAB", None)
    MODEL_BERT4NEWS_CONFIG: Optional[str] = os.getenv("MODEL_BERT4NEWS_CONFIG", None)
    
    # PhoBERT Model
    MODEL_PHOBERT_PATH: Optional[str] = os.getenv("MODEL_PHOBERT_PATH", None)
    MODEL_PHOBERT_TYPE: Optional[str] = os.getenv("MODEL_PHOBERT_TYPE", None)
    MODEL_PHOBERT_VOCAB: Optional[str] = os.getenv("MODEL_PHOBERT_VOCAB", None)
    MODEL_PHOBERT_CONFIG: Optional[str] = os.getenv("MODEL_PHOBERT_CONFIG", None)
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: Optional[int] = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Vector database settings
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "sqlite")  # sqlite, postgres, milvus
    VECTOR_DB_DIMENSION: int = int(os.getenv("VECTOR_DB_DIMENSION", "768"))
    
    # Hugging Face settings
    HUGGINGFACE_API_URL: str = os.getenv("HUGGINGFACE_API_URL", "https://api-inference.huggingface.co/models/")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL_ID: str = os.getenv("HUGGINGFACE_MODEL_ID", "")
    USE_HUGGINGFACE_API: bool = os.getenv("USE_HUGGINGFACE_API", "False").lower() == "true"
    
    # Social Media API settings
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "EAAJmqkktUHABO9VveoWDm4JvVRKrec3Q7EoyZAoWSWZBnMrdLo4hqg1G2oBm2Y5mU1UThZBwEJ2TPR8bjcBiuwJ3mZC5fe8Cq7xxZCCnubZCt3yf6PsGCNbjVfHfM8Ieu9Ymcl36U4Aby0PZCUIXffShW32nOP39DU3PVr8fj0sJPH1GK9lAypsKQE8lAGO7vKxBG7pd9bPj8e7geAC56xvHxXT8TGbLLMJTPgQA6lCDhpcu5KCowthipoTsZA0ycv4ZD")
    FACEBOOK_APP_ID: str = os.getenv("FACEBOOK_APP_ID", "675831511601264")
    FACEBOOK_APP_SECRET: str = os.getenv("FACEBOOK_APP_SECRET", "796f4b5ee03dde5c112be6708e0b76eb")
    
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    
    TIKTOK_API_KEY: str = os.getenv("TIKTOK_API_KEY", "")
    
    # Email settings
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "anpham25052004@gmail.com")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "pzro nhir xhnb iurt")
    MAIL_FROM: EmailStr = os.getenv("MAIL_FROM", "anpham25052004@gmail.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Toxic Language Detector")
    MAIL_TLS: bool = os.getenv("MAIL_TLS", "True").lower() == "true"
    MAIL_SSL: bool = os.getenv("MAIL_SSL", "False").lower() == "true"
    MAIL_DEBUG: bool = os.getenv("MAIL_DEBUG", "True").lower() == "true"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # In seconds
    
    # Redis settings (optional - falls back to in-memory if not configured)
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "False").lower() == "true"
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)  # e.g., "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
    REDIS_SOCKET_TIMEOUT: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    REDIS_SOCKET_CONNECT_TIMEOUT: int = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
    
    # Prometheus monitoring (optional)
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "False").lower() == "true"
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    PROMETHEUS_PREFIX: str = os.getenv("PROMETHEUS_PREFIX", "toxic_detector")
    
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
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v):
        if v == "supersecretkey" and os.getenv("ENVIRONMENT", "development") == "production":
            raise ValueError("SECRET_KEY must be changed in production")
        return v

    @field_validator('EXTENSION_API_KEY')
    @classmethod
    def validate_extension_api_key(cls, v):
        if v == "extension-api-key" and os.getenv("ENVIRONMENT", "development") == "production":
            raise ValueError("EXTENSION_API_KEY must be changed in production")
        return v

    @field_validator('ADMIN_PASSWORD')
    @classmethod
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