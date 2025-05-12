"""
Core agent implementation for the Learning Coach.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, TypedDict, Union, Callable
from typing_extensions import Annotated

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from app.core.intent_recognition import IntentRecognizer
from app.core.learning_path_manager import LearningPathManager
from app.core.content_discovery import ContentDiscovery
from app.core.quiz_generator import QuizGenerator


# Define the state schema as a TypedDict
class AgentState(TypedDict):
    """State for the Learning Coach Agent."""
    user_input: str
    intent: Optional[Dict[str, Any]]
    context: Dict[str, Any]
    response: Optional[str]
    learning_path: Optional[Dict[str, Any]]
    resources: Optional[Dict[str, Any]]
    quiz: Optional[Dict[str, Any]]


class LearningCoachAgent:
    """Learning Coach Agent implementation using LangChain and LangGraph."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the Learning Coach Agent.

        Args:
            model_name: The name of the LLM model to use
        """
        # Get API key from environment
        import os
        import logging

        logger = logging.getLogger(__name__)
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")

        # Initialize components with explicit API key
        self.llm = ChatOpenAI(model=model_name, temperature=0.2, api_key=api_key)
        self.intent_recognizer = IntentRecognizer(model_name=model_name)
        self.learning_path_manager = LearningPathManager(model_name=model_name)
        self.content_discovery = ContentDiscovery(model_name=model_name)
        self.quiz_generator = QuizGenerator(model_name=model_name)

        # Build the state graph
        self.state_graph = self._build_state_graph()

        # Create response templates
        self.response_templates = self._create_response_templates()

    def _create_response_templates(self) -> Dict[str, PromptTemplate]:
        """Create response templates for different intents.

        Returns:
            Dict of response templates
        """
        templates = {}

        # General response template
        templates["general"] = PromptTemplate(
            template="""
            You are a helpful Learning Coach assistant. Respond to the user's message in a friendly and educational tone.

            User message: {user_input}

            Intent: {intent}

            Additional context: {context}

            Guidelines for your response:
            1. Be friendly, encouraging, and supportive
            2. Use clear, concise language
            3. Provide educational value in every response
            4. Tailor your response to the user's intent and needs
            5. If the user's intent is unclear, ask clarifying questions
            6. Suggest next steps or related topics when appropriate
            7. Use markdown formatting for better readability

            Your response:
            """,
            input_variables=["user_input", "intent", "context"]
        )

        # Learning path template
        templates["learning_path"] = PromptTemplate(
            template="""
            You are a helpful Learning Coach assistant. The user is interested in a learning path.

            User message: {user_input}

            Learning path details: {learning_path}

            Guidelines for your response:
            1. Format the learning path in a clear, structured way using markdown
            2. Start with an introduction explaining the learning path's purpose and benefits
            3. Highlight the key topics, estimated time, and difficulty level
            4. For each topic, include:
               - A brief description
               - Estimated time to complete
               - Prerequisites (if any)
               - Key concepts covered
            5. Mention the total estimated time to complete the entire path
            6. Suggest how the user might get started with the first topic
            7. Offer to generate a quiz or find resources for specific topics
            8. Be encouraging and motivational about the learning journey

            Your response:
            """,
            input_variables=["user_input", "learning_path"]
        )

        # Resources template
        templates["resources"] = PromptTemplate(
            template="""
            You are a helpful Learning Coach assistant. The user is looking for learning resources.

            User message: {user_input}

            Resources found: {resources}

            Guidelines for your response:
            1. Format the resources in a clear, structured way using markdown
            2. Start with a brief introduction about the topic and why these resources are valuable
            3. Group resources by type (articles, videos, courses, etc.) if there are many
            4. For each resource, include:
               - Title (as a markdown link to the URL)
               - Brief description of what the resource covers
               - Difficulty level
               - Estimated time to complete
               - Whether it's free or paid
            5. If a recommended sequence is provided, explain the suggested order for consuming these resources
            6. Suggest which resource might be best to start with based on the user's context
            7. Offer to generate a quiz on this topic to help reinforce learning
            8. Ask if the user would like resources on related topics

            Your response:
            """,
            input_variables=["user_input", "resources"]
        )

        # Quiz template
        templates["quiz"] = PromptTemplate(
            template="""
            You are a helpful Learning Coach assistant. The user wants a quiz.

            User message: {user_input}

            Quiz details: {quiz}

            Guidelines for your response:
            1. Format the quiz in a clear, structured way using markdown
            2. Start with an introduction explaining the quiz's purpose and topic
            3. Include the title, description, difficulty level, and estimated time
            4. Present each question with its multiple choice options
            5. Number the questions and options clearly
            6. Don't reveal the answers immediately - format it so the user can try to answer first
            7. After presenting all questions, include a section called "ANSWERS" with the correct answers and explanations
            8. Use spoiler formatting or suggest the user scroll down only when ready to see answers
            9. Encourage the user to attempt the quiz before looking at the answers
            10. Suggest related topics or resources for further learning

            Your response:
            """,
            input_variables=["user_input", "quiz"]
        )

        # Explanation template
        templates["explanation"] = PromptTemplate(
            template="""
            You are a helpful Learning Coach assistant. The user wants an explanation of a concept.

            User message: {user_input}

            Intent: {intent}

            Topic to explain: {topic}

            Additional context: {context}

            Guidelines for your response:
            1. Provide a clear, concise explanation of the topic using markdown formatting
            2. Start with a simple definition or overview
            3. Break down complex concepts into smaller, more digestible parts
            4. Use analogies or examples to illustrate the concept
            5. Explain why this concept is important or how it relates to other concepts
            6. Include any key formulas, principles, or rules if applicable
            7. Suggest resources for further learning on this topic
            8. Ask if the user would like more details or has follow-up questions
            9. Tailor the explanation to the user's apparent knowledge level

            Your response:
            """,
            input_variables=["user_input", "intent", "topic", "context"]
        )

        return templates

    def _build_state_graph(self) -> StateGraph:
        """Build the state graph for the agent workflow.

        Returns:
            StateGraph: The state graph for the agent workflow.
        """
        # Create the state graph with the TypedDict schema
        graph = StateGraph(AgentState)

        # Add nodes to the graph
        graph.add_node("recognize_intent", self._recognize_intent)
        graph.add_node("create_learning_path", self._create_learning_path)
        graph.add_node("discover_resources", self._discover_resources)
        graph.add_node("generate_quiz", self._generate_quiz)
        graph.add_node("generate_response", self._generate_response)

        # Define the entry point
        graph.set_entry_point("recognize_intent")

        # Define conditional edges
        graph.add_conditional_edges(
            "recognize_intent",
            self._route_by_intent,
            {
                "create_learning_path": "create_learning_path",
                "discover_resources": "discover_resources",
                "generate_quiz": "generate_quiz",
                "default": "generate_response"
            }
        )

        # Connect other nodes to response generation
        graph.add_edge("create_learning_path", "generate_response")
        graph.add_edge("discover_resources", "generate_response")
        graph.add_edge("generate_quiz", "generate_response")

        # Define the exit point
        graph.add_edge("generate_response", END)

        # Compile the graph
        return graph.compile()

    async def _recognize_intent(self, state: AgentState) -> AgentState:
        """Recognize the user's intent.

        Args:
            state: The current state

        Returns:
            Updated state with recognized intent
        """
        # Pass context to the intent recognizer for better intent recognition
        intent_result = await self.intent_recognizer.recognize_intent(
            state["user_input"],
            context=state["context"]
        )
        state["intent"] = intent_result

        # Log the recognized intent
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Recognized intent: {intent_result['intent']} with confidence: {intent_result['confidence']}")

        return state

    def _route_by_intent(self, state: AgentState) -> str:
        """Route to the next node based on the recognized intent.

        Args:
            state: The current state

        Returns:
            Name of the next node
        """
        import logging
        logger = logging.getLogger(__name__)

        if not state["intent"]:
            logger.warning("No intent recognized, using default route")
            return "default"

        intent = state["intent"].get("intent", "")
        confidence = state["intent"].get("confidence", 0.0)
        entities = state["intent"].get("entities", {})
        context = state["context"]

        # Log the routing decision
        logger.info(f"Routing based on intent: {intent} with confidence: {confidence}")

        # Route based on intent with confidence threshold
        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}) for intent: {intent}, using default route")
            return "default"

        # Check for multi-step queries in the user input
        user_input = state["user_input"].lower()
        has_learning_path_request = "learning path" in user_input or "path" in user_input
        has_quiz_request = "quiz" in user_input or "test" in user_input
        has_resources_request = "resources" in user_input or "materials" in user_input

        # Check if we have a learning path in context
        has_learning_path_in_context = "learning_path_id" in context

        # Handle multi-step queries
        if has_learning_path_request and has_quiz_request:
            if has_learning_path_in_context:
                # If we already have a learning path, prioritize the quiz generation
                logger.info("Multi-step query detected: Learning path exists, routing to generate_quiz")
                return "generate_quiz"
            else:
                # Otherwise, create the learning path first
                logger.info("Multi-step query detected: No learning path yet, routing to create_learning_path")
                # Store the fact that we need to generate a quiz after the learning path
                state["context"]["generate_quiz_after_path"] = True
                return "create_learning_path"

        # Check for update requests on existing learning paths
        if has_learning_path_in_context and ("update" in user_input or "modify" in user_input or
                                            "change" in user_input or "make it" in user_input):
            logger.info(f"Detected update request for existing learning path: {context.get('learning_path_id')}")
            return "create_learning_path"  # We use the same node for updates

        # Standard routing based on intent
        if intent == "create_learning_path" or intent == "update_learning_path":
            logger.info(f"Routing to create_learning_path for intent: {intent}")
            return "create_learning_path"
        elif intent in ["discover_resources", "get_recommendations"]:
            logger.info(f"Routing to discover_resources for intent: {intent}")
            return "discover_resources"
        elif intent == "generate_quiz" or intent == "check_progress":
            logger.info(f"Routing to generate_quiz for intent: {intent}")
            return "generate_quiz"
        elif intent == "explain_concept" or intent == "summarize_topic":
            # For now, we'll handle these with the default response generator
            # In a more complete implementation, we would have dedicated nodes for these
            logger.info(f"Routing to default for intent: {intent}")
            return "default"
        else:
            logger.info(f"Unknown intent: {intent}, using default route")
            return "default"

    async def _create_learning_path(self, state: AgentState) -> AgentState:
        """Create or update a learning path based on the user's request.

        Args:
            state: The current state

        Returns:
            Updated state with learning path
        """
        import logging
        logger = logging.getLogger(__name__)

        entities = state["intent"].get("entities", {})
        intent = state["intent"].get("intent", "")
        context = state["context"]
        user_input = state["user_input"].lower()

        # Check if this is an update request
        is_update = (intent == "update_learning_path" or
                    "update" in user_input or
                    "modify" in user_input or
                    "change" in user_input or
                    "make it" in user_input)

        # Check if we have an existing learning path to update
        existing_path_id = context.get("learning_path_id")

        if is_update and existing_path_id:
            logger.info(f"Updating existing learning path with ID: {existing_path_id}")

            # Extract update requirements
            update_requirements = state["user_input"]

            # Extract entities with defaults
            current_knowledge = entities.get("current_knowledge", "beginner")
            learning_style = entities.get("learning_style", "visual")
            time_commitment = entities.get("time_commitment", "5 hours per week")

            try:
                # Update the learning path
                learning_path = await self.learning_path_manager.update_learning_path(
                    path_id=existing_path_id,
                    update_requirements=update_requirements,
                    current_knowledge=current_knowledge,
                    learning_style=learning_style,
                    time_commitment=time_commitment
                )

                state["learning_path"] = learning_path
                logger.info(f"Updated learning path with ID: {learning_path.get('id', 'unknown')}")
                return state
            except Exception as e:
                logger.error(f"Error updating learning path: {str(e)}")
                # Fall back to creating a new learning path
                logger.info("Falling back to creating a new learning path")

        # If not updating or update failed, create a new learning path
        subject = entities.get("subject", "")
        if not subject:
            # Try to extract subject from user input
            subject = state["user_input"]
            logger.info(f"No subject found in entities, using user input: {subject}")

        # Extract entities with defaults
        goal = entities.get("goal", "learn the fundamentals")
        current_knowledge = entities.get("current_knowledge", "beginner")
        learning_style = entities.get("learning_style", "visual")
        time_commitment = entities.get("time_commitment", "5 hours per week")
        additional_requirements = entities.get("additional_requirements", "")

        # Get user ID from context if available
        user_id = context.get("user_id")

        logger.info(f"Creating learning path for subject: {subject}, goal: {goal}")

        # Create the learning path with additional parameters
        learning_path = await self.learning_path_manager.create_learning_path(
            subject=subject,
            goal=goal,
            current_knowledge=current_knowledge,
            learning_style=learning_style,
            time_commitment=time_commitment,
            additional_requirements=additional_requirements,
            user_id=user_id
        )

        state["learning_path"] = learning_path

        # Add the learning path ID to the context for future reference
        if "id" in learning_path:
            state["context"]["learning_path_id"] = learning_path["id"]

        # Save the learning path to the database
        try:
            from sqlalchemy.orm import Session
            from app.db.base import get_db
            from app.models.learning_path import LearningPath

            # Get a database session
            db = next(get_db())

            # Create a new learning path record
            db_learning_path = LearningPath(
                title=learning_path["title"],
                description=learning_path["description"],
                user_id=int(user_id) if user_id else None,
                topics=[
                    {"name": topic["title"], "order": i+1}
                    for i, topic in enumerate(learning_path["topics"])
                ],
                resources=[
                    {
                        "title": resource["title"],
                        "url": resource["url"],
                        "type": resource["type"],
                        "description": resource["description"],
                        "topic_order": i+1,  # Associate resource with its topic
                        "topic_id": i+1,     # Add topic_id for compatibility
                        "topic_name": topic["title"]  # Add topic name for better filtering
                    }
                    for i, topic in enumerate(learning_path["topics"])
                    for resource in topic.get("resources", [])
                ],
                progress={"completed_topics": 0, "total_topics": len(learning_path["topics"])}
            )

            # Add to database and commit
            db.add(db_learning_path)
            db.commit()
            db.refresh(db_learning_path)

            # Update the learning path ID in the context with the database ID
            state["context"]["learning_path_id"] = db_learning_path.id
            logger.info(f"Saved learning path to database with ID: {db_learning_path.id}")
        except Exception as e:
            logger.error(f"Error saving learning path to database: {str(e)}")
            # Continue with the in-memory learning path if database save fails

        logger.info(f"Created learning path with ID: {learning_path.get('id', 'unknown')}")
        return state

    async def _discover_resources(self, state: AgentState) -> AgentState:
        """Discover learning resources based on the user's request.

        Args:
            state: The current state

        Returns:
            Updated state with resources
        """
        import logging
        logger = logging.getLogger(__name__)

        entities = state["intent"].get("entities", {})
        topic = entities.get("topic", "")
        if not topic:
            # Try to extract topic from user input
            topic = state["user_input"]
            logger.info(f"No topic found in entities, using user input: {topic}")

        # Extract entities with defaults
        difficulty = entities.get("difficulty", "beginner")
        resource_type = entities.get("resource_type", "any")
        learning_style = entities.get("learning_style", "visual")
        additional_requirements = entities.get("additional_requirements", "")

        # Check if we should use cached results
        use_cache = state["context"].get("use_cache", True)

        logger.info(f"Discovering resources for topic: {topic}, difficulty: {difficulty}, resource_type: {resource_type}")

        # Discover resources with additional parameters
        resources = await self.content_discovery.discover_resources(
            topic=topic,
            difficulty=difficulty,
            resource_type=resource_type,
            learning_style=learning_style,
            additional_requirements=additional_requirements,
            use_cache=use_cache
        )

        state["resources"] = resources

        # Add the topic to the context for future reference
        state["context"]["last_topic"] = topic

        # If there's a learning path ID in the context, add these resources to it
        if "learning_path_id" in state["context"]:
            logger.info(f"Adding resources to learning path: {state['context']['learning_path_id']}")
            # This would be implemented in a real system to update the learning path with these resources

        # Save resources to the database
        try:
            from sqlalchemy.orm import Session
            from app.db.base import get_db
            from app.models.resource import Resource as ResourceModel
            from app.models.learning_path import LearningPath

            # Get user ID from context if available
            user_id = state["context"].get("user_id")

            # Get a database session
            db = next(get_db())

            # Save each resource
            saved_count = 0
            for resource in resources.get("resources", []):
                try:
                    # Create a new resource record
                    db_resource = ResourceModel(
                        id=resource.get("id", str(uuid.uuid4())),
                        title=resource["title"],
                        url=resource["url"],
                        type=resource.get("type", "article"),
                        description=resource.get("description", ""),
                        difficulty=resource.get("difficulty", "beginner"),
                        estimated_time=resource.get("estimated_time", "unknown"),
                        topics=resource.get("topics", [topic]),
                        source=resource.get("source", ""),
                        user_id=int(user_id) if user_id and user_id.isdigit() else None
                    )

                    # If we have a learning path ID in the context, associate this resource with it
                    if "learning_path_id" in state["context"] and "last_topic" in state["context"]:
                        # Get the learning path from the database
                        learning_path = db.query(LearningPath).filter(LearningPath.id == state["context"]["learning_path_id"]).first()
                        if learning_path:
                            # Find the topic order for the current topic
                            topic_order = None
                            for t in learning_path.topics:
                                if t.get("name") == state["context"]["last_topic"]:
                                    topic_order = t.get("order")
                                    break

                            # Add topic association to the resource
                            if topic_order:
                                db_resource.topic_order = topic_order
                                db_resource.topic_id = topic_order
                                db_resource.topic_name = state["context"]["last_topic"]

                    # Add to database and commit
                    db.add(db_resource)
                    db.commit()
                    db.refresh(db_resource)
                    saved_count += 1
                except Exception as resource_error:
                    logger.error(f"Error saving resource to database: {str(resource_error)}")
                    # Continue with the next resource
                    continue

            logger.info(f"Saved {saved_count} resources to database")
        except Exception as e:
            logger.error(f"Error saving resources to database: {str(e)}")
            # Continue with the in-memory resources if database save fails

        logger.info(f"Discovered {resources.get('total_count', 0)} resources for topic: {topic}")
        return state

    async def _generate_quiz(self, state: AgentState) -> AgentState:
        """Generate a quiz based on the user's request.

        Args:
            state: The current state

        Returns:
            Updated state with quiz
        """
        import logging
        logger = logging.getLogger(__name__)

        entities = state["intent"].get("entities", {})
        topic = entities.get("topic", "")

        # Check if we should generate a quiz from a learning path
        learning_path_id = state["context"].get("learning_path_id")

        # Check if the user explicitly mentioned the learning path
        user_input = state["user_input"].lower()
        mentions_learning_path = "learning path" in user_input or "path" in user_input

        # Generate quiz from learning path if:
        # 1. We have a learning path ID in context, and
        # 2. Either no topic is specified or the user explicitly mentioned the learning path
        if learning_path_id and (not topic or mentions_learning_path):
            logger.info(f"Generating quiz from learning path: {learning_path_id}")

            # In a real implementation, we would retrieve the learning path from the database
            # For now, we'll just use the learning path manager
            if hasattr(self.learning_path_manager, "get_learning_path"):
                try:
                    learning_path = self.learning_path_manager.get_learning_path(learning_path_id)

                    # Extract difficulty from entities or use the learning path difficulty
                    if "difficulty" in entities:
                        difficulty = entities.get("difficulty")
                    else:
                        difficulty = learning_path.get("difficulty", "beginner")

                    # Extract number of questions per topic
                    num_questions_per_topic = int(entities.get("num_questions", 2))

                    quiz = self.quiz_generator.generate_quiz_from_learning_path(
                        learning_path=learning_path,
                        num_questions_per_topic=num_questions_per_topic,
                        difficulty=difficulty
                    )
                    state["quiz"] = quiz
                    logger.info(f"Generated quiz from learning path with ID: {quiz.get('id', 'unknown')}")
                    return state
                except Exception as e:
                    logger.error(f"Error generating quiz from learning path: {str(e)}")
                    # Fall back to regular quiz generation

        if not topic:
            # Try to extract topic from user input or context
            topic = state["context"].get("last_topic", state["user_input"])
            logger.info(f"No topic found in entities, using: {topic}")

        # Extract entities with defaults
        difficulty = entities.get("difficulty", "beginner")
        num_questions = int(entities.get("num_questions", 5))
        question_types = entities.get("question_types", ["multiple_choice"])
        if isinstance(question_types, str):
            question_types = [question_types]

        # Get learning objectives if available
        learning_objectives = entities.get("learning_objectives", [f"Understand the basics of {topic}"])
        if isinstance(learning_objectives, str):
            learning_objectives = [learning_objectives]

        # Get user ID from context if available
        user_id = state["context"].get("user_id")

        logger.info(f"Generating quiz on topic: {topic}, difficulty: {difficulty}, num_questions: {num_questions}")

        # Generate the quiz with additional parameters
        quiz = await self.quiz_generator.generate_quiz(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            question_types=question_types,
            learning_objectives=learning_objectives,
            user_id=user_id
        )

        state["quiz"] = quiz

        # Add the quiz ID to the context for future reference
        if "id" in quiz:
            state["context"]["quiz_id"] = quiz["id"]
            logger.info(f"Added quiz ID to context: {quiz['id']}")
        else:
            logger.warning("Quiz does not have an ID!")

        # Log quiz details for debugging
        logger.info(f"Generated quiz with ID: {quiz.get('id', 'unknown')}")
        logger.info(f"Quiz title: {quiz.get('title', 'unknown')}")
        logger.info(f"Quiz topic: {quiz.get('topic', 'unknown')}")
        logger.info(f"Quiz has {len(quiz.get('questions', []))} questions")

        # Save the quiz to the database
        try:
            from sqlalchemy.orm import Session
            from app.db.base import get_db
            from app.models.quiz import Quiz as QuizModel

            # Get a database session
            db = next(get_db())

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

            # Update the quiz ID in the context with the database ID
            state["context"]["quiz_id"] = db_quiz.id
            logger.info(f"Saved quiz to database with ID: {db_quiz.id}")
        except Exception as e:
            logger.error(f"Error saving quiz to database: {str(e)}")
            # Continue with the in-memory quiz if database save fails

        return state

    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate a response based on the current state.

        Args:
            state: The current state

        Returns:
            Updated state with response
        """
        import logging
        logger = logging.getLogger(__name__)

        # Determine which template to use
        template_key = "general"

        # Check for specific content types in the state
        if state.get("learning_path"):
            template_key = "learning_path"
            logger.info("Using learning_path response template")
        elif state.get("resources"):
            template_key = "resources"
            logger.info("Using resources response template")
        elif state.get("quiz"):
            template_key = "quiz"
            logger.info("Using quiz response template")
        elif state["intent"].get("intent") in ["explain_concept", "summarize_topic"]:
            template_key = "explanation"
            logger.info("Using explanation response template")
        else:
            logger.info("Using general response template")

        # Prepare inputs for the template
        template_inputs = {
            "user_input": state["user_input"],
            "intent": state["intent"],
            "context": state["context"]
        }

        if state.get("learning_path"):
            template_inputs["learning_path"] = state["learning_path"]

        if state.get("resources"):
            template_inputs["resources"] = state["resources"]

        if state.get("quiz"):
            template_inputs["quiz"] = state["quiz"]

        if template_key == "explanation":
            # Extract the topic from entities or use the user input
            topic = state["intent"].get("entities", {}).get("topic", state["user_input"])
            template_inputs["topic"] = topic

        logger.info(f"Generating response using template: {template_key}")

        # Create and run the chain
        prompt = self.response_templates[template_key]
        chain = prompt | self.llm

        try:
            # Check if we need to generate a quiz after creating a learning path
            generate_quiz_after_path = state["context"].get("generate_quiz_after_path", False)

            if generate_quiz_after_path and template_key == "learning_path" and "learning_path_id" in state["context"]:
                logger.info("Detected generate_quiz_after_path flag, will generate quiz after learning path")

                # First, generate the learning path response
                response = await chain.ainvoke(template_inputs)
                learning_path_response = response.content

                # Now generate a quiz based on the learning path
                try:
                    # Get the learning path from the state
                    learning_path = state["learning_path"]

                    # Generate a quiz from the learning path
                    quiz = self.quiz_generator.generate_quiz_from_learning_path(
                        learning_path=learning_path,
                        num_questions_per_topic=2
                    )

                    # Store the quiz in the state
                    state["quiz"] = quiz

                    # Add the quiz ID to the context
                    if "id" in quiz:
                        state["context"]["quiz_id"] = quiz["id"]

                    # Save the quiz to the database
                    try:
                        from sqlalchemy.orm import Session
                        from app.db.base import get_db
                        from app.models.quiz import Quiz as QuizModel

                        # Get user ID from context if available
                        user_id = state["context"].get("user_id")

                        # Get a database session
                        db = next(get_db())

                        # Create a new quiz record
                        db_quiz = QuizModel(
                            id=quiz["id"],
                            title=quiz["title"],
                            description=quiz["description"],
                            topic=quiz["topic"],
                            difficulty=quiz.get("difficulty", "beginner"),
                            questions=quiz["questions"],
                            estimated_time_minutes=quiz.get("estimated_time_minutes", 10),
                            created_at=datetime.now(timezone.utc),
                            learning_objectives=quiz.get("learning_objectives", []),
                            tags=quiz.get("tags", []),
                            user_id=int(user_id) if user_id and user_id.isdigit() else None
                        )

                        # Add to database and commit
                        db.add(db_quiz)
                        db.commit()
                        db.refresh(db_quiz)

                        # Update the quiz ID in the context with the database ID
                        state["context"]["quiz_id"] = db_quiz.id
                        logger.info(f"Saved quiz from learning path to database with ID: {db_quiz.id}")
                    except Exception as e:
                        logger.error(f"Error saving quiz from learning path to database: {str(e)}")
                        # Continue with the in-memory quiz if database save fails

                    # Get the quiz template
                    quiz_template = self.response_templates["quiz"]
                    quiz_inputs = {
                        "user_input": "Generate a quiz based on the learning path",
                        "quiz": quiz,
                        "intent": state["intent"],
                        "context": state["context"]
                    }

                    # Generate the quiz response
                    quiz_response = await (quiz_template | self.llm).ainvoke(quiz_inputs)

                    # Combine the responses
                    state["response"] = f"{learning_path_response}\n\n---\n\n{quiz_response.content}"
                    state["response_type"] = "learning_path_with_quiz"

                    # Clear the flag
                    state["context"]["generate_quiz_after_path"] = False

                    logger.info("Successfully generated quiz after learning path")
                except Exception as e:
                    logger.error(f"Error generating quiz after learning path: {str(e)}")
                    # Just use the learning path response if quiz generation fails
                    state["response"] = learning_path_response
                    state["response_type"] = template_key
            else:
                # Normal response generation
                response = await chain.ainvoke(template_inputs)
                state["response"] = response.content
                state["response_type"] = template_key

            # Update the context with the last response type
            state["context"]["last_response_type"] = state["response_type"]

            logger.info(f"Generated response of type: {state['response_type']}")

            # Add message to conversation history
            if "conversation_history" not in state["context"]:
                state["context"]["conversation_history"] = []

            state["context"]["conversation_history"].append({
                "role": "user",
                "content": state["user_input"]
            })

            state["context"]["conversation_history"].append({
                "role": "assistant",
                "content": state["response"],
                "response_type": state["response_type"]
            })

            # Trim conversation history if it gets too long
            if len(state["context"]["conversation_history"]) > 20:
                state["context"]["conversation_history"] = state["context"]["conversation_history"][-20:]

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            state["response"] = f"I'm sorry, I encountered an error while generating a response. Please try again or rephrase your question."
            state["response_type"] = "error"

        return state

    async def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input and generate a response.

        Args:
            user_input: The user's input text
            context: Optional context information

        Returns:
            Dict containing the agent's response and any additional information
        """
        # Initialize context if not provided
        if context is None:
            context = {}

        # Create initial state
        initial_state: AgentState = {
            "user_input": user_input,
            "intent": None,
            "context": context,
            "response": None,
            "learning_path": None,
            "resources": None,
            "quiz": None
        }

        # Run the state graph with the initial state
        try:
            final_state = await self.state_graph.ainvoke(initial_state)

            # Return the response, response type, and context
            return {
                "response": final_state["response"] or "I'm not sure how to respond to that.",
                "response_type": final_state.get("response_type", "general"),
                "context": final_state["context"],
            }
        except Exception as e:
            # Handle any errors
            import logging
            logging.error(f"Error processing input: {str(e)}")

            return {
                "response": f"I encountered an error while processing your request. Please try again with a different query.",
                "response_type": "error",
                "context": context,
            }
