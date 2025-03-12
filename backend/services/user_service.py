from typing import Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, or_, and_

from backend.db.models.user import User
from backend.db.models.role import Role
from backend.core.security import get_password_hash, verify_password
from datetime import datetime

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get a user by ID
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get a user by email
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Get a user by username
    """
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_users(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None
) -> List[User]:
    """
    Get a list of users with pagination and optional search
    """
    query = select(User)
    
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_user(
    db: AsyncSession,
    user_data: Dict[str, Any],
    role_name: str = "user"
) -> User:
    """
    Create a new user with specified role
    """
    # Check if role exists, create if not
    result = await db.execute(select(Role).filter(Role.name == role_name))
    role = result.scalars().first()
    
    if not role:
        role = Role(name=role_name, description=f"{role_name.capitalize()} role")
        db.add(role)
        await db.commit()
        await db.refresh(role)
    
    # Create new user
    new_user = User(
        email=user_data["email"],
        username=user_data["username"],
        hashed_password=get_password_hash(user_data["password"]),
        role_id=role.id,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

async def update_user(
    db: AsyncSession,
    user_id: int,
    user_data: Dict[str, Any]
) -> Optional[User]:
    """
    Update a user's information
    """
    user = await get_user(db, user_id)
    if not user:
        return None
    
    # Update user attributes
    for key, value in user_data.items():
        if key == "password":
            user.hashed_password = get_password_hash(value)
        elif hasattr(user, key):
            setattr(user, key, value)
    
    # If role_name is provided, update role
    if "role_name" in user_data:
        role_name = user_data["role_name"]
        result = await db.execute(select(Role).filter(Role.name == role_name))
        role = result.scalars().first()
        
        if not role:
            role = Role(name=role_name, description=f"{role_name.capitalize()} role")
            db.add(role)
            await db.commit()
            await db.refresh(role)
        
        user.role_id = role.id
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Delete a user
    """
    user = await get_user(db, user_id)
    if not user:
        return False
    
    await db.delete(user)
    await db.commit()
    
    return True

async def change_password(
    db: AsyncSession,
    user_id: int,
    current_password: str,
    new_password: str
) -> bool:
    """
    Change a user's password
    """
    user = await get_user(db, user_id)
    if not user:
        return False
    
    # Verify current password
    if not verify_password(current_password, user.hashed_password):
        return False
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    
    db.add(user)
    await db.commit()
    
    return True

async def activate_user(db: AsyncSession, user_id: int, is_active: bool = True) -> bool:
    """
    Activate or deactivate a user
    """
    user = await get_user(db, user_id)
    if not user:
        return False
    
    user.is_active = is_active
    
    db.add(user)
    await db.commit()
    
    return True

async def get_role(db: AsyncSession, role_id: int) -> Optional[Role]:
    """
    Get a role by ID
    """
    result = await db.execute(select(Role).filter(Role.id == role_id))
    return result.scalars().first()

async def get_role_by_name(db: AsyncSession, role_name: str) -> Optional[Role]:
    """
    Get a role by name
    """
    result = await db.execute(select(Role).filter(Role.name == role_name))
    return result.scalars().first()

async def get_roles(db: AsyncSession) -> List[Role]:
    """
    Get all roles
    """
    result = await db.execute(select(Role))
    return result.scalars().all()

async def create_role(db: AsyncSession, name: str, description: Optional[str] = None) -> Role:
    """
    Create a new role
    """
    role = Role(
        name=name,
        description=description or f"{name.capitalize()} role"
    )
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return role

async def change_user_role(db: AsyncSession, user_id: int, role_name: str) -> bool:
    """
    Change a user's role
    """
    user = await get_user(db, user_id)
    if not user:
        return False
    
    # Get or create role
    result = await db.execute(select(Role).filter(Role.name == role_name))
    role = result.scalars().first()
    
    if not role:
        role = await create_role(db, role_name)
    
    user.role_id = role.id
    
    db.add(user)
    await db.commit()
    
    return True