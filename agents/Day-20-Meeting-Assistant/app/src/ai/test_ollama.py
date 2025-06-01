"""
Tests for Ollama client and integration.

These tests verify the functionality of the Ollama client and its integration
with the LLMService.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.ai.ollama_client import OllamaClient, OllamaError
from src.ai.llm_service import LLMService, LLMResponse, LLMProvider

@pytest.fixture
def ollama_client():
    """Fixture providing an Ollama client instance"""
    return OllamaClient()

@pytest.fixture
def llm_service():
    """Fixture providing an LLMService instance with local LLM enabled"""
    return LLMService(use_local_llm=True)

@pytest.mark.asyncio
async def test_ollama_client_generate_completion(ollama_client):
    """Test generating a completion with Ollama"""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "response": "Test response",
            "done": True
        })
        mock_post.return_value = mock_response
        
        result = await ollama_client.generate_completion("Test prompt")
        
        assert "response" in result
        assert result["response"] == "Test response"

@pytest.mark.asyncio
async def test_ollama_client_health_check(ollama_client):
    """Test Ollama health check"""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        healthy = await ollama_client.health_check()
        assert healthy is True

@pytest.mark.asyncio
async def test_llm_service_ollama_fallback(llm_service):
    """Test LLMService using Ollama as primary with OpenRouter fallback"""
    with patch("src.ai.ollama_client.OllamaClient.generate_completion") as mock_ollama:
        # First try with Ollama
        mock_ollama.return_value = {"response": "Ollama response"}
        
        response = await llm_service._call_llm("Test prompt")
        
        assert response.provider == LLMProvider.OLLAMA
        assert response.content == "Ollama response"
        
        # Test fallback to OpenRouter when Ollama fails
        mock_ollama.side_effect = OllamaError("Test error")
        with patch("src.ai.openrouter_client.OpenRouterClient.generate_completion") as mock_openrouter:
            mock_openrouter.return_value = {
                "choices": [{"message": {"content": "OpenRouter response"}}]
            }
            
            response = await llm_service._call_llm("Test prompt")
            
            assert response.provider == LLMProvider.OPENROUTER
            assert response.content == "OpenRouter response"

@pytest.mark.asyncio
async def test_llm_service_ollama_health_check(llm_service):
    """Test LLMService health check with Ollama"""
    with patch("src.ai.ollama_client.OllamaClient.health_check") as mock_health:
        mock_health.return_value = True
        
        health_status = await llm_service.health_check()
        assert health_status["ollama"]["available"] is True
        assert health_status["ollama"]["healthy"] is True

@pytest.mark.asyncio
async def test_ollama_error_handling(ollama_client):
    """Test error handling in Ollama client"""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response
        
        with pytest.raises(OllamaError):
            await ollama_client.generate_completion("Test prompt")