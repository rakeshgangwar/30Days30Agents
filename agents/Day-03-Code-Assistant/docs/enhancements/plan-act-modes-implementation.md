# Plan and Act Modes Implementation

## Overview

This document outlines the implementation plan for adding Plan and Act modes to our Code Assistant, inspired by Cline's approach to structured AI development. This enhancement will improve the quality of code analysis and implementation by separating the planning and execution phases.

## Current Approach

Our current implementation uses a single-mode approach where the AI model is used for both planning and execution in a single context. This approach has several limitations:

1. **Lack of Structured Thinking**: The AI may jump directly to implementation without proper planning
2. **Context Inefficiency**: The same context is used for both planning and execution, wasting tokens
3. **Model Optimization**: We can't optimize model selection for different tasks (planning vs. execution)
4. **User Experience**: Users can't easily distinguish between planning and implementation phases

## Proposed Solution

We propose implementing a dual-mode system:

1. **Plan Mode**: Focused on understanding requirements, gathering context, and creating a detailed plan
2. **Act Mode**: Focused on executing the plan, generating code, and implementing solutions

Each mode will have:
- Optimized prompts for its specific purpose
- Potentially different AI models optimized for planning or execution
- Separate context management strategies
- Distinct user interfaces and workflows

## Implementation Details

### 1. Task Mode Management

We'll enhance the `Task` class to support different modes:

```javascript
// src/core/task/index.js
class Task {
  constructor(options = {}) {
    this.options = options;
    this.mode = options.initialMode || 'plan'; // 'plan' or 'act'
    this.planContext = null;
    this.actContext = null;
    this.currentPlan = null;
  }
  
  async switchMode(newMode) {
    if (newMode === this.mode) return;
    
    if (newMode === 'act' && !this.currentPlan) {
      throw new Error('Cannot switch to Act mode without a plan');
    }
    
    // Save context from current mode
    if (this.mode === 'plan') {
      this.planContext = this.context;
    } else {
      this.actContext = this.context;
    }
    
    // Switch mode
    this.mode = newMode;
    
    // Restore context for new mode
    this.context = this.mode === 'plan' ? this.planContext : this.actContext;
    
    // If switching to Act mode, include the plan in the context
    if (this.mode === 'act' && this.currentPlan) {
      this.context = {
        ...this.context,
        plan: this.currentPlan
      };
    }
    
    return {
      success: true,
      mode: this.mode
    };
  }
  
  async savePlan(plan) {
    this.currentPlan = plan;
    return {
      success: true,
      plan: this.currentPlan
    };
  }
  
  // Other methods...
}
```

### 2. Mode-Specific Prompts

We'll create mode-specific prompt templates:

```javascript
// src/components/aiAnalysisCoordinator/promptEngineer.js
class PromptEngineer {
  constructor(options = {}) {
    this.options = options;
    this.loadPromptTemplates();
  }
  
  loadPromptTemplates() {
    this.promptTemplates = {
      planMode: `
        You are a software architecture expert analyzing a repository.
        
        Your task is to create a detailed plan for: {task}
        
        Repository: {repositoryName}
        Description: {repositoryDescription}
        
        Available files:
        {fileList}
        
        Key code structures:
        {codeStructures}
        
        Create a detailed plan that includes:
        1. Understanding of the requirements
        2. Files that need to be modified
        3. Specific changes to make
        4. Potential challenges and how to address them
        5. Testing strategy
        
        Format your response as a structured plan with clear steps.
      `,
      
      actMode: `
        You are a software implementation expert.
        
        Your task is to implement the following plan: {plan}
        
        Repository: {repositoryName}
        Description: {repositoryDescription}
        
        Relevant code:
        {relevantCode}
        
        Implement the plan step by step, providing detailed code changes and explanations.
        For each file that needs to be modified, provide the exact changes to make.
        
        Format your response with clear code blocks and explanations.
      `
    };
  }
  
  createPrompt(mode, context) {
    const template = this.promptTemplates[`${mode}Mode`];
    if (!template) {
      throw new Error(`No prompt template found for mode: ${mode}`);
    }
    
    // Replace placeholders with context values
    let prompt = template;
    Object.entries(context).forEach(([key, value]) => {
      prompt = prompt.replace(new RegExp(`{${key}}`, 'g'), value);
    });
    
    return prompt;
  }
}
```

### 3. Mode-Specific API Configuration

We'll enhance the `AIAnalysisCoordinator` to support different API configurations for each mode:

