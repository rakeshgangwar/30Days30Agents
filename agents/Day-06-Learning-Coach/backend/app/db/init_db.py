"""
Database initialization script.
"""

import logging

from sqlalchemy.orm import Session

from app.db.base import Base, engine
from app.models.user import User
from app.models.learning_path import LearningPath


logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize the database."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


def create_initial_data(db: Session) -> None:
    """Create initial data in the database."""
    # Check if there are any users
    user_count = db.query(User).count()
    if user_count == 0:
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",  # In production, use proper password hashing
            preferences={"theme": "light"},
            learning_styles=["visual", "reading"],
            interests=["programming", "machine learning"],
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        logger.info("Created test user")
        
        # Create a sample learning path
        sample_path = LearningPath(
            title="Introduction to Python",
            description="A beginner's guide to Python programming",
            user_id=test_user.id,
            topics=[
                {"name": "Python Basics", "order": 1},
                {"name": "Data Structures", "order": 2},
                {"name": "Functions", "order": 3},
            ],
            resources=[
                {"name": "Python Documentation", "url": "https://docs.python.org/3/", "type": "documentation"},
                {"name": "Python Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "tutorial"},
            ],
            progress={"completed_topics": 0, "total_topics": 3},
        )
        db.add(sample_path)
        db.commit()
        logger.info("Created sample learning path")
