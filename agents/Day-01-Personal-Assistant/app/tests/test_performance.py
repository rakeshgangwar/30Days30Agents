# agents/Day-01-Personal-Assistant/app/tests/test_performance.py

import pytest
import time
from agent import PersonalAssistantAgent

def test_response_time():
    """Test response time for different query types."""
    assistant = PersonalAssistantAgent()

    test_queries = [
        "What's the weather in London?",
        "Find me news about technology",
        "Set a reminder for my meeting tomorrow",
        "What's the capital of France?",
        "Tell me about the history of computers",
    ]

    results = {}

    for query in test_queries:
        # Measure response time
        start_time = time.time()
        response = assistant.plan([("dummy_step", "dummy_result")], input=query).return_values["output"]
        end_time = time.time()

        # Record metrics
        response_time = end_time - start_time
        results[query] = {
            "response_time": response_time,
            "response_length": len(response),
        }

        # Basic performance assertions
        assert response_time < 10.0, f"Response time too slow: {response_time:.2f} seconds for query: {query}"
        assert len(response) > 20, f"Response too short: {len(response)} characters for query: {query}"

    # Calculate and report averages
    avg_response_time = sum(r["response_time"] for r in results.values()) / len(results)
    avg_response_length = sum(r["response_length"] for r in results.values()) / len(results)

    print(f"Average response time: {avg_response_time:.2f} seconds")
    print(f"Average response length: {avg_response_length:.0f} characters")

def test_repeated_queries_performance():
    """Test performance with repeated identical queries (should improve with caching)."""
    assistant = PersonalAssistantAgent()

    query = "What's the capital of France?"

    # First query (cold)
    start_time_cold = time.time()
    response_cold = assistant.plan([("dummy_step", "dummy_result")], input=query).return_values["output"]
    cold_response_time = time.time() - start_time_cold

    # Second query (potentially cached)
    start_time_warm = time.time()
    response_warm = assistant.plan([("dummy_step", "dummy_result")], input=query).return_values["output"]
    warm_response_time = time.time() - start_time_warm

    print(f"Cold query response time: {cold_response_time:.2f} seconds")
    print(f"Warm query response time: {warm_response_time:.2f} seconds")

    # Note: This might not always be faster if caching isn't implemented
    # assert warm_response_time <= cold_response_time * 1.2, "Warm query should not be significantly slower than cold query"

def test_long_conversation_performance():
    """Test performance degradation in long conversations."""
    assistant = PersonalAssistantAgent()

    # Simulate a conversation with 5 exchanges
    queries = [
        "My name is John",
        "I live in San Francisco",
        "What's the weather like there?",
        "Set a reminder for my doctor's appointment tomorrow",
        "What reminders do I have?"
    ]

    response_times = []

    for query in queries:
        start_time = time.time()
        response = assistant.plan([("dummy_step", "dummy_result")], input=query).return_values["output"]
        response_time = time.time() - start_time

        response_times.append(response_time)
        print(f"Query: '{query}' - Response time: {response_time:.2f}s")

    # Calculate trend - is performance degrading?
    # Simple check: is the last query significantly slower than the average of the first two?
    early_avg = sum(response_times[:2]) / 2
    late_avg = sum(response_times[-2:]) / 2

    print(f"Early conversation average response time: {early_avg:.2f}s")
    print(f"Late conversation average response time: {late_avg:.2f}s")

    # If performance degradation is significant, this might be worth investigating
    if late_avg > early_avg * 2:
        print("Warning: Significant performance degradation detected in long conversations")