```javascript
// src/components/aiAnalysisCoordinator/index.js
class AIAnalysisCoordinator {
  constructor(config = {}) {
    this.config = config;
    this.promptEngineer = new PromptEngineer();
    this.contextPreparer = new ContextPreparer();
    
    // Mode-specific API configurations
    this.apiConfigs = {
      plan: {
        provider: config.planMode?.provider || config.provider || 'openai',
        model: config.planMode?.model || 'gpt-4',
        temperature: config.planMode?.temperature !== undefined ? config.planMode.temperature : 0.2,
        maxTokens: config.planMode?.maxTokens || 2000
      },
      act: {
        provider: config.actMode?.provider || config.provider || 'openai',
        model: config.actMode?.model || 'gpt-4',
        temperature: config.actMode?.temperature !== undefined ? config.actMode.temperature : 0.2,
        maxTokens: config.actMode?.maxTokens || 2000
      }
    };
  }
  
  async analyzeWithMode(mode, context) {
    // Get mode-specific API configuration
    const apiConfig = this.apiConfigs[mode];
    if (!apiConfig) {
      throw new Error(`No API configuration found for mode: ${mode}`);
    }
    
    // Create mode-specific prompt
    const prompt = this.promptEngineer.createPrompt(mode, context);
    
    // Call API with mode-specific configuration
    const response = await this.callAPI(prompt, apiConfig);
    
    return response;
  }
  
  async callAPI(prompt, config) {
    // Implementation of API call with specific configuration
    // ...
  }
}
```

### 4. User Interface Integration

We'll update the CLI interface to support mode switching:

```javascript
// src/cli.js
const { program } = require('commander');
const RepositoryAnalysisAgent = require('./app');

program
  .command('analyze <owner> <repo>')
  .description('Analyze a GitHub repository')
  .option('-m, --mode <mode>', 'Initial mode (plan or act)', 'plan')
  .option('-d, --description <description>', 'Repository description')
  .option('--dry-run', 'Do not create issues')
  .action(async (owner, repo, options) => {
    const agent = new RepositoryAnalysisAgent({
      initialMode: options.mode
    });
    
    await agent.initialize();
    
    const result = await agent.analyzeRepository(owner, repo, {
      description: options.description,
      dryRun: options.dryRun
    });
    
    console.log(result);
  });

program
  .command('switch-mode <mode>')
  .description('Switch between Plan and Act modes')
  .action(async (mode) => {
    if (mode !== 'plan' && mode !== 'act') {
      console.error('Invalid mode. Use "plan" or "act".');
      return;
    }
    
    const agent = new RepositoryAnalysisAgent();
    await agent.initialize();
    
    const result = await agent.switchMode(mode);
    console.log(`Switched to ${result.mode} mode`);
  });

program
  .command('save-plan <planFile>')
  .description('Save the current plan to a file')
  .action(async (planFile) => {
    const agent = new RepositoryAnalysisAgent();
    await agent.initialize();
    
    const result = await agent.savePlan(planFile);
    console.log(`Plan saved to ${planFile}`);
  });

program.parse(process.argv);
```

## Implementation Plan

### Phase 1: Core Mode Implementation (1 week)

1. **Enhance Task Class**:
   - Add mode support (plan/act)
   - Implement mode switching
   - Add plan storage and retrieval

2. **Create Mode-Specific Prompts**:
   - Implement the PromptEngineer class
   - Create templates for Plan and Act modes
   - Add context preparation for each mode

3. **Add Mode-Specific API Configuration**:
   - Enhance AIAnalysisCoordinator to support mode-specific configs
   - Implement API provider selection based on mode
   - Add configuration options for each mode

### Phase 2: User Interface and Experience (1 week)

1. **Update CLI Interface**:
   - Add mode-specific commands
   - Implement mode switching in the CLI
   - Add plan saving and loading

2. **Enhance User Experience**:
   - Add clear mode indicators
   - Implement smooth transitions between modes
   - Create mode-specific output formatting

3. **Add Configuration Options**:
   - Add mode-specific configuration in config files
   - Implement model selection for each mode
   - Add temperature and token limit configuration

### Phase 3: Integration and Testing (1 week)

1. **Integrate with Main Application**:
   - Update the main application to support modes
   - Add mode-specific error handling
   - Implement mode persistence

2. **Implement Testing**:
   - Create unit tests for mode-specific functionality
   - Add integration tests for mode switching
   - Test with different model configurations

3. **Documentation and Refinement**:
   - Create documentation for Plan and Act modes
   - Add examples and usage guidelines
   - Refine the implementation based on testing results

## Expected Benefits

1. **Improved Planning**: Dedicated planning phase will result in more thorough analysis
2. **Better Implementation**: Act mode can focus on executing the plan without redoing analysis
3. **Optimized Model Usage**: Different models can be used for planning and implementation
4. **Enhanced User Experience**: Clear separation of planning and implementation phases
5. **Reduced Token Usage**: More efficient use of context in each mode

## Example Workflow

1. **Start in Plan Mode**:
   ```
   $ node src/cli.js analyze owner/repo --mode plan
   ```

2. **Review and Save Plan**:
   ```
   $ node src/cli.js save-plan plan.json
   ```

3. **Switch to Act Mode**:
   ```
   $ node src/cli.js switch-mode act
   ```

4. **Execute Plan**:
   ```
   $ node src/cli.js execute-plan
   ```

## Conclusion

Implementing Plan and Act modes will significantly improve the quality and efficiency of our Code Assistant. By separating the planning and execution phases, we can provide more structured and effective assistance for code analysis and implementation.

## References

1. Cline's Plan and Act modes documentation
2. OpenAI API documentation for different models
3. Cline Code Assistant implementation in `agents/Day-03-Code-Assistant/cline/`
