# # api/routes/extension.py
# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
# from sqlalchemy.orm import Session
# from typing import List, Dict, Any
# from backend.db.models import get_db, Comment
# from backend.api.models.prediction import PredictionRequest, PredictionResponse
# from backend.services.ml_model import MLModel
# from backend.config.security import verify_api_key
# from backend.utils.vector_utils import extract_features

# router = APIRouter()
# ml_model = MLModel()

# @router.post("/detect", response_model=PredictionResponse)
# async def extension_detect(
#     request: PredictionRequest,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
#     api_key: str = Depends(verify_api_key)
# ):
#     # Make prediction
#     prediction, confidence = ml_model.predict(request.text)
    
#     # Map prediction to text
#     prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
    
#     # Store prediction in background, but without user_id since this is from extension
#     background_tasks.add_task(
#         store_extension_prediction, 
#         db=db, 
#         content=request.text, 
#         platform=request.platform, 
#         platform_id=request.platform_id, 
#         prediction=prediction, 
#         confidence=confidence,
#         metadata=request.metadata
#     )
    
#     return {
#         "text": request.text,
#         "prediction": prediction,
#         "confidence": confidence,
#         "prediction_text": prediction_text
#     }

# def store_extension_prediction(
#     db: Session, 
#     content: str, 
#     platform: str, 
#     platform_id: str, 
#     prediction: int, 
#     confidence: float,
#     metadata: Dict[str, Any] = None
# ):
#     # Extract vector features
#     vector = extract_features(content)
    
#     # Create comment
#     comment = Comment(
#         content=content,
#         platform=platform,
#         platform_id=platform_id,
#         prediction=prediction,
#         confidence=confidence,
#         user_id=None,  # No user associated with extension predictions
#         metadata=metadata
#     )
    
#     # Set vector
#     comment.set_vector(vector)
    
#     # Store in database
#     db.add(comment)
#     db.commit()
# api/routes/extension.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from backend.db.models import get_db, Comment, User, Log
from backend.api.models.prediction import (
    PredictionRequest, 
    PredictionResponse, 
    BatchPredictionRequest, 
    BatchPredictionResponse,
    ExtensionStatsResponse
)
from backend.services.ml_model import MLModel
from backend.utils.vector_utils import extract_features
from backend.api.routes.auth import get_current_user

router = APIRouter()
ml_model = MLModel()

# Hàm xác thực tùy chọn
def get_optional_current_user(db: Session = Depends(get_db)):
    """Hàm xác thực không bắt buộc, luôn trả về None"""
    return None

