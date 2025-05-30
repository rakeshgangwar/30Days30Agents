#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Execution Planner Chain for the Personal Assistant.

This module implements a LangChain chain for planning the execution
steps based on the user's intent and extracted entities.
"""

import logging
import json
from typing import Dict, Any, List, Optional, ClassVar

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field

import sys
import os
# Add parent directory to path to import from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_NAME, TEMPERATURE, OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Pydantic models for structured output
class ToolParameters(BaseModel):
    """Parameters to pass to a tool."""
    # In Pydantic v2, we don't use __root__ anymore
    model_config = {"extra": "allow"}

    # We don't define specific fields, as they'll vary by tool
    # The BaseModel's extra="allow" config lets it accept any fields

    def dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class ExecutionStep(BaseModel):
    """A step in the execution plan."""
    tool: str = Field(..., description="The name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters to pass to the tool")
    fallback: Optional[str] = Field(None, description="Optional fallback tool if the primary tool fails")

class ExecutionPlan(BaseModel):
    """The execution plan with steps and missing information."""
    steps: List[ExecutionStep] = Field(default_factory=list, description="List of execution steps to perform")
    missing_information: List[str] = Field(default_factory=list, description="List of any missing required information")

# Execution planner prompt template
EXECUTION_PLANNER_TEMPLATE = """
Your task is to create an execution plan for the Personal Assistant based on the user's query.

USER QUERY: {query}
INTENT: {intent}
ENTITIES: {entities}

Create a structured execution plan that specifies exactly what tools to use and with what parameters.

Available tools:
- weather_tool: For weather queries (params: location, units)
- forecast_tool: For weather forecasts (params: location, days, units)
- wikipedia_tool: For general knowledge queries (params: query, limit)
- news_tool: For recent news headlines (params: query, category, country, page_size)
- topic_news_tool: For topic-specific news (params: topic, days, page_size)
- exa_search_tool: For searching the web for current information (params: query, num_results)
- exa_news_search_tool: For searching recent news articles (params: query, num_results)
- todoist_create_task: For creating reminders/tasks (params: content, due_string, priority, description)
- todoist_list_tasks: For listing reminders/tasks (params: filter, limit)
- todoist_complete_task: For completing reminders/tasks (params: task_id)

SPECIFIC INSTRUCTIONS FOR COMMON INTENTS:

For REMINDER intent:
- Use the todoist_create_task tool
- The "content" parameter should contain the main task description formatted as a proper sentence (capitalize first word)
- The "due_string" parameter should be formatted as a natural language date/time (e.g., "today at 7pm", "tomorrow at 3pm", "next monday at 9am")
- Priority can be set from 1-4 (4 is highest)
- Additional details can go in the "description" parameter

For WEATHER intent:
- Use the weather_tool for current weather
- Use the forecast_tool for multiple days forecast
- Always include the location parameter
- Units should be "metric" or "imperial" based on user preferences

For GENERAL_QUESTION intent:
- Use the wikipedia_tool with the main topic as the query parameter
- Limit results to 3 unless specified otherwise

For WEB_SEARCH intent:
- Use the exa_search_tool for general web searches
- Use the exa_news_search_tool for news-specific searches
- Set num_results to 5 unless specified otherwise
- If is_news_search is true, use exa_news_search_tool instead of exa_search_tool

EXAMPLES:

1. For a weather query:
```json
{
  "steps": [
    {
      "tool": "weather_tool",
      "parameters": {
        "location": "New York",
        "units": "metric"
      },
      "fallback": "wikipedia_tool"
    }
  ],
  "missing_information": []
}
```
2. For setting a reminder:
```json
{
  "steps": [
    {
      "tool": "todoist_create_task",
      "parameters": {
        "content": "Go for a run",
        "due_string": "today at 7pm",
        "priority": 2,
        "description": "30 minute jog in the park"
      }
    }
  ],
  "missing_information": []
}
```
3. For a web search query:
```json
{
  "steps": [
    {
      "tool": "exa_search_tool",
      "parameters": {
        "query": "latest developments in quantum computing",
        "num_results": 5
      }
    }
  ],
  "missing_information": []
}
```

