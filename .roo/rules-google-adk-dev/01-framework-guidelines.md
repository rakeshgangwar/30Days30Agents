# Google ADK Developer: Framework Guidelines

As a Google Agent Development Kit (ADK) expert for the "30 Days 30 Agents" project, your role is to provide specialized guidance on implementing AI agents using Google's Agent Development Kit.

## Understanding Google ADK

### Key Capabilities
- **Agent Abstractions**: Comprehensive agent abstraction modeling
- **Multi-Agent Support**: First-class support for multi-agent systems
- **Memory Management**: Both short-term and long-term memory capabilities
- **Streaming**: Support for streaming responses
- **Code Interpreter**: Built-in code generation and execution capabilities
- **Studio**: Visual interface for designing and monitoring agent systems
- **Prescribed Project Setup**: Clear, standardized project structure

## Google ADK in the Agent Ecosystem

Google's Agent Development Kit provides a structured approach to building agents with Google's AI models. It offers:

- Seamless integration with Google's AI models (like Gemini)
- Built-in support for multi-agent systems
- Standardized project structure and development patterns
- Strong support for code generation and execution
- Visual tools for agent design and monitoring

## Implementation Patterns

### Basic Agent Setup
```python
from google.adk import Agent, Tool, ChatSession

# Define a tool
class CalculatorTool(Tool):
    def add(self, a: float, b: float) -> float:
        """Add two numbers together."""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b

# Create an agent with the tool
calculator_tool = CalculatorTool()
agent = Agent(
    name="Math Helper",
    description="I can help with mathematical operations",
    tools=[calculator_tool]
)

# Create a chat session
session = ChatSession(agent)

# Interact with the agent
response = session.send_message("I need to add 5 and 3")
print(response.text)
```

### Multi-Agent System
```python
from google.adk import Agent, MultiAgentSystem, ChatSession

# Create specialized agents
researcher = Agent(
    name="Researcher",
    description="I gather and analyze information",
    model="gemini-pro"
)

writer = Agent(
    name="Writer",
    description="I create compelling content based on research",
    model="gemini-pro"
)

editor = Agent(
    name="Editor",
    description="I review and improve content for clarity and accuracy",
    model="gemini-pro"
)

# Create a multi-agent system
content_team = MultiAgentSystem(
    name="Content Creation Team",
    agents=[researcher, writer, editor],
    workflow="sequential"  # or "collaborative"
)

# Create a session with the multi-agent system
session = ChatSession(content_team)

# Interact with the multi-agent system
response = session.send_message("Create a 2-paragraph summary about AI agents")
print(response.text)
```

### Using Code Interpreter
```python
from google.adk import Agent, CodeInterpreter, ChatSession

# Create an agent with code interpreter
code_agent = Agent(
    name="Python Coder",
    description="I can write and execute Python code",
    tools=[CodeInterpreter()]
)

# Create a session
session = ChatSession(code_agent)

# Ask the agent to write and execute code
response = session.send_message("Create a Python function to calculate the Fibonacci sequence up to n terms")
print(response.text)

# Execute the generated code
result = session.send_message("Execute this code with n=10")
print(result.text)
```

## Application in 30 Days 30 Agents Project

### Ideal Agent Types for Google ADK
1. **Google Services Integration**: Agents that leverage Google's APIs and services
2. **Multi-Agent Systems**: When multiple agents need to collaborate
3. **Code Generation Agents**: For agents that write and execute code
4. **Content Creation**: For agents that generate, analyze, and edit content
5. **Data Analysis**: For processing and visualizing Google-hosted data

### Specific Day Recommendations
- **Research Assistant** (Day 2): Leverage Google's search capabilities
- **Code Assistant** (Day 3): Use the built-in code interpreter
- **Data Analysis Agent** (Day 5): Connect to Google Sheets and BigQuery
- **Meeting Assistant** (Day 20): Integrate with Google Meet and Calendar
- **Multi-Agent System** (Day 29): Use the multi-agent capabilities

## Best Practices

1. **Standardized Structure**: Follow the prescribed project setup
2. **Clear Agent Definition**: Define clear roles and capabilities
3. **Tool Integration**: Leverage the built-in tools and create custom ones
4. **Testing**: Use the testing facilities in the ADK
5. **Monitoring**: Leverage the studio for visualization and debugging

## Integration with Other Frameworks

Google ADK works well with:
- **LangChain**: For additional tools and chains
- **LlamaIndex**: For knowledge base integration
- **Streamlit/Gradio**: For building web interfaces
- **Google Cloud Services**: For deployment and scaling

By leveraging Google ADK's capabilities, you can create agents that seamlessly integrate with Google's ecosystem while benefiting from standardized development patterns and powerful multi-agent support.