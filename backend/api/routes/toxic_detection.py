# # api/routes/toxic_detection.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from backend.db.models import get_db, Comment
# from backend.api.models.prediction import CommentResponse
# from backend.api.routes.auth import get_current_user
# from backend.db.models import User
# from backend.utils.vector_utils import compute_similarity, extract_features
# import numpy as np

# router = APIRouter()

# @router.get("/similar", response_model=List[CommentResponse])
# def find_similar_comments(
#     text: str,
#     limit: int = 10,
#     threshold: float = 0.7,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     # Extract features for the query text
#     query_vector = extract_features(text)
    
#     # Get all comments from the database
#     comments = db.query(Comment).all()
    
#     # Compute similarity
#     similar_comments = []
#     for comment in comments:
#         comment_vector = comment.get_vector()
#         if comment_vector is not None:
#             similarity = compute_similarity(query_vector, comment_vector)
#             if similarity >= threshold:
#                 similar_comments.append((comment, similarity))
    
#     # Sort by similarity (descending)
#     similar_comments.sort(key=lambda x: x[1], reverse=True)
    
#     # Return top N comments
#     return [comment for comment, _ in similar_comments[:limit]]

# @router.get("/statistics")
# def get_statistics(
#     platform: Optional[str] = None,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     query = db.query(Comment)
    
#     if platform:
#         query = query.filter(Comment.platform == platform)
    
#     total = query.count()
#     clean = query.filter(Comment.prediction == 0).count()
#     offensive = query.filter(Comment.prediction == 1).count()
#     hate = query.filter(Comment.prediction == 2).count()
#     spam = query.filter(Comment.prediction == 3).count()
    
#     return {
#         "total": total,
#         "clean": clean,
#         "offensive": offensive,
#         "hate": hate,
#         "spam": spam,
#         "clean_percentage": (clean / total * 100) if total > 0 else 0,
#         "offensive_percentage": (offensive / total * 100) if total > 0 else 0,
#         "hate_percentage": (hate / total * 100) if total > 0 else 0,
#         "spam_percentage": (spam / total * 100) if total > 0 else 0,
#     }
# api/routes/toxic_detection.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from backend.db.models import get_db, Comment, User, Log
from backend.api.models.prediction import CommentResponse, StatisticsResponse, TrendResponse
from backend.api.routes.auth import get_current_user
from backend.utils.vector_utils import compute_similarity, extract_features
from backend.utils.text_processing import preprocess_text
import numpy as np
import sqlalchemy as sa

router = APIRouter()

