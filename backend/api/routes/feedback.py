"""
API routes for feedback system
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Dict, Any, Optional, List
from datetime import datetime
from backend.db.models import get_db, Log, User
from backend.api.routes.auth import get_current_user, get_optional_current_user, get_admin_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/list")
async def get_feedbacks(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    feedback_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    API endpoint để lấy danh sách feedback từ hệ thống
    Chỉ admin mới có quyền truy cập
    """
    try:
        # Query logs với action chứa "Feedback" hoặc "Report incorrect analysis"
        query = db.query(Log).filter(
            or_(
                Log.action.like("Feedback:%"),
                Log.action.like("Report incorrect analysis%")
            )
        )
        
        # Lọc theo loại feedback nếu có
        if feedback_type:
            if feedback_type == "analysis_error":
                query = query.filter(Log.action.like("Report incorrect analysis%"))
            else:
                query = query.filter(Log.action.like(f"Feedback: {feedback_type}%"))
        
        # Đếm tổng số
        total = query.count()
        
        # Lấy dữ liệu với pagination
        feedbacks = query.order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()
        
        # Chuyển đổi sang dict
        result = []
        for feedback in feedbacks:
            # Parse action để lấy type và source
            if feedback.action.startswith("Report incorrect analysis"):
                # Format: "Report incorrect analysis: original=X, suggested=Y"
                feedback_type_part = "analysis_error"
                source = "extension-content"
            elif feedback.action.startswith("Feedback:"):
                # Format: "Feedback: {type} from {source}"
                action_parts = feedback.action.split(" from ")
                feedback_type_part = action_parts[0].replace("Feedback: ", "") if len(action_parts) > 0 else "general"
                source = action_parts[1] if len(action_parts) > 1 else "unknown"
            else:
                feedback_type_part = "general"
                source = "unknown"
            
            result.append({
                "id": feedback.id,
                "user_id": feedback.user_id,
                "feedback_type": feedback_type_part,
                "source": source,
                "action": feedback.action,
                "timestamp": feedback.timestamp.isoformat() if feedback.timestamp else None,
                "created_at": feedback.timestamp.isoformat() if feedback.timestamp else None,
            })
        
        return {
            "total": total,
            "data": result,
            "limit": limit,
            "skip": skip
        }
    
    except Exception as e:
        logger.error(f"Error fetching feedbacks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách feedback: {str(e)}")

@router.post("/report")
async def report_feedback(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    API endpoint để gửi phản hồi về phân tích hoặc cải thiện hệ thống
    """
    # Kiểm tra dữ liệu
    if not request.get("text"):
        raise HTTPException(status_code=400, detail="Dữ liệu không hợp lệ, cần có text")
    
    # Trích xuất thông tin từ request
    text = request.get("text")
    source = request.get("source", "unknown")
    feedback_type = request.get("type", "general")
    details = request.get("details", "")
    reported_by = request.get("reported_by") or (current_user.id if current_user else None)
    
    # Ghi log phản hồi
    try:
        log = Log(
            user_id=current_user.id if current_user else None,
            action=f"Feedback: {feedback_type} from {source}",
            timestamp=datetime.utcnow()
        )
        db.add(log)
        
        # TODO: Lưu chi tiết phản hồi vào bảng feedback nếu có
        # Có thể thêm code để lưu feedback vào database hoặc gửi email thông báo
        
        db.commit()
        return {"detail": "Phản hồi đã được ghi nhận, cảm ơn đóng góp của bạn"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error reporting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi gửi phản hồi: {str(e)}") 