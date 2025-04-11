# # api/routes/prediction.py
# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
# from sqlalchemy.orm import Session
# from typing import List
# from backend.db.models import get_db, Comment, User
# from backend.api.models.prediction import PredictionRequest, PredictionResponse, BatchPredictionRequest, BatchPredictionResponse
# from backend.services.ml_model import MLModel
# from backend.api.routes.auth import get_current_user
# from backend.utils.vector_utils import extract_features
# import numpy as np

# router = APIRouter()
# ml_model = MLModel()

# @router.post("/single", response_model=PredictionResponse)
# async def predict_single(
#     request: PredictionRequest,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     # Make prediction
#     prediction, confidence = ml_model.predict(request.text)
    
#     # Map prediction to text
#     prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
    
#     # Store prediction in background
#     background_tasks.add_task(
#         store_prediction, 
#         db=db, 
#         content=request.text, 
#         platform=request.platform, 
#         platform_id=request.platform_id, 
#         prediction=prediction, 
#         confidence=confidence, 
#         user_id=current_user.id,
#         metadata=request.metadata
#     )
    
#     return {
#         "text": request.text,
#         "prediction": prediction,
#         "confidence": confidence,
#         "prediction_text": prediction_text
#     }

# @router.post("/batch", response_model=BatchPredictionResponse)
# async def predict_batch(
#     request: BatchPredictionRequest,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     results = []
    
#     for comment in request.comments:
#         prediction, confidence = ml_model.predict(comment.text)
#         prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
        
#         # Store prediction in background
#         background_tasks.add_task(
#             store_prediction, 
#             db=db, 
#             content=comment.text, 
#             platform=comment.platform, 
#             platform_id=comment.platform_id, 
#             prediction=prediction, 
#             confidence=confidence, 
#             user_id=current_user.id,
#             metadata=comment.metadata
#         )
        
#         results.append({
#             "text": comment.text,
#             "prediction": prediction,
#             "confidence": confidence,
#             "prediction_text": prediction_text
#         })
    
#     return {"results": results}

# def store_prediction(
#     db: Session, 
#     content: str, 
#     platform: str, 
#     platform_id: str, 
#     prediction: int, 
#     confidence: float, 
#     user_id: int,
#     metadata: dict = None
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
#         user_id=user_id,
#         metadata=metadata
#     )
    
#     # Set vector
#     comment.set_vector(vector)
    
#     # Store in database
#     db.add(comment)
#     db.commit()
# api/routes/prediction.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from io import StringIO
import csv
import pandas as pd
import json
from backend.db.models import get_db, Comment, User, Log
from backend.api.models.prediction import (
    PredictionRequest, 
    PredictionResponse, 
    BatchPredictionRequest, 
    BatchPredictionResponse,
    SimilarCommentsResponse,
    TextAnalysisResponse
)
from backend.services.ml_model import MLModel
from backend.api.routes.auth import get_current_user
from backend.utils.vector_utils import extract_features
from backend.utils.text_processing import preprocess_text, extract_keywords

router = APIRouter()
ml_model = MLModel()