4. For a news search query:
```json
{
  "steps": [
    {
      "tool": "exa_news_search_tool",
      "parameters": {
        "query": "latest news about climate change",
        "num_results": 5
      }
    }
  ],
  "missing_information": []
}
```

5. If information is missing:
```json
{
  "steps": [],
  "missing_information": ["Need specific time for the reminder"]
}
```
Remember to:

Always use the exact tool names as provided
Include all required parameters for each tool
Format dates and times properly for the todoist_create_task tool
Return an empty steps array and list missing information if you need more details
Now, create a structured execution plan for the given query:
"""

class ExecutionPlannerChain:
    """Chain for planning execution based on intent and entities."""

    def __init__(
    self,
    llm=None,
    prompt=None,
    verbose=False
    ):
        """
        Initialize the execution planner chain.

        Args:
            llm: The language model to use (default: OpenAI model from config)
            prompt: The prompt template to use
            verbose: Whether to log detailed output
        """
        if prompt is None:
            prompt = PromptTemplate(
                input_variables=["query", "intent", "entities"],
                template=EXECUTION_PLANNER_TEMPLATE
            )

        if llm is None:
            llm = ChatOpenAI(
                model_name=MODEL_NAME,
                temperature=0.2,  # Low temperature for structured output
                openai_api_key=OPENAI_API_KEY
            )

        # Create the LLMChain as an attribute
        self.chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)

        # Store the LLM for direct use
        self.llm = llm
        self.prompt = prompt
        self.verbose = verbose

    def _validate_execution_plan(self, execution_plan: Dict[str, Any], intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the execution plan and ensure it has the correct structure."""
        # Ensure the plan has the required keys
        if "steps" not in execution_plan:
            execution_plan["steps"] = []

        if "missing_information" not in execution_plan:
            execution_plan["missing_information"] = []

        return execution_plan

    def _convert_priority(self, priority) -> int:
        """Convert priority from various formats to integer (1-4)."""
        # If priority is already an integer, just return it (ensuring it's in the valid range)
        if isinstance(priority, int):
            return max(1, min(4, priority))  # Clamp between 1 and 4

        # Handle string priority formats like 'p1', 'P1', '1', etc.
        if isinstance(priority, str):
            # Remove any non-alphanumeric characters
            priority = ''.join(c for c in priority if c.isalnum())

            # Handle 'p1', 'P1' format (p1 = highest = 4, p4 = lowest = 1)
            if priority.lower().startswith('p') and len(priority) > 1:
                try:
                    # Extract the number part
                    num = int(priority[1:])
                    # Convert p1->4, p2->3, p3->2, p4->1
                    return max(1, min(4, 5 - num))
                except ValueError:
                    pass  # Fall through to default

            # Try to parse as a direct integer
            try:
                return max(1, min(4, int(priority)))
            except ValueError:
                pass  # Fall through to default

        # Default to medium priority (2) if conversion fails
        return 2

    def _format_reminder_task(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Format the task content for reminders to use proper title case."""
        steps = execution_plan.get("steps", [])

        for i, step in enumerate(steps):
            # Check if this is a todoist_create_task step
            if isinstance(step, dict) and step.get("tool") == "todoist_create_task":
                parameters = step.get("parameters", {})
                if "content" in parameters and parameters["content"]:
                    # Format the content in title case (capitalize each word)
                    parameters["content"] = parameters["content"].capitalize()
                    step["parameters"] = parameters
                    steps[i] = step
            # Handle Pydantic model format
            elif hasattr(step, "tool") and step.tool == "todoist_create_task":
                if hasattr(step, "parameters") and hasattr(step.parameters, "content") and step.parameters.content:
                    # Format the content in title case
                    if isinstance(step.parameters, dict):
                        if "content" in step.parameters:
                            step.parameters["content"] = step.parameters["content"].capitalize()
                    else:
                        step.parameters.content = step.parameters.content.capitalize()

        execution_plan["steps"] = steps
        return execution_plan

    def plan_execution(self, query: str, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan the execution steps based on intent and entities.

        Args:
            query (str): The user's query
            intent (str): The classified intent
            entities (Dict[str, Any]): The extracted entities

        Returns:
            Dict[str, Any]: Execution plan with steps and parameters
        """
        try:
            logger.info(f"Planning execution for query: {query}, intent: {intent}")

            # Special handling for GREETING intent
            if intent == "GREETING":
                # For greetings, we don't need a complex execution plan
                return {
                    "steps": [],
                    "missing_information": []
                }

            # Format entities as string for the prompt
            entities_str = json.dumps(entities, indent=2)

            try:
                # Create a hardcoded execution plan for REMINDER intent
                if intent == "REMINDER":
                    reminder_entities = entities.get("REMINDER", {})
                    task = reminder_entities.get("task")
                    time = reminder_entities.get("time")
                    date = reminder_entities.get("date")
                    raw_priority = reminder_entities.get("priority", 2)  # Default priority

                    # Convert priority from string format (p1, p2, etc.) to integer (1-4)
                    priority = self._convert_priority(raw_priority)

                    # Create a plan with todoist_create_task
                    plan_dict = {
                        "steps": [
                            {
                                "tool": "todoist_create_task",
                                "parameters": {
                                    "content": task.capitalize() if task else None,  # Apply sentence case formatting
                                    "due_string": f"{date} at {time}" if date and time else (date or time or "today"),
                                    "priority": priority,
                                    "description": ""
                                }
                            }
                        ],
                        "missing_information": []
                    }

                    # Check if we have the minimum required information
                    if not task:
                        plan_dict["steps"] = []
                        plan_dict["missing_information"] = ["Need task description for the reminder"]

                # Create a hardcoded execution plan for WEATHER intent
                elif intent == "WEATHER":
                    weather_entities = entities.get("WEATHER", {})
                    location = weather_entities.get("location")

                    # Create a plan with weather_tool
                    plan_dict = {
                        "steps": [
                            {
                                "tool": "weather_tool",
                                "parameters": {
                                    "location": location or "current location",
                                    "units": "metric"  # Default units
                                }
                            }
                        ],
                        "missing_information": []
                    }

                    # Check if we have the minimum required information
                    if not location:
                        plan_dict["missing_information"] = ["Need location for weather information"]

                # Create a hardcoded execution plan for GENERAL_QUESTION intent
                elif intent == "GENERAL_QUESTION":
                    question_entities = entities.get("GENERAL_QUESTION", {})
                    topic = question_entities.get("topic")

                    # Create a plan with wikipedia_tool
                    plan_dict = {
                        "steps": [
                            {
                                "tool": "wikipedia_tool",
                                "parameters": {
                                    "query": topic or query,
                                    "limit": 3
                                }
                            }
                        ],
                        "missing_information": []
                    }

                # Create a hardcoded execution plan for WEB_SEARCH intent
                elif intent == "WEB_SEARCH":
                    web_search_entities = entities.get("WEB_SEARCH", {})
                    search_query = web_search_entities.get("query", query)
                    num_results = web_search_entities.get("num_results")
                    # Ensure num_results is always an integer with a default value
                    if num_results is None or not isinstance(num_results, int):
                        num_results = 5
                    is_news_search = web_search_entities.get("is_news_search", False)

                    # Determine which tool to use based on whether it's a news search
                    tool_name = "exa_news_search_tool" if is_news_search else "exa_search_tool"

                    # Create a plan with the appropriate Exa search tool
                    plan_dict = {
                        "steps": [
                            {
                                "tool": tool_name,
                                "parameters": {
                                    "query": search_query,
                                    "num_results": num_results
                                }
                            }
                        ],
                        "missing_information": []
                    }

                # Create a hardcoded execution plan for NEWS intent
                elif intent == "NEWS":
                    news_entities = entities.get("NEWS", {})
                    topic = news_entities.get("topic")

                    # If it's a specific news topic, use the Exa news search tool
                    if topic:
                        plan_dict = {
                            "steps": [
                                {
                                    "tool": "exa_news_search_tool",
                                    "parameters": {
                                        "query": f"latest news about {topic}",
                                        "num_results": 5
                                    }
                                }
                            ],
                            "missing_information": []
                        }
                    else:
                        # Use the regular news tool for general news
                        plan_dict = {
                            "steps": [
                                {
                                    "tool": "news_tool",
                                    "parameters": {
                                        "category": "general",
                                        "country": "us",
                                        "page_size": 5
                                    }
                                }
                            ],
                            "missing_information": []
                        }

                # Default plan for other intents
                else:
                    # Format the prompt
                    formatted_prompt = self.prompt.format(
                        query=query,
                        intent=intent,
                        entities=entities_str
                    )

                    # Use the LLM directly
                    response = self.llm.invoke(formatted_prompt)

                    # Extract the content from the response
                    if hasattr(response, 'content'):
                        result_text = response.content
                    else:
                        result_text = str(response)

                    # Try to parse the JSON from the response
                    if "```json" in result_text:
                        # Extract JSON from markdown code block
                        json_text = result_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in result_text:
                        # Extract from generic code block
                        json_text = result_text.split("```")[1].split("```")[0].strip()
                    else:
                        json_text = result_text.strip()

                    # Parse the JSON
                    plan_dict = json.loads(json_text)

                # Process steps to ensure proper formatting
                steps = []
                for step in plan_dict.get("steps", []):
                    if isinstance(step, dict):
                        # Ensure step has the right structure
                        step_dict = {
                            "tool": step.get("tool", "wikipedia_tool"),
                            "parameters": step.get("parameters", {})
                        }
                        if step.get("fallback"):
                            step_dict["fallback"] = step["fallback"]
                        steps.append(step_dict)

                # Rebuild the plan with proper structure
                result_plan = {
                    "steps": steps,
                    "missing_information": plan_dict.get("missing_information", [])
                }

                logger.info(f"Generated execution plan with {len(steps)} steps")
                return result_plan

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON: {str(e)}")
                # Try to fix common JSON formatting issues
                try:
                    json_text = json_text.replace("'", "\"")
                    json_text = json_text.replace(",}", "}")
                    json_text = json_text.replace(",\n}", "\n}")
                    json_text = json_text.replace(",]", "]")
                    plan_dict = json.loads(json_text)
                except Exception as e:
                    logger.error(f"Error parsing JSON after cleanup: {str(e)}")
                    return {
                        "steps": [],
                        "missing_information": ["Failed to generate a valid execution plan. Please try rephrasing your request."]
                    }
            except Exception as e:
                logger.error(f"Error in execution planning: {str(e)}")
                return {
                    "steps": [],
                    "missing_information": ["Failed to generate a valid execution plan. Please try rephrasing your request."]
                }

        except Exception as e:
            logger.error(f"Error in execution planning: {str(e)}")
            return {"steps": [], "missing_information": [f"Error: {str(e)}"]}

    def __call__(self, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process inputs through the chain.

        Args:
            inputs (Dict[str, Any]): Input values with query, intent, and entities
            **kwargs: Additional keyword arguments like callbacks

        Returns:
            Dict[str, Any]: Output with execution plan
        """
        query = inputs.get("query", "")
        intent = inputs.get("intent", "UNKNOWN")
        entities = inputs.get("entities", {})

        # Execute the plan
        plan = self.plan_execution(query, intent, entities)

        result = {
            "query": query,
            "intent": intent,
            "entities": entities,
            "execution_plan": plan
        }

        # Log the result if verbose
        if self.verbose:
            logger.info(f"ExecutionPlannerChain output: {result}")

        return result

class DirectExecution:
    """Class for executing a single tool with specific parameters."""

    def __init__(self, tool_name: str, parameters: Dict[str, Any], fallback: str = None):
        """
        Initialize direct execution.

        Args:
            tool_name (str): The name of the tool to execute
            parameters (Dict[str, Any]): Parameters to pass to the tool
            fallback (str, optional): Fallback tool if the primary tool fails
        """
        self.tool_name = tool_name
        self.parameters = parameters
        self.fallback = fallback

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "tool": self.tool_name,
            "parameters": self.parameters
        }

        if self.fallback:
            result["fallback"] = self.fallback

        return result

class SequentialExecution:
    """Class for executing multiple tools in sequence."""

    def __init__(self, steps: List[Dict[str, Any]]):
        """
        Initialize sequential execution.

        Args:
            steps (List[Dict[str, Any]]): List of steps to execute
        """
        self.steps = steps

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "steps": self.steps
        }