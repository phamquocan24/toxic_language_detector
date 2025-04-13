# # api/routes/admin.py
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from backend.db.models import get_db, User, Role, Log, Comment
# from backend.api.models.prediction import UserResponse, LogResponse, CommentResponse
# from backend.api.routes.auth import get_admin_user

# router = APIRouter()

# @router.get("/users", response_model=List[UserResponse])
# def get_users(
#     skip: int = 0, 
#     limit: int = 100, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_admin_user)
# ):
#     users = db.query(User).offset(skip).limit(limit).all()
#     return users

# @router.get("/users/{user_id}", response_model=UserResponse)
# def get_user(
#     user_id: int, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_admin_user)
# ):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# @router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_user(
#     user_id: int, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_admin_user)
# ):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return {"detail": "User deleted successfully"}

# @router.get("/logs", response_model=List[LogResponse])
# def get_logs(
#     skip: int = 0, 
#     limit: int = 100, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_admin_user)
# ):
#     logs = db.query(Log).order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()
#     return logs

# @router.get("/comments", response_model=List[CommentResponse])
# def get_comments(
#     skip: int = 0, 
#     limit: int = 100, 
#     platform: str = None,
#     prediction: int = None,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_admin_user)
# ):
#     query = db.query(Comment)
    
#     if platform:
#         query = query.filter(Comment.platform == platform)
    
#     if prediction is not None:
#         query = query.filter(Comment.prediction == prediction)
    
#     comments = query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
#     return comments
# api/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from backend.db.models import get_db, User, Role, Log, Comment
from backend.api.models.prediction import UserResponse, LogResponse, CommentResponse, UserCreate, UserUpdate, DashboardData
from backend.api.routes.auth import get_admin_user
from backend.services.ml_model import get_model_stats

router = APIRouter()

