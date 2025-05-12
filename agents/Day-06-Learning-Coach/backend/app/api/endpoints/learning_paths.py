"""
Learning Paths endpoints for the Learning Coach Agent.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.learning_path import LearningPath
from app.schemas.learning_path import LearningPathCreate, LearningPathRead, LearningPathUpdate

router = APIRouter()


@router.get("/", response_model=List[LearningPathRead])
def read_learning_paths(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all learning paths, optionally filtered by user_id."""
    query = db.query(LearningPath)

    if user_id is not None:
        query = query.filter(LearningPath.user_id == user_id)

    learning_paths = query.offset(skip).limit(limit).all()
    return learning_paths


@router.post("/", response_model=LearningPathRead)
def create_learning_path(
    learning_path: LearningPathCreate,
    db: Session = Depends(get_db)
):
    """Create a new learning path."""
    # Create learning path object with optional user_id
    learning_path_data = {
        "title": learning_path.title,
        "description": learning_path.description,
        "topics": learning_path.topics,
        "resources": learning_path.resources
    }

    # Only add user_id if it's provided
    if learning_path.user_id is not None:
        learning_path_data["user_id"] = learning_path.user_id

    db_learning_path = LearningPath(**learning_path_data)
    db.add(db_learning_path)
    db.commit()
    db.refresh(db_learning_path)
    return db_learning_path


@router.get("/{learning_path_id}", response_model=LearningPathRead)
def read_learning_path(
    learning_path_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific learning path."""
    learning_path = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
    if learning_path is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return learning_path


@router.put("/{learning_path_id}", response_model=LearningPathRead)
def update_learning_path(
    learning_path_id: int,
    learning_path: LearningPathUpdate,
    db: Session = Depends(get_db)
):
    """Update a learning path."""
    db_learning_path = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
    if db_learning_path is None:
        raise HTTPException(status_code=404, detail="Learning path not found")

    update_data = learning_path.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_learning_path, key, value)

    db.commit()
    db.refresh(db_learning_path)
    return db_learning_path


@router.delete("/{learning_path_id}")
def delete_learning_path(
    learning_path_id: int,
    db: Session = Depends(get_db)
):
    """Delete a learning path."""
    db_learning_path = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
    if db_learning_path is None:
        raise HTTPException(status_code=404, detail="Learning path not found")

    db.delete(db_learning_path)
    db.commit()
    return {"message": f"Learning path {learning_path_id} deleted"}


@router.get("/{learning_path_id}/progress", response_model=dict)
def get_learning_path_progress(
    learning_path_id: int,
    db: Session = Depends(get_db)
):
    """Get progress for a specific learning path."""
    learning_path = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
    if learning_path is None:
        raise HTTPException(status_code=404, detail="Learning path not found")

    return learning_path.progress


@router.put("/{learning_path_id}/progress", response_model=dict)
def update_learning_path_progress(
    learning_path_id: int,
    progress: dict,
    db: Session = Depends(get_db)
):
    """Update progress for a specific learning path."""
    learning_path = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
    if learning_path is None:
        raise HTTPException(status_code=404, detail="Learning path not found")

    learning_path.progress = progress
    db.commit()
    db.refresh(learning_path)
    return learning_path.progress
