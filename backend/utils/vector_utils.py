import numpy as np
import json
from typing import List, Dict, Any, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.comment import Comment
from backend.services.ml_model import toxicity_detector

async def find_similar_comments(
    db: AsyncSession, 
    text: str, 
    limit: int = 10, 
    classification: int = None
) -> List[Dict[str, Any]]:
    """
    Find comments similar to the given text using vector similarity
    
    Args:
        db: Database session
        text: Text to find similar comments for
        limit: Maximum number of similar comments to return
        classification: Filter by classification (optional)
        
    Returns:
        List of similar comments with similarity scores
    """
    # Get vector representation of the text
    embedding = await toxicity_detector.get_embeddings(text)
    
    # Build query to get comments
    query = select(Comment)
    
    # Add classification filter if provided
    if classification is not None:
        query = query.filter(Comment.classification_result == classification)
    
    # Execute query
    result = await db.execute(query)
    comments = result.scalars().all()
    
    # Calculate similarities manually
    comments_with_distances = []
    for comment in comments:
        try:
            # Get the vector from content_vector_json
            if hasattr(comment, "content_vector_json") and comment.content_vector_json:
                comment_vector = np.array(json.loads(comment.content_vector_json))
            elif hasattr(comment, "content_vector") and comment.content_vector:
                comment_vector = np.array(comment.content_vector)
            else:
                continue
                
            # Calculate L2 distance
            distance = np.linalg.norm(embedding - comment_vector)
            comments_with_distances.append((comment, distance))
        except (TypeError, ValueError, json.JSONDecodeError):
            # Skip comments with invalid vectors
            continue
    
    # Sort by distance (lowest first)
    comments_with_distances.sort(key=lambda x: x[1])
    
    # Take only the top 'limit' results
    comments_with_distances = comments_with_distances[:limit]
    
    # Format results
    similar_comments = []
    for comment, distance in comments_with_distances:
        # Convert distance to similarity score (0-100)
        similarity = max(0, min(100, 100 * (1 - distance / 10)))
        
        similar_comments.append({
            "id": comment.id,
            "content": comment.content,
            "classification": comment.classification_result,
            "platform": comment.source_platform,
            "similarity_score": round(similarity, 2),
            "created_at": comment.created_at.isoformat() if comment.created_at else None
        })
    
    return similar_comments

async def cluster_comments(
    db: AsyncSession, 
    limit: int = 100, 
    classification: int = None
) -> List[Dict[str, Any]]:
    """
    Perform basic clustering on comments to find groups of similar content
    
    Args:
        db: Database session
        limit: Maximum number of comments to analyze
        classification: Filter by classification (optional)
        
    Returns:
        List of comment clusters
    """
    # Build query to get comments
    query = select(Comment).limit(limit)
    
    # Add classification filter if provided
    if classification is not None:
        query = query.filter(Comment.classification_result == classification)
    
    # Execute query
    result = await db.execute(query)
    comments = result.scalars().all()
    
    # Extract comment vectors
    comment_vectors = []
    for comment in comments:
        try:
            # Get vector from content_vector_json or content_vector
            if hasattr(comment, "content_vector_json") and comment.content_vector_json:
                vector = np.array(json.loads(comment.content_vector_json))
            elif hasattr(comment, "content_vector") and comment.content_vector:
                vector = np.array(comment.content_vector)
            else:
                continue
                
            comment_vectors.append({
                "id": comment.id,
                "content": comment.content,
                "classification": comment.classification_result,
                "platform": comment.source_platform,
                "vector": vector,
                "created_at": comment.created_at
            })
        except (TypeError, ValueError, json.JSONDecodeError):
            # Skip comments with invalid vectors
            continue
    
    # If too few comments, return them all as one cluster
    if len(comment_vectors) < 5:
        return [{
            "cluster_id": 0,
            "size": len(comment_vectors),
            "comments": [
                {
                    "id": c["id"],
                    "content": c["content"],
                    "classification": c["classification"],
                    "platform": c["platform"],
                    "created_at": c["created_at"].isoformat() if c["created_at"] else None
                }
                for c in comment_vectors
            ]
        }]
    
    # Simple clustering based on vector similarity
    # This is a basic implementation - in a real system, you'd use a more sophisticated algorithm
    clusters = []
    assigned_comments = set()
    
    # For each unassigned comment, find similar ones to form a cluster
    for i, comment in enumerate(comment_vectors):
        if comment["id"] in assigned_comments:
            continue
        
        # This comment becomes the centroid of a new cluster
        cluster_comments = [comment]
        assigned_comments.add(comment["id"])
        
        # Find similar comments
        for j, other_comment in enumerate(comment_vectors):
            if other_comment["id"] in assigned_comments:
                continue
            
            # Calculate similarity
            vec1 = comment["vector"]
            vec2 = other_comment["vector"]
            distance = np.linalg.norm(vec1 - vec2)
            similarity = max(0, min(100, 100 * (1 - distance / 10)))
            
            # If similar enough, add to cluster
            if similarity > 70:  # Threshold for similarity
                cluster_comments.append(other_comment)
                assigned_comments.add(other_comment["id"])
        
        # Only create clusters with at least 2 comments
        if len(cluster_comments) > 1:
            clusters.append({
                "cluster_id": len(clusters),
                "size": len(cluster_comments),
                "comments": [
                    {
                        "id": c["id"],
                        "content": c["content"],
                        "classification": c["classification"],
                        "platform": c["platform"],
                        "created_at": c["created_at"].isoformat() if c["created_at"] else None
                    }
                    for c in cluster_comments
                ]
            })
    
    # Add remaining comments as individual clusters
    remaining = [c for c in comment_vectors if c["id"] not in assigned_comments]
    if remaining:
        clusters.append({
            "cluster_id": len(clusters),
            "size": len(remaining),
            "comments": [
                {
                    "id": c["id"],
                    "content": c["content"],
                    "classification": c["classification"],
                    "platform": c["platform"],
                    "created_at": c["created_at"].isoformat() if c["created_at"] else None
                }
                for c in remaining
            ]
        })
    
    return clusters