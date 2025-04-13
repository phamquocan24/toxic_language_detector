# # api/models/prediction.py
# from pydantic import BaseModel, Field
# from typing import List, Optional, Dict, Any
# from datetime import datetime

# class CommentBase(BaseModel):
#     content: str
#     platform: str
#     platform_id: str
#     metadata: Optional[Dict[str, Any]] = None

# class CommentCreate(CommentBase):
#     pass

# class CommentResponse(CommentBase):
#     id: int
#     prediction: int
#     confidence: float
#     created_at: datetime
    
#     class Config:
#         orm_mode = True

# class PredictionRequest(BaseModel):
#     text: str
#     platform: Optional[str] = "unknown"
#     platform_id: Optional[str] = None
#     metadata: Optional[Dict[str, Any]] = None

# class PredictionResponse(BaseModel):
#     text: str
#     prediction: int = Field(..., description="0: clean, 1: offensive, 2: hate, 3: spam")
#     confidence: float
#     prediction_text: str
    
#     class Config:
#         schema_extra = {
#             "example": {
#                 "text": "This is a sample comment",
#                 "prediction": 0,
#                 "confidence": 0.95,
#                 "prediction_text": "clean"
#             }
#         }

# class BatchPredictionRequest(BaseModel):
#     comments: List[PredictionRequest]

# class BatchPredictionResponse(BaseModel):
#     results: List[PredictionResponse]
    
# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str = "bearer"
    
# class UserCreate(BaseModel):
#     username: str
#     email: str
#     password: str
    
# class UserResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#     is_active: bool
#     role: str
    
#     class Config:
#         orm_mode = True

# class UserLogin(BaseModel):
#     username: str
#     password: str

# class LogResponse(BaseModel):
#     id: int
#     request_path: str
#     request_method: str
#     response_status: int
#     timestamp: datetime
#     client_ip: str
    
#     class Config:
#         orm_mode = True
# api/models/prediction.py
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class CommentBase(BaseModel):
    content: str
    platform: str = "unknown"
    source_user_name: Optional[str] = None
    source_url: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class CommentCreate(CommentBase):
    processed_content: Optional[str] = None

class CommentResponse(CommentBase):
    id: int
    prediction: int
    prediction_text: Optional[str] = None  # Thêm prediction_text
    confidence: float
    probabilities: Optional[Dict[str, float]] = None  # Thêm probabilities cho từng nhãn
    processed_content: Optional[str] = None
    created_at: datetime
    user_id: Optional[int] = None
    similarity: Optional[float] = None  # Cho kết quả tìm kiếm tương tự
    
    model_config = {
        "from_attributes": True
    }

class PredictionRequest(BaseModel):
    text: str
    platform: Optional[str] = "unknown"
    source_user_name: Optional[str] = None
    source_url: Optional[str] = None
    save_result: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    text: str
    processed_text: Optional[str] = None
    prediction: int = Field(..., description="0: clean, 1: offensive, 2: hate, 3: spam")
    confidence: float
    probabilities: Optional[Dict[str, float]] = None
    prediction_text: str
    keywords: Optional[List[str]] = None
    timestamp: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a sample comment",
                "processed_text": "this is a sample comment",
                "prediction": 0,
                "confidence": 0.95,
                "probabilities": {"clean": 0.95, "offensive": 0.02, "hate": 0.01, "spam": 0.02},
                "prediction_text": "clean",
                "keywords": ["sample", "comment"],
                "timestamp": "2023-08-01T12:30:45.123456"
            }
        }

class BatchPredictionItemRequest(BaseModel):
    text: str
    platform: Optional[str] = "unknown"
    source_user_name: Optional[str] = None
    source_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BatchPredictionRequest(BaseModel):
    comments: List[BatchPredictionItemRequest]
    save_results: Optional[bool] = True

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]
    count: int
    timestamp: Optional[str] = None
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str
    expires_in: int  # Thời hạn token (giây)
    
class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: Optional[str] = None  # Thêm trường name (tên hiển thị)

class UserCreate(UserBase):
    password: str
    confirm_password:str
    
    @field_validator('password', 'confirm_password')
    @classmethod
    def validate_passwords(cls, v):
        if len(v) < 8:
            raise ValueError('Mật khẩu phải có ít nhất 8 ký tự')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None  # Thêm trường name
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    name: Optional[str] = None  # Thêm trường name
    is_active: bool
    role: str
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    username: str
    password: str
    remember_me: Optional[bool] = False

class LogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    timestamp: datetime
    
    model_config = {
        "from_attributes": True
    }

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    
    @field_validator('new_password')
    @classmethod
    def validate_passwords(cls, v):
        if len(v) < 8:
            raise ValueError('Mật khẩu phải có ít nhất 8 ký tự')
        return v

class StatisticsResponse(BaseModel):
    total: int
    clean: int
    offensive: int
    hate: int
    spam: int
    percentages: Dict[str, float]
    platforms: Dict[str, int]
    confidence: Dict[str, float]
    toxic_users: Optional[List[Dict[str, Any]]] = None
    filters: Dict[str, Any]

class TrendResponse(BaseModel):
    dates: List[str]
    series: Dict[str, List[int]]
    period: str
    filters: Dict[str, Any]

class SimilarCommentsResponse(BaseModel):
    source_comment: Dict[str, Any]
    similar_comments: List[Dict[str, Any]]
    count: int

class TextAnalysisResponse(BaseModel):
    text: str
    processed_text: str
    prediction: int
    prediction_text: str
    confidence: float
    probabilities: Optional[Dict[str, float]] = None
    keywords: Optional[List[str]] = None
    sentiment: Optional[Dict[str, Any]] = None
    word_count: int
    char_count: int

class DashboardData(BaseModel):
    statistics: Dict[str, int]
    platforms: Dict[str, int]
    ml_stats: Optional[Dict[str, Any]] = None
    period: str

class ExtensionStatsResponse(BaseModel):
    total_count: int
    clean_count: int
    offensive_count: int
    hate_count: int
    spam_count: int
    platforms: Dict[str, int]
    recent: List[Dict[str, Any]]
    period: str