"""
OpenRouter service module for LLM integration.

This module provides a service for interacting with various LLMs through the OpenRouter API.
It handles the configuration, API communication, and prompt formatting for different writing tasks.
"""
import logging
from typing import Dict, List, Optional, Union, Any

import sys
import os

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.preferences_service import preferences_service

logger = logging.getLogger(__name__)


class OpenRouterService:
    """Service for interacting with OpenRouter API."""

    def __init__(self):
        """Initialize the OpenRouter service with configuration from settings."""
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.default_model = settings.DEFAULT_LLM_MODEL

        # Default headers for site identification (optional for OpenRouter)
        self.headers = {
            "HTTP-Referer": "https://writing-assistant.app",  # Update with actual site URL
            "X-Title": "Writing Assistant",  # Update with actual site name
        }

    def _apply_user_preferences(
        self,
        db: Optional[Session],
        user_id: Optional[str],
        model: Optional[str],
        temperature: Optional[float]
    ) -> Dict[str, Any]:
        """
        Apply user preferences to the request parameters.

        Args:
            db: Database session (optional)
            user_id: User ID to load preferences for (optional)
            model: Model ID provided in the request (overrides preferences)
            temperature: Temperature provided in the request (overrides preferences)

        Returns:
            Dictionary with model and temperature parameters
        """
        params = {
            "model": model or self.default_model,
            "temperature": temperature or 0.7
        }

        # If no user ID or DB session, use provided params
        if not user_id or not db:
            return params

        # Load user preferences
        user_prefs = preferences_service.get_user_preferences(db, user_id)

        # Apply preferences if found (with request params taking precedence)
        if user_prefs:
            if not model and user_prefs.get("preferred_model"):
                params["model"] = user_prefs["preferred_model"]

            if not temperature and user_prefs.get("temperature"):
                params["temperature"] = user_prefs["temperature"]

        return params

    async def _generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        db: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate a completion using the OpenRouter API.

        Args:
            prompt: The user prompt text
            model: The model identifier to use (defaults to service default)
            temperature: Controls randomness (0-1, higher = more random)
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system prompt to set context

        Returns:
            Generated text response
        """
        try:
            messages = []

            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add user prompt
            messages.append({"role": "user", "content": prompt})

            # Apply user preferences
            params = self._apply_user_preferences(db, user_id, model, temperature)

            # Make the API call
            completion = self.client.chat.completions.create(
                model=params["model"],
                messages=messages,
                temperature=params["temperature"],
                max_tokens=max_tokens,
                extra_headers=self.headers,
            )

            # Extract and return the response text
            return completion.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in OpenRouter completion: {str(e)}")
            raise

    async def generate_draft(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        db: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate a draft text based on the provided prompt.

        Args:
            prompt: The input prompt describing what to write
            max_length: Optional target length of the generated draft (no limit if None)
            model: Optional specific model to use

        Returns:
            Generated draft text
        """
        system_prompt = """You are a skilled writing assistant. Create a well-structured,
        coherent piece of text based on the user's prompt. The text should be clear, engaging,
        and appropriate for the requested context and audience."""

        # Use a high token limit if max_length is None, otherwise convert to tokens
        max_tokens = 4000 if max_length is None else max(100, int(max_length / 4))

        return await self._generate_completion(
            prompt=prompt,
            model=model,
            temperature=temperature,  # Will use user preference if defined
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            db=db,
            user_id=user_id
        )

    async def analyze_grammar_style(
        self,
        text: str,
        check_grammar: bool = True,
        check_style: bool = True,
        check_spelling: bool = True,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        db: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Analyze text for grammar, style, and spelling issues.

        Args:
            text: The text to analyze
            check_grammar: Whether to check grammar
            check_style: Whether to check writing style
            check_spelling: Whether to check spelling
            model: Optional specific model to use

        Returns:
            Dictionary containing analysis results, issues found, and improved text
        """
        checks = []
        if check_grammar:
            checks.append("grammar")
        if check_style:
            checks.append("style")
        if check_spelling:
            checks.append("spelling")

        checks_str = ", ".join(checks)

        system_prompt = f"""You are a professional editor and writing coach. Analyze the
        provided text for {checks_str} issues.

        Your response MUST be in valid JSON format with the following structure:
        {{
            "issues": [
                {{
                    "type": "grammar|style|spelling",
                    "description": "Detailed description of the issue",
                    "suggestion": "Suggested correction",
                    "severity": "high|medium|low"
                }}
                // Additional issues...
            ],
            "improved_text": "The full corrected version of the text with all issues fixed"
        }}

        Be thorough in your analysis. If you find issues, make sure to include them in the issues array.
        The improved_text should be a corrected version of the original text with all issues fixed.
        If there are no issues, return an empty issues array and set improved_text to the original text.

        IMPORTANT: Your entire response must be valid JSON. Do not include any explanatory text outside the JSON structure."""

        prompt = f"Please analyze the following text for {checks_str} issues:\n\n{text}"

        # Use a lower temperature for more deterministic, analytical response
        result = await self._generate_completion(
            prompt=prompt,
            model=model,
            temperature=temperature or 0.3,
            max_tokens=4000,  # Increased token limit for comprehensive analysis
            system_prompt=system_prompt,
            db=db,
            user_id=user_id
        )

        # Note: In a production setting, we'd use a more robust approach to ensure
        # proper JSON parsing with error handling, but this is simplified for the MVP

        # For MVP, we're returning the raw response; in a production system
        # we would parse the returned JSON and return a properly structured dictionary
        return {
            "raw_analysis": result,
            "model_used": model or self.default_model
        }

    async def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        format: str = "paragraph",
        focus: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        db: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate a summary of the provided text.

        Args:
            text: The text to summarize
            max_length: Optional maximum length of the summary in characters (no limit if None)
            format: Format of the summary (paragraph, bullets)
            focus: Optional focus area for the summary
            model: Optional specific model to use

        Returns:
            Summarized text
        """
        focus_instruction = f" Focus on aspects related to {focus}." if focus else ""
        format_instruction = f" Format the summary as {format}."

        system_prompt = f"""You are a professional summarizer. Create a concise, accurate
        summary of the provided text.{focus_instruction}{format_instruction}"""

        # Adjust prompt based on whether max_length is specified
        length_instruction = f" in approximately {max_length} characters" if max_length else ""
        prompt = f"Please summarize the following text{length_instruction}:\n\n{text}"

        # Use a high token limit if max_length is None, otherwise convert to tokens
        max_tokens = 3000 if max_length is None else max(50, int(max_length / 4))

        return await self._generate_completion(
            prompt=prompt,
            model=model,
            temperature=temperature or 0.4,  # Lower temperature for more factual summary
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            db=db,
            user_id=user_id
        )

    async def adjust_tone(
        self,
        text: str,
        target_tone: str,
        preserve_meaning: bool = True,
        strength: float = 0.7,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        db: Optional[Session] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Adjust the tone of the provided text.

        Args:
            text: The text to adjust
            target_tone: Desired tone (e.g., professional, casual, friendly)
            preserve_meaning: Whether to prioritize preserving the original meaning
            strength: How strongly to adjust the tone (0.0-1.0)
            model: Optional specific model to use

        Returns:
            Dictionary with original text, adjusted text, and tone changes
        """
        preservation_str = "Carefully preserve the original meaning." if preserve_meaning else ""
        strength_str = f"Apply a {strength:.1f}/1.0 strength level for the tone adjustment."

        system_prompt = f"""You are a skilled writing assistant specializing in tone adjustment.
        Rewrite the provided text to match a {target_tone} tone. {preservation_str} {strength_str}
        Your response should maintain the core message while adjusting phrasings, word choice,
        sentence structure, and other elements to achieve the target tone."""

        prompt = f"Please adjust the following text to have a {target_tone} tone:\n\n{text}"

        adjusted_text = await self._generate_completion(
            prompt=prompt,
            model=model,
            temperature=temperature or 0.6,
            max_tokens=max(4000, int(len(text) / 2) + 500),  # Significantly increased token limit
            system_prompt=system_prompt,
            db=db,
            user_id=user_id
        )

        return {
            "original_text": text,
            "adjusted_text": adjusted_text,
            "target_tone": target_tone,
            "model_used": model or self.default_model
        }


# Singleton instance for use throughout the application
openrouter_service = OpenRouterService()