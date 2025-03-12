from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, select

from backend.config.settings import settings

# Xác định loại database và tạo URL kết nối phù hợp
if "sqlite" in settings.DATABASE_URL:
    # SQLite connection
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    # PostgreSQL connection
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Tạo engine với tùy chọn phù hợp cho cả SQLite và PostgreSQL
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    # SQLite cần connect_args đặc biệt cho async
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL không cần connect_args đặc biệt
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Create session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create declarative base with metadata
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Async dependency to get DB session
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    
    # Tạo tài khoản admin mặc định
    async with async_session() as session:
        from backend.core.security import get_password_hash
        from backend.db.models.user import User
        from backend.db.models.role import Role
        
        # Check if admin role exists
        result = await session.execute(select(Role).filter(Role.name == "admin"))
        admin_role = result.scalars().first()
        
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator role")
            session.add(admin_role)
            await session.commit()
            await session.refresh(admin_role)
        
        # Check if admin user exists
        result = await session.execute(select(User).filter(User.email == "admin@example.com"))
        admin_user = result.scalars().first()
        
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),  # Mật khẩu mặc định
                role_id=admin_role.id,
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
        
        # Tạo thêm tài khoản user thường nếu cần
        result = await session.execute(select(Role).filter(Role.name == "user"))
        user_role = result.scalars().first()
        
        if not user_role:
            user_role = Role(name="user", description="Regular user role")
            session.add(user_role)
            await session.commit()
            await session.refresh(user_role)
        
        # Tạo tài khoản user thường
        result = await session.execute(select(User).filter(User.email == "user@example.com"))
        regular_user = result.scalars().first()
        
        if not regular_user:
            regular_user = User(
                email="user@example.com",
                username="user",
                hashed_password=get_password_hash("user123"),  # Mật khẩu mặc định
                role_id=user_role.id,
                is_active=True
            )
            session.add(regular_user)
            await session.commit()