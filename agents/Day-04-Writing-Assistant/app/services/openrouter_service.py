"""
OpenRouter service module for LLM integration.

This module provides a service for interacting with various LLMs through the OpenRouter API.
It handles the configuration, API communication, and prompt formatting for different writing tasks.
"""
import logging
from typing import Dict, List, Optional, Union

import sys
import os

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from openai import OpenAI
from pydantic import BaseModel

from app.core.config import settings

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
    
    async def _generate_completion(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
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
            
            # Make the API call
            completion = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
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
        max_length: int = 500, 
        model: Optional[str] = None
    ) -> str:
        """
        Generate a draft text based on the provided prompt.
        
        Args:
            prompt: The input prompt describing what to write
            max_length: Target length of the generated draft
            model: Optional specific model to use
            
        Returns:
            Generated draft text
        """
        system_prompt = """You are a skilled writing assistant. Create a well-structured, 
        coherent piece of text based on the user's prompt. The text should be clear, engaging, 
        and appropriate for the requested context and audience."""
        
        # Convert max_length to approximate token count (roughly 4 chars per token)
        max_tokens = max(100, int(max_length / 4))
        
        return await self._generate_completion(
            prompt=prompt,
            model=model,
            temperature=0.7,  # Moderate creativity
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
    
    async def analyze_grammar_style(
        self, 
        text: str, 
        check_grammar: bool = True,
        check_style: bool = True,
        check_spelling: bool = True,
        model: Optional[str] = None
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
        provided text for {checks_str} issues. Your response should be in JSON format with 
        an 'issues' array containing objects with 'type', 'description', 'suggestion', and 
        'severity' fields. Also include an 'improved_text' field with the corrected version."""
        
        prompt = f"Please analyze the following text for {checks_str} issues:\n\n{text}"
        
        # Use a lower temperature for more deterministic, analytical response
        result = await self._generate_completion(
            prompt=prompt,
            model=model,
            temperature=0.3,
            max_tokens=2000,  # Analysis may require more tokens
            system_prompt=system_prompt
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
        max_length: int = 200,
        format: str = "paragraph",
        focus: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Generate a summary of the provided text.
        
        Args:
            text: The text to summarize
            max_length: Maximum length of the summary in characters
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
        
        prompt = f"Please summarize the following text in approximately {max_length} characters:\n\n{text}"
        
        # Convert max_length to approximate token count (roughly 4 chars per token)
        max_tokens = max(50, int(max_length / 4))
        
        return await self._generate_completion(
            prompt=prompt,
            model=model,
            temperature=0.4,  # Lower temperature for more factual summary
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
    
    async def adjust_tone(
        self, 
        text: str, 
        target_tone: str,
        preserve_meaning: bool = True,
        strength: float = 0.7,
        model: Optional[str] = None
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
            temperature=0.6,
            max_tokens=int(len(text) / 2) + 200,  # Adjusted text might be longer
            system_prompt=system_prompt
        )
        
        return {
            "original_text": text,
            "adjusted_text": adjusted_text,
            "target_tone": target_tone,
            "model_used": model or self.default_model
        }


# Singleton instance for use throughout the application
openrouter_service = OpenRouterService()