#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Execution Planner Chain for the Personal Assistant.

This module implements a LangChain chain for planning the execution
steps based on the user's intent and extracted entities.
"""

import logging
import json
from typing import Dict, Any, List

from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

import sys
import os
# Add parent directory to path to import from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_NAME, TEMPERATURE, OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Execution planner prompt template
EXECUTION_PLANNER_TEMPLATE = """
Given the user's query, the classified intent, and extracted entities, determine the best execution plan.

USER QUERY: {query}
INTENT: {intent}
ENTITIES: {entities}

Create an execution plan that specifies:
1. The main tool(s) to use
2. The parameters to pass to each tool
3. Any fallback strategies if the primary tools fail

Available tools:
- weather_tool: For weather queries (params: location, units)
- forecast_tool: For weather forecasts (params: location, days, units)
- wikipedia_tool: For general knowledge queries (params: query, limit)
- news_tool: For recent news headlines (params: query, category, country, page_size)
- topic_news_tool: For topic-specific news (params: topic, days, page_size)
- todoist_create_task: For creating reminders/tasks (params: content, due_string, priority, description)
- todoist_list_tasks: For listing reminders/tasks (params: filter, limit)
- todoist_complete_task: For completing reminders/tasks (params: task_id)

Return the execution plan in JSON format with the following structure:
{
  "steps": [
    {
      "tool": "tool_name",
      "parameters": {
        "param1": "value1",
        "param2": "value2"
      },
      "fallback": "fallback_tool_name" (optional)
    }
  ],
  "missing_information": [] (list of any missing required information)
}

EXECUTION PLAN:
"""

class ExecutionPlannerChain(LLMChain):
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
        
        super().__init__(llm=llm, prompt=prompt, verbose=verbose)
    
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
            
            # Use invoke instead of run to avoid recursion
            inputs = {
                "query": query,
                "intent": intent,
                "entities": entities_str
            }
            result = self.invoke(inputs)
            
            # Get text output from result
            if isinstance(result, dict) and "text" in result:
                result_text = result["text"]
            else:
                result_text = str(result)
                
            try:
                # Clean up the result text to handle markdown code blocks
                cleaned_text = result_text
                if "```json" in result_text:
                    # Extract JSON from markdown code block
                    cleaned_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    # Extract from generic code block
                    cleaned_text = result_text.split("```")[1].split("```")[0].strip()
                
                # Ensure the JSON has the required structure
                if not cleaned_text.strip().startswith("{"):
                    cleaned_text = "{" + cleaned_text
                if not cleaned_text.strip().endswith("}"):
                    cleaned_text = cleaned_text + "}"
                
                plan = json.loads(cleaned_text)
                
                # Ensure the plan has the required keys
                if "steps" not in plan:
                    plan["steps"] = []
                if "missing_information" not in plan:
                    plan["missing_information"] = []
                logger.info(f"Generated execution plan with {len(plan.get('steps', []))} steps")
                return plan
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing execution plan result: {str(e)}")
                logger.error(f"Raw result: {result_text}")
                return {"steps": [], "missing_information": ["Failed to generate a valid execution plan"]}
            
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
        
        plan = self.plan_execution(query, intent, entities)
        
        return {
            "query": query,
            "intent": intent,
            "entities": entities,
            "execution_plan": plan
        }

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
            steps (List[Dict[str, Any]]): List of execution steps
        """
        self.steps = steps
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "steps": self.steps
        }