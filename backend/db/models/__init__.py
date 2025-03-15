# db/models/__init__.py
from .base import Base, engine, SessionLocal
from .user import User
from .role import Role
from .comment import Comment
from .log import Log

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()