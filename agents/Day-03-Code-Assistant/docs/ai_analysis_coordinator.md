# AI Analysis Coordinator

This document provides implementation details for the AI Analysis Coordinator of the Repository Analysis and Issue Creation Agent. This component is responsible for leveraging AI models to analyze code and generate actionable insights.

## Table of Contents

1. [Overview](#overview)
2. [Key Responsibilities](#key-responsibilities)
3. [Implementation Details](#implementation-details)
4. [Code Examples](#code-examples)
5. [Best Practices](#best-practices)
6. [Integration Points](#integration-points)

## Overview

The AI Analysis Coordinator is the intelligence layer of the agent, responsible for coordinating interactions with AI models to analyze code, identify issues, and generate recommendations. It transforms the structured data from the Code Analysis Engine into prompts for AI models and processes the responses into actionable insights.

## Key Responsibilities

- **Context Preparation**: Prepare code snippets and context for AI analysis
- **Prompt Engineering**: Craft effective prompts for AI models
- **AI Interaction**: Manage API calls to AI models
- **Response Processing**: Parse and structure AI responses
- **Insight Generation**: Transform AI outputs into actionable insights
- **Prioritization**: Rank findings by importance and impact

## Implementation Details

### Context Preparation

The first step is to prepare the code context for AI analysis:

```javascript
class ContextPreparer {
  prepareFileContext(file, analysisResult) {
    // Extract relevant information from the analysis result
    const { path, language, structure, metrics, content } = analysisResult;
    
    // Create a structured context object
    const context = {
      filePath: path,
      language,
      structure: this.summarizeStructure(structure),
      metrics: this.summarizeMetrics(metrics),
      content: this.prepareContent(content, language)
    };
    
    return context;
  }
  
  summarizeStructure(structure) {
    if (!structure) return 'No structure information available';
    
    // Create a summary of the code structure
    const summary = [];
    
    if (structure.classes.length > 0) {
      summary.push(`Classes (${structure.classes.length}): ${structure.classes.map(c => c.name).join(', ')}`);
    }
    
    if (structure.functions.length > 0) {
      summary.push(`Functions (${structure.functions.length}): ${structure.functions.map(f => f.name).join(', ')}`);
    }
    
    if (structure.methods.length > 0) {
      summary.push(`Methods (${structure.methods.length}): ${structure.methods.map(m => m.name).join(', ')}`);
    }
    
    return summary.join('\n');
  }
  
  summarizeMetrics(metrics) {
    if (!metrics) return 'No metrics available';
    
    // Create a summary of the code metrics
    return `
      Lines of Code: ${metrics.lineCount}
      Comment Ratio: ${(metrics.commentRatio * 100).toFixed(2)}%
      Cyclomatic Complexity: ${metrics.cyclomaticComplexity}
    `;
  }
  
  prepareContent(content, language) {
    // Format the content with language-specific syntax highlighting
    return `\`\`\`${language}\n${content}\n\`\`\``;
  }
  
  prepareRepositoryContext(repositoryInfo, analysisResults) {
    // Create a summary of the repository
    const summary = {
      name: repositoryInfo.name,
      description: repositoryInfo.description,
      languages: this.summarizeLanguages(analysisResults),
      structure: this.summarizeRepositoryStructure(analysisResults),
      metrics: this.summarizeRepositoryMetrics(analysisResults)
    };
    
    return summary;
  }
  
  summarizeLanguages(analysisResults) {
    // Count files by language
    const languageCounts = {};
    
    analysisResults.forEach(result => {
      if (result.success && result.language) {
        languageCounts[result.language] = (languageCounts[result.language] || 0) + 1;
      }
    });
    
    // Convert to array and sort by count
    const languages = Object.entries(languageCounts)
      .map(([language, count]) => ({ language, count }))
      .sort((a, b) => b.count - a.count);
    
    return languages;
  }
  
  summarizeRepositoryStructure(analysisResults) {
    // Aggregate structure information
    const structure = {
      classes: 0,
      functions: 0,
      methods: 0
    };
    
    analysisResults.forEach(result => {
      if (result.success && result.structure) {
        structure.classes += result.structure.classes.length;
        structure.functions += result.structure.functions.length;
        structure.methods += result.structure.methods.length;
      }
    });
    
    return structure;
  }
  
  summarizeRepositoryMetrics(analysisResults) {
    // Aggregate metrics
    let totalLines = 0;
    let totalComplexity = 0;
    let fileCount = 0;
    
    analysisResults.forEach(result => {
      if (result.success && result.metrics) {
        totalLines += result.metrics.lineCount;
        totalComplexity += result.metrics.cyclomaticComplexity;
        fileCount++;
      }
    });
    
    return {
      totalFiles: fileCount,
      totalLines,
      averageComplexity: fileCount > 0 ? totalComplexity / fileCount : 0
    };
  }
}
```

### Prompt Engineering

Next, we need to craft effective prompts for the AI models:

```javascript
class PromptEngineer {
  constructor() {
    this.promptTemplates = {
      fileAnalysis: `
        You are a code review expert analyzing a file in a repository.
        
        File: {filePath}
        Language: {language}
        
        Code Structure:
        {structure}
        
        Metrics:
        {metrics}
        
        Code Content:
        {content}
        
        Please analyze this code and identify:
        1. Potential bugs or issues
        2. Code smells or anti-patterns
        3. Performance concerns
        4. Security vulnerabilities
        5. Improvement suggestions
        
        For each finding, provide:
        - A clear title
        - A detailed description of the issue
        - The specific location in the code (line number if possible)
        - A suggested solution or improvement
        - The priority level (Critical, High, Medium, Low)
        
        Format your response as JSON with the following structure:
        {
          "findings": [
            {
              "title": "Finding title",
              "description": "Detailed description",
              "location": "Line number or code snippet",
              "suggestion": "Suggested solution",
              "priority": "Priority level"
            }
          ]
        }
      `,
      
      repositoryAnalysis: `
        You are a software architecture expert analyzing a repository.
        
        Repository: {name}
        Description: {description}
        
        Languages:
        {languages}
        
        Structure Summary:
        - Classes: {structure.classes}
        - Functions: {structure.functions}
        - Methods: {structure.methods}
        
        Metrics:
        - Total Files: {metrics.totalFiles}
        - Total Lines: {metrics.totalLines}
        - Average Complexity: {metrics.averageComplexity}
        
        Please analyze this repository and identify:
        1. Architectural issues or concerns
        2. Potential technical debt
        3. Structural improvements
        4. Feature suggestions
        5. Documentation needs
        
        For each finding, provide:
        - A clear title
        - A detailed description of the issue or suggestion
        - The affected area of the codebase
        - A suggested solution or improvement
        - The priority level (Critical, High, Medium, Low)
        
        Format your response as JSON with the following structure:
        {
          "findings": [
            {
              "title": "Finding title",
              "description": "Detailed description",
              "area": "Affected area",
              "suggestion": "Suggested solution",
              "priority": "Priority level"
            }
          ]
        }
      `
    };
  }
  
  createFileAnalysisPrompt(fileContext) {
    // Replace placeholders in the template with actual values
    let prompt = this.promptTemplates.fileAnalysis;
    
    Object.entries(fileContext).forEach(([key, value]) => {
      prompt = prompt.replace(new RegExp(`{${key}}`, 'g'), value);
    });
    
    return prompt;
  }
  
  createRepositoryAnalysisPrompt(repositoryContext) {
    // Replace placeholders in the template with actual values
    let prompt = this.promptTemplates.repositoryAnalysis;
    
    // Handle simple replacements
    prompt = prompt.replace('{name}', repositoryContext.name);
    prompt = prompt.replace('{description}', repositoryContext.description);
    
    // Handle languages
    const languagesText = repositoryContext.languages
      .map(l => `${l.language}: ${l.count} files`)
      .join('\n');
    prompt = prompt.replace('{languages}', languagesText);
    
    // Handle structure
    prompt = prompt.replace('{structure.classes}', repositoryContext.structure.classes);
    prompt = prompt.replace('{structure.functions}', repositoryContext.structure.functions);
    prompt = prompt.replace('{structure.methods}', repositoryContext.structure.methods);
    
    // Handle metrics
    prompt = prompt.replace('{metrics.totalFiles}', repositoryContext.metrics.totalFiles);
    prompt = prompt.replace('{metrics.totalLines}', repositoryContext.metrics.totalLines);
    prompt = prompt.replace('{metrics.averageComplexity}', repositoryContext.metrics.averageComplexity.toFixed(2));
    
    return prompt;
  }
}
```

### AI Interaction

Now we need to implement the interaction with AI models:

```javascript
const { Configuration, OpenAIApi } = require('openai');

class AIInteractor {
  constructor(config) {
    this.config = config;
    this.openai = this.initializeOpenAI(config.openai);
  }
  
  initializeOpenAI(config) {
    if (!config || !config.apiKey) {
      console.warn('OpenAI API key not provided');
      return null;
    }
    
    const configuration = new Configuration({
      apiKey: config.apiKey
    });
    
    return new OpenAIApi(configuration);
  }
  
  async analyzeWithAI(prompt, options = {}) {
    if (!this.openai) {
      return { success: false, error: 'OpenAI API not initialized' };
    }
    
    try {
      const response = await this.openai.createChatCompletion({
        model: options.model || 'gpt-4',
        messages: [
          { role: 'system', content: 'You are a code analysis expert.' },
          { role: 'user', content: prompt }
        ],
        temperature: options.temperature || 0.2,
        max_tokens: options.maxTokens || 2000
      });
      
      return {
        success: true,
        response: response.data.choices[0].message.content
      };
    } catch (error) {
      console.error('Error calling OpenAI API:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }
}
```

### Response Processing

Finally, we need to process the AI responses:

```javascript
class ResponseProcessor {
  processFileAnalysisResponse(response) {
    if (!response.success) {
      return { success: false, error: response.error };
    }
    
    try {
      // Parse the JSON response
      const findings = JSON.parse(response.response).findings;
      
      // Process and validate findings
      const processedFindings = findings.map(finding => ({
        title: finding.title,
        description: finding.description,
        location: finding.location,
        suggestion: finding.suggestion,
        priority: this.normalizePriority(finding.priority)
      }));
      
      return {
        success: true,
        findings: processedFindings
      };
    } catch (error) {
      console.error('Error processing AI response:', error.message);
      return {
        success: false,
        error: error.message,
        rawResponse: response.response
      };
    }
  }
  
  processRepositoryAnalysisResponse(response) {
    if (!response.success) {
      return { success: false, error: response.error };
    }
    
    try {
      // Parse the JSON response
      const findings = JSON.parse(response.response).findings;
      
      // Process and validate findings
      const processedFindings = findings.map(finding => ({
        title: finding.title,
        description: finding.description,
        area: finding.area,
        suggestion: finding.suggestion,
        priority: this.normalizePriority(finding.priority)
      }));
      
      return {
        success: true,
        findings: processedFindings
      };
    } catch (error) {
      console.error('Error processing AI response:', error.message);
      return {
        success: false,
        error: error.message,
        rawResponse: response.response
      };
    }
  }
  
  normalizePriority(priority) {
    // Normalize priority values
    const normalizedPriority = priority.toLowerCase();
    
    if (normalizedPriority.includes('critical')) return 'Critical';
    if (normalizedPriority.includes('high')) return 'High';
    if (normalizedPriority.includes('medium')) return 'Medium';
    if (normalizedPriority.includes('low')) return 'Low';
    
    return 'Medium'; // Default priority
  }
}
```

## Code Examples

### Complete AI Analysis Coordinator

Here's a more complete example of an AI Analysis Coordinator that combines the above components:

```javascript
// aiAnalysisCoordinator.js
const ContextPreparer = require('./ContextPreparer');
const PromptEngineer = require('./PromptEngineer');
const AIInteractor = require('./AIInteractor');
const ResponseProcessor = require('./ResponseProcessor');

class AIAnalysisCoordinator {
  constructor(config) {
    this.contextPreparer = new ContextPreparer();
    this.promptEngineer = new PromptEngineer();
    this.aiInteractor = new AIInteractor(config);
    this.responseProcessor = new ResponseProcessor();
  }
  
  async analyzeFile(file, analysisResult) {
    // Prepare context
    const fileContext = this.contextPreparer.prepareFileContext(file, analysisResult);
    
    // Create prompt
    const prompt = this.promptEngineer.createFileAnalysisPrompt(fileContext);
    
    // Call AI
    const aiResponse = await this.aiInteractor.analyzeWithAI(prompt);
    
    // Process response
    const processedResponse = this.responseProcessor.processFileAnalysisResponse(aiResponse);
    
    return {
      ...processedResponse,
      filePath: file.path
    };
  }
  
  async analyzeRepository(repositoryInfo, analysisResults) {
    // Prepare context
    const repositoryContext = this.contextPreparer.prepareRepositoryContext(repositoryInfo, analysisResults);
    
    // Create prompt
    const prompt = this.promptEngineer.createRepositoryAnalysisPrompt(repositoryContext);
    
    // Call AI
    const aiResponse = await this.aiInteractor.analyzeWithAI(prompt, { maxTokens: 4000 });
    
    // Process response
    const processedResponse = this.responseProcessor.processRepositoryAnalysisResponse(aiResponse);
    
    return {
      ...processedResponse,
      repositoryName: repositoryInfo.name
    };
  }
  
  async analyzeMultipleFiles(files, analysisResults) {
    const results = [];
    
    for (const file of files) {
      const analysisResult = analysisResults.find(r => r.path === file.path);
      if (!analysisResult || !analysisResult.success) continue;
      
      const result = await this.analyzeFile(file, analysisResult);
      results.push(result);
    }
    
    return results;
  }
  
  prioritizeFindings(fileResults, repositoryResult) {
    // Combine all findings
    const allFindings = [];
    
    // Add file-level findings
    fileResults.forEach(result => {
      if (result.success && result.findings) {
        result.findings.forEach(finding => {
          allFindings.push({
            ...finding,
            source: 'file',
            filePath: result.filePath
          });
        });
      }
    });
    
    // Add repository-level findings
    if (repositoryResult.success && repositoryResult.findings) {
      repositoryResult.findings.forEach(finding => {
        allFindings.push({
          ...finding,
          source: 'repository',
          area: finding.area
        });
      });
    }
    
    // Sort by priority
    const priorityOrder = { 'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3 };
    allFindings.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    
    return allFindings;
  }
}

module.exports = AIAnalysisCoordinator;
```

## Best Practices

1. **Prompt Engineering**: Craft clear, specific prompts that guide the AI to produce structured outputs
2. **Error Handling**: Implement robust error handling for AI API calls and response parsing
3. **Rate Limiting**: Respect API rate limits and implement backoff strategies
4. **Context Management**: Carefully manage context size to avoid token limits
5. **Response Validation**: Validate AI responses to ensure they match expected formats
6. **Fallback Mechanisms**: Implement fallbacks for when AI responses are unusable
7. **Prioritization**: Develop a clear system for prioritizing findings

## Integration Points

The AI Analysis Coordinator interfaces with:

1. **Code Analysis Engine**: Receives structured code analysis data
2. **Issue Management System**: Provides prioritized findings for issue creation
3. **Configuration Manager**: Receives AI model settings and analysis preferences

By implementing a robust AI Analysis Coordinator, the agent will be able to leverage AI capabilities to generate meaningful insights and recommendations from code analysis data, forming the basis for automated issue creation.
