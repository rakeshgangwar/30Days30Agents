#!/usr/bin/env python3
"""
Demo script for Ollama integration.

This script demonstrates the Ollama local LLM functionality and fallback mechanism.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ai.llm_service import LLMService, MeetingSummaryRequest


async def demo_ollama_integration():
    """Demo the Ollama integration with fallback to OpenRouter"""
    print("🦙 Ollama Integration Demo")
    print("=" * 50)
    
    # Test with local LLM preference
    print("\n1. Testing with local LLM preference (Ollama first)...")
    async with LLMService(use_local_llm=True) as service:
        status = service.get_status()
        print(f"   - Use Local LLM: {status['use_local_llm']}")
        print(f"   - OpenRouter Available: {status['openrouter_available']}")
        print(f"   - Ollama Available: {status['ollama_available']}")
        
        # Test health check
        print("\n2. Testing health checks...")
        health = await service.health_check()
        print(f"   - OpenRouter Health: {health['openrouter']}")
        print(f"   - Ollama Health: {health['ollama']}")
    
    # Test with cloud LLM preference
    print("\n3. Testing with cloud LLM preference (OpenRouter only)...")
    async with LLMService(use_local_llm=False) as service:
        status = service.get_status()
        print(f"   - Use Local LLM: {status['use_local_llm']}")
        print(f"   - Default Model: {status['default_model']}")
    
    print("\n✅ Demo completed successfully!")
    print("\nNote: To test actual LLM calls, ensure either:")
    print("  - Ollama is running locally (http://localhost:11434)")
    print("  - OpenRouter API key is configured in .env")


if __name__ == "__main__":
    asyncio.run(demo_ollama_integration())