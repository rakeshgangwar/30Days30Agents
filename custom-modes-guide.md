# Custom Modes Guide: 30 Days 30 Agents

This guide explains how to use the custom modes created for the "30 Days 30 Agents" project. Custom modes transform Roo into specialized experts for different aspects of your project, from agent development to content creation.

## What Are Custom Modes?

Custom modes are specialized configurations that change Roo's expertise, focus, and behavior to assist with specific tasks in your agent development journey. Each mode has:

- A specialized role definition
- Specific permissions
- Custom instructions and guidelines
- Access to reference materials

## Benefits of Using Custom Modes

- **Specialized Expertise**: Get guidance tailored to specific frameworks or tasks
- **Consistent Approach**: Maintain consistent patterns across similar agents
- **Contextual Knowledge**: Access relevant best practices and patterns
- **Task-Focused Assistance**: Receive help optimized for your current activity
- **Workflow Efficiency**: Switch contexts without losing project momentum

## How to Switch Between Modes

### Using Chat Command

Type the following in the chat:
```
/mode [mode-slug]
```

For example:
```
/mode langchain-dev
```

### Using Mode Selector UI

1. Click on the mode selector dropdown in the Roo interface
2. Browse available modes
3. Select the desired mode

## Available Custom Modes

We've created 22 custom modes grouped into these categories:

### Architecture & Planning
- **🏗️ Agent Architect** (`agent-architect`): For designing agent capabilities and workflows

### Framework-Specific Development
- **🔗 LangChain Developer** (`langchain-dev`): For LangChain-based agent implementation
- **📊 LangGraph Developer** (`langgraph-dev`): For graph-based workflow orchestration
- **🦙 LlamaIndex Developer** (`llamaindex-dev`): For knowledge-intensive applications
- **👥 CrewAI Developer** (`crewai-dev`): For multi-agent collaborative systems
- **🤖 AutoGen Developer** (`autogen-dev`): For conversational multi-agent systems
- **⚡ DSPy Developer** (`dspy-dev`): For optimizing language model programs
- **🌐 Google ADK Developer** (`google-adk-dev`): For Google Agent Development Kit
- **⏱️ Temporal Developer** (`temporal-dev`): For fault-tolerant workflow orchestration
- **☁️ Cloudflare Agent Developer** (`cloudflare-agent-dev`): For always-online agents

### Weekly Progression
- **🔨 Foundation Agent Developer** (`foundation-agent-dev`): Week 1 basic agents
- **🧩 Specialized Agent Developer** (`specialized-agent-dev`): Week 2 domain-specific agents
- **🚀 Advanced Agent Developer** (`advanced-agent-dev`): Week 3 advanced capability agents
- **🧠 Complex Agent Developer** (`complex-agent-dev`): Week 4 sophisticated agents
- **🔄 Integration Specialist** (`integration-specialist`): For multi-agent system integration

### Content Creation
- **✍️ Content Creator** (`content-creator`): General content across platforms
- **📱 Social Media Creator** (`social-media-creator`): Twitter threads and LinkedIn posts
- **📓 Technical Blogger** (`technical-blogger`): In-depth technical articles
- **💬 Community Manager** (`community-manager`): Forum and community content

### Documentation & Testing
- **📝 Agent Documenter** (`agent-documenter`): For comprehensive documentation
- **🧪 Agent Tester** (`agent-tester`): For testing and evaluation
- **📊 Project Tracker** (`project-tracker`): For progress tracking

## When to Use Each Mode

### Daily Development Workflow

#### Planning Phase
1. Start with **Agent Architect** mode to design the day's agent
   ```
   /mode agent-architect
   ```
2. Plan out the agent's capabilities, components, and workflow

#### Implementation Phase
3. Switch to the appropriate weekly development mode
   ```
   /mode foundation-agent-dev  # For Week 1
   /mode specialized-agent-dev  # For Week 2
   /mode advanced-agent-dev  # For Week 3
   /mode complex-agent-dev  # For Week 4
   ```
4. Use the most relevant framework-specific mode for implementation
   ```
   /mode langchain-dev
   /mode llamaindex-dev
   /mode crewai-dev
   ```

#### Testing Phase
5. Switch to Agent Tester mode to validate your implementation
   ```
   /mode agent-tester
   ```

#### Documentation Phase
6. Use Agent Documenter mode to create comprehensive documentation
   ```
   /mode agent-documenter
   ```

#### Content Sharing Phase
7. Use the appropriate content creation mode for sharing
   ```
   /mode social-media-creator  # For Twitter/LinkedIn
   /mode technical-blogger  # For in-depth articles
   /mode community-manager  # For forum posts
   ```

### Weekly Planning Workflow

1. Start the week with **Agent Architect** for planning multiple agents
2. End the week with **Project Tracker** to update progress
   ```
   /mode project-tracker
   ```

### Framework Selection Workflow

1. Review frameworks in **Agent Architect** mode
2. Explore specific frameworks with dedicated modes
   ```
   /mode langgraph-dev
   /mode autogen-dev
   ```
3. Make selection and implement with chosen framework

## Custom Mode Details

Each mode has detailed guidelines available in the `.roo/rules-*` directories. For example:

- `.roo/rules-langchain-dev/01-framework-guidelines.md`
- `.roo/rules-agent-architect/01-role-guidelines.md`
- `.roo/rules-content-creator/01-creation-guidelines.md`

These files contain specialized instructions, best practices, and implementation patterns specific to each mode.

## Best Practices for Using Custom Modes

1. **Start with Architecture**: Begin each agent with the Agent Architect mode
2. **Match Framework to Task**: Choose framework-specific modes based on agent requirements
3. **Follow Weekly Progression**: Use weekly modes that match your current phase
4. **Document as You Go**: Switch to Agent Documenter regularly
5. **Consistent Testing**: Use Agent Tester before finalizing any agent
6. **Share Strategically**: Use appropriate content modes for different platforms
7. **Track Progress**: Regularly update with Project Tracker mode

## Customizing Modes Further

If you need to modify or create new custom modes:

1. Edit the `.roomodes` file to add or modify mode definitions
2. Create corresponding rule files in `.roo/rules-[mode-slug]/` directory
3. Restart or reload Roo to apply changes

## Troubleshooting

If a mode isn't working as expected:

1. Ensure the mode exists in `.roomodes` file
2. Check that the corresponding rule files exist in the `.roo/rules-*` directory
3. Try switching to another mode and back
4. Reload Roo if necessary

---

By leveraging these custom modes effectively, you'll streamline your development process for the "30 Days 30 Agents" challenge, maintain consistency, and benefit from specialized expertise throughout your project.