"""
Resources endpoints for the Learning Coach Agent.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.resource_manager import ResourceManager
from app.models import Resource as ResourceModel

router = APIRouter()

# Initialize the resource manager
resource_manager = ResourceManager()

class Resource(BaseModel):
    """Resource schema."""

    id: str
    title: str
    url: str
    type: str
    description: str
    difficulty: str
    estimated_time: str
    topics: List[str]
    source: str


@router.get("/", response_model=List[Resource])
def get_resources(
    topic: Optional[str] = None,
    type: Optional[str] = None,
    difficulty: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get learning resources, optionally filtered by topic, type, and difficulty.
    """
    try:
        # First try to get resources from the database
        query = db.query(ResourceModel)

        if topic:
            # For JSON arrays in SQLite, we need a workaround
            # This is a simplified approach - in production you might want to use a more robust solution
            query = query.filter(ResourceModel.topics.like(f'%{topic}%'))

        if type:
            query = query.filter(ResourceModel.type == type)

        if difficulty:
            query = query.filter(ResourceModel.difficulty == difficulty)

        db_resources = query.offset(skip).limit(limit).all()

        # If we have resources in the database, return them
        if db_resources:
            return [
                Resource(
                    id=resource.id,
                    title=resource.title,
                    url=resource.url,
                    type=resource.type,
                    description=resource.description,
                    difficulty=resource.difficulty,
                    estimated_time=resource.estimated_time,
                    topics=resource.topics,
                    source=resource.source
                ) for resource in db_resources
            ]

        # Otherwise, fall back to the in-memory resources
        resources = resource_manager.get_resources(
            topic=topic,
            resource_type=type,
            difficulty=difficulty,
            skip=skip,
            limit=limit
        )
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resources: {str(e)}")


@router.get("/{resource_id}", response_model=Resource)
def get_resource(
    resource_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific resource by ID.
    """
    try:
        resource = resource_manager.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        return resource
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resource: {str(e)}")


@router.post("/search", response_model=List[Resource])
def search_resources(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search for resources based on a query string.
    """
    try:
        resources = resource_manager.search_resources(
            query=query,
            skip=skip,
            limit=limit
        )
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching resources: {str(e)}")


@router.post("/recommend", response_model=List[Resource])
def recommend_resources(
    topic: str,
    learning_style: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get personalized resource recommendations based on topic and learning style.
    """
    try:
        resources = resource_manager.recommend_resources(
            topic=topic,
            learning_style=learning_style,
            difficulty=difficulty,
            limit=limit
        )
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recommending resources: {str(e)}")


@router.post("/rate/{resource_id}")
def rate_resource(
    resource_id: str,
    rating: int,
    user_id: int,
    feedback: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Rate a resource and provide optional feedback.
    """
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    try:
        resource_manager.rate_resource(
            resource_id=resource_id,
            user_id=user_id,
            rating=rating,
            feedback=feedback
        )
        return {"message": "Resource rated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rating resource: {str(e)}")