@router.post("/detect", response_model=PredictionResponse)
async def extension_detect(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    API endpoint để extension gửi và phân tích một comment
    """
    # Thực hiện dự đoán
    prediction, confidence, probabilities = ml_model.predict(request.text)
    
    # Ánh xạ dự đoán sang text
    prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
    
    # Lưu dự đoán trong background nếu người dùng đã xác thực
    if current_user:
        background_tasks.add_task(
            store_extension_prediction, 
            db=db, 
            content=request.text, 
            platform=request.platform, 
            source_user_name=request.source_user_name,
            source_url=request.source_url,
            prediction=prediction, 
            confidence=confidence,
            user_id=current_user.id,
            metadata=request.metadata
        )
    
    return {
        "text": request.text,
        "prediction": prediction,
        "confidence": confidence,
        "probabilities": probabilities,
        "prediction_text": prediction_text,
        "user_id": current_user.id if current_user else None,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/batch-detect", response_model=BatchPredictionResponse)
async def extension_batch_detect(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    API endpoint để extension gửi và phân tích nhiều comments cùng lúc
    """
    results = []
    
    for item in request.dict().get('items', []):
        # Thực hiện dự đoán
        prediction, confidence, probabilities = ml_model.predict(item.text)
        
        # Ánh xạ dự đoán sang text
        prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
        
        # Chỉ lưu kết quả nếu không phải là "clean" hoặc nếu yêu cầu lưu tất cả
        if prediction != 0 or request.store_clean:
            # Lưu dự đoán trong background
            background_tasks.add_task(
                store_extension_prediction, 
                db=db, 
                content=item.text, 
                platform=item.platform, 
                source_user_name=item.source_user_name,
                source_url=item.source_url,
                prediction=prediction, 
                confidence=confidence,
                user_id=current_user.id if current_user else None,
                metadata=item.metadata
            )
        
        # Thêm kết quả vào danh sách
        results.append({
            "text": item.text,
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": probabilities,
            "prediction_text": prediction_text
        })
    
    # Ghi log
    log = Log(
        user_id=current_user.id if current_user else None,
        action=f"Batch prediction: {len(request.dict().get('items', []))} items",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {
        "count": len(results),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/stats", response_model=ExtensionStatsResponse)
async def extension_stats(
    period: Optional[str] = Query("all", regex="^(day|week|month|all)$"),
    admin_token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    API endpoint để lấy thống kê cho extension
    """
    # If there is no authenticated user, check for a valid admin_token
    if current_user is None and admin_token:
         from backend.config.settings import settings
         if admin_token == settings.ADMIN_TOKEN:
              from backend.db.models import User, Role
              # Create a dummy admin user with ID -1
              current_user = User(id=-1, role=Role(name="admin"))
    if current_user is None:
         raise HTTPException(status_code=401, detail="Authentication required for stats endpoint")

    # Xác định khoảng thời gian
    filter_date = None
    if period == "day":
        filter_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        today = datetime.utcnow()
        filter_date = today - timedelta(days=today.weekday())
        filter_date = filter_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        filter_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Query cơ bản chỉ lấy comment của user hiện tại
    query = db.query(Comment).filter(Comment.user_id == current_user.id)
    
    # Áp dụng lọc theo thời gian nếu có
    if filter_date:
        query = query.filter(Comment.created_at >= filter_date)
    
    # Tổng số comment
    total_count = query.count()
    
    # Số lượng theo phân loại
    offensive_count = query.filter(Comment.prediction == 1).count()
    hate_count = query.filter(Comment.prediction == 2).count()
    spam_count = query.filter(Comment.prediction == 3).count()
    clean_count = query.filter(Comment.prediction == 0).count()
    
    # Số lượng theo platform
    platforms = db.query(
        Comment.platform, 
        db.func.count(Comment.id).label('count')
    ).filter(
        Comment.user_id == current_user.id
    )
    
    if filter_date:
        platforms = platforms.filter(Comment.created_at >= filter_date)
    
    platforms = platforms.group_by(Comment.platform).all()
    platform_stats = {platform: count for platform, count in platforms}
    
    # Recent comments (từ tất cả labels)
    recent_comments = query.order_by(Comment.created_at.desc()).limit(5).all()
    
    recent_items = []
    for comment in recent_comments:
        prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[comment.prediction]
        recent_items.append({
            "id": comment.id,
            "content": comment.content,
            "prediction": comment.prediction,
            "prediction_text": prediction_text,
            "confidence": comment.confidence,
            "platform": comment.platform,
            "source_user_name": comment.source_user_name,
            "source_url": comment.source_url,
            "created_at": comment.created_at.isoformat()
        })
    
    return {
        "total_count": total_count,
        "clean_count": clean_count,
        "offensive_count": offensive_count,
        "hate_count": hate_count,
        "spam_count": spam_count,
        "platforms": platform_stats,
        "recent": recent_items,
        "period": period
    }

@router.delete("/comments/{comment_id}")
async def delete_extension_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    API endpoint để extension xóa một comment đã phát hiện
    """
    # Tìm comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment không tồn tại")
    
    # Kiểm tra quyền - chỉ cho phép xóa comment của chính user hoặc admin
    if comment.user_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền xóa comment này")
    
    # Xóa comment
    db.delete(comment)
    db.commit()
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action=f"Deleted comment ID {comment_id}",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {"detail": "Comment đã được xóa thành công"}

@router.get("/settings")
async def get_extension_settings(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    API endpoint để lấy cài đặt của extension cho user hiện tại
    """
    # If no user is authenticated, return default settings
    if current_user is None:
        default_settings = {
            "enabled_platforms": ["facebook", "youtube", "twitter", "tiktok"],
            "auto_analyze": True,
            "highlight_comments": True,
            "notification": True,
            "store_clean": False,
            "threshold": 0.7
        }
        return {
            "settings": default_settings,
            "user_id": None,
            "role": "anonymous"
        }

    # Lấy settings từ database nếu có, hoặc sử dụng mặc định
    if hasattr(current_user, 'extension_settings') and current_user.extension_settings:
        settings = current_user.extension_settings
    else:
        settings = {
            "enabled_platforms": ["facebook", "youtube", "twitter", "tiktok"],
            "auto_analyze": True,
            "highlight_comments": True,
            "notification": True,
            "store_clean": False,
            "threshold": 0.7
        }

    return {
        "settings": settings,
        "user_id": current_user.id,
        "role": current_user.role.name
    }

@router.post("/settings")
async def update_extension_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    API endpoint để cập nhật cài đặt của extension cho user hiện tại
    """
    # Cập nhật settings
    current_user.extension_settings = settings
    db.commit()
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action="Updated extension settings",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {"detail": "Cài đặt đã được cập nhật thành công"}

def store_extension_prediction(
    db: Session, 
    content: str, 
    platform: str, 
    source_user_name: Optional[str] = None,
    source_url: Optional[str] = None,
    prediction: int = 0, 
    confidence: float = 0.0,
    user_id: Optional[int] = None,
    metadata: Dict[str, Any] = None
):
    """
    Hàm lưu kết quả dự đoán vào database
    """
    # Trích xuất vector features
    vector = extract_features(content)
    
    # Tạo comment
    comment = Comment(
        content=content,
        platform=platform,
        source_user_name=source_user_name,
        source_url=source_url,
        prediction=prediction,
        confidence=confidence,
        user_id=user_id,
        created_at=datetime.utcnow(),
        metadata=metadata
    )
    
    # Lưu vector
    if hasattr(comment, 'set_vector') and callable(getattr(comment, 'set_vector')):
        comment.set_vector(vector)
    
    # Lưu vào database
    db.add(comment)
    db.commit()
    
    return comment.id