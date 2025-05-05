# Cloudflare Agent Developer: Integration Guidelines

As a developer specializing in Cloudflare Agents for the "30 Days 30 Agents" project, your focus is on implementing always-online AI agents using the Cloudflare Agents SDK that can run autonomously, maintain state, and operate in real-time.

## Understanding Cloudflare Agents

### Key Benefits for Always-Online Agents
- **Persistent Stateful Execution**: Agents run on Durable Objects, providing always-online capabilities with automatic state persistence
- **Built-in State Management**: Includes integrated SQL database for storing conversation history, user preferences, and agent state
- **Real-time Communication**: WebSocket support for streaming responses and maintaining live connections
- **Task Scheduling**: Built-in scheduling for autonomous operation and recurring tasks
- **AI Model Integration**: Support for multiple AI providers including OpenAI, Anthropic, and Cloudflare Workers AI
- **Global Deployment**: Run agents on Cloudflare's global network for low-latency access worldwide
- **Scalability**: Each agent instance can handle many users and tasks concurrently

## Use Cases in 30 Days 30 Agents Project

### Ideal Agent Types for Cloudflare Implementation
1. **Personal Assistant Agent** (Day 1): Always available to handle tasks and respond to requests
2. **Task Automation Agent** (Day 7): Can run scheduled tasks autonomously
3. **Social Media Manager** (Day 13): Can schedule posts and monitor engagement
4. **Meeting Assistant** (Day 20): Can join scheduled meetings and take notes
5. **Home Automation Controller** (Day 25): Can monitor and control smart home devices continuously
6. **Personal AI Hub** (Day 30): Can integrate multiple agents and maintain consistent state

## Cloudflare Agent Implementation

### Basic Setup
```javascript
// Install the Cloudflare Agents SDK
npm create cloudflare@latest agents-starter -- --template=cloudflare/agents-starter

// Define the Agent class
import { Agent } from "agents";

export class MyAgent extends Agent {
  // Initial state for the agent
  initialState = {
    conversations: [],
    preferences: {},
    lastActive: null
  };

  // Called when a new Agent instance starts
  async onStart() {
    console.log('Agent started with state:', this.state);
    // Initialize any resources or connections
  }

  // Handle WebSocket connections
  async onConnect(connection, ctx) {
    // Authentication can be handled here
    // ctx.request contains the original HTTP request
    
    // Send current state to the connecting client
    connection.send(JSON.stringify({
      type: 'state',
      state: this.state
    }));
  }

  // Process incoming WebSocket messages
  async onMessage(connection, message) {
    const data = JSON.parse(message);
    
    // Handle different message types
    if (data.type === 'query') {
      await this.processQuery(connection, data.content);
    }
  }

  // Process a user query using an AI model
  async processQuery(connection, query) {
    // Update state to include the new query
    this.setState({
      ...this.state,
      conversations: [
        ...this.state.conversations,
        { role: 'user', content: query, timestamp: new Date() }
      ]
    });

    // Connect to an AI model (OpenAI example)
    const openai = new OpenAI({
      apiKey: this.env.OPENAI_API_KEY,
    });

    // Stream the response back to the client
    const stream = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: query }],
      stream: true,
    });

    // Send each chunk as it arrives
    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content || "";
      if (content) {
        connection.send(JSON.stringify({ type: "chunk", content }));
      }
    }

    // Once complete, update state with the full response
    // This could be implemented with a buffer that collects the chunks
  }

  // Schedule a periodic task
  async schedulePeriodicCheck() {
    // Schedule a task to run every hour
    await this.schedule("0 * * * *", "runPeriodicCheck", {
      timestamp: new Date()
    });
  }

  // Method that will be called by the scheduler
  async runPeriodicCheck(data) {
    // Perform autonomous tasks here
    console.log(`Running periodic check scheduled at ${data.timestamp}`);
    
    // Could fetch new data, update state, send notifications, etc.
  }
}
```

### Deployment Configuration
```javascript
// wrangler.toml example
name = "my-agent"
main = "src/index.js"

[durable_objects]
bindings = [
  { name = "AGENT", class_name = "MyAgent" }
]

[ai]
binding = "AI"

[vars]
OPENAI_API_KEY = ""
```

## Integration with Other Frameworks

### Combining with LangChain/LlamaIndex
- Use LangChain for tool orchestration and LLM chains
- Use LlamaIndex for knowledge retrieval
- Deploy the integrated agent on Cloudflare for always-online availability

### React Frontend Integration
```javascript
// Client-side React component example
import { useAgent } from "agents/react";

function AgentChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  
  const agent = useAgent({
    agent: "my-agent",
    name: "user-123", // Unique identifier for this agent instance
    onStateUpdate: (state) => {
      // Update local state based on agent state
      setMessages(state.conversations);
    },
    onMessage: (message) => {
      // Handle streaming messages
      const data = JSON.parse(message);
      if (data.type === "chunk") {
        // Handle streaming chunks
      }
    }
  });
  
  const sendMessage = () => {
    agent.send(JSON.stringify({ type: "query", content: input }));
    setInput("");
  };
  
  return (
    <div>
      {/* Chat UI implementation */}
    </div>
  );
}
```

## Best Practices for Cloudflare Agents

1. **Optimized State Management**: Store only essential data in agent state to maintain performance
2. **Error Handling**: Implement robust error recovery for long-running agents
3. **Authentication**: Secure agent connections and validate client identities
4. **Streaming Responses**: Always stream AI model responses for better user experience
5. **Scheduled Maintenance**: Implement periodic state cleanup and maintenance tasks
6. **Connection Management**: Handle connection drops and reconnections gracefully
7. **Resource Conservation**: Be mindful of CPU and memory usage for long-running agents

By leveraging Cloudflare Agents for your always-online agents, you can create robust, persistent agent experiences that maintain state and operate autonomously even when users are disconnected.