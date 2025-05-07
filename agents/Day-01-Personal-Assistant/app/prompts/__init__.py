"""
Prompt templates for the Personal Assistant.

This package contains prompt templates used by the Personal Assistant agent,
including system prompts, classification prompts, and response formatting.
"""

from .base_prompts import (
    system_prompt,
    intent_classification_prompt,
    entity_extraction_prompt,
    weather_tool_prompt,
    reminder_tool_prompt,
    response_format_prompt,
    error_handling_prompt,
    clarification_prompt
)

__all__ = [
    'system_prompt',
    'intent_classification_prompt',
    'entity_extraction_prompt',
    'weather_tool_prompt',
    'reminder_tool_prompt',
    'response_format_prompt',
    'error_handling_prompt',
    'clarification_prompt'
]