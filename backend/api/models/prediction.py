from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class TextAnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str = Field(..., description="Text content to analyze")
    platform: Optional[str] = Field("unknown", description="Source platform (facebook, twitter, youtube)")
    comment_id: Optional[str] = Field(None, description="Platform-specific comment ID")

class ProbabilityScores(BaseModel):
    """Model for probability scores"""
    clean: float = Field(..., description="Probability of being clean content")
    offensive: float = Field(..., description="Probability of being offensive content")
    hate: float = Field(..., description="Probability of being hate speech")
    spam: float = Field(..., description="Probability of being spam")

class TextAnalysisResponse(BaseModel):
    """Response model for text analysis"""
    success: bool = Field(..., description="Whether the analysis was successful")
    comment_id: Optional[int] = Field(None, description="Database ID of the comment")
    classification: int = Field(..., description="Classification result (0-clean, 1-offensive, 2-hate, 3-spam)")
    probabilities: ProbabilityScores
    is_new: bool = Field(..., description="Whether this is a new analysis or from cache")

class CommentModel(BaseModel):
    """Model for a comment"""
    id: int
    content: str
    classification_result: int
    source_platform: str
    platform_comment_id: Optional[str] = None
    clean_score: Optional[float] = None
    offensive_score: Optional[float] = None
    hate_score: Optional[float] = None
    spam_score: Optional[float] = None
    is_checked: bool
    created_at: datetime
    checked_at: Optional[datetime] = None

class SimilaritySearchRequest(BaseModel):
    """Request model for similarity search"""
    text: str = Field(..., description="Text to find similar comments for")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of results")
    classification: Optional[int] = Field(None, ge=0, le=3, description="Filter by classification")

class SimilarCommentModel(BaseModel):
    """Model for a similar comment result"""
    id: int
    content: str
    classification: int
    platform: str
    similarity_score: float
    created_at: Optional[str] = None

class SimilaritySearchResponse(BaseModel):
    """Response model for similarity search"""
    success: bool
    query: str
    results: List[SimilarCommentModel]
    count: int

class ClusterResponse(BaseModel):
    """Response model for comment clusters"""
    success: bool
    total_clusters: int
    clusters: List[Dict[str, Any]]