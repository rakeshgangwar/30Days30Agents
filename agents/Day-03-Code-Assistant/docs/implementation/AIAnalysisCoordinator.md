# AIAnalysisCoordinator Implementation

## Overview

The AIAnalysisCoordinator is responsible for coordinating AI model interactions for code analysis. It has been refactored into a modular architecture with separate classes for different responsibilities.

## Components

### ContextPreparer

The ContextPreparer class prepares code context for AI analysis:

```javascript
class ContextPreparer {
  constructor(options = {}) {
    this.options = {
      maxContentLength: options.maxContentLength || 10000,
      ...options
    };
  }
  
  prepareFileContext(file, analysisResult) {
    // Create a structured context object
    const context = {
      filePath: file.path,
      language: analysisResult.language || 'unknown',
      structure: this.summarizeStructure(analysisResult.structure),
      metrics: this.summarizeMetrics(analysisResult.metrics),
      content: this.prepareContent(analysisResult.content || file.content, analysisResult.language)
    };
    
    return context;
  }
  
  prepareRepositoryContext(repositoryInfo, analysisResults) {
    // Create a summary of the repository
    const context = {
      name: repositoryInfo.name,
      description: repositoryInfo.description || `Repository ${repositoryInfo.name}`,
      languages: this.summarizeLanguages(analysisResults),
      structure: this.summarizeRepositoryStructure(analysisResults),
      metrics: this.summarizeRepositoryMetrics(analysisResults),
      filePatterns: this.identifyFilePatterns(analysisResults)
    };
    
    return context;
  }
  
  // ...helper methods for summarizing structure, metrics, etc.
}
```

### PromptEngineer

The PromptEngineer class creates effective prompts for AI models:

```javascript
class PromptEngineer {
  constructor(options = {}) {
    this.options = {
      templatePath: options.templatePath || path.join(process.cwd(), 'templates'),
      defaultTemplate: options.defaultTemplate || 'default',
      ...options
    };
    
    this.templates = {
      fileAnalysis: null,
      repositoryAnalysis: null
    };
    
    // Load templates
    this.loadTemplates();
  }
  
  async loadTemplates() {
    try {
      // Try to load templates from files
      const fileTemplatePath = path.join(this.options.templatePath, 'file-analysis.txt');
      const repoTemplatePath = path.join(this.options.templatePath, 'repository-analysis.txt');
      
      try {
        this.templates.fileAnalysis = await fs.readFile(fileTemplatePath, 'utf8');
        console.log('Loaded file analysis template from file');
      } catch (error) {
        this.templates.fileAnalysis = this.getDefaultFileTemplate();
      }
      
      try {
        this.templates.repositoryAnalysis = await fs.readFile(repoTemplatePath, 'utf8');
        console.log('Loaded repository analysis template from file');
      } catch (error) {
        this.templates.repositoryAnalysis = this.getDefaultRepositoryTemplate();
      }
    } catch (error) {
      // Use default templates
      this.templates.fileAnalysis = this.getDefaultFileTemplate();
      this.templates.repositoryAnalysis = this.getDefaultRepositoryTemplate();
    }
  }
  
  createFileAnalysisPrompt(fileContext) {
    // Use template if available, otherwise create a default prompt
    if (this.templates.fileAnalysis) {
      return this.fillTemplate(this.templates.fileAnalysis, fileContext);
    }
    
    return this.getDefaultFilePrompt(fileContext);
  }
  
  createRepositoryAnalysisPrompt(repositoryContext) {
    // Use template if available, otherwise create a default prompt
    if (this.templates.repositoryAnalysis) {
      return this.fillTemplate(this.templates.repositoryAnalysis, repositoryContext);
    }
    
    return this.getDefaultRepositoryPrompt(repositoryContext);
  }
  
  // ...helper methods for filling templates, etc.
}
```

### AIInteractor

The AIInteractor class handles API calls to AI models:

