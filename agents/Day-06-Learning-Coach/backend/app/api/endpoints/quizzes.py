"""
Quizzes endpoints for the Learning Coach Agent.
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.quiz_generator import QuizGenerator

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
    db: Session = Depends(get_db)
):
    """
    Generate a new quiz based on the given parameters.
    """
    try:
        quiz = await quiz_generator.generate_quiz(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            question_types=question_types,
            learning_objectives=learning_objectives,
            user_id=user_id
        )
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
        result = quiz_generator.submit_quiz_attempt(
            quiz_id=quiz_id,
            user_id=user_id,
            answers=answers
        )
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
