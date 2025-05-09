// AI Analysis Coordinator Component
// This component coordinates AI model interactions for code analysis

const { Configuration, OpenAIApi } = require('openai');
const fs = require('fs').promises;
const path = require('path');

/**
 * ContextPreparer class
 * Prepares code context for AI analysis
 */
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

  prepareContent(content, language) {
    // Truncate content if it's too long
    if (content.length > this.options.maxContentLength) {
      return content.substring(0, this.options.maxContentLength) + '...';
    }
    return content;
  }

  summarizeStructure(structure) {
    if (!structure) return 'No structure information available';

    // Create a summary of the code structure
    const summary = [];

    if (structure.classes && structure.classes.length > 0) {
      summary.push(`Classes (${structure.classes.length}): ${structure.classes.map(c => c.name).join(', ')}`);
    }

    if (structure.functions && structure.functions.length > 0) {
      summary.push(`Functions (${structure.functions.length}): ${structure.functions.map(f => f.name).join(', ')}`);
    }

    if (structure.methods && structure.methods.length > 0) {
      summary.push(`Methods (${structure.methods.length}): ${structure.methods.map(m => m.name).join(', ')}`);
    }

    return summary.join('\n');
  }

  summarizeMetrics(metrics) {
    if (!metrics) return 'No metrics available';

    // Create a summary of the code metrics
    return `
      Lines of Code: ${metrics.lineCount || 0}
      Comment Ratio: ${metrics.commentRatio ? (metrics.commentRatio * 100).toFixed(2) + '%' : 'N/A'}
      Cyclomatic Complexity: ${metrics.cyclomaticComplexity || 'N/A'}
      Duplication Score: ${metrics.duplicationScore !== undefined ? metrics.duplicationScore + '%' : 'N/A'}
    `;
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
        if (result.structure.classes) {
          structure.classes += result.structure.classes.length || 0;
        }
        if (result.structure.functions) {
          structure.functions += result.structure.functions.length || 0;
        }
        if (result.structure.methods) {
          structure.methods += result.structure.methods.length || 0;
        }
      }
    });

    return structure;
  }

  summarizeRepositoryMetrics(analysisResults) {
    // Aggregate metrics
    let totalLines = 0;
    let totalComplexity = 0;
    let totalDuplicationScore = 0;
    let fileCount = 0;

    analysisResults.forEach(result => {
      if (result.success && result.metrics) {
        if (result.metrics.lineCount) {
          totalLines += result.metrics.lineCount;
        }
        if (result.metrics.cyclomaticComplexity) {
          totalComplexity += result.metrics.cyclomaticComplexity;
        }
        if (result.metrics.duplicationScore !== undefined) {
          totalDuplicationScore += result.metrics.duplicationScore;
        }
        fileCount++;
      }
    });

    return {
      totalFiles: fileCount,
      totalLines,
      averageComplexity: fileCount > 0 ? totalComplexity / fileCount : 0,
      averageDuplicationScore: fileCount > 0 ? totalDuplicationScore / fileCount : 0
    };
  }

  identifyFilePatterns(analysisResults) {
    // Identify common file patterns in the repository
    const patterns = {
      testFiles: 0,
      configFiles: 0,
      documentationFiles: 0,
      sourceFiles: 0
    };

    analysisResults.forEach(result => {
      if (!result.success) return;

      const filePath = result.path.toLowerCase();

      // Identify test files
      if (filePath.includes('test') || filePath.includes('spec') || filePath.includes('__tests__')) {
        patterns.testFiles++;
      }
      // Identify config files
      else if (filePath.includes('config') || filePath.endsWith('.json') || filePath.endsWith('.yaml') ||
               filePath.endsWith('.yml') || filePath.endsWith('.toml') || filePath.endsWith('.ini')) {
        patterns.configFiles++;
      }
      // Identify documentation files
      else if (filePath.endsWith('.md') || filePath.endsWith('.txt') || filePath.includes('docs/') ||
               filePath.includes('documentation/')) {
        patterns.documentationFiles++;
      }
      // Count remaining as source files
      else {
        patterns.sourceFiles++;
      }
    });

    return patterns;
  }
}

