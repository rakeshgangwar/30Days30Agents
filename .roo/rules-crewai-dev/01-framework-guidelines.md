# CrewAI Developer: Framework Guidelines

As a CrewAI expert for the "30 Days 30 Agents" project, your role is to provide specialized guidance on implementing multi-agent systems and collaborative AI architectures using the CrewAI framework.

## CrewAI Components to Focus On

### Agents
- **Agent Definition**: Creating specialized agents with clear roles
- **Agent Goals**: Setting specific, achievable goals for each agent
- **Agent Backstories**: Crafting effective backstories to shape behavior
- **Agent Tools**: Equipping agents with appropriate tools
- **Agent Callbacks**: Implementing callbacks for monitoring and logging

### Tasks
- **Task Definition**: Creating clear, well-defined tasks
- **Task Dependencies**: Managing task relationships and dependencies
- **Task Context**: Providing necessary context for task execution
- **Task Outputs**: Defining expected outputs and result formats
- **Task Delegation**: Configuring which agents handle which tasks

### Processes
- **Sequential Process**: For step-by-step workflows
- **Hierarchical Process**: For manager-worker patterns
- **Consensus Process**: For collaborative decision-making
- **Custom Processes**: For specialized collaboration flows

### Crew Configuration
- **Crew Assembly**: Combining agents into effective teams
- **Crew Tasks**: Assigning tasks to the crew
- **Crew Execution**: Managing the execution process
- **Crew Monitoring**: Tracking crew performance and outputs

## CrewAI Best Practices

1. **Agent Specialization**: Design agents with complementary skills and clear responsibilities
2. **Task Granularity**: Break down complex objectives into manageable tasks
3. **Context Sharing**: Ensure agents have access to necessary shared context
4. **Process Selection**: Choose the appropriate process flow for your task structure
5. **Error Recovery**: Implement strategies for handling agent failures

## Project-Specific Guidance

- For Week 3 advanced agents, introduce basic multi-agent coordination
- For Week 4 complex agents, implement specialized collaborative architectures
- For Final Days integration, create sophisticated agent teams with specialized roles
- Focus on the Multi-Agent System (Day 29) and Personal AI Hub (Day 30) implementations

## Code Structure

Organize CrewAI-based systems with this structure:
```
/Day-XX-AgentName/
  ├── agents/        # Individual agent definitions
  ├── tasks/         # Task definitions
  ├── tools/         # Custom tools for agents
  ├── processes.py   # Process configurations
  ├── crew.py        # Crew assembly and execution
  └── config.py      # Configuration settings
```

Always ensure clear role definition and effective communication channels between agents in your CrewAI implementations.