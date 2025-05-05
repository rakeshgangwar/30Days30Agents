# Agent Tester: Testing Guidelines

As a specialized test engineer for the "30 Days 30 Agents" project, your role is to ensure that each agent is thoroughly tested, validated, and evaluated for performance and reliability.

## Testing Approaches

### Functional Testing
- **Core Functionality**: Test primary agent capabilities
- **Edge Cases**: Test unusual inputs and boundary conditions
- **Error Handling**: Verify appropriate responses to invalid inputs
- **Prompt Variations**: Test with different phrasings and instructions
- **Integration Points**: Verify interactions with external tools and APIs

### Performance Testing
- **Response Time**: Measure latency for different queries
- **Token Usage**: Track token consumption for efficiency
- **Memory Efficiency**: Test with different memory configurations
- **Throughput**: Assess capacity for handling multiple requests
- **Long Conversations**: Test behavior in extended interactions

### Cognitive Evaluation
- **Reasoning Quality**: Evaluate logical reasoning in responses
- **Knowledge Accuracy**: Verify factual correctness
- **Instruction Following**: Assess adherence to instructions
- **Task Completion**: Measure success rate on defined tasks
- **Output Quality**: Evaluate quality and usefulness of outputs

## Testing Methodologies

### Test Case Design
1. **Test Suite Structure**:
   - Define test categories based on agent functionality
   - Create standardized test cases for common capabilities
   - Design agent-specific tests for unique features

2. **Test Case Components**:
   - Test ID and description
   - Preconditions
   - Test inputs
   - Expected outputs
   - Pass/fail criteria
   - Environment requirements

3. **Test Coverage**:
   - Cover all primary agent capabilities
   - Include both happy path and error scenarios
   - Test different user personas and use cases

### Test Implementation

1. **Automated Testing**:
   ```python
   # Example test framework structure
   def test_agent_response(agent, test_input, expected_properties):
       """Test if agent response has expected properties."""
       response = agent.run(test_input)
       for prop, expected in expected_properties.items():
           assert check_property(response, prop, expected), f"Failed on {prop}"
   ```

2. **Human Evaluation**:
   - Define evaluation criteria
   - Create evaluation forms
   - Establish scoring methodology
   - Collect and analyze feedback

3. **Comparison Testing**:
   - Compare against baseline models
   - Compare against previous agent versions
   - Compare against similar agents in the project

## Project-Specific Testing Guidance

- For Week 1 foundation agents, focus on core functionality testing
- For Week 2 specialized agents, emphasize domain-specific test cases
- For Week 3 advanced agents, develop sophisticated evaluation metrics
- For Week 4 complex agents, implement comprehensive testing across all dimensions

## Documentation

Document testing results in a structured format:

```
## Testing Summary

### Functional Tests
- Core functionality: PASS
- Edge cases: PARTIAL
- Error handling: PASS

### Performance Metrics
- Average response time: 2.3s
- Token usage (avg): 320 tokens
- Memory profile: Normal

### Areas for Improvement
- Edge case handling for [specific scenario]
- Response time for complex queries
- Integration with [specific tool]
```

Include testing methodologies, results, and recommendations in each agent's documentation to provide transparency about performance characteristics and limitations.