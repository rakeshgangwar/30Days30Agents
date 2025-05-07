#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Day 1: Personal Assistant - Main Agent

This module implements the core agent functionality using LangChain,
integrating intent classification, entity extraction, memory management,
and tool orchestration.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional, Union
import copy

from langchain.agents import AgentExecutor, BaseSingleActionAgent
from langchain.memory import ConversationBufferMemory
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Import local modules
from config import MODEL_NAME, TEMPERATURE, OPENAI_API_KEY, SYSTEM_PROMPT
from memory import HierarchicalMemory
from langgraph_memory import LangGraphMemory
from chains.intent_classification import IntentClassificationChain
from chains.entity_extraction import EntityExtractionChain
from chains.execution_planner import ExecutionPlannerChain

# Import tools
from tools.weather_tool import WeatherTool, ForecastTool
from tools.wikipedia_tool import WikipediaTool
from tools.news_tool import NewsTool, TopicNewsTool
from tools.todoist_tool import TodoistCreateTool, TodoistListTool, TodoistCompleteTool
from tools.exa_search_tool import ExaSearchTool, ExaNewsSearchTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalAssistantAgent(BaseSingleActionAgent):
    """
    Personal Assistant Agent implementation using LangChain.

    This agent:
    1. Classifies the intent of user queries
    2. Extracts relevant entities
    3. Plans and executes appropriate actions
    4. Maintains conversation context
    5. Formats responses for the user
    """
    verbose: bool = False
    llm: Any = None
    memory: Any = None
    intent_chain: Any = None
    entity_chain: Any = None
    planner_chain: Any = None
    tools: Dict[str, BaseTool] = {}
    response_template: Any = None
    thread_id: str = "default"
    use_langgraph_memory: bool = True

    def __init__(
        self,
        memory=None,
        llm=None,
        verbose: bool = False,
        use_langgraph_memory: bool = True,
        thread_id: str = "default"
    ):
        """
        Initialize the Personal Assistant agent.

        Args:
            memory: Memory system (HierarchicalMemory or LangGraphMemory)
            llm: Language model for response generation
            verbose (bool): Whether to log detailed output
            use_langgraph_memory (bool): Whether to use LangGraph memory
            thread_id (str): Thread ID for LangGraph memory
        """
        super().__init__()
        self.verbose = verbose
        self.thread_id = thread_id
        self.use_langgraph_memory = use_langgraph_memory

        # Set up language model
        if llm is None:
            self.llm = ChatOpenAI(
                model_name=MODEL_NAME,
                temperature=TEMPERATURE,
                openai_api_key=OPENAI_API_KEY
            )
        else:
            self.llm = llm

        # Set up memory
        if memory is None:
            if use_langgraph_memory:
                self.memory = LangGraphMemory()
            else:
                self.memory = HierarchicalMemory()
        else:
            self.memory = memory

        # Set up component chains
        self.intent_chain = IntentClassificationChain(verbose=verbose)
        self.entity_chain = EntityExtractionChain(verbose=verbose)
        self.planner_chain = ExecutionPlannerChain(verbose=verbose)

        # Set up tools
        self.tools = {
            "weather_tool": WeatherTool(),
            "forecast_tool": ForecastTool(),
            "wikipedia_tool": WikipediaTool(),
            "news_tool": NewsTool(),
            "topic_news_tool": TopicNewsTool(),
            "todoist_create_task": TodoistCreateTool(),
            "todoist_list_tasks": TodoistListTool(),
            "todoist_complete_task": TodoistCompleteTool(),
            "exa_search_tool": ExaSearchTool(),
            "exa_news_search_tool": ExaNewsSearchTool()
        }

        # Set up response template
        self.response_template = PromptTemplate(
            input_variables=["query", "context", "result"],
            template="""
            Given the user query and the result of your actions, generate a helpful and friendly response.

            USER QUERY: {query}

            CONTEXT: {context}

            RESULT: {result}

            Please provide a natural-sounding response that addresses the user's query directly.
            Use conversational language but be concise and focused on answering what was asked.

            RESPONSE:
            """
        )

    @property
    def input_keys(self) -> List[str]:
        """Return the input keys required by the agent."""
        return ["input"]

    @property
    def return_values(self) -> List[str]:
        """Return the output keys produced by the agent."""
        return ["output"]

    def _detect_sensitive_info(self, text: str) -> bool:
        """
        Detect if the input contains sensitive information.

        This checks for common patterns of sensitive information like
        passwords, credit card numbers, SSNs, etc.

        Args:
            text (str): The text to check

        Returns:
            bool: True if sensitive information is detected
        """
        # Skip empty inputs
        if not text.strip():
            return False

        # Check for common sensitive information patterns
        sensitive_patterns = [
            "password is", "my password",
            "credit card", "card number",
            "social security", "ssn",
            "bank account", "account number",
            "address is", "home address",
            "phone number", "my phone",
            "secret", "confidential"
        ]

        text_lower = text.lower()
        for pattern in sensitive_patterns:
            if pattern in text_lower:
                return True

        # Check for credit card number pattern (4+ groups of 4 digits)
        import re
        cc_pattern = re.compile(r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}')
        if cc_pattern.search(text):
            return True

        # Check for SSN pattern (XXX-XX-XXXX)
        ssn_pattern = re.compile(r'\d{3}[- ]?\d{2}[- ]?\d{4}')
        if ssn_pattern.search(text):
            return True

        return False

    def _handle_sensitive_info(self, text: str) -> str:
        """
        Generate a response for input containing sensitive information.

        Args:
            text (str): The input with sensitive information

        Returns:
            str: A response about privacy and security
        """
        prompt = f"""
        The user has shared what appears to be sensitive information.

        Generate a friendly, helpful response that:
        1. Does NOT repeat any of the sensitive information
        2. Explains that you don't store or save sensitive information
        3. Advises on privacy and security best practices
        4. Offers to help with their task in a more secure way

        Generate a response:
        """

        response = self.llm.invoke(prompt)

        # Extract content from the message
        if hasattr(response, 'content'):
            return response.content.strip()
        else:
            return str(response).strip()

    def _redact_sensitive_info(self, text: str) -> str:
        """
        Redact sensitive information from text.

        Args:
            text (str): The text containing sensitive information

        Returns:
            str: The text with sensitive information redacted
        """
        # Replace credit card numbers
        import re
        text = re.sub(r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}', '[REDACTED CARD NUMBER]', text)

        # Replace SSNs
        text = re.sub(r'\d{3}[- ]?\d{2}[- ]?\d{4}', '[REDACTED SSN]', text)

        # Replace passwords
        text_lower = text.lower()
        if "password" in text_lower:
            # Find the password part and replace it
            password_idx = text_lower.find("password")
            if password_idx >= 0:
                # Look for the password value after "password is" or similar
                after_password = text[password_idx + 8:]  # 8 = len("password")
                # Find the first space or end of string
                space_idx = after_password.find(" ")
                if space_idx > 0:
                    # Replace the password value
                    text = text[:password_idx + 8] + " [REDACTED]" + after_password[space_idx:]
                else:
                    # No space found, replace the rest of the string
                    text = text[:password_idx + 8] + " [REDACTED]"

        return text

    def _detect_non_english(self, text: str) -> bool:
        """
        Detect if the input is likely not in English.

        This is a simple heuristic that checks for non-ASCII characters
        and common non-English patterns.

        Args:
            text (str): The text to check

        Returns:
            bool: True if the text is likely not in English
        """
        # Skip empty inputs
        if not text.strip():
            return False

        # Check for high percentage of non-ASCII characters
        non_ascii_count = sum(1 for char in text if ord(char) > 127)
        if non_ascii_count / len(text) > 0.3:  # If more than 30% non-ASCII
            return True

        # Check for common non-English characters/patterns
        non_english_markers = ['ñ', 'ç', 'ß', 'é', 'è', 'ê', 'à', 'ù', 'ü', 'ö', 'ä',
                              '¿', '¡', '€', '£', '¥', 'は', 'の', 'да', 'не']
        for marker in non_english_markers:
            if marker in text:
                return True

        return False

    def _handle_non_english(self, text: str) -> str:
        """
        Generate a response for non-English input.

        Args:
            text (str): The non-English input

        Returns:
            str: A response acknowledging the non-English input
        """
        prompt = f"""
        The user has sent a message that appears to be in a language other than English: "{text}"

        Please:
        1. Identify the likely language
        2. If you can understand it, briefly respond to their query
        3. Politely mention that English is preferred for best results

        Generate a friendly, helpful response:
        """

        response = self.llm.invoke(prompt)

        # Extract content from the message
        if hasattr(response, 'content'):
            return response.content.strip()
        else:
            return str(response).strip()

    def plan(
        self,
        intermediate_steps: List[tuple],
        **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        """
        Plan the next action based on the current state.

        Args:
            intermediate_steps: Steps taken so far
            **kwargs: Additional keyword arguments

        Returns:
            Union[AgentAction, AgentFinish]: Next action or final answer
        """
        user_input = kwargs["input"]

        # Check for empty input
        if not user_input.strip():
            response = "I need more information to help you. Could you please provide a specific query or request?"

            # Add the interaction to memory
            if self.use_langgraph_memory:
                self.memory.add_user_message(user_input, thread_id=self.thread_id)
                self.memory.add_ai_message(response, thread_id=self.thread_id)
            else:
                self.memory.add_user_message(user_input)
                self.memory.add_ai_message(response)

            return AgentFinish(
                return_values={"output": response},
                log="Handled empty input"
            )

        # Check for sensitive information
        if self._detect_sensitive_info(user_input):
            response = self._handle_sensitive_info(user_input)

            # Add the interaction to memory (with redacted input)
            redacted_input = self._redact_sensitive_info(user_input)
            if self.use_langgraph_memory:
                self.memory.add_user_message(redacted_input, thread_id=self.thread_id)
                self.memory.add_ai_message(response, thread_id=self.thread_id)
            else:
                self.memory.add_user_message(redacted_input)
                self.memory.add_ai_message(response)

            return AgentFinish(
                return_values={"output": response},
                log="Handled sensitive information"
            )

        # Check for non-English input
        if self._detect_non_english(user_input):
            response = self._handle_non_english(user_input)

            # Add the interaction to memory
            if self.use_langgraph_memory:
                self.memory.add_user_message(user_input, thread_id=self.thread_id)
                self.memory.add_ai_message(response, thread_id=self.thread_id)
            else:
                self.memory.add_user_message(user_input)
                self.memory.add_ai_message(response)

            return AgentFinish(
                return_values={"output": response},
                log="Handled non-English input"
            )

        # Add user input to memory
        if self.use_langgraph_memory:
            self.memory.add_user_message(user_input, thread_id=self.thread_id)
        else:
            self.memory.add_user_message(user_input)

        # Get conversation context
        if self.use_langgraph_memory:
            context = self.memory.get_relevant_context(user_input, thread_id=self.thread_id)
        else:
            context = self.memory.get_relevant_context(user_input)

        # Process the query through our chain components
        # 1. Classify intent
        intent_result = self.intent_chain({"query": user_input})
        intent = intent_result["intent"]

        # 2. Extract entities
        entity_result = self.entity_chain({
            "query": user_input,
            "intent": intent
        })
        entities = entity_result["entities"]

        # 3. Plan execution
        plan_result = self.planner_chain({
            "query": user_input,
            "intent": intent,
            "entities": entities
        })
        execution_plan = plan_result["execution_plan"]

        # Check if we're missing any required information
        missing_info = execution_plan.get("missing_information", [])
        if missing_info:
            # Ask for clarification and finish the agent execution
            clarification = self._generate_clarification(user_input, intent, missing_info)
            return AgentFinish(
                return_values={"output": clarification},
                log=f"Missing information: {missing_info}"
            )

        # Get the steps to execute
        steps = execution_plan.get("steps", [])

        # If we have previous steps, use their results for context
        context_dict = {}
        for step, result in intermediate_steps:
            # Handle both AgentAction objects and string tool names
            if hasattr(step, 'tool'):
                tool_name = step.tool
            else:
                # If step is a string, use it directly as the tool name
                tool_name = step
            context_dict[tool_name] = result

        # If we have steps to execute, take the next action
        if steps and len(intermediate_steps) < len(steps):
            # Get the next step
            next_step_index = len(intermediate_steps)
            next_step = steps[next_step_index]

            # Handle both dictionary format and Pydantic model format
            if hasattr(next_step, 'get'):
                # It's a dictionary
                tool_name = next_step.get("tool")
                tool_params = next_step.get("parameters", {})
            else:
                # It's a Pydantic model or other object
                tool_name = getattr(next_step, "tool", None)
                tool_params = getattr(next_step, "parameters", {})
                # Convert any Pydantic models to dictionaries
                if hasattr(tool_params, "dict") and callable(tool_params.dict):
                    tool_params = tool_params.dict()

            # Execute the tool
            return AgentAction(
                tool=tool_name,
                tool_input=tool_params,
                log=f"Executing {tool_name} with parameters {tool_params}"
            )

        # If we've executed all steps or there are no steps, generate a response
        result_dict = {}
        for step, result in intermediate_steps:
            # Handle both AgentAction objects and string tool names
            if hasattr(step, 'tool'):
                tool_name = step.tool
            else:
                # If step is a string, use it directly as the tool name
                tool_name = step
            result_dict[tool_name] = result

        # Generate the final response
        response = self._generate_response(user_input, context, result_dict)

        # Add AI response to memory
        if self.use_langgraph_memory:
            self.memory.add_ai_message(response, thread_id=self.thread_id)
        else:
            self.memory.add_ai_message(response)

        return AgentFinish(
            return_values={"output": response},
            log="Task complete, generated final response."
        )

    def _generate_clarification(
        self,
        query: str,
        intent: str,
        missing_info: List[str]
    ) -> str:
        """
        Generate a clarification request.

        Args:
            query (str): The original query
            intent (str): The classified intent
            missing_info (List[str]): The missing information

        Returns:
            str: A clarification request
        """
        # Create a prompt for clarification
        clarification_prompt = f"""
        The user has asked: "{query}"

        I need to get more information to help properly. Specifically, I need:
        {", ".join(missing_info)}

        Generate a friendly request for this information:
        """

        # Get clarification from LLM using invoke
        response = self.llm.invoke(clarification_prompt)

        # Extract content from the message
        if hasattr(response, 'content'):
            clarification = response.content.strip()
        else:
            clarification = str(response).strip()

        # Log the clarification
        logger.info(f"Generated clarification: {clarification}")

        return clarification

    def _generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        results: Dict[str, Any]
    ) -> str:
        """
        Generate a response based on the executed steps.

        Args:
            query (str): The original query
            context (Dict[str, Any]): The conversation context
            results (Dict[str, Any]): The results of executed tools

        Returns:
            str: A user-friendly response
        """
        # Convert context to string with custom serialization
        def make_json_serializable(obj):
            """Make an object JSON serializable by converting non-serializable objects to strings."""
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(i) for i in obj]
            else:
                return str(obj) if not isinstance(obj, (str, int, float, bool, type(None))) else obj

        # Create serializable copies
        serializable_context = make_json_serializable(copy.deepcopy(context))
        serializable_results = make_json_serializable(copy.deepcopy(results))

        # Convert to string
        context_str = json.dumps(serializable_context, indent=2)
        results_str = json.dumps(serializable_results, indent=2)

        # Format the prompt
        prompt_text = self.response_template.format(
            query=query,
            context=context_str,
            result=results_str
        )

        # Use invoke instead of direct call
        llm_response = self.llm.invoke(prompt_text)

        # Extract content from the message
        if hasattr(llm_response, 'content'):
            response = llm_response.content.strip()
        else:
            response = str(llm_response).strip()

        # Log the response
        logger.info(f"Generated response: {response}")

        return response

    async def aplan(
        self,
        intermediate_steps: List[tuple],
        **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        """
        Async version of plan method.

        Args:
            intermediate_steps: Steps taken so far
            **kwargs: Additional keyword arguments

        Returns:
            Union[AgentAction, AgentFinish]: Next action or final answer
        """
        # This is a placeholder - for actual async implementation,
        # we would use async versions of all the components
        return self.plan(intermediate_steps, **kwargs)


def create_agent(verbose=False, use_langgraph_memory=True, thread_id="default"):
    """
    Create and configure the Personal Assistant agent.

    Args:
        verbose (bool): Whether to log detailed output
        use_langgraph_memory (bool): Whether to use LangGraph memory
        thread_id (str): Thread ID for LangGraph memory

    Returns:
        AgentExecutor: Configured agent executor
    """
    # Initialize the agent
    agent = PersonalAssistantAgent(
        verbose=verbose,
        use_langgraph_memory=use_langgraph_memory,
        thread_id=thread_id
    )

    # Create an agent executor
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=list(agent.tools.values()),
        verbose=verbose,
        max_iterations=5  # Limit the number of steps to prevent infinite loops
    )

    return agent_executor


if __name__ == "__main__":
    agent_executor = create_agent(verbose=True)

    print("Welcome to the Personal Assistant!")
    print("I can help with weather, reminders, general knowledge, and more.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("> ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using the Personal Assistant. Goodbye!")
            break

        try:
            response = agent_executor.invoke({"input": user_input})["output"]
            print(f"\n{response}\n")
        except Exception as e:
            print(f"\nI'm sorry, I encountered an error: {str(e)}")
            print("Please try again with a different query.")