/**
 * PromptEngineer class
 * Creates effective prompts for AI models
 */
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
        console.warn(`Could not load file analysis template: ${error.message}`);
        this.templates.fileAnalysis = this.getDefaultFileTemplate();
      }

      try {
        this.templates.repositoryAnalysis = await fs.readFile(repoTemplatePath, 'utf8');
        console.log('Loaded repository analysis template from file');
      } catch (error) {
        console.warn(`Could not load repository analysis template: ${error.message}`);
        this.templates.repositoryAnalysis = this.getDefaultRepositoryTemplate();
      }
    } catch (error) {
      console.warn(`Error loading templates: ${error.message}`);
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

  fillTemplate(template, context) {
    // Replace placeholders in template with context values
    let filledTemplate = template;

    // Replace simple placeholders
    Object.entries(context).forEach(([key, value]) => {
      if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
        filledTemplate = filledTemplate.replace(new RegExp(`\\{\\{${key}\\}\\}`, 'g'), value);
      }
    });

    // Handle complex placeholders
    if (context.languages && Array.isArray(context.languages)) {
      let languagesText = '';
      context.languages.forEach(lang => {
        languagesText += `${lang.language}: ${lang.count} files\n`;
      });
      filledTemplate = filledTemplate.replace(/\{\{languagesList\}\}/g, languagesText);
    }

    if (context.structure) {
      const structureText = `
        Classes: ${context.structure.classes || 0}
        Functions: ${context.structure.functions || 0}
        Methods: ${context.structure.methods || 0}
      `;
      filledTemplate = filledTemplate.replace(/\{\{structureSummary\}\}/g, structureText);
    }

    if (context.metrics) {
      let metricsText = '';
      if (typeof context.metrics === 'string') {
        metricsText = context.metrics;
      } else {
        metricsText = `
          Total Files: ${context.metrics.totalFiles || 0}
          Total Lines: ${context.metrics.totalLines || 0}
          Average Complexity: ${(context.metrics.averageComplexity || 0).toFixed(2)}
          Average Duplication: ${(context.metrics.averageDuplicationScore || 0).toFixed(2)}%
        `;
      }
      filledTemplate = filledTemplate.replace(/\{\{metricsSummary\}\}/g, metricsText);
    }

    return filledTemplate;
  }

  getDefaultFileTemplate() {
    return `
      You are a code review expert analyzing a file in a repository.

      File: {{filePath}}
      Language: {{language}}

      Code Structure:
      {{structure}}

      Metrics:
      {{metrics}}

      Code Content:
      \`\`\`{{language}}
      {{content}}
      \`\`\`

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
    `;
  }

  getDefaultRepositoryTemplate() {
    return `
      You are a software architecture expert analyzing a repository.

      Repository: {{name}}
      Description: {{description}}

      {{languagesList}}

      Structure Summary:
      {{structureSummary}}

      Metrics:
      {{metricsSummary}}

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
    `;
  }

  getDefaultFilePrompt(fileContext) {
    // Create a prompt for file analysis
    return `
      You are a code review expert analyzing a file in a repository.

      File: ${fileContext.filePath}
      Language: ${fileContext.language}

      Code Structure:
      ${fileContext.structure}

      Metrics:
      ${fileContext.metrics}

      Code Content:
      \`\`\`${fileContext.language}
      ${fileContext.content}
      \`\`\`

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
    `;
  }

  getDefaultRepositoryPrompt(repositoryContext) {
    // Create a prompt for repository analysis
    let languagesText = 'Languages:\n';
    repositoryContext.languages.forEach(lang => {
      languagesText += `${lang.language}: ${lang.count} files\n`;
    });

    return `
      You are a software architecture expert analyzing a repository.

      Repository: ${repositoryContext.name}
      Description: ${repositoryContext.description}

      ${languagesText}

      Structure Summary:
      - Classes: ${repositoryContext.structure.classes}
      - Functions: ${repositoryContext.structure.functions}
      - Methods: ${repositoryContext.structure.methods}

      Metrics:
      - Total Files: ${repositoryContext.metrics.totalFiles}
      - Total Lines: ${repositoryContext.metrics.totalLines}
      - Average Complexity: ${repositoryContext.metrics.averageComplexity.toFixed(2)}
      - Average Duplication: ${repositoryContext.metrics.averageDuplicationScore.toFixed(2)}%

      File Patterns:
      - Source Files: ${repositoryContext.filePatterns.sourceFiles}
      - Test Files: ${repositoryContext.filePatterns.testFiles}
      - Config Files: ${repositoryContext.filePatterns.configFiles}
      - Documentation Files: ${repositoryContext.filePatterns.documentationFiles}

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
    `;
  }
}

/**
 * AIInteractor class
 * Handles API calls to AI models
 */
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
      console.log(`Calling OpenAI API with model: ${requestOptions.model}`);
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

  createMockResponse(prompt) {
    // Create a mock response based on the prompt content
    console.log('Creating mock AI response');

    // Simulate a delay to mimic API call
    return new Promise(resolve => {
      setTimeout(() => {
        if (prompt.includes('File:') || prompt.toLowerCase().includes('code review')) {
          // File analysis
          resolve({
            success: true,
            response: JSON.stringify({
              findings: [
                {
                  title: 'Missing error handling',
                  description: 'This code does not have proper error handling, which could lead to unhandled exceptions.',
                  location: 'Line 10-15',
                  suggestion: 'Add try/catch blocks or error handling middleware.',
                  priority: 'Medium'
                },
                {
                  title: 'Potential performance issue',
                  description: 'The loop implementation could be optimized for better performance.',
                  location: 'Line 20-25',
                  suggestion: 'Consider using a more efficient algorithm or caching results.',
                  priority: 'Low'
                }
              ]
            })
          });
        } else {
          // Repository analysis
          resolve({
            success: true,
            response: JSON.stringify({
              findings: [
                {
                  title: 'Missing documentation',
                  description: 'The repository lacks comprehensive documentation, making it difficult for new contributors.',
                  area: 'Repository-wide',
                  suggestion: 'Add a detailed README, code comments, and API documentation.',
                  priority: 'Medium'
                },
                {
                  title: 'Inconsistent code style',
                  description: 'Different files follow different code styles, making the codebase harder to maintain.',
                  area: 'Repository-wide',
                  suggestion: 'Implement a linter and code formatter with consistent rules.',
                  priority: 'Low'
                },
                {
                  title: 'Monolithic architecture',
                  description: 'The application is structured as a monolith, which could limit scalability.',
                  area: 'Architecture',
                  suggestion: 'Consider breaking down into microservices or modular components.',
                  priority: 'High'
                }
              ]
            })
          });
        }
      }, 100);
    });
  }
}

