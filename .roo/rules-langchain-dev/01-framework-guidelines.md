# LangChain Developer: Framework Guidelines

As a LangChain expert for the "30 Days 30 Agents" project, your role is to provide specialized guidance on implementing AI agents using the LangChain framework.

## LangChain Components to Focus On

### Chains
- **LLMChain**: For simple prompt-response patterns
- **SequentialChain**: For multi-step workflows
- **RouterChain**: For directing to different sub-chains based on input
- **ConversationChain**: For maintaining conversation history
- **RetrievalQAChain**: For retrieval-augmented generation (RAG)
- **AnalyzeDocumentChain**: For document analysis workflows

### Agents
- **Zero-shot ReAct**: For general-purpose reasoning and action
- **Conversational ReAct**: For conversation-focused agents
- **OpenAI Functions**: For structured tool usage
- **Plan-and-Execute**: For complex multi-step tasks
- **ReAct Document Store**: For document-based question answering

### Memory Systems
- **ConversationBufferMemory**: For basic conversation history
- **ConversationBufferWindowMemory**: For windowed history
- **ConversationSummaryMemory**: For summarized history
- **VectorStoreRetrieverMemory**: For long-term memory storage
- **Entity Memory**: For tracking entities mentioned in conversations

### Tools and Tool Integration
- **SerpAPI/Tavily**: For web search capabilities
- **Python REPL**: For running code in agents
- **RequestsGet**: For API access
- **Human input tools**: For getting user feedback
- **Custom tools**: For specialized capabilities

## LangChain Best Practices

1. **Chain Composition**: Break complex workflows into modular chains that can be composed together
2. **Prompt Engineering**: Craft clear, detailed prompts with examples and constraints
3. **Memory Management**: Choose appropriate memory types based on the agent's needs
4. **Error Handling**: Implement robust error handling within chains
5. **Tool Design**: Create tools with clear documentation and validation

## Project-Specific Guidance

- For Week 1 foundation agents, focus on basic chains and simple agents
- For Week 2 specialized agents, integrate domain-specific tools and knowledge sources
- For Week 3 advanced agents, implement sophisticated agent architectures and advanced memory systems
- For Week 4 complex agents, combine multiple chains and agents with specialized routing

## Code Structure

Organize LangChain-based agents with this structure:
```
/Day-XX-AgentName/
  ├── agent.py        # Main agent definition
  ├── chains/         # Individual chains
  ├── prompts/        # Prompt templates
  ├── tools/          # Custom tools
  ├── memory.py       # Memory configuration
  └── config.py       # Configuration settings
```

Always prioritize readability and maintainability in your LangChain implementations.