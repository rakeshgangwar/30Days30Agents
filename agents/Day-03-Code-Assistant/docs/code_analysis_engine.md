# Code Analysis Engine

This document provides implementation details for the Code Analysis Engine of the Repository Analysis and Issue Creation Agent. This component is responsible for parsing and analyzing code to extract structure, identify patterns, and detect potential issues.

## Table of Contents

1. [Overview](#overview)
2. [Key Responsibilities](#key-responsibilities)
3. [Implementation Details](#implementation-details)
4. [Code Examples](#code-examples)
5. [Best Practices](#best-practices)
6. [Integration Points](#integration-points)

## Overview

The Code Analysis Engine is the core component that processes source code files to extract meaningful information about the codebase structure, quality, and patterns. It leverages language-specific parsers and analysis tools to provide a rich understanding of the code that can be used by the AI Analysis Coordinator for deeper insights.

## Key Responsibilities

- **Code Parsing**: Parse source code into abstract syntax trees (ASTs)
- **Structure Extraction**: Extract code structure (classes, functions, modules)
- **Pattern Detection**: Identify common patterns and anti-patterns
- **Metrics Calculation**: Calculate code quality metrics
- **Dependency Analysis**: Analyze dependencies between components
- **Issue Detection**: Identify potential bugs, code smells, and security issues

## Implementation Details

### Code Parsing with Tree-sitter

Drawing inspiration from Cline's use of Tree-sitter, we can implement a language-agnostic code parsing system:

```javascript
const Parser = require('web-tree-sitter');
const path = require('path');
const fs = require('fs').promises;

class CodeParser {
  constructor() {
    this.initialized = false;
    this.parsers = {};
  }
  
  async initialize() {
    if (this.initialized) return;
    
    await Parser.init();
    this.initialized = true;
    
    // Load language parsers as needed
    await this.loadLanguage('javascript');
    await this.loadLanguage('python');
    await this.loadLanguage('typescript');
    // Add more languages as needed
  }
  
  async loadLanguage(langName) {
    try {
      const langPath = path.join(__dirname, `parsers/tree-sitter-${langName}.wasm`);
      const language = await Parser.Language.load(langPath);
      
      const parser = new Parser();
      parser.setLanguage(language);
      
      this.parsers[langName] = {
        parser,
        language
      };
      
      return true;
    } catch (error) {
      console.error(`Failed to load language ${langName}: ${error.message}`);
      return false;
    }
  }
  
  async parseFile(filePath, content, languageHint = null) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    // Determine language from file extension if not provided
    const language = languageHint || this.detectLanguage(filePath);
    if (!language || !this.parsers[language]) {
      return { success: false, error: `Unsupported language: ${language || 'unknown'}` };
    }
    
    try {
      const { parser } = this.parsers[language];
      const tree = parser.parse(content);
      
      return {
        success: true,
        tree,
        language,
        path: filePath
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        language,
        path: filePath
      };
    }
  }
  
  detectLanguage(filePath) {
    const ext = path.extname(filePath).toLowerCase().slice(1);
    
    // Map file extensions to languages
    const extensionMap = {
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'py': 'python',
      'rb': 'ruby',
      'java': 'java',
      'go': 'go',
      'rs': 'rust',
      'c': 'c',
      'cpp': 'cpp',
      'h': 'c',
      'hpp': 'cpp',
      'cs': 'c_sharp',
      'php': 'php',
      'swift': 'swift',
      'kt': 'kotlin'
    };
    
    return extensionMap[ext] || null;
  }
}
```

### Structure Extraction

Once we have the AST, we can extract code structure using queries similar to Cline's approach:

```javascript
class StructureExtractor {
  constructor(codeParser) {
    this.codeParser = codeParser;
    this.queries = {};
    this.loadQueries();
  }
  
  loadQueries() {
    // Load language-specific queries
    this.queries.javascript = `
      (class_declaration
        name: (identifier) @name.definition.class
      ) @definition.class
      
      (function_declaration
        name: (identifier) @name.definition.function
      ) @definition.function
      
      (method_definition
        name: (property_identifier) @name.definition.method
      ) @definition.method
    `;
    
    this.queries.python = `
      (class_definition
        name: (identifier) @name.definition.class
      ) @definition.class
      
      (function_definition
        name: (identifier) @name.definition.function
      ) @definition.function
    `;
    
    // Add more language queries as needed
  }
  
  async extractStructure(filePath, content) {
    const parseResult = await this.codeParser.parseFile(filePath, content);
    if (!parseResult.success) {
      return { success: false, error: parseResult.error };
    }
    
    const { tree, language } = parseResult;
    const query = this.queries[language];
    
    if (!query) {
      return { success: false, error: `No query available for language: ${language}` };
    }
    
    try {
      const queryInstance = this.codeParser.parsers[language].language.query(query);
      const captures = queryInstance.captures(tree.rootNode);
      
      // Process captures to extract structure
      const structure = this.processCaptures(captures, content);
      
      return {
        success: true,
        structure,
        language,
        path: filePath
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        language,
        path: filePath
      };
    }
  }
  
  processCaptures(captures, content) {
    // Sort captures by position
    captures.sort((a, b) => a.node.startPosition.row - b.node.startPosition.row);
    
    const lines = content.split('\n');
    const structure = {
      classes: [],
      functions: [],
      methods: []
    };
    
    captures.forEach(capture => {
      const { node, name } = capture;
      const startLine = node.startPosition.row;
      const endLine = node.endPosition.row;
      const text = lines[startLine];
      
      if (name.includes('class')) {
        structure.classes.push({
          name: node.text,
          line: startLine + 1,
          text
        });
      } else if (name.includes('function')) {
        structure.functions.push({
          name: node.text,
          line: startLine + 1,
          text
        });
      } else if (name.includes('method')) {
        structure.methods.push({
          name: node.text,
          line: startLine + 1,
          text
        });
      }
    });
    
    return structure;
  }
}
```

### Metrics Calculation

We can implement code quality metrics calculation:

```javascript
class CodeMetricsCalculator {
  calculateMetrics(content, language) {
    const metrics = {
      lineCount: this.countLines(content),
      commentRatio: this.calculateCommentRatio(content, language),
      cyclomaticComplexity: this.calculateCyclomaticComplexity(content, language),
      // Add more metrics as needed
    };
    
    return metrics;
  }
  
  countLines(content) {
    return content.split('\n').length;
  }
  
  calculateCommentRatio(content, language) {
    // Implementation depends on language
    // This is a simplified example
    let commentLines = 0;
    const lines = content.split('\n');
    
    const commentPatterns = {
      'javascript': [/^\s*\/\//, /^\s*\/\*/, /\*\//],
      'python': [/^\s*#/],
      // Add more languages as needed
    };
    
    const patterns = commentPatterns[language] || [];
    
    lines.forEach(line => {
      for (const pattern of patterns) {
        if (pattern.test(line)) {
          commentLines++;
          break;
        }
      }
    });
    
    return commentLines / lines.length;
  }
  
  calculateCyclomaticComplexity(content, language) {
    // Simplified implementation
    // In a real implementation, this would analyze the AST
    
    const complexityPatterns = {
      'javascript': [/if\s*\(/, /else/, /for\s*\(/, /while\s*\(/, /case\s+/, /catch\s*\(/, /\?\s*/, /&&/, /\|\|/],
      'python': [/if\s+/, /elif\s+/, /else\s*:/, /for\s+/, /while\s+/, /except\s+/, /and\s+/, /or\s+/],
      // Add more languages as needed
    };
    
    const patterns = complexityPatterns[language] || [];
    let complexity = 1; // Base complexity
    
    patterns.forEach(pattern => {
      const matches = content.match(pattern) || [];
      complexity += matches.length;
    });
    
    return complexity;
  }
}
```

## Code Examples

### Complete Code Analysis Engine

Here's a more complete example of a Code Analysis Engine that combines the above components:

```javascript
// codeAnalysisEngine.js
const CodeParser = require('./CodeParser');
const StructureExtractor = require('./StructureExtractor');
const CodeMetricsCalculator = require('./CodeMetricsCalculator');

class CodeAnalysisEngine {
  constructor() {
    this.parser = new CodeParser();
    this.structureExtractor = new StructureExtractor(this.parser);
    this.metricsCalculator = new CodeMetricsCalculator();
  }
  
  async initialize() {
    await this.parser.initialize();
  }
  
  async analyzeFile(filePath, content) {
    try {
      // Extract code structure
      const structureResult = await this.structureExtractor.extractStructure(filePath, content);
      
      // Calculate metrics
      const language = this.parser.detectLanguage(filePath);
      const metrics = this.metricsCalculator.calculateMetrics(content, language);
      
      // Combine results
      return {
        success: true,
        path: filePath,
        language,
        structure: structureResult.success ? structureResult.structure : null,
        metrics,
        content: content.substring(0, 1000) + (content.length > 1000 ? '...' : '') // Include truncated content for context
      };
    } catch (error) {
      return {
        success: false,
        path: filePath,
        error: error.message
      };
    }
  }
  
  async analyzeFiles(files) {
    const results = [];
    
    for (const file of files) {
      const result = await this.analyzeFile(file.path, file.content);
      results.push(result);
    }
    
    return results;
  }
  
  generateCodebaseOverview(analysisResults) {
    // Aggregate analysis results to create a codebase overview
    const overview = {
      fileCount: analysisResults.length,
      languageBreakdown: {},
      totalLines: 0,
      averageComplexity: 0,
      structureSummary: {
        classes: 0,
        functions: 0,
        methods: 0
      }
    };
    
    // Calculate aggregates
    analysisResults.forEach(result => {
      if (!result.success) return;
      
      // Count languages
      overview.languageBreakdown[result.language] = (overview.languageBreakdown[result.language] || 0) + 1;
      
      // Sum lines
      overview.totalLines += result.metrics.lineCount;
      
      // Sum complexity
      overview.averageComplexity += result.metrics.cyclomaticComplexity;
      
      // Sum structure elements
      if (result.structure) {
        overview.structureSummary.classes += result.structure.classes.length;
        overview.structureSummary.functions += result.structure.functions.length;
        overview.structureSummary.methods += result.structure.methods.length;
      }
    });
    
    // Calculate averages
    const successfulAnalyses = analysisResults.filter(r => r.success).length;
    if (successfulAnalyses > 0) {
      overview.averageComplexity /= successfulAnalyses;
    }
    
    return overview;
  }
}

module.exports = CodeAnalysisEngine;
```

## Best Practices

1. **Language Agnosticism**: Support multiple programming languages
2. **Performance Optimization**: Use efficient parsing techniques for large codebases
3. **Memory Management**: Handle large files and repositories without excessive memory usage
4. **Error Tolerance**: Continue analysis even if some files fail to parse
5. **Extensibility**: Design for easy addition of new languages and analysis techniques
6. **Caching**: Cache parsing results for improved performance
7. **Incremental Analysis**: Support analyzing only changed files in subsequent runs

## Integration Points

The Code Analysis Engine interfaces with:

1. **Repository Access Layer**: Receives file contents for analysis
2. **AI Analysis Coordinator**: Provides analysis results for AI processing
3. **Configuration Manager**: Receives settings for analysis depth and focus

By implementing a robust Code Analysis Engine, the agent will be able to extract meaningful information from codebases across multiple languages, providing a solid foundation for AI-powered analysis and issue creation.
