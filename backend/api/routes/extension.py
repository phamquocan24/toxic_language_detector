from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from backend.db.base import get_db
from backend.db.models.comment import Comment
from backend.db.models.log import Log
from backend.core.security import get_current_active_user
from backend.db.models.user import User
from backend.services.ml_model import toxicity_detector

router = APIRouter()

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_comment(
    request: Request,
    data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a comment for toxicity
    """
    comment_text = data.get("text", "")
    platform = data.get("platform", "unknown")
    platform_comment_id = data.get("comment_id", "")
    
    if not comment_text:
        raise HTTPException(status_code=400, detail="Comment text is required")
    
    # Check if comment was already analyzed
    result = await db.execute(
        select(Comment).where(
            Comment.source_platform == platform,
            Comment.platform_comment_id == platform_comment_id
        )
    )
    existing_comment = result.scalars().first()
    
    if existing_comment and existing_comment.is_checked:
        # Return existing analysis
        return {
            "success": True,
            "comment_id": existing_comment.id,
            "classification": existing_comment.classification_result,
            "probabilities": {
                "clean": existing_comment.clean_score,
                "offensive": existing_comment.offensive_score,
                "hate": existing_comment.hate_score,
                "spam": existing_comment.spam_score
            },
            "is_new": False
        }
    
    # Get prediction from model
    prediction = await toxicity_detector.predict(comment_text)
    classification = prediction.get("classification", 0)
    probabilities = prediction.get("probabilities", {})
    
    # Get comment vector embedding
    embedding = await toxicity_detector.get_embeddings(comment_text)
    
    # Create or update comment record
    if existing_comment:
        # Update existing comment
        existing_comment.is_checked = True
        existing_comment.classification_result = classification
        existing_comment.clean_score = probabilities.get("clean", 0.0)
        existing_comment.offensive_score = probabilities.get("offensive", 0.0)
        existing_comment.hate_score = probabilities.get("hate", 0.0)
        existing_comment.spam_score = probabilities.get("spam", 0.0)
        existing_comment.checked_at = datetime.now()
        existing_comment.content_vector = embedding.tolist()
        
        db.add(existing_comment)
        await db.commit()
        await db.refresh(existing_comment)
        
        comment_id = existing_comment.id
        is_new = False
    else:
        # Create new comment record
        new_comment = Comment(
            user_id=current_user.id,
            source_platform=platform,
            platform_comment_id=platform_comment_id,
            content=comment_text,
            content_vector=embedding.tolist(),
            is_checked=True,
            classification_result=classification,
            clean_score=probabilities.get("clean", 0.0),
            offensive_score=probabilities.get("offensive", 0.0),
            hate_score=probabilities.get("hate", 0.0),
            spam_score=probabilities.get("spam", 0.0),
            checked_at=datetime.now()
        )
        
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        
        comment_id = new_comment.id
        is_new = True
    
    # Log the request
    log_entry = Log(
        user_id=current_user.id,
        action="analyze_comment",
        endpoint="/api/extension/analyze",
        request_data={"platform": platform, "comment_id": platform_comment_id},
        response_data={"classification": classification, "is_new": is_new},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status_code=200,
        details=f"Comment analyzed: {platform}/{platform_comment_id}"
    )
    db.add(log_entry)
    await db.commit()
    
    return {
        "success": True,
        "comment_id": comment_id,
        "classification": classification,
        "probabilities": probabilities,
        "is_new": is_new
    }