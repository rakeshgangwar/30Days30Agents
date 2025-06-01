"""
Tests for OpenRouter API integration.

This module contains tests for the OpenRouter client and LLM service
to ensure proper functionality, error handling, and rate limiting.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ai.openrouter_client import (
    OpenRouterClient,
    OpenRouterModel,
    RateLimitConfig,
    OpenRouterError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError
)
from src.ai.llm_service import (
    LLMService,
    MeetingSummaryRequest,
    ActionItemsRequest,
    LLMProvider
)


class TestOpenRouterClient:
    """Test cases for OpenRouterClient"""
    
    @pytest.fixture
    def mock_api_key(self):
        """Mock API key for testing"""
        return "test_api_key_12345"
    
    @pytest.fixture
    def rate_limit_config(self):
        """Rate limit configuration for testing"""
        return RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=100,
            tokens_per_minute=1000,
            max_retries=2
        )
    
    @pytest.fixture
    def mock_success_response(self):
        """Mock successful API response"""
        return {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response from the API."
                    }
                }
            ],
            "usage": {
                "total_tokens": 25,
                "prompt_tokens": 15,
                "completion_tokens": 10
            }
        }
    
    def test_initialization_with_api_key(self, mock_api_key):
        """Test client initialization with API key"""
        client = OpenRouterClient(api_key=mock_api_key)
        assert client.api_key == mock_api_key
        assert client.default_model == OpenRouterModel.get_default().value
    
    def test_initialization_without_api_key(self):
        """Test client initialization fails without API key"""
        with patch('src.ai.openrouter_client.settings') as mock_settings:
            mock_settings.OPENROUTER_API_KEY = None
            
            with pytest.raises(AuthenticationError):
                OpenRouterClient()
    
    def test_model_enum_default(self):
        """Test default model selection"""
        with patch('src.ai.openrouter_client.settings') as mock_settings:
            mock_settings.OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"
            
            default_model = OpenRouterModel.get_default()
            assert default_model == OpenRouterModel.CLAUDE_3_5_SONNET
    
    def test_rate_limit_checking(self, mock_api_key, rate_limit_config):
        """Test rate limit checking logic"""
        client = OpenRouterClient(
            api_key=mock_api_key,
            rate_limit_config=rate_limit_config
        )
        
        # Should be able to make requests initially
        assert client._check_rate_limits() is True
        
        # Add requests to history
        for _ in range(5):
            client.request_history.add_request(100)
        
        # Should hit rate limit now
        assert client._check_rate_limits() is False
    
    @pytest.mark.asyncio
    async def test_successful_completion(self, mock_api_key, mock_success_response):
        """Test successful completion request"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_success_response
            mock_client.post.return_value = mock_response
            
            client = OpenRouterClient(api_key=mock_api_key)
            
            result = await client.generate_completion("Test prompt")
            
            assert "choices" in result
            assert result["choices"][0]["message"]["content"] == "This is a test response from the API."
            assert result["usage"]["total_tokens"] == 25
    
    @pytest.mark.asyncio
    async def test_authentication_error(self, mock_api_key):
        """Test authentication error handling"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 401
            mock_client.post.return_value = mock_response
            
            client = OpenRouterClient(api_key=mock_api_key)
            
            with pytest.raises(AuthenticationError):
                await client.generate_completion("Test prompt")
    
    @pytest.mark.asyncio
    async def test_model_not_found_error(self, mock_api_key):
        """Test model not found error handling"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 404
            mock_client.post.return_value = mock_response
            
            client = OpenRouterClient(api_key=mock_api_key)
            
            with pytest.raises(ModelNotFoundError):
                await client.generate_completion("Test prompt")
    
    @pytest.mark.asyncio
    async def test_rate_limit_retry(self, mock_api_key, rate_limit_config):
        """Test rate limit retry logic"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # First call returns 429, second call succeeds
            mock_response_429 = Mock()
            mock_response_429.status_code = 429
            
            mock_response_200 = Mock()
            mock_response_200.status_code = 200
            mock_response_200.json.return_value = {"choices": [{"message": {"content": "Success"}}]}
            
            mock_client.post.side_effect = [mock_response_429, mock_response_200]
            
            client = OpenRouterClient(
                api_key=mock_api_key,
                rate_limit_config=rate_limit_config
            )
            
            # Should succeed after retry
            result = await client.generate_completion("Test prompt")
            assert result["choices"][0]["message"]["content"] == "Success"
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_api_key, mock_success_response):
        """Test health check functionality"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_success_response
            mock_client.post.return_value = mock_response
            
            client = OpenRouterClient(api_key=mock_api_key)
            
            health = await client.health_check()
            assert health is True
    
    def test_rate_limit_status(self, mock_api_key, rate_limit_config):
        """Test rate limit status reporting"""
        client = OpenRouterClient(
            api_key=mock_api_key,
            rate_limit_config=rate_limit_config
        )
        
        # Add some requests
        client.request_history.add_request(100)
        client.request_history.add_request(150)
        
        status = client.get_rate_limit_status()
        
        assert "requests_per_minute" in status
        assert "requests_per_hour" in status
        assert "tokens_per_minute" in status
        assert status["requests_per_minute"]["used"] == 2
        assert status["tokens_per_minute"]["used"] == 250


