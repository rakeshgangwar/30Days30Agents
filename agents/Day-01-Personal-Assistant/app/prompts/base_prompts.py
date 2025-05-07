#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prompt templates for the Personal Assistant.

This module contains all the prompt templates used by the agent,
including the system prompt, classification prompts, and tool-specific prompts.
"""

from langchain.prompts import PromptTemplate

# System prompt template for the main agent
SYSTEM_PROMPT_TEMPLATE = """You are a helpful Personal Assistant that can answer questions, provide information, and help with simple tasks.

You have access to the following tools:
1. Weather API - For checking weather information
2. Wikipedia API - For retrieving general knowledge
3. News API - For getting recent news
4. Todoist API - For setting reminders and tasks

USER PREFERENCES:
{user_preferences}

RECENT CONVERSATION:
{chat_history}

CONVERSATION SUMMARY:
{conversation_summary}

Remember to be helpful, accurate, and friendly. If you don't know something or can't complete a task, be honest about your limitations.

Now, please respond to the user's request:
"""

# Intent classification prompt
INTENT_CLASSIFICATION_PROMPT = """Analyze the following user query and determine the primary intent. Choose ONE of the following intents that best matches:

- WEATHER: Requesting weather information
- REMINDER: Setting a reminder or task
- GENERAL_QUESTION: Asking a factual or knowledge question
- NEWS: Requesting news information
- PREFERENCE: Setting or changing user preferences
- GREETING: General greeting or chitchat
- UNKNOWN: Unable to determine intent

USER QUERY: {query}

INTENT:"""

# Entity extraction prompt
ENTITY_EXTRACTION_PROMPT = """Extract key entities from the following user query based on the determined intent.

USER QUERY: {query}
INTENT: {intent}

Extract the following entities as applicable for the intent:
- WEATHER: location, date, specific_info (temperature, forecast, etc.)
- REMINDER: task, time, date, priority
- GENERAL_QUESTION: topic, specific_question
- NEWS: topic, source, timeframe
- PREFERENCE: setting, value

Return the entities in JSON format. Include null for any entity that is not present in the query.

ENTITIES:"""

# Weather tool prompt
WEATHER_TOOL_PROMPT = """Generate a weather API request for the following query:

USER QUERY: {query}
LOCATION: {location}
DATE: {date}

Specify the exact parameters needed for the weather API call:"""

# Reminder creation prompt
REMINDER_TOOL_PROMPT = """Create a reminder based on the following information:

TASK: {task}
TIME: {time}
DATE: {date}
PRIORITY: {priority}

Format the reminder details for the Todoist API:"""

# Response formatting prompt
RESPONSE_FORMAT_PROMPT = """Generate a user-friendly response based on the following information:

USER QUERY: {query}
INTENT: {intent}
API_RESULT: {api_result}

Format your response in a natural, conversational way that addresses the user's query directly:"""

# Error handling prompt
ERROR_HANDLING_PROMPT = """The following API call has failed:

INTENT: {intent}
API: {api_name}
ERROR: {error_message}

Generate an appropriate error message for the user that explains the issue in a friendly way and offers alternative suggestions:"""

# Clarification request prompt
CLARIFICATION_PROMPT = """The user's query is missing some information:

USER QUERY: {query}
INTENT: {intent}
MISSING_INFO: {missing_info}

Generate a friendly request for clarification that specifies exactly what additional information is needed:"""

# Define the prompt templates
system_prompt = PromptTemplate(
    input_variables=["user_preferences", "chat_history", "conversation_summary"],
    template=SYSTEM_PROMPT_TEMPLATE
)

intent_classification_prompt = PromptTemplate(
    input_variables=["query"],
    template=INTENT_CLASSIFICATION_PROMPT
)

entity_extraction_prompt = PromptTemplate(
    input_variables=["query", "intent"],
    template=ENTITY_EXTRACTION_PROMPT
)

weather_tool_prompt = PromptTemplate(
    input_variables=["query", "location", "date"],
    template=WEATHER_TOOL_PROMPT
)

reminder_tool_prompt = PromptTemplate(
    input_variables=["task", "time", "date", "priority"],
    template=REMINDER_TOOL_PROMPT
)

response_format_prompt = PromptTemplate(
    input_variables=["query", "intent", "api_result"],
    template=RESPONSE_FORMAT_PROMPT
)

error_handling_prompt = PromptTemplate(
    input_variables=["intent", "api_name", "error_message"],
    template=ERROR_HANDLING_PROMPT
)

clarification_prompt = PromptTemplate(
    input_variables=["query", "intent", "missing_info"],
    template=CLARIFICATION_PROMPT
)