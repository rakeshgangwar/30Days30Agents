"""
Agent Prompts Package

This package provides prompt templates for LLM agents with persona context.
"""

from app.core.agent.prompts.persona_prompts import get_persona_prompt, get_content_generation_prompt

__all__ = ["get_persona_prompt", "get_content_generation_prompt"]