@router.get("/similar", response_model=List[CommentResponse])
def find_similar_comments(
    text: str,
    limit: int = Query(10, ge=1, le=100),
    threshold: float = Query(0.7, ge=0, le=1.0),
    platform: Optional[str] = None,
    prediction: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tìm các comments tương tự với một đoạn text
    """
    # Tiền xử lý và trích xuất đặc trưng cho văn bản truy vấn
    processed_text = preprocess_text(text)
    query_vector = extract_features(processed_text)
    
    # Xây dựng query cơ sở
    query = db.query(Comment)
    
    # Áp dụng bộ lọc nếu có
    if platform:
        query = query.filter(Comment.platform == platform)
    
    if prediction is not None:
        query = query.filter(Comment.prediction == prediction)
    
    # Lấy tất cả comments từ database phù hợp với bộ lọc
    comments = query.all()
    
    # Tính toán độ tương tự
    similar_comments = []
    for comment in comments:
        comment_vector = comment.get_vector()
        if comment_vector is not None:
            similarity = compute_similarity(query_vector, comment_vector)
            if similarity >= threshold:
                similar_comments.append((comment, similarity))
    
    # Sắp xếp theo độ tương tự (giảm dần)
    similar_comments.sort(key=lambda x: x[1], reverse=True)
    
    # Chuyển đổi thành CommentResponse
    result = []
    for comment, similarity in similar_comments[:limit]:
        prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[comment.prediction]
        result.append({
            "id": comment.id,
            "content": comment.content,
            "processed_content": comment.processed_content,
            "prediction": comment.prediction,
            "prediction_text": prediction_text,
            "confidence": comment.confidence,
            "platform": comment.platform,
            "source_user_name": comment.source_user_name,
            "source_url": comment.source_url,
            "similarity": similarity,
            "created_at": comment.created_at,
            "user_id": comment.user_id
        })
    
    # Ghi log
    log = Log(
        user_id=current_user.id,
        action="Searched for similar comments",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return result

@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(
    platform: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thống kê về các comments đã phát hiện
    """
    # Xây dựng query cơ sở
    query = db.query(Comment)
    
    # Áp dụng các bộ lọc
    if platform:
        query = query.filter(Comment.platform == platform)
    
    if start_date:
        query = query.filter(Comment.created_at >= start_date)
    
    if end_date:
        query = query.filter(Comment.created_at <= end_date)
    
    if user_id and (current_user.role.name == "admin" or current_user.id == user_id):
        query = query.filter(Comment.user_id == user_id)
    elif not current_user.role.name == "admin":
        # Nếu không phải admin, chỉ xem được comments của mình
        query = query.filter(Comment.user_id == current_user.id)
    
    # Thống kê tổng quan
    total = query.count()
    clean = query.filter(Comment.prediction == 0).count()
    offensive = query.filter(Comment.prediction == 1).count()
    hate = query.filter(Comment.prediction == 2).count()
    spam = query.filter(Comment.prediction == 3).count()
    
    # Thống kê theo platform
    platforms = db.query(
        Comment.platform, 
        sa.func.count(Comment.id).label('count')
    ).filter(
        Comment.id.in_([c.id for c in query])
    ).group_by(Comment.platform).all()
    
    platform_stats = {platform: count for platform, count in platforms}
    
    # Thống kê về tin cậy
    confidence_query = db.query(
        sa.func.avg(Comment.confidence).label('avg'),
        sa.func.min(Comment.confidence).label('min'),
        sa.func.max(Comment.confidence).label('max')
    ).filter(
        Comment.id.in_([c.id for c in query])
    ).first()
    
    confidence_stats = {
        "average": confidence_query.avg if confidence_query.avg else 0,
        "min": confidence_query.min if confidence_query.min else 0,
        "max": confidence_query.max if confidence_query.max else 0
    }
    
    # Thống kê người dùng tiêu cực nhất (chỉ admin mới thấy)
    toxic_users = []
    if current_user.role.name == "admin":
        toxic_user_query = db.query(
            Comment.source_user_name,
            sa.func.count(Comment.id).label('count')
        ).filter(
            Comment.id.in_([c.id for c in query]),
            Comment.prediction.in_([1, 2, 3]),  # offensive, hate, spam
            Comment.source_user_name != None
        ).group_by(Comment.source_user_name).order_by(sa.desc('count')).limit(10).all()
        
        toxic_users = [{"username": username, "count": count} for username, count in toxic_user_query]
    
    return {
        "total": total,
        "clean": clean,
        "offensive": offensive,
        "hate": hate,
        "spam": spam,
        "percentages": {
            "clean": (clean / total * 100) if total > 0 else 0,
            "offensive": (offensive / total * 100) if total > 0 else 0,
            "hate": (hate / total * 100) if total > 0 else 0,
            "spam": (spam / total * 100) if total > 0 else 0,
        },
        "platforms": platform_stats,
        "confidence": confidence_stats,
        "toxic_users": toxic_users,
        "filters": {
            "platform": platform,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "user_id": user_id
        }
    }

@router.get("/trend", response_model=TrendResponse)
def get_trend(
    period: str = Query("week", regex="^(day|week|month|year)$"),
    platform: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy dữ liệu xu hướng theo thời gian
    """
    # Xác định khoảng thời gian
    now = datetime.utcnow()
    if period == "day":
        start_date = now - timedelta(days=1)
        date_format = "%H:00"  # Format theo giờ
        group_by = sa.func.date_trunc('hour', Comment.created_at)
    elif period == "week":
        start_date = now - timedelta(days=7)
        date_format = "%Y-%m-%d"  # Format theo ngày
        group_by = sa.func.date_trunc('day', Comment.created_at)
    elif period == "month":
        start_date = now - timedelta(days=30)
        date_format = "%Y-%m-%d"  # Format theo ngày
        group_by = sa.func.date_trunc('day', Comment.created_at)
    elif period == "year":
        start_date = now - timedelta(days=365)
        date_format = "%Y-%m"  # Format theo tháng
        group_by = sa.func.date_trunc('month', Comment.created_at)
    else:
        start_date = now - timedelta(days=7)
        date_format = "%Y-%m-%d"
        group_by = sa.func.date_trunc('day', Comment.created_at)
    
    # Xây dựng query cơ sở
    query = db.query(
        group_by.label('date'),
        Comment.prediction,
        sa.func.count(Comment.id).label('count')
    ).filter(
        Comment.created_at >= start_date
    )
    
    # Áp dụng các bộ lọc
    if platform:
        query = query.filter(Comment.platform == platform)
    
    if user_id and (current_user.role.name == "admin" or current_user.id == user_id):
        query = query.filter(Comment.user_id == user_id)
    elif not current_user.role.name == "admin":
        # Nếu không phải admin, chỉ xem được comments của mình
        query = query.filter(Comment.user_id == current_user.id)
    
    # Nhóm và sắp xếp
    query = query.group_by('date', Comment.prediction).order_by('date')
    
    # Thực hiện query
    trend_data = query.all()
    
    # Tổ chức dữ liệu
    dates = []
    clean_counts = []
    offensive_counts = []
    hate_counts = []
    spam_counts = []
    
    # Tạo từ điển để lưu trữ dữ liệu
    data_by_date = {}
    
    # Xử lý dữ liệu từ database
    for date, prediction, count in trend_data:
        # Format date string
        date_str = date.strftime(date_format)
        
        # Kiểm tra xem đã có date này chưa
        if date_str not in data_by_date:
            data_by_date[date_str] = {0: 0, 1: 0, 2: 0, 3: 0}
        
        # Cập nhật count
        data_by_date[date_str][prediction] = count
    
    # Sắp xếp các date
    sorted_dates = sorted(data_by_date.keys())
    
    # Tạo series cho từng loại
    for date in sorted_dates:
        dates.append(date)
        clean_counts.append(data_by_date[date].get(0, 0))
        offensive_counts.append(data_by_date[date].get(1, 0))
        hate_counts.append(data_by_date[date].get(2, 0))
        spam_counts.append(data_by_date[date].get(3, 0))
    
    return {
        "dates": dates,
        "series": {
            "clean": clean_counts,
            "offensive": offensive_counts,
            "hate": hate_counts,
            "spam": spam_counts
        },
        "period": period,
        "filters": {
            "platform": platform,
            "user_id": user_id
        }
    }

@router.get("/platforms")
def get_platforms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách các platforms có trong database
    """
    # Nếu là admin, lấy tất cả platforms
    if current_user.role.name == "admin":
        platforms = db.query(Comment.platform).distinct().all()
    else:
        # Nếu không phải admin, chỉ lấy platforms của comments mình phát hiện
        platforms = db.query(Comment.platform).filter(
            Comment.user_id == current_user.id
        ).distinct().all()
    
    return {"platforms": [p[0] for p in platforms if p[0] is not None]}

@router.get("/toxic-keywords")
def get_toxic_keywords(
    limit: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy các từ khóa độc hại thường xuất hiện
    """
    from collections import Counter
    import re
    
    # Xây dựng query cơ sở
    query = db.query(Comment).filter(
        Comment.prediction.in_([1, 2])  # offensive, hate
    )
    
    # Áp dụng bộ lọc
    if platform:
        query = query.filter(Comment.platform == platform)
    
    if not current_user.role.name == "admin":
        # Nếu không phải admin, chỉ xem được comments của mình
        query = query.filter(Comment.user_id == current_user.id)
    
    # Lấy tất cả comments
    toxic_comments = query.all()
    
    # Trích xuất từ khóa
    all_words = []
    for comment in toxic_comments:
        # Sử dụng processed_content nếu có, nếu không thì dùng content
        text = comment.processed_content if comment.processed_content else comment.content
        
        # Bỏ các ký tự đặc biệt và chuyển thành chữ thường
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Tách thành từng từ
        words = text.split()
        
        # Thêm vào danh sách
        all_words.extend(words)
    
    # Đếm số lần xuất hiện
    word_counts = Counter(all_words)
    
    # Lọc bỏ các từ có 1 ký tự hoặc là stopwords
    stopwords = {"và", "hoặc", "là", "của", "trong", "có", "không", "những", "các", "để", "với", "thì", "mà", "một", "này", "đó", "cho", "từ", "như", "nhưng", "còn", "đã", "cũng", "về", "người", "gì", "thế", "được", "sẽ", "vì", "khi", "tôi", "bạn", "anh", "chị", "họ", "nó", "đó"}
    filtered_words = {word: count for word, count in word_counts.items() if len(word) > 1 and word not in stopwords}
    
    # Lấy top N từ
    top_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    return {"keywords": [{"word": word, "count": count} for word, count in top_words]}

@router.get("/comment-clusters")
def get_comment_clusters(
    prediction: int = Query(..., ge=0, le=3),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Phân cụm các comments có cùng nhãn
    """
    # Xác thực quyền admin
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền truy cập chức năng này")
    
    # Lấy các comments có cùng nhãn dự đoán
    comments = db.query(Comment).filter(
        Comment.prediction == prediction
    ).order_by(Comment.created_at.desc()).limit(limit).all()
    
    if len(comments) < 5:
        return {"clusters": [], "message": "Không đủ dữ liệu để phân cụm"}
    
    # Trích xuất vectors
    comment_vectors = []
    for comment in comments:
        vector = comment.get_vector()
        if vector is not None:
            comment_vectors.append((comment, vector))
    
    # Nếu không có vectors, thử trích xuất lại
    if len(comment_vectors) < 5:
        comment_vectors = []
        for comment in comments:
            # Sử dụng processed_content nếu có, nếu không thì dùng content
            text = comment.processed_content if comment.processed_content else comment.content
            vector = extract_features(text)
            comment_vectors.append((comment, vector))
    
    # Sử dụng KMeans để phân cụm
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import normalize
        
        # Xác định số cụm dựa trên số lượng dữ liệu
        n_clusters = min(5, len(comment_vectors) // 2)
        
        # Chuẩn hóa vectors
        vectors = np.array([vec for _, vec in comment_vectors])
        vectors = normalize(vectors)
        
        # Phân cụm
        kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(vectors)
        labels = kmeans.labels_
        
        # Tổ chức dữ liệu theo cụm
        clusters = [[] for _ in range(n_clusters)]
        for i, (comment, _) in enumerate(comment_vectors):
            cluster_id = int(labels[i])
            prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[comment.prediction]
            
            clusters[cluster_id].append({
                "id": comment.id,
                "content": comment.content,
                "prediction": comment.prediction,
                "prediction_text": prediction_text,
                "confidence": comment.confidence,
                "platform": comment.platform,
                "source_user_name": comment.source_user_name,
                "created_at": comment.created_at.isoformat()
            })
        
        # Loại bỏ các cụm rỗng
        clusters = [cluster for cluster in clusters if cluster]
        
        # Sắp xếp các cụm theo số lượng comments (giảm dần)
        clusters.sort(key=len, reverse=True)
        
        return {"clusters": clusters, "total_comments": len(comment_vectors)}
        
    except ImportError:
        raise HTTPException(status_code=500, detail="Không có thư viện scikit-learn để phân cụm")