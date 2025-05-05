# Foundation Agent Developer: Implementation Guidelines

As a developer specializing in Week 1 foundation agents for the "30 Days 30 Agents" project, your focus is on implementing fundamental AI agent capabilities that will serve as building blocks for more complex agents in later weeks.

## Week 1 Foundation Agents

1. **Personal Assistant Agent** (Day 1)
   - Basic task management
   - Information retrieval
   - Simple scheduling
   - Note taking
   - Reminder setting

2. **Research Assistant** (Day 2)
   - Web search capabilities
   - Information synthesis
   - Source citation
   - Query refinement
   - Content summarization

3. **Code Assistant** (Day 3)
   - Code generation
   - Code explanation
   - Debugging support
   - Refactoring suggestions
   - Implementation guidance

4. **Writing Assistant** (Day 4)
   - Content generation
   - Text editing and improvement
   - Style adaptation
   - Grammar correction
   - Format conversion

5. **Data Analysis Agent** (Day 5)
   - Data processing
   - Basic visualization
   - Pattern identification
   - Statistical analysis
   - Insight generation

6. **Learning Coach** (Day 6)
   - Personalized learning recommendations
   - Concept explanation
   - Quiz generation
   - Progress tracking
   - Resource curation

7. **Task Automation Agent** (Day 7)
   - Workflow automation
   - Process optimization
   - Repetitive task handling
   - Integration with tools
   - Action sequencing

## Core Implementation Focus Areas

### Framework Integration
- Establish clean patterns for using agent frameworks
- Create reusable components for future agents
- Implement basic patterns that can be extended later

### Prompt Engineering
- Develop effective prompt templates for each agent type
- Balance specificity with flexibility in instructions
- Document prompt patterns for reuse in later agents

### Memory & Context
- Implement basic conversation memory
- Create appropriate context windows
- Establish patterns for maintaining agent state

### Tool Use
- Integrate essential external tools and APIs
- Create wrappers for common functionalities
- Develop patterns for tool selection and execution

### User Interaction
- Create simple, intuitive interfaces (CLI or basic UI)
- Implement clear feedback mechanisms
- Establish consistent interaction patterns

## Implementation Guidelines

1. **Modularity**: Build each agent with modular components that can be reused
2. **Documentation**: Document code thoroughly for future reference
3. **Testing**: Create basic test cases to verify functionality
4. **Simplicity**: Focus on core capabilities before adding advanced features
5. **Extensibility**: Design with future enhancements in mind

## Code Structure

Implement foundation agents with this structure:
```
/Day-XX-AgentName/
  ├── main.py         # Entry point
  ├── agent.py        # Core agent logic
  ├── prompts.py      # Prompt templates
  ├── tools.py        # Tool definitions
  ├── utils.py        # Utility functions
  ├── config.py       # Configuration
  ├── requirements.txt # Dependencies
  └── README.md       # Documentation
```

Your foundation agents should prioritize reliability and clarity over complexity, establishing solid building blocks for the more advanced agents to come in later weeks.