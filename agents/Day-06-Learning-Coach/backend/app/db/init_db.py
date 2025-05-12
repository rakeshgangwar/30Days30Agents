"""
Database initialization script.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.base import Base, engine
from app.models.user import User
from app.models.learning_path import LearningPath
from app.models.resource import Resource
from app.models.quiz import Quiz, QuizAttempt


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
            interests=["programming", "machine learning", "web development"],
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        logger.info("Created test user")

        # Create a sample learning path for Python
        python_path = LearningPath(
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
        db.add(python_path)

        # Create a sample learning path for Web Development
        web_dev_path = LearningPath(
            title="Web Development Fundamentals",
            description="Learn the basics of HTML, CSS, and JavaScript",
            user_id=test_user.id,
            topics=[
                {"name": "HTML Basics", "order": 1},
                {"name": "CSS Styling", "order": 2},
                {"name": "JavaScript Fundamentals", "order": 3},
                {"name": "Responsive Design", "order": 4},
            ],
            resources=[
                {"name": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/docs/Web", "type": "documentation"},
                {"name": "W3Schools", "url": "https://www.w3schools.com/", "type": "tutorial"},
            ],
            progress={"completed_topics": 0, "total_topics": 4},
        )
        db.add(web_dev_path)
        db.commit()
        logger.info("Created sample learning paths")

        # Create sample resources
        resources = [
            Resource(
                id=str(uuid.uuid4()),
                title="Python for Beginners",
                url="https://www.python.org/about/gettingstarted/",
                type="article",
                description="Official Python getting started guide",
                difficulty="beginner",
                estimated_time="30 minutes",
                topics=["Python", "Programming Basics"],
                source="python.org",
                user_id=test_user.id
            ),
            Resource(
                id=str(uuid.uuid4()),
                title="MDN Web Docs",
                url="https://developer.mozilla.org/en-US/docs/Web",
                type="documentation",
                description="Comprehensive web development documentation",
                difficulty="beginner",
                estimated_time="ongoing",
                topics=["HTML", "CSS", "JavaScript", "Web Development"],
                source="mozilla.org",
                user_id=test_user.id
            ),
            Resource(
                id=str(uuid.uuid4()),
                title="JavaScript.info",
                url="https://javascript.info/",
                type="tutorial",
                description="Modern JavaScript tutorial from basics to advanced",
                difficulty="beginner",
                estimated_time="20 hours",
                topics=["JavaScript", "Web Development"],
                source="javascript.info",
                user_id=test_user.id
            )
        ]

        for resource in resources:
            db.add(resource)

        db.commit()
        logger.info("Created sample resources")

        # Create sample quizzes
        quizzes = [
            Quiz(
                id=str(uuid.uuid4()),
                title="Web Development Fundamentals Quiz",
                description="Test your knowledge of HTML, CSS, and JavaScript fundamentals",
                topic="Web Development",
                difficulty="beginner",
                questions=[
                    {
                        "question": "What does HTML stand for?",
                        "options": [
                            "Hyper Text Markup Language",
                            "High Tech Modern Language",
                            "Hyperlink and Text Markup Language",
                            "Home Tool Markup Language"
                        ],
                        "correct_answer": 0,
                        "explanation": "HTML stands for Hyper Text Markup Language, which is the standard markup language for creating web pages.",
                        "question_type": "multiple_choice"
                    },
                    {
                        "question": "Which CSS property is used to change the text color of an element?",
                        "options": [
                            "text-color",
                            "font-color",
                            "color",
                            "text-style"
                        ],
                        "correct_answer": 2,
                        "explanation": "The 'color' property is used to set the color of text in CSS.",
                        "question_type": "multiple_choice"
                    }
                ],
                estimated_time_minutes=5,
                created_at=datetime.now(timezone.utc),
                learning_objectives=["Understand basic web development concepts"],
                tags=["Web Development", "HTML", "CSS", "JavaScript"],
                user_id=test_user.id
            ),
            Quiz(
                id=str(uuid.uuid4()),
                title="Python Basics Quiz",
                description="Test your knowledge of Python fundamentals",
                topic="Python",
                difficulty="beginner",
                questions=[
                    {
                        "question": "What is the correct way to create a variable in Python?",
                        "options": [
                            "var x = 5",
                            "x = 5",
                            "int x = 5",
                            "create x = 5"
                        ],
                        "correct_answer": 1,
                        "explanation": "In Python, you can simply assign a value to a variable name without declaring its type.",
                        "question_type": "multiple_choice"
                    },
                    {
                        "question": "Which of the following is a mutable data type in Python?",
                        "options": [
                            "String",
                            "Tuple",
                            "List",
                            "Integer"
                        ],
                        "correct_answer": 2,
                        "explanation": "Lists are mutable, meaning they can be changed after creation. Strings, tuples, and integers are immutable.",
                        "question_type": "multiple_choice"
                    }
                ],
                estimated_time_minutes=5,
                created_at=datetime.now(timezone.utc),
                learning_objectives=["Understand Python basics"],
                tags=["Python", "Programming"],
                user_id=test_user.id
            )
        ]

        for quiz in quizzes:
            db.add(quiz)

        db.commit()
        logger.info("Created sample quizzes")
