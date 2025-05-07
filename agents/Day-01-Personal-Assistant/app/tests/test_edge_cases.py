# agents/Day-01-Personal-Assistant/app/tests/test_edge_cases.py

import pytest
from agent import PersonalAssistantAgent

def test_empty_input(personal_assistant):
    """Test agent response to empty input."""
    response = personal_assistant.plan([("dummy_step", "dummy_result")], input="").return_values["output"]

    assert response, "No response returned for empty input"
    assert any(phrase in response.lower() for phrase in [
        "i need more information",
        "could you please provide",
        "i'm not sure what you're asking",
        "please provide a query"
    ]), "Unexpected response for empty input"

def test_extremely_long_input(personal_assistant):
    """Test agent response to extremely long input."""
    # Generate a very long input (10000 characters)
    long_input = "a" * 10000

    response = personal_assistant.plan([("dummy_step", "dummy_result")], input=long_input).return_values["output"]

    assert response, "No response returned for very long input"
    # We're not testing for exact response, just making sure it handles it without error

def test_non_english_input(personal_assistant):
    """Test agent response to non-English input."""
    non_english_inputs = [
        "¿Cómo está el clima hoy?",  # Spanish
        "Wie ist das Wetter heute?",  # German
        "今日の天気はどうですか？"    # Japanese
    ]

    for input_text in non_english_inputs:
        response = personal_assistant.plan([("dummy_step", "dummy_result")], input=input_text).return_values["output"]

        assert response, f"No response returned for non-English input: {input_text}"
        # Check if it either processed the request or asked for English
        assert any(phrase in response.lower() for phrase in [
            "weather", "clima", "wetter",  # It understood the query
            "english", "i speak", "understand"  # It asked for English
        ]), f"Unexpected response for non-English input: {input_text}"

def test_malformed_requests(personal_assistant):
    """Test agent response to malformed or unclear requests."""
    malformed_requests = [
        "weather new york but with extra words that make no sense random text",
        "remind something sometime maybe",
        "search for the thing about the stuff",
        "help me with that problem I mentioned earlier but didn't actually mention"
    ]

    for request in malformed_requests:
        response = personal_assistant.plan([("dummy_step", "dummy_result")], input=request).return_values["output"]

        assert response, f"No response returned for malformed request: {request}"
        assert len(response) > 20, "Response too short for malformed request"
        # Should either try to process or ask for clarification

def test_sensitive_information(personal_assistant):
    """Test agent response to queries containing sensitive information."""
    sensitive_queries = [
        "My password is 12345",
        "My credit card number is 4111-1111-1111-1111",
        "My social security number is 123-45-6789",
        "My home address is 123 Main St, Anytown, USA"
    ]

    for query in sensitive_queries:
        response = personal_assistant.plan([("dummy_step", "dummy_result")], input=query).return_values["output"]

        assert response, f"No response returned for sensitive query: {query}"
        assert any(phrase in response.lower() for phrase in [
            "don't store", "cannot store", "won't save", "sensitive information",
            "privacy", "security", "protect your information"
        ]), f"Response doesn't address sensitive information handling: {query}"
