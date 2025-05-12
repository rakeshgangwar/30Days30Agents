"""
Quiz generator for the Learning Coach Agent.

This module provides functionality for generating educational quizzes on various topics
with different difficulty levels and question types.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator


logger = logging.getLogger(__name__)


class QuizQuestion(BaseModel):
    """A quiz question."""

    question: str = Field(description="The question text")
    options: List[str] = Field(description="Multiple choice options")
    correct_answer: int = Field(description="Index of the correct answer (0-based)")
    explanation: str = Field(description="Explanation of the correct answer")
    question_type: str = Field(description="Type of question (multiple_choice, true_false, fill_in_blank)", default="multiple_choice")

    @field_validator('correct_answer')
    @classmethod
    def validate_correct_answer(cls, v: int, values: Dict[str, Any]) -> int:
        """Validate that the correct answer index is valid."""
        if 'options' in values.data and (v < 0 or v >= len(values.data['options'])):
            raise ValueError(f"Correct answer index {v} is out of range for options list of length {len(values.data['options'])}")
        return v


class QuizOutput(BaseModel):
    """Output schema for quiz generation."""

    title: str = Field(description="Title of the quiz")
    description: str = Field(description="Description of the quiz")
    topic: str = Field(description="Topic of the quiz")
    difficulty: str = Field(description="Difficulty level (beginner, intermediate, advanced)")
    questions: List[QuizQuestion] = Field(description="List of quiz questions")
    estimated_time_minutes: int = Field(description="Estimated time to complete in minutes")
    learning_objectives: List[str] = Field(
        description="Learning objectives covered by this quiz",
        default_factory=list
    )
    tags: List[str] = Field(
        description="Tags for categorizing the quiz",
        default_factory=list
    )

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Validate difficulty level."""
        valid_levels = ["beginner", "intermediate", "advanced"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Difficulty must be one of: {', '.join(valid_levels)}")
        return v.lower()

    @field_validator('estimated_time_minutes')
    @classmethod
    def validate_time(cls, v: int) -> int:
        """Validate that estimated time is positive."""
        if v <= 0:
            raise ValueError("Estimated time must be positive")
        return v


class QuizResult(BaseModel):
    """Result of a quiz attempt."""

    quiz_id: str = Field(description="ID of the quiz")
    user_id: Optional[str] = Field(description="ID of the user who took the quiz", default=None)
    score: float = Field(description="Score as a percentage (0-100)")
    correct_answers: int = Field(description="Number of correct answers")
    total_questions: int = Field(description="Total number of questions")
    answers: List[int] = Field(description="User's answers (indices)")
    feedback: Dict[str, Any] = Field(description="Feedback on the quiz attempt")
    completed_at: str = Field(description="Timestamp when the quiz was completed")


class QuizGenerator:
    """Generates and manages educational quizzes.

    This class provides functionality to create, evaluate, and manage quizzes
    on various topics with different difficulty levels.
    """

    # Define question types
    QUESTION_TYPES = [
        "multiple_choice",
        "true_false",
        "fill_in_blank"
    ]

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the quiz generator.

        Args:
            model_name: The name of the LLM model to use
        """
        # Get API key from environment
        import os
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(model=model_name, temperature=0.2, api_key=api_key)
        self.output_parser = JsonOutputParser(pydantic_object=QuizOutput)

        # In-memory storage for quizzes and results
        self.quizzes = {}
        self.quiz_results = {}

        # Add sample quizzes for development
        self._add_sample_quizzes()

        # Create the prompt template for quiz generation
        template = """
        You are a Learning Coach that creates educational quizzes.

        Create a quiz based on the following information:

        Topic: {topic}
        Difficulty level: {difficulty}
        Number of questions: {num_questions}
        Question types: {question_types}
        Learning objectives: {learning_objectives}

        For each question, provide:
        1. The question text - Clear, concise, and focused on testing understanding
        2. Multiple choice options (4 options) - Make sure they are plausible and distinct
        3. The index of the correct answer (0-based) - Double-check this is correct
        4. An explanation of why the answer is correct - Provide educational value
        5. Question type - The type of question (multiple_choice, true_false, fill_in_blank)

        Make sure the questions:
        - Are diverse and cover different aspects of the topic
        - Match the specified difficulty level
        - Test different cognitive skills (recall, understanding, application, analysis)
        - Are free from ambiguity
        - Have clearly correct answers
        - Include both conceptual and practical questions

        Also provide:
        - A descriptive title for the quiz
        - A brief description of what the quiz covers
        - Estimated time to complete in minutes
        - Learning objectives covered by the quiz
        - Tags for categorizing the quiz

        {format_instructions}
        """

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["topic", "difficulty", "num_questions", "question_types", "learning_objectives"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

        # Create the chain
        self.chain = self.prompt | self.llm | self.output_parser

        # Create the prompt template for quiz evaluation
        evaluate_template = """
        You are a Learning Coach that evaluates quiz responses.

        Evaluate the user's answers to the following quiz:

        Quiz: {quiz}

        User's answers: {answers}

        For each question, determine if the user's answer is correct and provide feedback.
        Calculate the overall score as a percentage.
        Identify areas of strength and weakness based on the answers.
        Provide suggestions for further learning based on the results.

        {format_instructions}
        """

        self.evaluate_prompt = PromptTemplate(
            template=evaluate_template,
            input_variables=["quiz", "answers"],
            partial_variables={
                "format_instructions": "Return a JSON object with the following structure: { 'score': float, 'correct_answers': int, 'total_questions': int, 'feedback': { 'strengths': [string], 'weaknesses': [string], 'suggestions': [string] }, 'question_feedback': [{ 'question_index': int, 'correct': boolean, 'feedback': string }] }"
            }
        )

        # Create the evaluation chain
        self.evaluate_chain = self.evaluate_prompt | self.llm

        logger.info(f"Quiz generator initialized with model: {model_name}")

    def _add_sample_quizzes(self):
        """Add sample quizzes for development."""
        import uuid
        from datetime import datetime, timezone

        # Web Development Quiz
        web_dev_quiz = {
            "id": str(uuid.uuid4()),
            "title": "Web Development Fundamentals Quiz",
            "description": "Test your knowledge of HTML, CSS, and JavaScript fundamentals",
            "topic": "Web Development",
            "difficulty": "beginner",
            "questions": [
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
                },
                {
                    "question": "Which of the following is NOT a JavaScript data type?",
                    "options": [
                        "String",
                        "Boolean",
                        "Float",
                        "Object"
                    ],
                    "correct_answer": 2,
                    "explanation": "JavaScript has number type for both integers and floating-point values, but 'Float' is not a distinct data type in JavaScript.",
                    "question_type": "multiple_choice"
                },
                {
                    "question": "What is the correct HTML element for the largest heading?",
                    "options": [
                        "<h1>",
                        "<heading>",
                        "<head>",
                        "<h6>"
                    ],
                    "correct_answer": 0,
                    "explanation": "<h1> defines the largest heading in HTML. Headings range from h1 (largest) to h6 (smallest).",
                    "question_type": "multiple_choice"
                },
                {
                    "question": "Which CSS property is used to add space between the elements?",
                    "options": [
                        "spacing",
                        "margin",
                        "padding",
                        "border"
                    ],
                    "correct_answer": 1,
                    "explanation": "The 'margin' property in CSS is used to create space around elements, outside of any defined borders.",
                    "question_type": "multiple_choice"
                }
            ],
            "estimated_time_minutes": 10,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "learning_objectives": ["Understand basic web development concepts", "Test knowledge of HTML, CSS, and JavaScript"],
            "tags": ["Web Development", "HTML", "CSS", "JavaScript", "beginner"]
        }

        # JavaScript Quiz
        js_quiz = {
            "id": str(uuid.uuid4()),
            "title": "JavaScript Fundamentals Quiz",
            "description": "Test your knowledge of JavaScript basics",
            "topic": "JavaScript",
            "difficulty": "beginner",
            "questions": [
                {
                    "question": "Which of the following is used to declare a variable in JavaScript?",
                    "options": [
                        "var",
                        "let",
                        "const",
                        "All of the above"
                    ],
                    "correct_answer": 3,
                    "explanation": "In JavaScript, you can declare variables using 'var', 'let', or 'const'. Each has different scoping rules and behaviors.",
                    "question_type": "multiple_choice"
                },
                {
                    "question": "What will the following code return: typeof []?",
                    "options": [
                        "'array'",
                        "'object'",
                        "'list'",
                        "'undefined'"
                    ],
                    "correct_answer": 1,
                    "explanation": "In JavaScript, arrays are actually objects, so typeof [] returns 'object'.",
                    "question_type": "multiple_choice"
                },
                {
                    "question": "Which method is used to add an element to the end of an array?",
                    "options": [
                        "push()",
                        "append()",
                        "add()",
                        "insert()"
                    ],
                    "correct_answer": 0,
                    "explanation": "The push() method adds one or more elements to the end of an array and returns the new length of the array.",
                    "question_type": "multiple_choice"
                }
            ],
            "estimated_time_minutes": 6,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "learning_objectives": ["Understand JavaScript basics", "Test knowledge of JavaScript syntax and concepts"],
            "tags": ["JavaScript", "Programming", "beginner"]
        }

        # Add the sample quizzes to the in-memory storage
        self.quizzes[web_dev_quiz["id"]] = web_dev_quiz
        self.quizzes[js_quiz["id"]] = js_quiz

        logger.info(f"Added {len(self.quizzes)} sample quizzes")

    async def generate_quiz(
        self,
        topic: str,
        difficulty: str = "beginner",
        num_questions: int = 5,
        question_types: List[str] = None,
        learning_objectives: List[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a quiz.

        Args:
            topic: The topic for the quiz
            difficulty: The difficulty level
            num_questions: Number of questions to generate
            question_types: Types of questions to include
            learning_objectives: Learning objectives to cover
            user_id: Optional user ID to associate with the quiz

        Returns:
            Dict containing the quiz details
        """
        logger.info(f"Generating quiz on topic: {topic}")

        if question_types is None:
            question_types = ["multiple_choice"]

        if learning_objectives is None:
            learning_objectives = [f"Understand the basics of {topic}"]

        try:
            result = await self.chain.ainvoke({
                "topic": topic,
                "difficulty": difficulty,
                "num_questions": num_questions,
                "question_types": ", ".join(question_types),
                "learning_objectives": ", ".join(learning_objectives)
            })

            # Generate a unique ID for the quiz
            quiz_id = str(uuid.uuid4())

            # Add metadata
            result["id"] = quiz_id
            result["created_at"] = datetime.utcnow().isoformat()
            result["user_id"] = user_id

            # Store the quiz
            self.quizzes[quiz_id] = result

            # Log the quiz details for debugging
            logger.info(f"Generated quiz with ID: {quiz_id}")
            logger.info(f"Quiz title: {result['title']}")
            logger.info(f"Quiz topic: {result['topic']}")
            logger.info(f"Quiz has {len(result['questions'])} questions")

            # Log that the quiz is ready to be saved to the database
            logger.info(f"Quiz ready for database storage: {quiz_id}")

            return result
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            # Return a simplified quiz if generation fails
            fallback_quiz = {
                "title": f"Quiz on {topic}",
                "description": f"A basic quiz to test your knowledge of {topic}",
                "topic": topic,
                "difficulty": difficulty,
                "questions": [
                    {
                        "question": f"What is {topic}?",
                        "options": [
                            f"A fundamental concept in {topic}",
                            f"An advanced technique in {topic}",
                            f"A historical figure related to {topic}",
                            f"None of the above"
                        ],
                        "correct_answer": 0,
                        "explanation": f"This is a basic definition question about {topic}.",
                        "question_type": "multiple_choice"
                    }
                ],
                "estimated_time_minutes": 5,
                "learning_objectives": [f"Understand the basics of {topic}"],
                "tags": [topic, difficulty]
            }

            # Generate a unique ID for the fallback quiz
            quiz_id = str(uuid.uuid4())

            # Add metadata
            fallback_quiz["id"] = quiz_id
            fallback_quiz["created_at"] = datetime.utcnow().isoformat()
            fallback_quiz["user_id"] = user_id

            # Store the fallback quiz
            self.quizzes[quiz_id] = fallback_quiz

            logger.info(f"Generated fallback quiz with ID: {quiz_id}")
            return fallback_quiz

    async def evaluate_quiz(
        self,
        quiz_id: str,
        answers: List[int],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluate a quiz attempt.

        Args:
            quiz_id: The ID of the quiz to evaluate
            answers: The user's answers (indices)
            user_id: Optional user ID to associate with the result

        Returns:
            Dict containing the evaluation results
        """
        logger.info(f"Evaluating quiz with ID: {quiz_id}")

        # Check if the quiz exists
        if quiz_id not in self.quizzes:
            logger.error(f"Quiz with ID {quiz_id} not found")
            raise ValueError(f"Quiz with ID {quiz_id} not found")

        quiz = self.quizzes[quiz_id]

        # Basic validation
        if len(answers) != len(quiz["questions"]):
            logger.error(f"Number of answers ({len(answers)}) does not match number of questions ({len(quiz['questions'])})")
            raise ValueError(f"Number of answers ({len(answers)}) does not match number of questions ({len(quiz['questions'])})")

        try:
            # Simple evaluation logic
            correct_answers = 0
            question_feedback = []

            for i, (question, answer) in enumerate(zip(quiz["questions"], answers)):
                is_correct = answer == question["correct_answer"]
                if is_correct:
                    correct_answers += 1

                feedback = question["explanation"] if is_correct else f"The correct answer is: {question['options'][question['correct_answer']]}. {question['explanation']}"
                question_feedback.append({
                    "question_index": i,
                    "correct": is_correct,
                    "feedback": feedback
                })

            total_questions = len(quiz["questions"])
            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

            # For more detailed feedback, use the LLM
            detailed_feedback = await self._generate_detailed_feedback(quiz, answers)

            # Combine basic and detailed feedback
            result = {
                "quiz_id": quiz_id,
                "user_id": user_id,
                "score": score,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "answers": answers,
                "feedback": detailed_feedback,
                "question_feedback": question_feedback,
                "completed_at": datetime.utcnow().isoformat()
            }

            # Store the result
            result_id = str(uuid.uuid4())
            self.quiz_results[result_id] = result

            logger.info(f"Evaluated quiz with score: {score:.1f}%")
            return result
        except Exception as e:
            logger.error(f"Error evaluating quiz: {str(e)}")
            # Return a simplified result if evaluation fails
            return {
                "quiz_id": quiz_id,
                "user_id": user_id,
                "score": 0,
                "correct_answers": 0,
                "total_questions": len(quiz["questions"]),
                "answers": answers,
                "feedback": {
                    "strengths": [],
                    "weaknesses": [f"Unable to evaluate quiz: {str(e)}"],
                    "suggestions": ["Try taking the quiz again"]
                },
                "completed_at": datetime.utcnow().isoformat()
            }

    async def _generate_detailed_feedback(
        self,
        quiz: Dict[str, Any],
        answers: List[int]
    ) -> Dict[str, Any]:
        """Generate detailed feedback for a quiz attempt.

        Args:
            quiz: The quiz data
            answers: The user's answers

        Returns:
            Dict containing detailed feedback
        """
        try:
            # Convert answers to a format that includes the selected option text
            formatted_answers = []
            for i, (question, answer_idx) in enumerate(zip(quiz["questions"], answers)):
                if 0 <= answer_idx < len(question["options"]):
                    selected_option = question["options"][answer_idx]
                    formatted_answers.append(f"Q{i+1}: {selected_option}")
                else:
                    formatted_answers.append(f"Q{i+1}: Invalid answer")

            # Get detailed feedback from the LLM
            response = await self.evaluate_chain.ainvoke({
                "quiz": quiz,
                "answers": formatted_answers
            })

            # Extract the JSON from the response
            import json
            import re

            # Try to find JSON in the response
            json_match = re.search(r'```json\n([\s\S]*?)\n```', response.content)
            if json_match:
                feedback_json = json.loads(json_match.group(1))
            else:
                # Try to find JSON without markdown code blocks
                try:
                    feedback_json = json.loads(response.content)
                except:
                    # If all else fails, extract just the feedback part
                    feedback_json = {
                        "strengths": ["You attempted the quiz"],
                        "weaknesses": ["Some areas need improvement"],
                        "suggestions": ["Review the topic and try again"]
                    }

            # Ensure the feedback has the expected structure
            if not isinstance(feedback_json, dict):
                feedback_json = {}

            feedback = {
                "strengths": feedback_json.get("strengths", []),
                "weaknesses": feedback_json.get("weaknesses", []),
                "suggestions": feedback_json.get("suggestions", [])
            }

            return feedback
        except Exception as e:
            logger.error(f"Error generating detailed feedback: {str(e)}")
            return {
                "strengths": ["You attempted the quiz"],
                "weaknesses": ["Some areas need improvement"],
                "suggestions": ["Review the topic and try again"]
            }

    def get_quiz(self, quiz_id: str) -> Dict[str, Any]:
        """Get a quiz by ID.

        Args:
            quiz_id: The ID of the quiz to retrieve

        Returns:
            Dict containing the quiz details
        """
        logger.info(f"Retrieving quiz with ID: {quiz_id}")

        if quiz_id not in self.quizzes:
            logger.error(f"Quiz with ID {quiz_id} not found")
            raise ValueError(f"Quiz with ID {quiz_id} not found")

        return self.quizzes[quiz_id]

    def get_all_quizzes(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all quizzes, optionally filtered by user ID.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of quizzes
        """
        if user_id:
            logger.info(f"Retrieving all quizzes for user: {user_id}")
            return [quiz for quiz in self.quizzes.values() if quiz.get("user_id") == user_id]
        else:
            logger.info("Retrieving all quizzes")
            return list(self.quizzes.values())

    def get_quizzes(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get quizzes, optionally filtered by topic, difficulty, and user_id.

        Args:
            topic: Optional topic to filter by
            difficulty: Optional difficulty level to filter by
            user_id: Optional user ID to filter by
            skip: Number of quizzes to skip
            limit: Maximum number of quizzes to return

        Returns:
            List of quizzes
        """
        logger.info(f"Getting quizzes with filters - topic: {topic}, difficulty: {difficulty}, user_id: {user_id}")

        filtered_quizzes = list(self.quizzes.values())

        if topic:
            filtered_quizzes = [
                q for q in filtered_quizzes
                if q.get("topic", "").lower() == topic.lower()
            ]

        if difficulty:
            filtered_quizzes = [
                q for q in filtered_quizzes
                if q.get("difficulty", "").lower() == difficulty.lower()
            ]

        if user_id:
            filtered_quizzes = [
                q for q in filtered_quizzes
                if q.get("user_id") == user_id
            ]

        # Sort by creation date if available
        filtered_quizzes.sort(
            key=lambda q: q.get("created_at", ""),
            reverse=True
        )

        # Apply pagination
        return filtered_quizzes[skip:skip + limit]

    def get_quiz_result(self, result_id: str) -> Dict[str, Any]:
        """Get a quiz result by ID.

        Args:
            result_id: The ID of the result to retrieve

        Returns:
            Dict containing the quiz result
        """
        logger.info(f"Retrieving quiz result with ID: {result_id}")

        if result_id not in self.quiz_results:
            logger.error(f"Quiz result with ID {result_id} not found")
            raise ValueError(f"Quiz result with ID {result_id} not found")

        return self.quiz_results[result_id]

    def get_user_quiz_results(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all quiz results for a user.

        Args:
            user_id: The user ID to get results for

        Returns:
            List of quiz results
        """
        logger.info(f"Retrieving all quiz results for user: {user_id}")
        return [result for result in self.quiz_results.values() if result.get("user_id") == user_id]

    def generate_quiz_from_learning_path(
        self,
        learning_path: Dict[str, Any],
        num_questions_per_topic: int = 2,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a quiz based on a learning path.

        Args:
            learning_path: The learning path to generate a quiz for
            num_questions_per_topic: Number of questions per topic
            difficulty: Optional difficulty override

        Returns:
            Dict containing the quiz details
        """
        logger.info(f"Generating quiz from learning path: {learning_path.get('title', 'Untitled')}")

        # Extract topics from the learning path
        topics = [topic.get("title") for topic in learning_path.get("topics", [])]

        if not topics:
            logger.error("No topics found in learning path")
            raise ValueError("No topics found in learning path")

        # Use the learning path difficulty if not specified
        if difficulty is None:
            difficulty = learning_path.get("difficulty", "beginner")

        # Create a combined quiz
        combined_quiz = {
            "title": f"Quiz on {learning_path.get('title', 'Learning Path')}",
            "description": f"A quiz covering the topics in the learning path: {learning_path.get('title', 'Learning Path')}",
            "topic": learning_path.get("title", "Learning Path"),
            "difficulty": difficulty,
            "questions": [],
            "estimated_time_minutes": 0,
            "learning_objectives": learning_path.get("learning_outcomes", []),
            "tags": [learning_path.get("title", "Learning Path"), difficulty]
        }

        # Generate questions for each topic
        for topic in topics:
            # Create a mini-quiz for this topic
            mini_quiz = {
                "title": f"Quiz on {topic}",
                "description": f"A quiz on {topic}",
                "topic": topic,
                "difficulty": difficulty,
                "questions": [
                    {
                        "question": f"What is {topic}?",
                        "options": [
                            f"A fundamental concept in {topic}",
                            f"An advanced technique in {topic}",
                            f"A historical figure related to {topic}",
                            f"None of the above"
                        ],
                        "correct_answer": 0,
                        "explanation": f"This is a basic definition question about {topic}.",
                        "question_type": "multiple_choice"
                    }
                ] * num_questions_per_topic,
                "estimated_time_minutes": 2 * num_questions_per_topic
            }

            # Add the questions to the combined quiz
            combined_quiz["questions"].extend(mini_quiz["questions"])
            combined_quiz["estimated_time_minutes"] += mini_quiz["estimated_time_minutes"]

        # Generate a unique ID for the quiz
        quiz_id = str(uuid.uuid4())

        # Add metadata
        combined_quiz["id"] = quiz_id
        combined_quiz["created_at"] = datetime.utcnow().isoformat()
        combined_quiz["user_id"] = learning_path.get("user_id")

        # Store the quiz
        self.quizzes[quiz_id] = combined_quiz

        logger.info(f"Generated quiz from learning path with ID: {quiz_id}")
        return combined_quiz
