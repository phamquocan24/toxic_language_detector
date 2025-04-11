# # db/models/base.py
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# import os

# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./toxic_detector.db")

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
# db/models/base.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.config.settings import settings
import logging
import time

# Thiết lập logging
logger = logging.getLogger("db.base")

# Xử lý URL database từ thiết lập
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Xác định tham số kết nối tùy thuộc vào loại database
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Tạo engine với tùy chọn bổ sung
try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args=connect_args,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=3600,  # Tái sử dụng kết nối sau 1 giờ
        echo=settings.DB_ECHO  # Log SQL queries nếu được bật
    )
    logger.info(f"Database engine created for {SQLALCHEMY_DATABASE_URL.split('://')[0]}")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

# Tạo session factory với scoped_session để hỗ trợ multi-threading
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine,
        expire_on_commit=False  # Tránh các vấn đề lazy-loading sau commit
    )
)

# Base class cho tất cả các models
Base = declarative_base()

# Thêm phương thức to_dict() cho tất cả các model
def to_dict(self):
    """
    Chuyển đổi model thành dictionary
    """
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Base.to_dict = to_dict

# Mixin class cho timestamps
class TimestampMixin:
    """
    Mixin class để thêm created_at và updated_at vào models
    """
    from sqlalchemy import Column, DateTime
    from datetime import datetime
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Hàm kiểm tra kết nối database
def check_database_connection():
    """
    Kiểm tra kết nối database
    
    Returns:
        tuple: (is_connected, latency_ms)
    """
    db = SessionLocal()
    try:
        start_time = time.time()
        db.execute("SELECT 1")
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        return True, latency_ms
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False, 0
    finally:
        db.close()

# Hàm kiểm tra kích thước database
def get_database_size():
    """
    Lấy kích thước database (chỉ hỗ trợ SQLite và PostgreSQL)
    
    Returns:
        int: Kích thước database theo bytes
    """
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        import os
        db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_path):
            return os.path.getsize(db_path)
    elif SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
        db = SessionLocal()
        try:
            db_name = SQLALCHEMY_DATABASE_URL.split("/")[-1]
            result = db.execute(
                "SELECT pg_database_size(%s)", (db_name,)
            ).scalar()
            return result
        except Exception as e:
            logger.error(f"Error getting database size: {str(e)}")
        finally:
            db.close()
    return 0