@router.get("/dashboard", response_model=DashboardData)
def get_dashboard_data(
    period: str = "month",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Lấy dữ liệu cho dashboard admin
    """
    # Xác định khoảng thời gian
    now = datetime.now()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # month (default)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Thống kê comments
    total_comments = db.query(Comment).filter(Comment.created_at >= start_date).count()
    
    clean_comments = db.query(Comment).filter(
        Comment.created_at >= start_date,
        Comment.prediction == 0  # 'clean'
    ).count()
    
    offensive_comments = db.query(Comment).filter(
        Comment.created_at >= start_date,
        Comment.prediction == 1  # 'offensive'
    ).count()
    
    hate_comments = db.query(Comment).filter(
        Comment.created_at >= start_date,
        Comment.prediction == 2  # 'hate'
    ).count()
    
    spam_comments = db.query(Comment).filter(
        Comment.created_at >= start_date,
        Comment.prediction == 3  # 'spam'
    ).count()
    
    # Thống kê users
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.last_login >= start_date).count()
    
    # Thống kê platforms
    platforms = db.query(
        Comment.platform, 
        db.func.count(Comment.id).label('count')
    ).filter(
        Comment.created_at >= start_date
    ).group_by(Comment.platform).all()
    
    platform_stats = {platform: count for platform, count in platforms}
    
    # Thống kê trend (theo ngày, tuần, tháng tùy vào period)
    if period == "day":
        trend_format = "%H"  # Theo giờ
        trend_interval = timedelta(hours=1)
    elif period == "week" or period == "month":
        trend_format = "%d/%m"  # Theo ngày
        trend_interval = timedelta(days=1)
    else:  # year
        trend_format = "%m/%Y"  # Theo tháng
        trend_interval = timedelta(days=30)
    
    # Sử dụng model stats
    ml_stats = get_model_stats()
    
    return {
        "statistics": {
            "total_comments": total_comments,
            "clean_comments": clean_comments,
            "offensive_comments": offensive_comments,
            "hate_comments": hate_comments,
            "spam_comments": spam_comments,
            "total_users": total_users,
            "active_users": active_users
        },
        "platforms": platform_stats,
        "model_stats": ml_stats,
        "period": period
    }

# Thêm hàm helper vào file backend/api/routes/admin.py để chuyển đổi đối tượng Role thành string

def prepare_user_response(user):
    """
    Chuẩn bị đối tượng User cho response, chuyển đổi role thành string
    """
    # Đảm bảo role là string
    if user.role and hasattr(user.role, 'name'):
        user_dict = user.__dict__.copy()
        user_dict['role'] = user.role.name
        return user_dict
    return user

@router.get("/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Lấy danh sách người dùng với bộ lọc
    """
    query = db.query(User)
    
    # Áp dụng bộ lọc
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) | 
            (User.email.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.join(Role).filter(Role.name == role)
    
    if active is not None:
        if active:
            query = query.filter(User.is_active == True)
        else:
            query = query.filter(User.is_active == False)
    
    # Thực hiện query
    users = query.offset(skip).limit(limit).all()
    
    # Chuẩn bị response để đảm bảo role là string
    return [prepare_user_response(user) for user in users]

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Lấy thông tin chi tiết của một người dùng
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Chuẩn bị response để đảm bảo role là string
    return prepare_user_response(user)

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Tạo người dùng mới (chỉ admin)
    """
    # Kiểm tra email đã tồn tại chưa
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Tìm role dựa trên tên role
    role = db.query(Role).filter(Role.name == user_data.role).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{user_data.role}' not found"
        )
    
    # Tạo người dùng mới
    from backend.core.security import get_password_hash
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        username=user_data.username,  # Thêm username vào
        hashed_password=get_password_hash(user_data.password),
        role_id=role.id,
        is_active=True,  # Mặc định là active
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action=f"Created user: {new_user.email}",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    # Trả về user đã chuẩn bị
    return prepare_user_response(new_user)

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Lấy thông tin chi tiết của một người dùng
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Cập nhật thông tin người dùng
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Kiểm tra email nếu thay đổi
    if user_data.email and user_data.email != user.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Cập nhật thông tin
    if user_data.name is not None:
        user.name = user_data.name
    
    if user_data.email is not None:
        user.email = user_data.email
    
    if user_data.username is not None:
        # Kiểm tra username đã tồn tại chưa
        existing_user = db.query(User).filter(
            User.username == user_data.username, 
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = user_data.username
    
    if user_data.role is not None:
        # Tìm role dựa trên tên role
        role = db.query(Role).filter(Role.name == user_data.role).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{user_data.role}' not found"
            )
        user.role_id = role.id
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    # Cập nhật mật khẩu nếu có
    if user_data.password:
        from backend.core.security import get_password_hash
        user.hashed_password = get_password_hash(user_data.password)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action=f"Updated user: {user.email}",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    # Trả về user đã chuẩn bị
    return prepare_user_response(user)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Xóa người dùng
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Không cho phép xóa chính mình
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Lưu thông tin cho log
    user_email = user.email
    
    # Xóa user
    db.delete(user)
    db.commit()
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action=f"Deleted user: {user_email}",
        timestamp=datetime.now()
    )
    db.add(log)
    db.commit()
    
    return {"detail": "User deleted successfully"}

@router.get("/logs", response_model=List[LogResponse])
def get_logs(
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Lấy logs hệ thống với bộ lọc
    """
    query = db.query(Log)
    
    # Áp dụng bộ lọc
    if user_id:
        query = query.filter(Log.user_id == user_id)
    
    if action:
        query = query.filter(Log.action.ilike(f"%{action}%"))
    
    if start_date:
        query = query.filter(Log.timestamp >= start_date)
    
    if end_date:
        query = query.filter(Log.timestamp <= end_date)
    
    # Thực hiện query
    logs = query.order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/comments", response_model=List[CommentResponse])
def get_comments(
    skip: int = 0, 
    limit: int = 100,
    platform: Optional[str] = None,
    prediction: Optional[int] = None,
    confidence_min: Optional[float] = None,
    confidence_max: Optional[float] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Lấy danh sách comments với bộ lọc nâng cao
    """
    query = db.query(Comment)
    
    # Áp dụng bộ lọc
    if platform:
        query = query.filter(Comment.platform == platform)
    
    if prediction is not None:
        query = query.filter(Comment.prediction == prediction)
    
    if confidence_min is not None:
        query = query.filter(Comment.confidence >= confidence_min)
    
    if confidence_max is not None:
        query = query.filter(Comment.confidence <= confidence_max)
    
    if user_id:
        query = query.filter(Comment.user_id == user_id)
    
    if start_date:
        query = query.filter(Comment.created_at >= start_date)
    
    if end_date:
        query = query.filter(Comment.created_at <= end_date)
    
    if search:
        query = query.filter(Comment.content.ilike(f"%{search}%"))
    
    # Thực hiện query
    comments = query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
    return comments

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Xóa một comment
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(comment)
    db.commit()
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action=f"Deleted comment: ID {comment_id}",
        timestamp=datetime.now()
    )
    db.add(log)
    db.commit()
    
    return {"detail": "Comment deleted successfully"}

@router.get("/export/comments")
def export_comments(
    format: str = Query(..., regex="^(csv|excel|pdf)$"),
    platform: Optional[str] = None,
    prediction: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Xuất report dạng CSV, Excel hoặc PDF
    """
    from fastapi.responses import StreamingResponse
    import io
    import pandas as pd
    
    # Xây dựng query tương tự get_comments
    query = db.query(Comment)
    
    if platform:
        query = query.filter(Comment.platform == platform)
    
    if prediction is not None:
        query = query.filter(Comment.prediction == prediction)
    
    if start_date:
        query = query.filter(Comment.created_at >= start_date)
    
    if end_date:
        query = query.filter(Comment.created_at <= end_date)
    
    comments = query.order_by(Comment.created_at.desc()).all()
    
    # Chuyển đổi thành DataFrame
    data = []
    for comment in comments:
        prediction_label = ["clean", "offensive", "hate", "spam"][comment.prediction]
        
        data.append({
            "ID": comment.id,
            "Content": comment.content,
            "Prediction": prediction_label,
            "Confidence": f"{comment.confidence:.2f}",
            "Platform": comment.platform,
            "User": comment.source_user_name,
            "Detected By": db.query(User).filter(User.id == comment.user_id).first().name,
            "Created At": comment.created_at
        })
    
    df = pd.DataFrame(data)
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action=f"Exported comments in {format} format",
        timestamp=datetime.now()
    )
    db.add(log)
    db.commit()
    
    # Trả về file theo định dạng yêu cầu
    if format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=comments_export.csv"}
        )
    
    elif format == "excel":
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=comments_export.xlsx"}
        )
    
    elif format == "pdf":
        # Sử dụng thư viện để tạo PDF
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        
        # Build PDF content
        styles = getSampleStyleSheet()
        elements = []
        
        # Thêm tiêu đề
        elements.append(Paragraph("Comments Export", styles['Title']))
        
        # Convert DataFrame to table data
        table_data = [df.columns.tolist()] + df.values.tolist()
        
        # Create the table with the data
        table = Table(table_data)
        
        # Add style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=comments_export.pdf"}
        )