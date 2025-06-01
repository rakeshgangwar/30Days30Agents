# OpenRouter API Integration

This document describes the OpenRouter API integration implemented for Task T3.1, providing cloud-based LLM access for the Meeting Assistant application.

## Overview

The OpenRouter integration provides:
- **OpenRouter API client** with authentication and error handling
- **Model selection configuration** supporting multiple LLM providers
- **Rate limiting and retry logic** to handle API limits gracefully
- **Unified LLM service** for meeting summarization and action item extraction
- **REST API endpoints** for client applications

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   LLM Service   │    │ OpenRouter      │
│   Endpoints     │───▶│                 │───▶│ Client          │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Ollama        │    │ OpenRouter API  │
                       │   (Future)      │    │ (Cloud LLMs)    │
                       └─────────────────┘    └─────────────────┘
```

## Components

### 1. OpenRouter Client (`src/ai/openrouter_client.py`)

The core client for interacting with the OpenRouter API.

**Features:**
- Async/await support with context manager
- Multiple model support (Claude, GPT-4, Llama, etc.)
- Rate limiting with configurable limits
- Automatic retry logic with exponential backoff
- Comprehensive error handling
- Health check functionality

**Usage:**
```python
from src.ai.openrouter_client import OpenRouterClient

async with OpenRouterClient(api_key="your-key") as client:
    result = await client.generate_completion("Summarize this meeting...")
    print(result["choices"][0]["message"]["content"])
```

**Supported Models:**
- `anthropic/claude-3.5-sonnet` (default)
- `anthropic/claude-3-haiku`
- `openai/gpt-4-turbo`
- `openai/gpt-4o`
- `meta-llama/llama-3.1-70b-instruct`
- And more...

### 2. LLM Service (`src/ai/llm_service.py`)

Unified service providing high-level LLM operations for meeting processing.

**Features:**
- Meeting summarization (brief, detailed, executive)
- Action item extraction with structured output
- Fallback mechanism (OpenRouter → Ollama)
- Response parsing and validation
- Convenience functions for common operations

**Usage:**
```python
from src.ai.llm_service import LLMService, MeetingSummaryRequest

async with LLMService() as service:
    request = MeetingSummaryRequest(
        transcript="Meeting transcript...",
        summary_type="detailed"
    )
    response = await service.summarize_meeting(request)
    print(response.content)
```

### 3. API Endpoints (`src/api/llm_routes.py`)

REST API endpoints for client applications.

**Available Endpoints:**

#### POST `/api/llm/summarize`
Generate meeting summaries from transcript text.

**Request:**
```json
{
  "transcript": "Meeting transcript text...",
  "meeting_title": "Q4 Planning Meeting",
  "participants": ["John", "Sarah", "Mike"],
  "duration_minutes": 60,
  "summary_type": "detailed"
}
```

**Response:**
```json
{
  "content": "Generated summary...",
  "provider": "openrouter",
  "model": "anthropic/claude-3.5-sonnet",
  "tokens_used": 156,
  "processing_time": 2.3
}
```

#### POST `/api/llm/extract-action-items`
Extract action items from meeting transcripts.

**Request:**
```json
{
  "transcript": "Meeting transcript...",
  "participants": ["John", "Sarah"],
  "context": "Project planning meeting"
}
```

**Response:**
```json
{
  "action_items": [
    {
      "action": "Prepare budget analysis",
      "assignee": "John",
      "deadline": "Friday",
      "priority": "high"
    }
  ],
  "llm_response": {
    "content": "Raw LLM response...",
    "provider": "openrouter",
    "model": "anthropic/claude-3.5-sonnet",
    "tokens_used": 89,
    "processing_time": 1.8
  }
}
```

#### GET `/api/llm/health`
Check health of LLM providers.

#### GET `/api/llm/status`
Get service status and rate limit information.

#### POST `/api/llm/test`
Test LLM connection with a simple prompt.

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# LLM Preferences
USE_LOCAL_LLM=false
OLLAMA_MODEL=llama3.1:8b
```

### Settings

The integration uses the existing settings system:

```python
# config/settings.py
class Settings(BaseSettings):
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "anthropic/claude-3.5-sonnet"
    USE_LOCAL_LLM: bool = False
    # ... other settings
```

## Rate Limiting

The client implements intelligent rate limiting:

```python
@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    tokens_per_minute: int = 100000
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_multiplier: float = 2.0
```

**Features:**
- Automatic request queuing when limits are approached
- Exponential backoff for retries
- Rate limit status monitoring
- Configurable limits per instance

## Error Handling

Comprehensive error handling for various scenarios:

```python
class OpenRouterError(Exception): pass
class AuthenticationError(OpenRouterError): pass
class RateLimitError(OpenRouterError): pass
class ModelNotFoundError(OpenRouterError): pass
```

**Error Recovery:**
- Automatic retries for transient failures
- Graceful degradation when services unavailable
- Detailed error logging for debugging

## Testing

### Unit Tests