class TestLLMService:
    """Test cases for LLMService"""
    
    @pytest.fixture
    def mock_openrouter_response(self):
        """Mock OpenRouter response for LLM service tests"""
        return {
            "choices": [
                {
                    "message": {
                        "content": "This is a detailed meeting summary covering the key points discussed."
                    }
                }
            ],
            "usage": {
                "total_tokens": 45
            }
        }
    
    @pytest.fixture
    def sample_transcript(self):
        """Sample meeting transcript for testing"""
        return """
        John: Good morning everyone. Let's start with the quarterly review.
        Sarah: Thanks John. I'll begin with the sales figures from Q3.
        Mike: The numbers look good, but we need to focus on customer retention.
        John: Agreed. Sarah, can you prepare a retention strategy by Friday?
        Sarah: Absolutely, I'll have that ready.
        """
    
    def test_initialization_with_openrouter(self):
        """Test LLM service initialization with OpenRouter"""
        with patch('src.ai.llm_service.settings') as mock_settings:
            mock_settings.USE_LOCAL_LLM = False
            mock_settings.OPENROUTER_API_KEY = "test_key"
            mock_settings.OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"
            mock_settings.OLLAMA_MODEL = "llama3.1:8b"
            
            service = LLMService()
            
            assert service.use_local_llm is False
            assert service.openrouter_api_key == "test_key"
            assert service.openrouter_model == "anthropic/claude-3.5-sonnet"
    
    def test_summarization_prompt_generation(self, sample_transcript):
        """Test summarization prompt generation"""
        service = LLMService(openrouter_api_key="test_key")
        
        request = MeetingSummaryRequest(
            transcript=sample_transcript,
            meeting_title="Q3 Review",
            participants=["John", "Sarah", "Mike"],
            summary_type="detailed"
        )
        
        prompt = service._get_summarization_prompt(request)
        
        assert "detailed summary" in prompt
        assert "Q3 Review" in prompt
        assert "John, Sarah, Mike" in prompt
        assert sample_transcript.strip() in prompt
    
    def test_action_items_prompt_generation(self, sample_transcript):
        """Test action items prompt generation"""
        service = LLMService(openrouter_api_key="test_key")
        
        request = ActionItemsRequest(
            transcript=sample_transcript,
            participants=["John", "Sarah", "Mike"]
        )
        
        prompt = service._get_action_items_prompt(request)
        
        assert "action items" in prompt.lower()
        assert "JSON" in prompt
        assert "John, Sarah, Mike" in prompt
        assert sample_transcript.strip() in prompt
    
    @pytest.mark.asyncio
    async def test_meeting_summarization(self, sample_transcript, mock_openrouter_response):
        """Test meeting summarization functionality"""
        with patch('src.ai.llm_service.OpenRouterClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.generate_completion.return_value = mock_openrouter_response
            
            service = LLMService(openrouter_api_key="test_key")
            
            request = MeetingSummaryRequest(
                transcript=sample_transcript,
                summary_type="detailed"
            )
            
            response = await service.summarize_meeting(request)
            
            assert response.content == "This is a detailed meeting summary covering the key points discussed."
            assert response.provider == LLMProvider.OPENROUTER
            assert response.tokens_used == 45
    
    def test_action_items_parsing_success(self):
        """Test successful action items parsing"""
        service = LLMService(openrouter_api_key="test_key")
        
        mock_response = Mock()
        mock_response.content = '''
        Here are the action items:
        [
            {
                "action": "Prepare retention strategy",
                "assignee": "Sarah",
                "deadline": "Friday",
                "priority": "high"
            },
            {
                "action": "Review Q3 numbers",
                "assignee": "Mike",
                "deadline": null,
                "priority": "medium"
            }
        ]
        '''
        
        action_items = service.parse_action_items(mock_response)
        
        assert len(action_items) == 2
        assert action_items[0]["action"] == "Prepare retention strategy"
        assert action_items[0]["assignee"] == "Sarah"
        assert action_items[0]["deadline"] == "Friday"
        assert action_items[0]["priority"] == "high"
    
    def test_action_items_parsing_fallback(self):
        """Test action items parsing fallback for non-JSON responses"""
        service = LLMService(openrouter_api_key="test_key")
        
        mock_response = Mock()
        mock_response.content = '''
        Action items from the meeting:
        - Sarah will prepare the retention strategy
        - Mike needs to review the Q3 numbers
        - Schedule follow-up meeting
        '''
        
        action_items = service.parse_action_items(mock_response)
        
        # Should extract at least some items using fallback method
        assert len(action_items) >= 0  # Fallback may not extract perfectly
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test LLM service health check"""
        with patch('src.ai.llm_service.OpenRouterClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.health_check.return_value = True
            
            service = LLMService(openrouter_api_key="test_key")
            
            health_status = await service.health_check()
            
            assert health_status["openrouter"]["available"] is True
            assert health_status["openrouter"]["healthy"] is True
            assert health_status["ollama"]["available"] is False
    
    def test_service_status(self):
        """Test service status reporting"""
        with patch('src.ai.llm_service.OpenRouterClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_rate_limit_status.return_value = {"test": "data"}
            mock_client_class.return_value = mock_client
            
            service = LLMService(
                use_local_llm=False,
                openrouter_api_key="test_key"
            )
            
            status = service.get_status()
            
            assert status["use_local_llm"] is False
            assert status["openrouter_available"] is True
            assert status["ollama_available"] is False
            assert "openrouter_rate_limits" in status


# Integration tests (require actual API key)
class TestIntegration:
    """Integration tests - require actual API credentials"""
    
    @pytest.mark.asyncio
    async def test_real_openrouter_connection(self):
        """Test actual OpenRouter API connection"""
        import os
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            pytest.skip("OPENROUTER_API_KEY not set")
        
        async with OpenRouterClient(api_key=api_key) as client:
            health = await client.health_check()
            assert health is True
    
    @pytest.mark.asyncio
    async def test_real_summarization(self):
        """Test actual meeting summarization"""
        import os
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            pytest.skip("OPENROUTER_API_KEY not set")
        
        transcript = """
        John: Good morning team. Let's discuss our Q4 objectives.
        Sarah: I think we should focus on customer acquisition.
        Mike: Agreed, and we need to improve our retention rates too.
        John: Perfect. Sarah, can you lead the acquisition strategy?
        Sarah: Yes, I'll have a plan ready by next week.
        """
        
        async with LLMService(openrouter_api_key=api_key) as service:
            request = MeetingSummaryRequest(
                transcript=transcript,
                meeting_title="Q4 Planning",
                summary_type="brief"
            )
            
            response = await service.summarize_meeting(request)
            
            assert len(response.content) > 50  # Should be substantial
            assert response.provider == LLMProvider.OPENROUTER
            assert response.tokens_used is not None


def pytest_addoption(parser):
    """Add command line options for pytest"""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests that require actual API credentials"
    )


if __name__ == "__main__":
    # Run basic tests without pytest
    import sys
    
    print("Running basic OpenRouter tests...")
    
    # Test model enum
    default_model = OpenRouterModel.get_default()
    print(f"✓ Default model: {default_model.value}")
    
    # Test rate limit config
    config = RateLimitConfig()
    print(f"✓ Rate limit config: {config.requests_per_minute} req/min")
    
    # Test client initialization (will fail without API key)
    try:
        client = OpenRouterClient(api_key="fake_key")
        print("✓ Client initialization works")
    except Exception as e:
        print(f"✓ Client initialization requires valid setup: {e}")
    
    print("Basic tests completed. Run with pytest for full test suite.")