/**
 * ResponseProcessor class
 * Processes AI responses into structured findings
 */
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

  extractFindingsFromText(text) {
    // Fallback method to extract findings from non-JSON text
    const findings = [];

    // Look for patterns like "1. Finding Title" or "Finding Title:"
    const lines = text.split('\n');
    let currentFinding = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      // Check for new finding patterns
      const titleMatch = line.match(/^(\d+\.\s+|#+\s+)?([A-Z][^:]+)(:|\s+-)/);

      if (titleMatch && titleMatch[2]) {
        // Save previous finding if exists
        if (currentFinding && currentFinding.title) {
          findings.push(currentFinding);
        }

        // Start new finding
        currentFinding = {
          title: titleMatch[2].trim(),
          description: '',
          location: '',
          suggestion: '',
          priority: 'Medium'
        };

        // If this is a repository finding, use 'area' instead of 'location'
        if (text.includes('Repository') || text.includes('Architecture')) {
          currentFinding.area = 'Repository';
          delete currentFinding.location;
        }
      }
      // Look for priority indicators
      else if (currentFinding && line.toLowerCase().includes('priority')) {
        if (line.toLowerCase().includes('critical')) currentFinding.priority = 'Critical';
        else if (line.toLowerCase().includes('high')) currentFinding.priority = 'High';
        else if (line.toLowerCase().includes('medium')) currentFinding.priority = 'Medium';
        else if (line.toLowerCase().includes('low')) currentFinding.priority = 'Low';
      }
      // Look for location/area indicators
      else if (currentFinding && (line.toLowerCase().includes('location') || line.toLowerCase().includes('line'))) {
        const locationMatch = line.match(/(?:location|line|at):\s*(.+)/i);
        if (locationMatch && locationMatch[1]) {
          if (currentFinding.location !== undefined) {
            currentFinding.location = locationMatch[1].trim();
          } else if (currentFinding.area !== undefined) {
            currentFinding.area = locationMatch[1].trim();
          }
        }
      }
      // Look for suggestion indicators
      else if (currentFinding && line.toLowerCase().includes('suggestion')) {
        const suggestionMatch = line.match(/suggestion:\s*(.+)/i);
        if (suggestionMatch && suggestionMatch[1]) {
          currentFinding.suggestion = suggestionMatch[1].trim();
        }
      }
      // Add to description
      else if (currentFinding && line && !line.startsWith('#') && !line.match(/^(\d+\.)/)) {
        currentFinding.description += (currentFinding.description ? ' ' : '') + line;
      }
    }

    // Add the last finding if exists
    if (currentFinding && currentFinding.title) {
      findings.push(currentFinding);
    }

    return findings;
  }

  normalizePriority(priority) {
    // Normalize priority values
    const normalizedPriority = (priority || '').toLowerCase();

    if (normalizedPriority.includes('critical')) return 'Critical';
    if (normalizedPriority.includes('high')) return 'High';
    if (normalizedPriority.includes('medium')) return 'Medium';
    if (normalizedPriority.includes('low')) return 'Low';

    return 'Medium'; // Default priority
  }
}

/**
 * AIAnalysisCoordinator class
 * Main coordinator class that integrates all components
 */
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

  async analyzeRepository(repositoryInfo, analysisResults) {
    try {
      // Prepare repository context
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
    } catch (error) {
      console.error(`Error analyzing repository ${repositoryInfo.name}:`, error.message);
      return {
        success: false,
        error: error.message,
        repositoryName: repositoryInfo.name
      };
    }
  }

  async analyzeMultipleFiles(files, analysisResults) {
    const results = [];

    // Process files in batches to avoid rate limiting
    const batchSize = 5;
    for (let i = 0; i < files.length; i += batchSize) {
      const batch = files.slice(i, i + batchSize);

      // Process batch sequentially to avoid rate limiting
      for (const file of batch) {
        const analysisResult = analysisResults.find(r => r.path === file.path);
        if (!analysisResult || !analysisResult.success) continue;

        const result = await this.analyzeFile(file, analysisResult);
        results.push(result);

        // Add a small delay between requests to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      console.log(`Analyzed ${Math.min(i + batchSize, files.length)} of ${files.length} files`);
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
    if (repositoryResult && repositoryResult.success && repositoryResult.findings) {
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