```javascript
class AIInteractor {
  constructor(config = {}) {
    this.config = {
      provider: config.provider || 'openai',
      model: config.model || 'gpt-4',
      temperature: config.temperature !== undefined ? config.temperature : 0.2,
      maxTokens: config.maxTokens || 2000,
      ...config
    };
    
    this.openaiApi = null;
    
    // Initialize AI provider
    if (this.config.provider === 'openai' && config.openai && config.openai.apiKey) {
      this.initializeOpenAI(config.openai);
    }
  }
  
  initializeOpenAI(config) {
    try {
      const configuration = new Configuration({
        apiKey: config.apiKey
      });
      
      this.openaiApi = new OpenAIApi(configuration);
      this.openaiInitialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize OpenAI client:', error.message);
      this.openaiInitialized = false;
      return false;
    }
  }
  
  async analyzeWithAI(prompt, options = {}) {
    if (!this.openaiInitialized || !this.openaiApi) {
      console.warn('OpenAI client not initialized, using mock response');
      return this.createMockResponse(prompt);
    }
    
    try {
      // Set up request parameters
      const requestOptions = {
        model: options.model || this.config.model,
        messages: [
          { role: 'system', content: 'You are a code analysis assistant that provides detailed, accurate analysis of code and repositories.' },
          { role: 'user', content: prompt }
        ],
        temperature: options.temperature !== undefined ? options.temperature : this.config.temperature,
        max_tokens: options.maxTokens || this.config.maxTokens,
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0
      };
      
      // Call OpenAI API
      const response = await this.openaiApi.createChatCompletion(requestOptions);
      
      // Extract and return the response content
      if (response.data && 
          response.data.choices && 
          response.data.choices.length > 0 && 
          response.data.choices[0].message) {
        return {
          success: true,
          response: response.data.choices[0].message.content,
          usage: response.data.usage
        };
      } else {
        throw new Error('Invalid response format from OpenAI API');
      }
    } catch (error) {
      console.error('Error calling OpenAI API:', error.message);
      
      // Fall back to mock response in case of error
      console.warn('Using mock response as fallback');
      return this.createMockResponse(prompt);
    }
  }
  
  // ...mock response creation
}
```

### ResponseProcessor

The ResponseProcessor class processes AI responses into structured findings:

```javascript
class ResponseProcessor {
  constructor(options = {}) {
    this.options = {
      ...options
    };
  }
  
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
        findings: processedFindings,
        usage: response.usage
      };
    } catch (error) {
      console.error('Error processing AI response:', error.message);
      
      // Try to extract findings using a more lenient approach
      try {
        const findings = this.extractFindingsFromText(response.response);
        if (findings.length > 0) {
          return {
            success: true,
            findings,
            extracted: true
          };
        }
      } catch (extractError) {
        console.error('Failed to extract findings from text:', extractError.message);
      }
      
      return {
        success: false,
        error: error.message,
        rawResponse: response.response
      };
    }
  }
  
  // ...similar method for repository analysis and helper methods
}
```

### AIAnalysisCoordinator

The main coordinator class that integrates all components:

```javascript
class AIAnalysisCoordinator {
  constructor(config = {}) {
    this.config = {
      provider: config.provider || 'openai',
      model: config.model || 'gpt-4',
      temperature: config.temperature !== undefined ? config.temperature : 0.2,
      maxTokens: config.maxTokens || 2000,
      promptTemplate: config.promptTemplate || 'default',
      ...config
    };
    
    // Initialize components
    this.contextPreparer = new ContextPreparer({
      maxContentLength: config.maxContentLength || 10000
    });
    
    this.promptEngineer = new PromptEngineer({
      templatePath: config.templatePath || path.join(process.cwd(), 'templates'),
      defaultTemplate: config.promptTemplate || 'default'
    });
    
    this.aiInteractor = new AIInteractor({
      provider: config.provider,
      model: config.model,
      temperature: config.temperature,
      maxTokens: config.maxTokens,
      openai: config.openai
    });
    
    this.responseProcessor = new ResponseProcessor();
  }
  
  async analyzeFile(file, analysisResult) {
    try {
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
    } catch (error) {
      console.error(`Error analyzing file ${file.path}:`, error.message);
      return {
        success: false,
        error: error.message,
        filePath: file.path
      };
    }
  }
  
  // ...similar method for repository analysis and helper methods
}
```

## Usage

```javascript
// Initialize the coordinator
const coordinator = new AIAnalysisCoordinator({
  provider: 'openai',
  model: 'gpt-4',
  openai: {
    apiKey: 'your-api-key'
  }
});

// Analyze a file
const fileAnalysisResult = await coordinator.analyzeFile(file, codeAnalysisResult);

// Analyze a repository
const repoAnalysisResult = await coordinator.analyzeRepository(repositoryInfo, analysisResults);

// Analyze multiple files
const fileAnalysisResults = await coordinator.analyzeMultipleFiles(files, analysisResults);

// Prioritize findings
const prioritizedFindings = coordinator.prioritizeFindings(fileAnalysisResults, repoAnalysisResult);
```
