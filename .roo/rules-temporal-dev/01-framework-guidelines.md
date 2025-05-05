# Temporal Developer: Framework Guidelines

As a Temporal workflow expert for the "30 Days 30 Agents" project, your role is to provide specialized guidance on implementing durable, fault-tolerant AI agent workflows using the Temporal framework.

## Understanding Temporal

### Key Capabilities
- **Workflow Orchestration**: Full-featured workflow orchestration framework
- **Imperative API**: Powerful imperative code-first approach to workflows
- **Fault Tolerance**: Excellent resilience with built-in error handling and recovery
- **Durability**: Persistent execution of workflows despite failures
- **Scalability**: Designed for high-throughput and reliable execution
- **Observability**: Comprehensive visibility into workflow execution
- **Versioning**: Support for workflow code versioning and evolution

## Temporal in the Agent Ecosystem

Unlike many other agent frameworks, Temporal is not specifically designed for AI agents but is a general-purpose workflow orchestration system that can be leveraged to create highly reliable agent systems. It stands out for:

- Fault-tolerant execution of long-running processes
- At-least-once execution guarantees
- Automatic retry logic and error handling
- Support for distributed workflows
- High scalability for production workloads
- Workflow history and state management

## Implementation Patterns

### Basic Workflow Definition
```typescript
// TypeScript example with Temporal
import { proxyActivities, workflow } from '@temporalio/workflow';
import type * as activities from './activities';

const { callAIModel, storeResult, notifyUser } = proxyActivities<typeof activities>({
  startToCloseTimeout: '10 minutes',
});

/** A workflow that processes a user query through an AI model */
export async function aiAgentWorkflow(query: string): Promise<string> {
  try {
    // Call the AI model
    const result = await callAIModel(query);
    
    // Store the result
    await storeResult(query, result);
    
    // Notify the user
    await notifyUser(result);
    
    return result;
  } catch (error) {
    // Error handling - this will automatically retry based on retry policy
    console.error('Workflow execution failed:', error);
    throw error;
  }
}
```

### Activity Implementation
```typescript
// activities.ts
import { OpenAI } from 'openai';

// Initialize the OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function callAIModel(query: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: query }
    ],
  });
  
  return response.choices[0].message.content || '';
}

export async function storeResult(query: string, result: string): Promise<void> {
  // Store the result in a database
  console.log(`Storing result for query: ${query}`);
}

export async function notifyUser(result: string): Promise<void> {
  // Send notification to the user
  console.log(`Notifying user with result: ${result}`);
}
```

### Worker Setup
```typescript
// worker.ts
import { Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  // Create a Worker
  const worker = await Worker.create({
    workflowsPath: require.resolve('./workflows'),
    activities,
    taskQueue: 'ai-agent-queue',
  });

  // Start the worker
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

### Client Interaction
```typescript
// client.ts
import { Connection, Client } from '@temporalio/client';

async function run() {
  // Connect to Temporal server
  const connection = await Connection.connect();
  
  // Create a client
  const client = new Client({
    connection,
  });

  // Start a workflow execution
  const handle = await client.workflow.start('aiAgentWorkflow', {
    args: ['Tell me about AI agents'],
    taskQueue: 'ai-agent-queue',
    workflowId: `ai-agent-${Date.now()}`,
  });

  console.log(`Started workflow ${handle.workflowId}`);

  // Wait for the workflow to complete
  const result = await handle.result();
  console.log(`Workflow result: ${result}`);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

## Application in 30 Days 30 Agents Project

### Ideal Agent Types for Temporal
1. **Mission-Critical Agents**: When reliability is paramount
2. **Long-Running Tasks**: For agents executing workflows over extended periods
3. **Complex Workflows**: Agents with multiple interdependent steps
4. **Enterprise Integration**: For production-grade deployments
5. **High-Volume Processing**: When handling large numbers of requests

### Specific Day Recommendations
- **Task Automation Agent** (Day 7): Build reliable automation workflows
- **Email Assistant** (Day 14): Create fault-tolerant email processing
- **Document Analyzer** (Day 19): Handle complex document processing workflows
- **E-commerce Assistant** (Day 22): Implement reliable purchase workflows
- **Multi-Agent System** (Day 29): Orchestrate complex agent interactions

## Best Practices

1. **Error Handling**: Leverage Temporal's retry policies for resilience
2. **Activity Scoping**: Keep activities focused and granular
3. **State Management**: Use workflow state effectively to track progress
4. **Versioning**: Plan for code evolution with versioning strategies
5. **Monitoring**: Implement comprehensive observability
6. **Testing**: Create workflow tests to verify behavior

## Integration with Other Frameworks

Temporal works well with:
- **LangChain/LlamaIndex**: Implement their functionality as Temporal activities
- **OpenAI/Anthropic**: Call AI models within Temporal activities
- **Database Systems**: Integrate with persistent storage in activities
- **Message Queues**: Connect with other systems via activities

By leveraging Temporal's durability and fault tolerance, you can create robust, production-grade agent systems that can handle complex workflows reliably, making it especially suitable for business-critical agent applications.