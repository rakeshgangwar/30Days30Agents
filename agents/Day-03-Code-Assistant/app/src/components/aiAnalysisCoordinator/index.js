// AI Analysis Coordinator Component
// This component coordinates AI model interactions for code analysis

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
    
    // Initialize OpenAI client if credentials are provided
    if (config.openai && config.openai.apiKey) {
      this.initializeOpenAI(config.openai);
    }
  }
  
  initializeOpenAI(config) {
    try {
      // In a real implementation, we would initialize the OpenAI client here
      // For now, we'll just set a flag
      this.openaiInitialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize OpenAI client:', error.message);
      this.openaiInitialized = false;
      return false;
    }
  }
  
  async analyzeFile(file, analysisResult) {
    try {
      // Prepare context
      const fileContext = this.prepareFileContext(file, analysisResult);
      
      // Create prompt
      const prompt = this.createFileAnalysisPrompt(fileContext);
      
      // Call AI
      const aiResponse = await this.callAI(prompt);
      
      // Process response
      const processedResponse = this.processFileAnalysisResponse(aiResponse);
      
      return {
        ...processedResponse,
        filePath: file.path
      };
    } catch (error) {
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
      const repositoryContext = this.prepareRepositoryContext(repositoryInfo, analysisResults);
      
      // Create prompt
      const prompt = this.createRepositoryAnalysisPrompt(repositoryContext);
      
      // Call AI
      const aiResponse = await this.callAI(prompt, { maxTokens: 4000 });
      
      // Process response
      const processedResponse = this.processRepositoryAnalysisResponse(aiResponse);
      
      return {
        ...processedResponse,
        repositoryName: repositoryInfo.name
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        repositoryName: repositoryInfo.name
      };
    }
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
  
  prepareFileContext(file, analysisResult) {
    // Create a structured context object
    const context = {
      filePath: file.path,
      language: analysisResult.language || 'unknown',
      structure: this.summarizeStructure(analysisResult.structure),
      metrics: this.summarizeMetrics(analysisResult.metrics),
      content: analysisResult.content || file.content
    };
    
    return context;
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
    `;
  }
  
  prepareRepositoryContext(repositoryInfo, analysisResults) {
    // Create a summary of the repository
    const context = {
      name: repositoryInfo.name,
      description: repositoryInfo.description || `Repository ${repositoryInfo.name}`,
      languages: this.summarizeLanguages(analysisResults),
      structure: this.summarizeRepositoryStructure(analysisResults),
      metrics: this.summarizeRepositoryMetrics(analysisResults)
    };
    
    return context;
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
    let fileCount = 0;
    
    analysisResults.forEach(result => {
      if (result.success && result.metrics) {
        if (result.metrics.lineCount) {
          totalLines += result.metrics.lineCount;
        }
        if (result.metrics.cyclomaticComplexity) {
          totalComplexity += result.metrics.cyclomaticComplexity;
        }
        fileCount++;
      }
    });
    
    return {
      totalFiles: fileCount,
      totalLines,
      averageComplexity: fileCount > 0 ? totalComplexity / fileCount : 0
    };
  }
  
  createFileAnalysisPrompt(fileContext) {
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
  
  createRepositoryAnalysisPrompt(repositoryContext) {
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
  
  async callAI(prompt, options = {}) {
    if (!this.openaiInitialized) {
      return {
        success: false,
        error: 'OpenAI client not initialized'
      };
    }
    
    try {
      // In a real implementation, we would call the OpenAI API here
      // For now, we'll return some mock data
      
      // Mock implementation with a delay to simulate API call
      await new Promise(resolve => setTimeout(resolve, 100));
      
      return {
        success: true,
        response: this.createMockResponse(prompt)
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  createMockResponse(prompt) {
    // Create a mock response based on the prompt content
    if (prompt.includes('File:')) {
      // File analysis
      return JSON.stringify({
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
      });
    } else {
      // Repository analysis
      return JSON.stringify({
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
      });
    }
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
    const normalizedPriority = (priority || '').toLowerCase();
    
    if (normalizedPriority.includes('critical')) return 'Critical';
    if (normalizedPriority.includes('high')) return 'High';
    if (normalizedPriority.includes('medium')) return 'Medium';
    if (normalizedPriority.includes('low')) return 'Low';
    
    return 'Medium'; // Default priority
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