Run the test suite:
```bash
python -m pytest src/ai/test_openrouter.py -v
```

### Integration Tests

Test with real API (requires API key):
```bash
python -m pytest src/ai/test_openrouter.py --integration -v
```

### Demo Script

Test the complete integration:
```bash
python src/ai/demo_openrouter.py
```

## Usage Examples

### Basic Summarization

```python
from src.ai.llm_service import summarize_meeting_text

summary = await summarize_meeting_text(
    transcript="Meeting transcript...",
    summary_type="brief"
)
print(summary)
```

### Action Item Extraction

```python
from src.ai.llm_service import extract_meeting_action_items

action_items = await extract_meeting_action_items(
    transcript="Meeting transcript...",
    participants=["John", "Sarah"]
)

for item in action_items:
    print(f"- {item['action']} ({item['assignee']})")
```

### Custom LLM Service

```python
async with LLMService(
    use_local_llm=False,
    openrouter_model="openai/gpt-4o"
) as service:
    # Use service...
```

## Performance Considerations

### Optimization Strategies

1. **Chunking Large Transcripts**
   - Split long transcripts into manageable chunks
   - Process chunks in parallel when possible
   - Combine results intelligently

2. **Caching**
   - Cache summaries for identical transcripts
   - Store processed results in database
   - Use Redis for temporary caching

3. **Model Selection**
   - Use faster models for simple tasks
   - Reserve powerful models for complex analysis
   - Implement model switching based on content length

4. **Rate Limit Management**
   - Monitor usage patterns
   - Implement user-level rate limiting
   - Use queue systems for batch processing

### Expected Performance

| Operation | Typical Time | Tokens Used |
|-----------|-------------|-------------|
| Brief Summary (15min meeting) | 2-4 seconds | 100-300 |
| Detailed Summary (60min meeting) | 5-10 seconds | 300-800 |
| Action Items (30min meeting) | 3-6 seconds | 150-400 |

## Security

### API Key Management

- Store keys in environment variables
- Never commit keys to version control
- Use different keys for development/production
- Implement key rotation procedures

### Data Privacy

- Transcripts are sent to OpenRouter (cloud service)
- Consider data sensitivity when choosing providers
- Implement option for local-only processing (Ollama)
- Log access and processing for audit trails

## Monitoring

### Metrics to Track

- Request success/failure rates
- Response times by model and operation
- Token usage and costs
- Rate limit hit rates
- Error frequencies by type

### Health Checks

The service provides comprehensive health monitoring:

```python
# Check overall health
health = await service.health_check()

# Get detailed status
status = service.get_status()

# Monitor rate limits
limits = client.get_rate_limit_status()
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API key is correct
   - Check key has necessary permissions
   - Ensure key isn't expired

2. **Rate Limit Errors**
   - Monitor usage patterns
   - Implement request queuing
   - Consider upgrading API plan

3. **Model Not Found**
   - Verify model name is correct
   - Check model availability in your region
   - Try fallback models

4. **Timeout Errors**
   - Increase timeout settings
   - Check network connectivity
   - Retry with smaller requests

### Debug Mode

Enable detailed logging:
```python
import logging
logging.getLogger("src.ai").setLevel(logging.DEBUG)
```

## Future Enhancements

### Ollama Integration (T3.2)

The application now supports local LLM processing via Ollama as an alternative to cloud-based OpenRouter.

**Features:**
- Local LLM processing for privacy-sensitive use cases
- Automatic fallback when OpenRouter is unavailable
- Support for multiple local models (Llama 3, Mistral, Phi-3)
- Configurable via settings (USE_LOCAL_LLM and OLLAMA_MODEL)

**Usage:**
```python
# Use local LLM by default
settings.USE_LOCAL_LLM = True
settings.OLLAMA_MODEL = "llama3:8b"

async with LLMService() as service:
    # Will use Ollama instead of OpenRouter
    response = await service.summarize_meeting(request)
```

**Fallback Behavior:**
1. If USE_LOCAL_LLM is True:
   - Try Ollama first
   - Fall back to OpenRouter if Ollama fails
2. If USE_LOCAL_LLM is False:
   - Use OpenRouter exclusively

### Future Enhancements (T3.3)

1. **Advanced Prompting**
   - Meeting-type specific prompts
   - Context-aware summarization
   - Multi-turn conversations

3. **Batch Processing**
   - Multiple transcript processing
   - Parallel execution
   - Progress tracking

4. **Custom Models**
   - Fine-tuned models for meetings
   - Domain-specific optimizations
   - Performance improvements

## Conclusion

The OpenRouter integration provides a robust foundation for cloud-based LLM operations in the Meeting Assistant. It offers:

- ✅ Reliable API client with error handling
- ✅ Rate limiting and retry logic
- ✅ Multiple model support
- ✅ REST API endpoints
- ✅ Comprehensive testing
- ✅ Production-ready architecture

The implementation satisfies all requirements for Task T3.1 and provides a solid foundation for future LLM-related tasks.