@router.post("/single", response_model=PredictionResponse)
async def predict_single(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    API endpoint để phân tích một comment đơn lẻ
    """
    # Tiền xử lý văn bản (optional)
    processed_text = preprocess_text(request.text)
    
    # Thực hiện dự đoán
    prediction, confidence, probabilities = ml_model.predict(processed_text)
    
    # Ánh xạ dự đoán sang text
    prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
    
    # Lưu dự đoán trong background
    comment_id = None
    if request.save_result:
        background_tasks.add_task(
            store_prediction, 
            db=db, 
            content=request.text, 
            processed_content=processed_text,
            platform=request.platform, 
            source_user_name=request.source_user_name,
            source_url=request.source_url,
            prediction=prediction, 
            confidence=confidence, 
            probabilities=probabilities,
            user_id=current_user.id,
            metadata=request.metadata
        )
    
    # Trích xuất các từ khóa
    keywords = extract_keywords(processed_text)
    
    return {
        "text": request.text,
        "processed_text": processed_text,
        "prediction": prediction,
        "confidence": confidence,
        "probabilities": probabilities,
        "prediction_text": prediction_text,
        "keywords": keywords,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    API endpoint để phân tích nhiều comments cùng lúc
    """
    results = []
    
    for comment in request.comments:
        # Tiền xử lý văn bản
        processed_text = preprocess_text(comment.text)
        
        # Thực hiện dự đoán
        prediction, confidence, probabilities = ml_model.predict(processed_text)
        prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
        
        # Lưu dự đoán nếu cần
        if request.save_results:
            background_tasks.add_task(
                store_prediction, 
                db=db, 
                content=comment.text, 
                processed_content=processed_text,
                platform=comment.platform, 
                source_user_name=comment.source_user_name,
                source_url=comment.source_url,
                prediction=prediction, 
                confidence=confidence,
                probabilities=probabilities,
                user_id=current_user.id,
                metadata=comment.metadata
            )
        
        results.append({
            "text": comment.text,
            "processed_text": processed_text,
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": probabilities,
            "prediction_text": prediction_text
        })
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action=f"Batch prediction: {len(request.comments)} items",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {
        "results": results,
        "count": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/upload-csv", response_model=BatchPredictionResponse)
async def upload_csv_file(
    file: UploadFile = File(...),
    text_column: str = Query(..., description="Tên cột chứa nội dung text"),
    platform: Optional[str] = Query("unknown", description="Platform nguồn"),
    save_results: bool = Query(True, description="Lưu kết quả vào database"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    API endpoint để tải lên và phân tích file CSV
    """
    # Kiểm tra file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file CSV")
    
    # Đọc file CSV
    content = await file.read()
    text_content = content.decode('utf-8')
    
    # Parse CSV
    try:
        df = pd.read_csv(StringIO(text_content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi khi đọc file CSV: {str(e)}")
    
    # Kiểm tra column
    if text_column not in df.columns:
        raise HTTPException(
            status_code=400, 
            detail=f"Không tìm thấy cột '{text_column}'. Các cột có sẵn: {', '.join(df.columns)}"
        )
    
    # Lấy source_user_name và source_url từ các cột trong CSV nếu có
    has_user_column = 'user' in df.columns or 'username' in df.columns or 'source_user' in df.columns
    has_url_column = 'url' in df.columns or 'link' in df.columns or 'source_url' in df.columns
    
    results = []
    
    # Xử lý từng hàng trong CSV
    for index, row in df.iterrows():
        # Lấy nội dung text
        text = str(row[text_column])
        if not text or text.lower() == 'nan':
            continue
            
        # Tiền xử lý text
        processed_text = preprocess_text(text)
        
        # Lấy source_user_name nếu có
        source_user_name = None
        if has_user_column:
            for col in ['user', 'username', 'source_user']:
                if col in df.columns and row[col] and str(row[col]).lower() != 'nan':
                    source_user_name = str(row[col])
                    break
        
        # Lấy source_url nếu có  
        source_url = None
        if has_url_column:
            for col in ['url', 'link', 'source_url']:
                if col in df.columns and row[col] and str(row[col]).lower() != 'nan':
                    source_url = str(row[col])
                    break
        
        # Thực hiện dự đoán
        prediction, confidence, probabilities = ml_model.predict(processed_text)
        prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
        
        # Lưu vào database nếu cần
        if save_results:
            # Tạo metadata từ các cột khác
            metadata = {}
            for col in df.columns:
                if col != text_column and col not in ['user', 'username', 'source_user', 'url', 'link', 'source_url']:
                    value = row[col]
                    # Chuyển đổi numpy types sang Python types
                    if hasattr(value, 'item'):
                        value = value.item()
                    # Bỏ qua nếu là NaN
                    if pd.isna(value):
                        continue
                    metadata[col] = value
            
            background_tasks.add_task(
                store_prediction, 
                db=db, 
                content=text, 
                processed_content=processed_text,
                platform=platform, 
                source_user_name=source_user_name,
                source_url=source_url,
                prediction=prediction, 
                confidence=confidence,
                probabilities=probabilities,
                user_id=current_user.id,
                metadata=metadata
            )
        
        # Thêm vào kết quả
        results.append({
            "text": text,
            "processed_text": processed_text,
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": probabilities,
            "prediction_text": prediction_text
        })
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action=f"CSV upload prediction: {len(results)} items",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {
        "results": results,
        "count": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/similar/{comment_id}", response_model=SimilarCommentsResponse)
async def get_similar_comments(
    comment_id: int,
    limit: int = Query(10, ge=1, le=100),
    threshold: float = Query(0.7, ge=0, le=1.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    API endpoint để tìm các comments tương tự với một comment cụ thể
    """
    # Lấy comment gốc
    source_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not source_comment:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy comment với ID {comment_id}")
    
    # Kiểm tra quyền truy cập
    if not current_user.role.name == "admin" and source_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập comment này")
    
    # Lấy vector đặc trưng của comment gốc
    source_vector = source_comment.get_vector()
    if not source_vector:
        raise HTTPException(status_code=400, detail="Comment không có vector đặc trưng")
    
    # Tìm các comment tương tự
    similar_comments = []
    
    # Lưu ý: Triển khai cụ thể phụ thuộc vào cách bạn lưu vector trong database
    # Ví dụ sử dụng cosine similarity
    
    # Giả sử bạn có hàm tính toán similarity trong database hoặc trong code
    # Đây là ví dụ giả định, cần thay thế bằng triển khai thực tế
    for comment in db.query(Comment).filter(Comment.id != comment_id).all():
        comment_vector = comment.get_vector()
        if comment_vector:
            # Tính cosine similarity
            similarity = cosine_similarity(source_vector, comment_vector)
            if similarity >= threshold:
                prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[comment.prediction]
                similar_comments.append({
                    "id": comment.id,
                    "content": comment.content,
                    "prediction": comment.prediction,
                    "prediction_text": prediction_text,
                    "confidence": comment.confidence,
                    "similarity": similarity,
                    "platform": comment.platform,
                    "created_at": comment.created_at.isoformat()
                })
    
    # Sắp xếp theo độ tương tự giảm dần và lấy theo limit
    similar_comments.sort(key=lambda x: x["similarity"], reverse=True)
    similar_comments = similar_comments[:limit]
    
    return {
        "source_comment": {
            "id": source_comment.id,
            "content": source_comment.content,
            "prediction": source_comment.prediction,
            "prediction_text": {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[source_comment.prediction],
            "confidence": source_comment.confidence
        },
        "similar_comments": similar_comments,
        "count": len(similar_comments)
    }

@router.post("/analyze-text", response_model=TextAnalysisResponse)
async def analyze_text(
    text: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    API endpoint để phân tích chi tiết một đoạn text không lưu vào database
    """
    # Tiền xử lý văn bản
    processed_text = preprocess_text(text)
    
    # Thực hiện dự đoán
    prediction, confidence, probabilities = ml_model.predict(processed_text)
    prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
    
    # Trích xuất keywords
    keywords = extract_keywords(processed_text)
    
    # Phân tích cảm xúc (nếu có module phù hợp)
    sentiment = None
    try:
        from backend.services.sentiment_analysis import analyze_sentiment
        sentiment = analyze_sentiment(processed_text)
    except ImportError:
        # Không có module phân tích cảm xúc
        pass
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action="Text analysis",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {
        "text": text,
        "processed_text": processed_text,
        "prediction": prediction,
        "prediction_text": prediction_text,
        "confidence": confidence,
        "probabilities": probabilities,
        "keywords": keywords,
        "sentiment": sentiment,
        "word_count": len(processed_text.split()),
        "char_count": len(processed_text)
    }

def store_prediction(
    db: Session, 
    content: str, 
    processed_content: str,
    platform: str, 
    source_user_name: Optional[str] = None,
    source_url: Optional[str] = None,
    prediction: int = 0, 
    confidence: float = 0.0,
    probabilities: Optional[Dict[str, float]] = None,
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Hàm lưu kết quả dự đoán vào database
    """
    # Trích xuất vector đặc trưng
    vector = extract_features(processed_content)
    
    # Tạo comment
    comment = Comment(
        content=content,
        processed_content=processed_content,
        platform=platform,
        source_user_name=source_user_name,
        source_url=source_url,
        prediction=prediction,
        confidence=confidence,
        probabilities=json.dumps(probabilities) if probabilities else None,
        user_id=user_id,
        created_at=datetime.utcnow(),
        metadata=json.dumps(metadata) if metadata else None
    )
    
    # Lưu vector
    if hasattr(comment, 'set_vector') and callable(getattr(comment, 'set_vector')):
        comment.set_vector(vector)
    
    # Lưu vào database
    db.add(comment)
    db.commit()
    
    return comment.id

def cosine_similarity(vec1, vec2):
    """
    Tính cosine similarity giữa hai vectors
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = sum(a * a for a in vec1) ** 0.5
    norm_b = sum(b * b for b in vec2) ** 0.5
    
    if norm_a == 0 or norm_b == 0:
        return 0
        
    return dot_product / (norm_a * norm_b)