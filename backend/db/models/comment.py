# # db/models/comment.py
# from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from backend.db.models.base import Base
# import numpy as np
# import json

# class Comment(Base):
#     __tablename__ = "comments"
    
#     id = Column(Integer, primary_key=True, index=True)
#     content = Column(Text, nullable=False)
#     platform = Column(String, nullable=False)  # e.g. "facebook", "youtube", "twitter"
#     platform_id = Column(String, index=True)  # Original ID from the platform
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
    
#     # Classification results
#     prediction = Column(Integer)  # 0: clean, 1: offensive, 2: hate, 3: spam
#     confidence = Column(Float)
    
#     # Vector representation for similarity search
#     vector_representation = Column(String)  # Stored as JSON string
    
#     # Relationships
#     user_id = Column(Integer, ForeignKey("users.id"))
#     user = relationship("User", back_populates="comments")
    
#     # Additional comment_metadata from the platform
#     comment_metadata = Column(JSON)
    
#     def set_vector(self, vector):
#         """Convert numpy array to JSON string for storage"""
#         if isinstance(vector, np.ndarray):
#             self.vector_representation = json.dumps(vector.tolist())
#         else:
#             self.vector_representation = json.dumps(vector)
    
#     def get_vector(self):
#         """Get vector as numpy array"""
#         if self.vector_representation:
#             return np.array(json.loads(self.vector_representation))
#         return None
# db/models/comment.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.models.base import Base, TimestampMixin
from backend.config.settings import settings
import numpy as np
import json
from datetime import datetime

class Comment(Base, TimestampMixin):
    """
    Model lưu trữ thông tin về bình luận được phân tích
    """
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    processed_content = Column(Text, nullable=True)  # Nội dung đã tiền xử lý
    platform = Column(String(50), nullable=False, index=True)  # e.g. "facebook", "youtube", "twitter"
    source_user_name = Column(String(255), nullable=True, index=True)  # Tên người dùng nguồn
    source_url = Column(Text, nullable=True)  # URL của bình luận
    
    # Kết quả phân loại
    prediction = Column(Integer, index=True)  # 0: clean, 1: offensive, 2: hate, 3: spam
    confidence = Column(Float)
    probabilities = Column(Text, nullable=True)  # Xác suất cho từng nhãn dưới dạng JSON
    
    # Lưu trữ vector đặc trưng cho tìm kiếm tương tự
    vector_representation = Column(Text)  # Stored as JSON string
    
    # Trường hỗ trợ (phục vụ xử lý)
    is_reviewed = Column(Boolean, default=False, index=True)  # Đánh dấu đã xem xét chưa
    review_result = Column(Integer, nullable=True)  # Kết quả xem xét thủ công
    review_notes = Column(Text, nullable=True)  # Ghi chú khi xem xét
    review_timestamp = Column(DateTime(timezone=True), nullable=True)  # Thời gian xem xét
    
    # Khóa ngoại
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="comments")
    
    # Metadata bổ sung từ nền tảng
    metadata = Column(JSON, nullable=True)
    
    # Để hỗ trợ báo cáo
    is_in_report = Column(Boolean, default=False, index=True)
    report_ids = Column(Text, nullable=True)  # Lưu danh sách IDs của báo cáo dưới dạng JSON
    
    # Tạo indexes để tối ưu hóa truy vấn
    __table_args__ = (
        Index('idx_comment_platform_prediction', 'platform', 'prediction'),
        Index('idx_comment_created_prediction', 'created_at', 'prediction'),
        Index('idx_comment_user_platform', 'user_id', 'platform'),
    )
    
    def set_vector(self, vector):
        """Chuyển đổi numpy array thành chuỗi JSON để lưu trữ"""
        if vector is None:
            self.vector_representation = None
            return
            
        if isinstance(vector, np.ndarray):
            self.vector_representation = json.dumps(vector.tolist())
        else:
            self.vector_representation = json.dumps(vector)
    
    def get_vector(self):
        """Lấy vector dưới dạng numpy array"""
        if self.vector_representation:
            try:
                return np.array(json.loads(self.vector_representation))
            except (json.JSONDecodeError, ValueError):
                return None
        return None
    
    def set_probabilities(self, probs_dict):
        """Lưu trữ xác suất cho các nhãn"""
        if probs_dict is None:
            self.probabilities = None
            return
            
        if isinstance(probs_dict, dict):
            self.probabilities = json.dumps(probs_dict)
        else:
            self.probabilities = probs_dict  # Nếu đã là string
    
    def get_probabilities(self):
        """Lấy xác suất dưới dạng dictionary"""
        if self.probabilities:
            try:
                return json.loads(self.probabilities)
            except (json.JSONDecodeError, ValueError):
                return {}
        return {}
    
    def get_prediction_text(self):
        """Lấy nhãn dự đoán dưới dạng text"""
        if self.prediction is None:
            return "unknown"
            
        labels = settings.MODEL_LABELS
        if self.prediction < len(labels):
            return labels[self.prediction]
        return "unknown"
    
    def add_to_report(self, report_id):
        """Thêm comment vào báo cáo"""
        if not self.report_ids:
            self.report_ids = json.dumps([report_id])
        else:
            report_ids = json.loads(self.report_ids)
            if report_id not in report_ids:
                report_ids.append(report_id)
                self.report_ids = json.dumps(report_ids)
        self.is_in_report = True
    
    def mark_reviewed(self, result=None, notes=None):
        """Đánh dấu comment đã được xem xét"""
        self.is_reviewed = True
        if result is not None:
            self.review_result = result
        if notes is not None:
            self.review_notes = notes
        self.review_timestamp = datetime.utcnow()
    
    @staticmethod
    def get_comments_by_prediction(db, prediction, limit=100, offset=0):
        """Lấy comments theo nhãn dự đoán"""
        return db.query(Comment).filter(
            Comment.prediction == prediction
        ).order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_comments_by_platform(db, platform, limit=100, offset=0):
        """Lấy comments theo nền tảng"""
        return db.query(Comment).filter(
            Comment.platform == platform
        ).order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_comments_by_user(db, user_id, limit=100, offset=0):
        """Lấy comments theo người dùng phát hiện"""
        return db.query(Comment).filter(
            Comment.user_id == user_id
        ).order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def count_by_prediction(db):
        """Đếm số lượng comments theo nhãn dự đoán"""
        from sqlalchemy import func
        counts = db.query(
            Comment.prediction,
            func.count(Comment.id).label('count')
        ).group_by(Comment.prediction).all()
        
        result = {0: 0, 1: 0, 2: 0, 3: 0}  # Khởi tạo với các nhãn mặc định
        for prediction, count in counts:
            if prediction is not None:
                result[prediction] = count
                
        return result