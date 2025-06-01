"""
LLM Service for meeting processing.

This module provides a unified interface for LLM operations including
summarization, action item extraction, and other meeting-related AI tasks.
Supports both OpenRouter (cloud) and Ollama (local) backends.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
import json
from loguru import logger

from config.settings import settings
from .openrouter_client import OpenRouterClient, OpenRouterModel, OpenRouterError
from .ollama_client import OllamaClient, OllamaModel, OllamaError
from .prompt_templates import PromptTemplates, MeetingType


class LLMProvider(Enum):
    """Available LLM providers"""
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


@dataclass
class MeetingSummaryRequest:
    """Request for meeting summarization"""
    transcript: str
    meeting_title: Optional[str] = None
    participants: Optional[List[str]] = None
    duration_minutes: Optional[int] = None
    summary_type: str = "detailed"  # brief, detailed, executive
    meeting_type: MeetingType = MeetingType.GENERAL
    use_enhanced_prompts: bool = True


@dataclass
class ActionItemsRequest:
    """Request for action item extraction"""
    transcript: str
    participants: Optional[List[str]] = None
    context: Optional[str] = None
    meeting_type: MeetingType = MeetingType.GENERAL
    use_enhanced_prompts: bool = True


@dataclass
class LLMResponse:
    """Standard response from LLM operations"""
    content: str
    provider: LLMProvider
    model: str
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMService:
    """Unified service for LLM operations in meeting processing"""
    
    def __init__(
        self,
        use_local_llm: Optional[bool] = None,
        openrouter_api_key: Optional[str] = None,
        openrouter_model: Optional[str] = None,
        ollama_model: Optional[str] = None
    ):
        """
        Initialize the LLM service.
        
        Args:
            use_local_llm: Whether to prefer local LLM. If None, uses settings
            openrouter_api_key: OpenRouter API key. If None, uses settings
            openrouter_model: OpenRouter model to use. If None, uses settings
            ollama_model: Ollama model to use. If None, uses settings
        """
        self.use_local_llm = use_local_llm if use_local_llm is not None else settings.USE_LOCAL_LLM
        self.openrouter_api_key = openrouter_api_key or settings.OPENROUTER_API_KEY
        self.openrouter_model = openrouter_model or settings.OPENROUTER_MODEL
        self.ollama_model = ollama_model or settings.OLLAMA_MODEL
        
        # Initialize clients
        self.openrouter_client: Optional[OpenRouterClient] = None
        self.ollama_client: Optional[OllamaClient] = None
        
        self._initialize_clients()
        
        logger.info(f"LLM Service initialized - Local LLM: {self.use_local_llm}")
    
    def _initialize_clients(self):
        """Initialize LLM clients based on configuration"""
        # Initialize OpenRouter client
        if self.openrouter_api_key:
            try:
                self.openrouter_client = OpenRouterClient(
                    api_key=self.openrouter_api_key,
                    model=self.openrouter_model
                )
                logger.info("OpenRouter client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenRouter client: {e}")
                self.openrouter_client = None
        else:
            logger.warning("OpenRouter API key not provided - cloud LLM unavailable")
        
        # Initialize Ollama client if local LLM is preferred
        if self.use_local_llm:
            try:
                self.ollama_client = OllamaClient(model=self.ollama_model)
                logger.info("Ollama client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Ollama client: {e}")
                self.ollama_client = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def close(self):
        """Close all clients"""
        if self.openrouter_client:
            await self.openrouter_client.close()
    
    def _get_summarization_prompt(self, request: MeetingSummaryRequest) -> str:
        """Generate a prompt for meeting summarization"""
        if request.use_enhanced_prompts:
            return PromptTemplates.get_summarization_prompt(
                transcript=request.transcript,
                meeting_title=request.meeting_title,
                participants=request.participants,
                duration_minutes=request.duration_minutes,
                summary_type=request.summary_type,
                meeting_type=request.meeting_type
            )
        
        # Fallback to original simple prompt
        prompt_parts = []
        
        # Base instruction
        if request.summary_type == "brief":
            prompt_parts.append(
                "Create a brief summary (2-3 sentences) of the following meeting transcript. "
                "Focus on the key decisions and outcomes."
            )
        elif request.summary_type == "executive":
            prompt_parts.append(
                "Create an executive summary of the following meeting transcript. "
                "Include key decisions, strategic points, and business impact. "
                "Format for senior leadership consumption."
            )
        else:  # detailed
            prompt_parts.append(
                "Create a detailed summary of the following meeting transcript. "
                "Include key discussion points, decisions made, and important details."
            )
        
        # Add context if available
        if request.meeting_title:
            prompt_parts.append(f"\nMeeting Title: {request.meeting_title}")
        
        if request.participants:
            participants_str = ", ".join(request.participants)
            prompt_parts.append(f"Participants: {participants_str}")
        
        if request.duration_minutes:
            prompt_parts.append(f"Duration: {request.duration_minutes} minutes")
        
        # Add transcript
        prompt_parts.append(f"\nTranscript:\n{request.transcript}")
        
        # Add formatting instructions
        prompt_parts.append(
            "\nPlease provide a well-structured summary with clear sections. "
            "Use bullet points where appropriate."
        )
        
        return "\n".join(prompt_parts)
    
    def _get_action_items_prompt(self, request: ActionItemsRequest) -> str:
        """Generate a prompt for action item extraction"""
        if request.use_enhanced_prompts:
            return PromptTemplates.get_action_items_prompt(
                transcript=request.transcript,
                participants=request.participants,
                context=request.context,
                meeting_type=request.meeting_type
            )
        
        # Fallback to original simple prompt
        prompt_parts = [
            "Extract action items from the following meeting transcript. "
            "For each action item, identify:",
            "- The specific task or action",
            "- Who is responsible (if mentioned)",
            "- Any deadline or timeline (if mentioned)",
            "- Priority level (high, medium, low)",
            "",
            "Return the result as a JSON array of objects with the following structure:",
            '{"action": "description", "assignee": "name or null", "deadline": "date or null", "priority": "level"}',
        ]
        
        if request.participants:
            participants_str = ", ".join(request.participants)
            prompt_parts.append(f"\nKnown participants: {participants_str}")
        
        if request.context:
            prompt_parts.append(f"Context: {request.context}")
        
        prompt_parts.append(f"\nTranscript:\n{request.transcript}")
        
        return "\n".join(prompt_parts)
    
    async def _call_openrouter(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> LLMResponse:
        """Call OpenRouter API"""
        if not self.openrouter_client:
            raise ValueError("OpenRouter client not available")
        
        import time
        start_time = time.time()
        
        try:
            result = await self.openrouter_client.generate_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            processing_time = time.time() - start_time
            
            if "choices" not in result or not result["choices"]:
                raise ValueError("Invalid response from OpenRouter")
            
            content = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens")
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.OPENROUTER,
                model=self.openrouter_model,
                tokens_used=tokens_used,
                processing_time=processing_time,
                metadata={"raw_response": result}
            )
        
        except Exception as e:
            logger.error(f"OpenRouter API call failed: {e}")
            raise
    
    async def _call_ollama(self, prompt: str, **kwargs) -> LLMResponse:
        """Call Ollama API"""
        if not self.ollama_client:
            raise ValueError("Ollama client not available")
        
        import time
        start_time = time.time()
        
        try:
            result = await self.ollama_client.generate_completion(
                prompt=prompt,
                **kwargs
            )
            
            processing_time = time.time() - start_time
            
            if "response" not in result:
                raise ValueError("Invalid response from Ollama")
            
            return LLMResponse(
                content=result["response"],
                provider=LLMProvider.OLLAMA,
                model=self.ollama_model,
                processing_time=processing_time,
                metadata={"raw_response": result}
            )
            
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise
    
    async def _call_llm(self, prompt: str, **kwargs) -> LLMResponse:
        """Call the appropriate LLM based on configuration"""
        # Try local first if preferred
        if self.use_local_llm:
            try:
                return await self._call_ollama(prompt, **kwargs)
            except NotImplementedError:
                logger.warning("Ollama not available, falling back to OpenRouter")
            except Exception as e:
                logger.warning(f"Local LLM failed, falling back to OpenRouter: {e}")
        
        # Fall back to OpenRouter
        if self.openrouter_client:
            return await self._call_openrouter(prompt, **kwargs)
        
        raise ValueError("No LLM provider available")
    
    async def summarize_meeting(self, request: MeetingSummaryRequest) -> LLMResponse:
        """
        Generate a meeting summary.
        
        Args:
            request: Meeting summarization request
            
        Returns:
            LLM response with the summary
        """
        prompt = self._get_summarization_prompt(request)
        
        logger.info(f"Generating {request.summary_type} meeting summary")
        logger.debug(f"Transcript length: {len(request.transcript)} characters")
        
        # Adjust max_tokens based on summary type
        max_tokens = {
            "brief": 500,
            "detailed": 2000,
            "executive": 1000
        }.get(request.summary_type, 1000)
        
        return await self._call_llm(prompt, max_tokens=max_tokens, temperature=0.3)
    
    async def extract_action_items(self, request: ActionItemsRequest) -> LLMResponse:
        """
        Extract action items from meeting transcript.
        
        Args:
            request: Action items extraction request
            
        Returns:
            LLM response with action items in JSON format
        """
        prompt = self._get_action_items_prompt(request)
        
        logger.info("Extracting action items from meeting transcript")
        logger.debug(f"Transcript length: {len(request.transcript)} characters")
        
        return await self._call_llm(prompt, max_tokens=1500, temperature=0.1)
    
    def parse_action_items(self, llm_response: LLMResponse) -> List[Dict[str, Any]]:
        """
        Parse action items from LLM response with enhanced validation.
        
        Args:
            llm_response: Response from extract_action_items
            
        Returns:
            List of parsed action items
        """
        try:
            # Try to find JSON in the response
            content = llm_response.content.strip()
            
            # Look for JSON array in the response
            start_idx = content.find('[')
            end_idx = content.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx + 1]
                action_items = json.loads(json_str)
                
                # Validate structure with enhanced validation
                if isinstance(action_items, list):
                    validated_items = []
                    for item in action_items:
                        if isinstance(item, dict) and "action" in item:
                            validated_item = {
                                "action": item.get("action", "").strip(),
                                "assignee": item.get("assignee"),
                                "deadline": item.get("deadline"),
                                "priority": item.get("priority", "medium").lower(),
                                "category": item.get("category", "general")
                            }
                            
                            # Additional validation
                            if validated_item["action"]:  # Only include non-empty actions
                                # Ensure priority is valid
                                if validated_item["priority"] not in ["high", "medium", "low"]:
                                    validated_item["priority"] = "medium"
                                
                                validated_items.append(validated_item)
                    
                    logger.info(f"Parsed {len(validated_items)} action items")
                    return validated_items
            
            # If JSON parsing fails, try to extract manually
            logger.warning("JSON parsing failed, attempting manual extraction")
            return self._extract_action_items_manually(content)
        
        except Exception as e:
            logger.error(f"Failed to parse action items: {e}")
            return []
    
    def _extract_action_items_manually(self, content: str) -> List[Dict[str, Any]]:
        """Manually extract action items if JSON parsing fails"""
        # This is a simple fallback - could be improved with regex
        lines = content.split('\n')
        action_items = []
        
        for line in lines:
            line = line.strip()
            if line and ('action' in line.lower() or 'task' in line.lower()):
                action_items.append({
                    "action": line,
                    "assignee": None,
                    "deadline": None,
                    "priority": "medium"
                })
        
        return action_items
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all available LLM providers"""
        health_status = {
            "openrouter": {"available": False, "healthy": False},
            "ollama": {"available": False, "healthy": False}
        }
        
        # Check OpenRouter
        if self.openrouter_client:
            health_status["openrouter"]["available"] = True
            try:
                healthy = await self.openrouter_client.health_check()
                health_status["openrouter"]["healthy"] = healthy
            except Exception as e:
                logger.error(f"OpenRouter health check failed: {e}")
        
        # Check Ollama
        if self.ollama_client:
            health_status["ollama"]["available"] = True
            try:
                healthy = await self.ollama_client.health_check()
                health_status["ollama"]["healthy"] = healthy
            except Exception as e:
                logger.error(f"Ollama health check failed: {e}")
        
        return health_status
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        status = {
            "use_local_llm": self.use_local_llm,
            "openrouter_available": self.openrouter_client is not None,
            "ollama_available": self.ollama_client is not None,
            "default_model": self.openrouter_model if not self.use_local_llm else self.ollama_model
        }
        
        if self.openrouter_client:
            status["openrouter_rate_limits"] = self.openrouter_client.get_rate_limit_status()
        
        if self.ollama_client:
            status["ollama_model"] = self.ollama_model
        
        return status
    
    async def extract_topics(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Extract key topics and themes from meeting transcript.
        
        Args:
            transcript: Meeting transcript
            
        Returns:
            List of extracted topics with metadata
        """
        from .prompt_templates import PromptTemplates
        
        prompt = PromptTemplates.get_topic_extraction_prompt(transcript)
        
        logger.info("Extracting topics from meeting transcript")
        
        response = await self._call_llm(prompt, max_tokens=1500, temperature=0.2)
        
        try:
            # Parse JSON response
            content = response.content.strip()
            start_idx = content.find('[')
            end_idx = content.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx + 1]
                topics = json.loads(json_str)
                
                if isinstance(topics, list):
                    logger.info(f"Extracted {len(topics)} topics")
                    return topics
            
            logger.warning("Failed to parse topics JSON, returning empty list")
            return []
            
        except Exception as e:
            logger.error(f"Failed to extract topics: {e}")
            return []
    
    async def analyze_sentiment(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze the sentiment and emotional tone of a meeting.
        
        Args:
            transcript: Meeting transcript
            
        Returns:
            Dictionary with sentiment analysis results
        """
        from .prompt_templates import PromptTemplates
        
        prompt = PromptTemplates.get_sentiment_analysis_prompt(transcript)
        
        logger.info("Analyzing meeting sentiment")
        
        response = await self._call_llm(prompt, max_tokens=800, temperature=0.1)
        
        try:
            # Parse JSON response
            content = response.content.strip()
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx + 1]
                sentiment = json.loads(json_str)
                
                if isinstance(sentiment, dict):
                    logger.info("Sentiment analysis completed")
                    return sentiment
            
            logger.warning("Failed to parse sentiment JSON, returning default")
            return {
                "overall_sentiment": "neutral",
                "engagement_level": "medium",
                "conflict_indicators": False,
                "collaboration_quality": "fair",
                "energy_level": "medium",
                "concerns_raised": 0,
                "positive_moments": 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            return {
                "overall_sentiment": "neutral",
                "engagement_level": "medium",
                "conflict_indicators": False,
                "collaboration_quality": "fair",
                "energy_level": "medium",
                "concerns_raised": 0,
                "positive_moments": 0
            }
    
    async def comprehensive_analysis(
        self,
        transcript: str,
        meeting_title: Optional[str] = None,
        participants: Optional[List[str]] = None,
        duration_minutes: Optional[int] = None,
        meeting_type: MeetingType = MeetingType.GENERAL
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis including summary, action items, topics, and sentiment.
        
        Args:
            transcript: Meeting transcript
            meeting_title: Optional meeting title
            participants: Optional list of participants
            duration_minutes: Optional meeting duration
            meeting_type: Type of meeting
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        logger.info("Starting comprehensive meeting analysis")
        
        # Run all analyses in parallel for efficiency
        summary_request = MeetingSummaryRequest(
            transcript=transcript,
            meeting_title=meeting_title,
            participants=participants,
            duration_minutes=duration_minutes,
            summary_type="detailed",
            meeting_type=meeting_type
        )
        
        action_items_request = ActionItemsRequest(
            transcript=transcript,
            participants=participants,
            meeting_type=meeting_type
        )
        
        # Execute all tasks concurrently
        summary_task = self.summarize_meeting(summary_request)
        action_items_task = self.extract_action_items(action_items_request)
        topics_task = self.extract_topics(transcript)
        sentiment_task = self.analyze_sentiment(transcript)
        
        # Wait for all results
        summary_response = await summary_task
        action_items_response = await action_items_task
        topics = await topics_task
        sentiment = await sentiment_task
        
        # Parse action items
        action_items = self.parse_action_items(action_items_response)
        
        # Compile results
        analysis = {
            "summary": {
                "content": summary_response.content,
                "provider": summary_response.provider.value,
                "model": summary_response.model,
                "processing_time": summary_response.processing_time
            },
            "action_items": action_items,
            "topics": topics,
            "sentiment": sentiment,
            "metadata": {
                "meeting_title": meeting_title,
                "participants": participants,
                "duration_minutes": duration_minutes,
                "meeting_type": meeting_type.value,
                "analysis_timestamp": time.time(),
                "total_action_items": len(action_items),
                "total_topics": len(topics)
            }
        }
        
        logger.info(f"Comprehensive analysis completed: {len(action_items)} action items, {len(topics)} topics")
        return analysis


# Convenience functions for common operations
async def summarize_meeting_text(
    transcript: str,
    meeting_title: Optional[str] = None,
    summary_type: str = "detailed",
    **kwargs
) -> str:
    """
    Convenience function to summarize meeting text.
    
    Args:
        transcript: Meeting transcript text
        meeting_title: Optional meeting title
        summary_type: Type of summary (brief, detailed, executive)
        **kwargs: Additional arguments for LLMService
        
    Returns:
        Meeting summary text
    """
    async with LLMService(**kwargs) as llm_service:
        request = MeetingSummaryRequest(
            transcript=transcript,
            meeting_title=meeting_title,
            summary_type=summary_type
        )
        response = await llm_service.summarize_meeting(request)
        return response.content


async def extract_meeting_action_items(
    transcript: str,
    participants: Optional[List[str]] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Convenience function to extract action items from meeting text.
    
    Args:
        transcript: Meeting transcript text
        participants: Optional list of participant names
        **kwargs: Additional arguments for LLMService
        
    Returns:
        List of action items
    """
    async with LLMService(**kwargs) as llm_service:
        request = ActionItemsRequest(
            transcript=transcript,
            participants=participants
        )
        response = await llm_service.extract_action_items(request)
        return llm_service.parse_action_items(response)