"""
Quizzes endpoints for the Learning Coach Agent.
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.quiz_generator import QuizGenerator
from app.models import Quiz as QuizModel, QuizAttempt as QuizAttemptModel

router = APIRouter()

# Initialize the quiz generator
quiz_generator = QuizGenerator()

class QuizQuestion(BaseModel):
    """Quiz question schema."""

    question: str
    options: List[str]
    correct_answer: int
    explanation: str


class Quiz(BaseModel):
    """Quiz schema."""

    id: str
    title: str
    description: str
    topic: str
    difficulty: str
    questions: List[QuizQuestion]
    estimated_time_minutes: int
    created_at: str
    user_id: Optional[str] = None


class QuizAttempt(BaseModel):
    """Quiz attempt schema."""

    quiz_id: str
    user_id: str
    answers: List[int]
    score: float
    completed: bool
    date: str


@router.get("/", response_model=List[Dict[str, Any]])
def get_quizzes(
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all quizzes, optionally filtered by topic, difficulty, and user_id.
    """
    try:
        # First try to get quizzes from the database
        query = db.query(QuizModel)

        if topic:
            query = query.filter(QuizModel.topic == topic)

        if difficulty:
            query = query.filter(QuizModel.difficulty == difficulty)

        if user_id:
            query = query.filter(QuizModel.user_id == user_id)

        db_quizzes = query.offset(skip).limit(limit).all()

        # If we have quizzes in the database, return them
        if db_quizzes:
            return [
                {
                    "id": quiz.id,
                    "title": quiz.title,
                    "description": quiz.description,
                    "topic": quiz.topic,
                    "difficulty": quiz.difficulty,
                    "questions": quiz.questions,
                    "estimated_time_minutes": quiz.estimated_time_minutes,
                    "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
                    "user_id": quiz.user_id,
                    "learning_objectives": quiz.learning_objectives,
                    "tags": quiz.tags
                } for quiz in db_quizzes
            ]

        # Otherwise, fall back to the in-memory quizzes
        quizzes = quiz_generator.get_quizzes(
            topic=topic,
            difficulty=difficulty,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quizzes: {str(e)}")


@router.get("/{quiz_id}", response_model=Dict[str, Any])
def get_quiz(
    quiz_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific quiz by ID.
    """
    try:
        quiz = quiz_generator.get_quiz(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quiz: {str(e)}")


@router.post("/generate", response_model=Dict[str, Any])
async def generate_quiz(
    topic: str,
    difficulty: str = "beginner",
    num_questions: int = 5,
    question_types: List[str] = ["multiple_choice"],
    learning_objectives: List[str] = [],
    user_id: Optional[str] = None,
    existing_quiz: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Generate a new quiz based on the given parameters.
    """
    try:
        # If we have an existing quiz, use that instead of generating a new one
        if existing_quiz:
            quiz = existing_quiz
        else:
            # Generate the quiz
            quiz = await quiz_generator.generate_quiz(
                topic=topic,
                difficulty=difficulty,
                num_questions=num_questions,
                question_types=question_types,
                learning_objectives=learning_objectives,
                user_id=user_id
            )

        # Save the quiz to the database
        try:
            # Log the quiz data for debugging
            print(f"Attempting to save quiz to database with ID: {quiz['id']}")
            print(f"Quiz title: {quiz['title']}")
            print(f"Quiz topic: {quiz['topic']}")

            # Create a new quiz record
            db_quiz = QuizModel(
                id=quiz["id"],
                title=quiz["title"],
                description=quiz["description"],
                topic=quiz["topic"],
                difficulty=quiz["difficulty"],
                questions=quiz["questions"],
                estimated_time_minutes=quiz["estimated_time_minutes"],
                created_at=datetime.now(timezone.utc),
                learning_objectives=quiz.get("learning_objectives", []),
                tags=quiz.get("tags", []),
                user_id=int(user_id) if user_id and user_id.isdigit() else None
            )

            # Add to database and commit
            db.add(db_quiz)
            db.commit()
            db.refresh(db_quiz)

            # Add the database ID to the result
            quiz["db_id"] = db_quiz.id

            # Log successful save
            print(f"Successfully saved quiz to database with ID: {db_quiz.id}")

            # Verify the quiz was saved by querying it back
            saved_quiz = db.query(QuizModel).filter(QuizModel.id == quiz["id"]).first()
            if saved_quiz:
                print(f"Verified quiz was saved: {saved_quiz.title}")
            else:
                print(f"WARNING: Quiz with ID {quiz['id']} not found in database after save!")

        except Exception as db_error:
            # Log the error but continue with the in-memory quiz
            print(f"Error saving quiz to database: {str(db_error)}")
            import traceback
            print(traceback.format_exc())

        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


@router.post("/{quiz_id}/submit", response_model=Dict[str, Any])
def submit_quiz_attempt(
    quiz_id: str,
    answers: List[int],
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Submit a quiz attempt and get the results.
    """
    try:
        # Get the result from the quiz generator
        result = quiz_generator.submit_quiz_attempt(
            quiz_id=quiz_id,
            user_id=user_id,
            answers=answers
        )

        # Save the attempt to the database
        try:
            # Create a new quiz attempt record
            db_quiz_attempt = QuizAttemptModel(
                id=str(uuid.uuid4()),
                quiz_id=quiz_id,
                user_id=int(user_id) if user_id and user_id.isdigit() else None,
                answers=answers,
                score=result.get("score", 0),
                correct_answers=result.get("correct_answers", 0),
                total_questions=result.get("total_questions", 0),
                feedback=result.get("feedback", {}),
                completed_at=datetime.now(timezone.utc)
            )

            # Add to database and commit
            db.add(db_quiz_attempt)
            db.commit()

            # Add the database ID to the result
            result["db_id"] = db_quiz_attempt.id
        except Exception as db_error:
            # Log the error but continue with the in-memory result
            print(f"Error saving quiz attempt to database: {str(db_error)}")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting quiz attempt: {str(e)}")


@router.get("/{quiz_id}/attempts", response_model=List[QuizAttempt])
def get_quiz_attempts(
    quiz_id: str,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all attempts for a specific quiz, optionally filtered by user_id.
    """
    try:
        attempts = quiz_generator.get_quiz_attempts(
            quiz_id=quiz_id,
            user_id=user_id
        )
        return attempts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quiz attempts: {str(e)}")


@router.post("/recommend", response_model=Dict[str, Any])
async def recommend_quiz(
    topic: str,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Recommend a quiz based on the user's learning history and the given topic.
    """
    try:
        quiz = await quiz_generator.recommend_quiz(
            topic=topic,
            user_id=user_id
        )
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recommending quiz: {str(e)}")
