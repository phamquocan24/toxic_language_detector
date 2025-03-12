from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, Request
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from datetime import datetime, timedelta

from backend.db.base import get_db
from backend.db.models.comment import Comment
from backend.db.models.user import User
from backend.db.models.role import Role
from backend.db.models.log import Log
from backend.core.security import admin_required, get_current_active_user, check_permission, get_password_hash

router = APIRouter()

# User management routes
@router.get("/users", response_model=Dict[str, Any])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    List all users (admin only)
    """
    query = select(User).join(Role)
    
    # Apply search filter if provided
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Get total count
    count_query = select(func.count()).select_from(User)
    if search:
        count_query = count_query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Format response
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]
    }

@router.post("/users", response_model=Dict[str, Any])
async def create_user(
    user_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Create a new user (admin only)
    """
    email = user_data.get("email")
    username = user_data.get("username")
    password = user_data.get("password")
    role_name = user_data.get("role", "user")
    
    # Validate required fields
    if not email or not username or not password:
        raise HTTPException(status_code=400, detail="Email, username and password are required")
    
    # Check if email already exists
    result = await db.execute(select(User).filter(User.email == email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    result = await db.execute(select(User).filter(User.username == username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Get role id
    result = await db.execute(select(Role).filter(Role.name == role_name))
    role = result.scalars().first()
    
    if not role:
        # Create role if it doesn't exist
        role = Role(name=role_name, description=f"{role_name.capitalize()} role")
        db.add(role)
        await db.commit()
        await db.refresh(role)
    
    # Create user
    new_user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        role_id=role.id,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Log the action
    log_entry = Log(
        user_id=current_user.id,
        action="create_user",
        endpoint="/api/admin/users",
        request_data={"email": email, "username": username, "role": role_name},
        status_code=200,
        details=f"Created user {username} with role {role_name}"
    )
    db.add(log_entry)
    await db.commit()
    
    return {
        "success": True,
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": role_name
    }

@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user(
    user_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Get a specific user by ID (admin only)
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.name,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }

@router.put("/users/{user_id}", response_model=Dict[str, Any])
async def update_user(
    user_id: int = Path(...),
    user_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Update a user (admin only)
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if "username" in user_data:
        # Check if username already exists
        result = await db.execute(select(User).filter(
            and_(User.username == user_data["username"], User.id != user_id)
        ))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = user_data["username"]
    
    if "email" in user_data:
        # Check if email already exists
        result = await db.execute(select(User).filter(
            and_(User.email == user_data["email"], User.id != user_id)
        ))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = user_data["email"]
    
    if "password" in user_data:
        user.hashed_password = get_password_hash(user_data["password"])
    
    if "is_active" in user_data:
        user.is_active = user_data["is_active"]
    
    if "role" in user_data:
        role_name = user_data["role"]
        result = await db.execute(select(Role).filter(Role.name == role_name))
        role = result.scalars().first()
        
        if not role:
            # Create role if it doesn't exist
            role = Role(name=role_name, description=f"{role_name.capitalize()} role")
            db.add(role)
            await db.commit()
            await db.refresh(role)
        
        user.role_id = role.id
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Log the action
    log_entry = Log(
        user_id=current_user.id,
        action="update_user",
        endpoint=f"/api/admin/users/{user_id}",
        request_data=user_data,
        status_code=200,
        details=f"Updated user {user.username}"
    )
    db.add(log_entry)
    await db.commit()
    
    return {
        "success": True,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.name,
        "is_active": user.is_active
    }

# Comment management routes
@router.get("/comments", response_model=Dict[str, Any])
async def list_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    classification: Optional[int] = Query(None, ge=0, le=3),
    platform: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_permission("read"))
):
    """
    List comments with filtering options
    """
    query = select(Comment).join(User)
    
    # Apply filters
    if classification is not None:
        query = query.filter(Comment.classification_result == classification)
    
    if platform:
        query = query.filter(Comment.source_platform == platform)
    
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
            query = query.filter(Comment.created_at >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)")
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            # Add one day to include the end date
            end_datetime = end_datetime + timedelta(days=1)
            query = query.filter(Comment.created_at < end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)")
    
    # Apply ordering
    query = query.order_by(desc(Comment.created_at))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    comments = result.scalars().all()
    
    # Get total count
    count_query = select(func.count()).select_from(Comment)
    
    # Apply the same filters to count query
    if classification is not None:
        count_query = count_query.filter(Comment.classification_result == classification)
    
    if platform:
        count_query = count_query.filter(Comment.source_platform == platform)
    
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
            count_query = count_query.filter(Comment.created_at >= start_datetime)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            end_datetime = end_datetime + timedelta(days=1)
            count_query = count_query.filter(Comment.created_at < end_datetime)
        except ValueError:
            pass
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Format response
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "comments": [
            {
                "id": comment.id,
                "user": {
                    "id": comment.user.id,
                    "username": comment.user.username
                },
                "source_platform": comment.source_platform,
                "platform_comment_id": comment.platform_comment_id,
                "content": comment.content,
                "classification_result": comment.classification_result,
                "classification_label": ["clean", "offensive", "hate", "spam"][comment.classification_result] if comment.classification_result in range(4) else "unknown",
                "scores": {
                    "clean": comment.clean_score,
                    "offensive": comment.offensive_score,
                    "hate": comment.hate_score,
                    "spam": comment.spam_score
                },
                "created_at": comment.created_at.isoformat() if comment.created_at else None,
                "checked_at": comment.checked_at.isoformat() if comment.checked_at else None
            }
            for comment in comments
        ]
    }

@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_overview_stats(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_permission("read"))
):
    """
    Get overview statistics
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get total comments count
    result = await db.execute(select(func.count()).select_from(Comment))
    total_comments = result.scalar()
    
    # Get comments count by classification
    counts_by_class = {}
    for class_idx, class_name in enumerate(["clean", "offensive", "hate", "spam"]):
        result = await db.execute(
            select(func.count()).select_from(Comment).filter(Comment.classification_result == class_idx)
        )
        counts_by_class[class_name] = result.scalar()
    
    # Get comments count by platform
    query = select(Comment.source_platform, func.count().label("count")).group_by(Comment.source_platform)
    result = await db.execute(query)
    counts_by_platform = {row[0]: row[1] for row in result.all()}
    
    # Get comments per day for time series
    daily_counts_query = text("""
        SELECT 
            date_trunc('day', created_at) as day, 
            classification_result, 
            count(*) 
        FROM comments 
        WHERE created_at >= :start_date 
        GROUP BY day, classification_result 
        ORDER BY day
    """)
    
    result = await db.execute(daily_counts_query, {"start_date": start_date})
    daily_results = result.all()
    
    daily_counts = {}
    for day, class_idx, count in daily_results:
        day_str = day.strftime("%Y-%m-%d")
        if day_str not in daily_counts:
            daily_counts[day_str] = {
                "clean": 0,
                "offensive": 0,
                "hate": 0,
                "spam": 0,
                "total": 0
            }
        
        class_name = ["clean", "offensive", "hate", "spam"][class_idx] if class_idx in range(4) else "other"
        daily_counts[day_str][class_name] = count
        daily_counts[day_str]["total"] += count
    
    # Fill in missing days
    day = start_date
    while day <= end_date:
        day_str = day.strftime("%Y-%m-%d")
        if day_str not in daily_counts:
            daily_counts[day_str] = {
                "clean": 0,
                "offensive": 0,
                "hate": 0,
                "spam": 0,
                "total": 0
            }
        day += timedelta(days=1)
    
    # Convert to sorted list for time series
    time_series = [
        {
            "date": day,
            **daily_counts[day]
        }
        for day in sorted(daily_counts.keys())
    ]
    
    return {
        "total_comments": total_comments,
        "classification_counts": counts_by_class,
        "platform_counts": counts_by_platform,
        "time_series": time_series
    }

# System logs route
@router.get("/logs", response_model=Dict[str, Any])
async def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    List system logs (admin only)
    """
    query = select(Log).join(User)
    
    # Apply filters
    if user_id:
        query = query.filter(Log.user_id == user_id)
    
    if action:
        query = query.filter(Log.action == action)
    
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
            query = query.filter(Log.created_at >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)")
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            # Add one day to include the end date
            end_datetime = end_datetime + timedelta(days=1)
            query = query.filter(Log.created_at < end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)")
    
    # Apply ordering
    query = query.order_by(desc(Log.created_at))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    logs = result.scalars().all()
    
    # Get total count
    count_query = select(func.count()).select_from(Log)
    
    # Apply the same filters to count query
    if user_id:
        count_query = count_query.filter(Log.user_id == user_id)
    
    if action:
        count_query = count_query.filter(Log.action == action)
    
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
            count_query = count_query.filter(Log.created_at >= start_datetime)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            end_datetime = end_datetime + timedelta(days=1)
            count_query = count_query.filter(Log.created_at < end_datetime)
        except ValueError:
            pass
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Format response
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": [
            {
                "id": log.id,
                "user": {
                    "id": log.user.id,
                    "username": log.user.username
                },
                "action": log.action,
                "endpoint": log.endpoint,
                "request_data": log.request_data,
                "response_data": log.response_data,
                "ip_address": log.ip_address,
                "status_code": log.status_code,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }