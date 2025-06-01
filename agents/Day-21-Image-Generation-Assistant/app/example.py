#!/usr/bin/env python3
"""
Example usage of the Image Generation Assistant.

This script demonstrates how to use the assistant programmatically
for generating images, enhancing prompts, and managing history.
"""

import asyncio
from pathlib import Path

# Import the agent functions
from agent import run_image_assistant_sync, run_image_assistant


def basic_usage():
    """Demonstrate basic synchronous usage."""
    print("🎨 Image Generation Assistant - Basic Usage Example")
    print("=" * 60)
    
    # Example 1: Generate an image
    print("\n1. Generating an image...")
    response = run_image_assistant_sync(
        "Generate a peaceful mountain landscape at sunset in watercolor style"
    )
    
    print(f"Success: {response.success}")
    print(f"Message: {response.message}")
    
    if response.images:
        print(f"Generated {len(response.images)} image(s):")
        for img_path in response.images:
            print(f"  - {img_path}")
    
    if response.suggestions:
        print("Suggestions:")
        for suggestion in response.suggestions:
            print(f"  • {suggestion}")
    
    print("\n" + "-" * 60)
    
    # Example 2: Enhance a prompt
    print("\n2. Enhancing a prompt...")
    response = run_image_assistant_sync(
        "Enhance this prompt: 'dragon flying' with cyberpunk style"
    )
    
    print(f"Message: {response.message}")
    
    # Example 3: View history
    print("\n3. Viewing generation history...")
    response = run_image_assistant_sync("Show my last 3 generations")
    print(f"Message: {response.message}")


async def advanced_usage():
    """Demonstrate advanced asynchronous usage."""
    print("\n🚀 Advanced Async Usage Example")
    print("=" * 60)
    
    # Multiple concurrent operations
    tasks = []
    
    # Task 1: Generate multiple images with different styles
    prompts = [
        "Generate a futuristic city with photorealistic style",
        "Generate a magical forest with fantasy style", 
        "Generate a vintage car with oil_painting style"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{i}. Starting: {prompt}")
        task = run_image_assistant(prompt)
        tasks.append(task)
    
    # Wait for all tasks to complete
    print("\nWaiting for all generations to complete...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        if isinstance(result, Exception):
            print(f"  Error: {result}")
        else:
            print(f"  Success: {result.success}")
            print(f"  Message: {result.message[:100]}...")
            if result.images:
                print(f"  Images: {len(result.images)}")


def interactive_example():
    """Demonstrate interactive usage patterns."""
    print("\n💬 Interactive Usage Patterns")
    print("=" * 60)
    
    # Simulate a conversation flow
    conversation = [
        "Generate a serene lake at dawn",
        "Make it more artistic and add some mist",
        "Show me my recent images",
        "Enhance this prompt: 'cat in space' with cartoon style"
    ]
    
    for i, user_input in enumerate(conversation, 1):
        print(f"\n{i}. User: {user_input}")
        
        response = run_image_assistant_sync(user_input)
        
        print(f"   Assistant: {response.message[:100]}...")
        if response.images:
            print(f"   Generated: {len(response.images)} image(s)")
        
        if response.suggestions:
            print(f"   Suggestions: {len(response.suggestions)} available")


def error_handling_example():
    """Demonstrate error handling and recovery."""
    print("\n⚠️  Error Handling Example")
    print("=" * 60)
    
    # Test various error conditions
    test_cases = [
        "Generate an image without any prompt",  # Should handle gracefully
        "Upscale a non-existent image at /fake/path.jpg",  # File not found
        "Generate 100 images at once",  # Parameter validation
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case}")
        
        try:
            response = run_image_assistant_sync(test_case)
            print(f"   Success: {response.success}")
            print(f"   Message: {response.message[:100]}...")
            
            if response.suggestions:
                print(f"   Suggestions provided: {len(response.suggestions)}")
                
        except Exception as e:
            print(f"   Exception caught: {e}")


def main():
    """Main example runner."""
    print("Image Generation Assistant - Example Usage")
    print("This script demonstrates various ways to use the assistant.")
    print("\nNote: Make sure you have set up your OpenAI API key in .env")
    
    try:
        # Run basic examples
        basic_usage()
        
        # Run interactive examples
        interactive_example()
        
        # Run error handling examples
        error_handling_example()
        
        # Run async examples
        print("\nRunning async examples...")
        asyncio.run(advanced_usage())
        
        print("\n✅ All examples completed!")
        print("\nNext steps:")
        print("- Try the CLI: python main.py chat")
        print("- Generate your first image: python main.py generate 'your prompt here'")
        print("- Check the README.md for more details")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you've installed dependencies: pip install -r requirements.txt")
        print("2. Set up your API key: python main.py setup")
        print("3. Check that all files are present in the directory")


if __name__ == "__main__":
    main() 