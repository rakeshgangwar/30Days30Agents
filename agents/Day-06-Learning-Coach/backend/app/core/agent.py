"""
Core agent implementation for the Learning Coach.
"""

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

            Format the learning path in a clear, structured way. Highlight the key topics, estimated time, and difficulty level.

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

            Format the resources in a clear, structured way. Include titles, descriptions, and links.

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

            Format the quiz in a clear, structured way. Include the title, description, and questions.
            Don't reveal the answers immediately - format it so the user can try to answer first.

            Your response:
            """,
            input_variables=["user_input", "quiz"]
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
        intent_result = await self.intent_recognizer.recognize_intent(state["user_input"])
        state["intent"] = intent_result
        return state

    def _route_by_intent(self, state: AgentState) -> str:
        """Route to the next node based on the recognized intent.

        Args:
            state: The current state

        Returns:
            Name of the next node
        """
        if not state["intent"]:
            return "default"

        intent = state["intent"].get("intent", "")

        if intent == "create_learning_path":
            return "create_learning_path"
        elif intent in ["discover_resources", "get_recommendations"]:
            return "discover_resources"
        elif intent == "generate_quiz":
            return "generate_quiz"
        else:
            return "default"

    async def _create_learning_path(self, state: AgentState) -> AgentState:
        """Create a learning path based on the user's request.

        Args:
            state: The current state

        Returns:
            Updated state with learning path
        """
        entities = state["intent"].get("entities", {})
        subject = entities.get("subject", "")
        if not subject:
            # Try to extract subject from user input
            subject = state["user_input"]

        goal = entities.get("goal", "learn the fundamentals")
        current_knowledge = entities.get("current_knowledge", "beginner")
        learning_style = entities.get("learning_style", "visual")
        time_commitment = entities.get("time_commitment", "5 hours per week")

        learning_path = await self.learning_path_manager.create_learning_path(
            subject=subject,
            goal=goal,
            current_knowledge=current_knowledge,
            learning_style=learning_style,
            time_commitment=time_commitment
        )

        state["learning_path"] = learning_path
        return state

    async def _discover_resources(self, state: AgentState) -> AgentState:
        """Discover learning resources based on the user's request.

        Args:
            state: The current state

        Returns:
            Updated state with resources
        """
        entities = state["intent"].get("entities", {})
        topic = entities.get("topic", "")
        if not topic:
            # Try to extract topic from user input
            topic = state["user_input"]

        difficulty = entities.get("difficulty", "beginner")
        resource_type = entities.get("resource_type", "any")
        learning_style = entities.get("learning_style", "visual")

        resources = await self.content_discovery.discover_resources(
            topic=topic,
            difficulty=difficulty,
            resource_type=resource_type,
            learning_style=learning_style
        )

        state["resources"] = resources
        return state

    async def _generate_quiz(self, state: AgentState) -> AgentState:
        """Generate a quiz based on the user's request.

        Args:
            state: The current state

        Returns:
            Updated state with quiz
        """
        entities = state["intent"].get("entities", {})
        topic = entities.get("topic", "")
        if not topic:
            # Try to extract topic from user input
            topic = state["user_input"]

        difficulty = entities.get("difficulty", "beginner")
        num_questions = entities.get("num_questions", 5)

        quiz = await self.quiz_generator.generate_quiz(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions
        )

        state["quiz"] = quiz
        return state

    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate a response based on the current state.

        Args:
            state: The current state

        Returns:
            Updated state with response
        """
        # Determine which template to use
        template_key = "general"

        if state.get("learning_path"):
            template_key = "learning_path"
        elif state.get("resources"):
            template_key = "resources"
        elif state.get("quiz"):
            template_key = "quiz"

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

        # Create and run the chain
        prompt = self.response_templates[template_key]
        chain = prompt | self.llm

        # Generate the response
        response = await chain.ainvoke(template_inputs)
        state["response"] = response.content

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

            # Return the response and context
            return {
                "response": final_state["response"] or "I'm not sure how to respond to that.",
                "context": final_state["context"],
            }
        except Exception as e:
            # Handle any errors
            import logging
            logging.error(f"Error processing input: {str(e)}")

            return {
                "response": f"I encountered an error while processing your request. Please try again with a different query.",
                "context": context,
            }
