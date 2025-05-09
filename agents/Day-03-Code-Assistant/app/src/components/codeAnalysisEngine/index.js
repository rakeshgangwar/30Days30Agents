// Code Analysis Engine Component
// This component parses and analyzes code structure and quality

const Parser = require('web-tree-sitter');
const fs = require('fs').promises;
const path = require('path');
const { promisify } = require('util');
const glob = promisify(require('glob'));

class CodeAnalysisEngine {
  constructor(options = {}) {
    this.initialized = false;
    this.parsers = {};
    this.languages = [];
    this.options = {
      parsersPath: options.parsersPath || path.join(process.cwd(), 'parsers'),
      ...options
    };
  }

  async initialize() {
    if (this.initialized) return true;

    try {
      // Initialize Tree-sitter
      await Parser.init();

      // Load language parsers
      await this.loadLanguageParsers();

      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize CodeAnalysisEngine:', error.message);
      return false;
    }
  }

  async loadLanguageParsers() {
    // Define supported languages and their parser files
    const languageParsers = [
      { name: 'javascript', file: 'tree-sitter-javascript.wasm' },
      { name: 'typescript', file: 'tree-sitter-typescript.wasm' },
      { name: 'python', file: 'tree-sitter-python.wasm' },
      { name: 'java', file: 'tree-sitter-java.wasm' },
      { name: 'go', file: 'tree-sitter-go.wasm' },
      { name: 'ruby', file: 'tree-sitter-ruby.wasm' },
      { name: 'c', file: 'tree-sitter-c.wasm' },
      { name: 'cpp', file: 'tree-sitter-cpp.wasm' },
      { name: 'csharp', file: 'tree-sitter-c_sharp.wasm' },
      { name: 'php', file: 'tree-sitter-php.wasm' },
      { name: 'rust', file: 'tree-sitter-rust.wasm' },
      { name: 'markdown', file: 'tree-sitter-markdown.wasm' }
    ];

    // Check if parsers directory exists
    try {
      await fs.access(this.options.parsersPath);
    } catch (error) {
      console.warn(`Parsers directory not found: ${this.options.parsersPath}`);
      console.warn('Using mock parsers instead');
      this.languages = languageParsers.map(lang => lang.name);
      return;
    }

    // Load each parser
    for (const langParser of languageParsers) {
      try {
        const parserPath = path.join(this.options.parsersPath, langParser.file);

        // Check if parser file exists
        try {
          await fs.access(parserPath);
        } catch (error) {
          console.warn(`Parser file not found: ${parserPath}`);
          continue;
        }

        // Load parser
        const parser = new Parser();
        const language = await Parser.Language.load(parserPath);
        parser.setLanguage(language);

        this.parsers[langParser.name] = parser;
        this.languages.push(langParser.name);

        console.log(`Loaded parser for ${langParser.name}`);
      } catch (error) {
        console.warn(`Failed to load parser for ${langParser.name}:`, error.message);
      }
    }

    console.log(`Loaded ${this.languages.length} language parsers`);
  }

  async analyzeFile(filePath, content) {
    try {
      // Detect language based on file extension
      const language = this.detectLanguage(filePath);

      // Check if we support this language
      if (!language) {
        return {
          success: false,
          path: filePath,
          error: 'Unsupported language',
          language: null
        };
      }

      let structure;

      // Use Tree-sitter parser if available, otherwise fall back to mock
      if (this.parsers[language]) {
        structure = await this.parseWithTreeSitter(language, content);
      } else {
        console.warn(`No parser available for ${language}, using mock structure`);
        structure = this.mockStructure(language, content);
      }

      // Calculate metrics
      const metrics = this.calculateMetrics(language, content, structure);

      // Truncate content for response
      const truncatedContent = content.length > 10000
        ? content.substring(0, 10000) + '...'
        : content;

      return {
        success: true,
        path: filePath,
        language,
        structure,
        metrics,
        content: truncatedContent
      };
    } catch (error) {
      return {
        success: false,
        path: filePath,
        error: error.message,
        language: this.detectLanguage(filePath)
      };
    }
  }

  async parseWithTreeSitter(language, content) {
    try {
      const parser = this.parsers[language];
      const tree = parser.parse(content);
      const rootNode = tree.rootNode;

      // Extract structure based on language
      const structure = {
        classes: [],
        functions: [],
        methods: []
      };

      // Use language-specific queries to extract structure
      if (language === 'javascript' || language === 'typescript') {
        this.extractJavaScriptStructure(rootNode, structure, content);
      } else if (language === 'python') {
        this.extractPythonStructure(rootNode, structure, content);
      } else if (language === 'java') {
        this.extractJavaStructure(rootNode, structure, content);
      } else if (language === 'go') {
        this.extractGoStructure(rootNode, structure, content);
      } else {
        // Generic structure extraction for other languages
        this.extractGenericStructure(rootNode, structure, content);
      }

      return structure;
    } catch (error) {
      console.error(`Error parsing with Tree-sitter: ${error.message}`);
      // Fall back to mock structure
      return this.mockStructure(language, content);
    }
  }

  extractJavaScriptStructure(rootNode, structure, content) {
    // Extract classes
    this.queryNodesByType(rootNode, 'class_declaration', (node) => {
      const nameNode = node.childForFieldName('name');
      if (nameNode) {
        const name = content.substring(nameNode.startIndex, nameNode.endIndex);
        const lineNumber = this.getLineNumber(content, node.startIndex);
        const text = content.substring(node.startIndex, node.endIndex).split('\n')[0] + '...';

        structure.classes.push({
          name,
          line: lineNumber,
          text
        });
      }
    });

    // Extract functions
    this.queryNodesByType(rootNode, 'function_declaration', (node) => {
      const nameNode = node.childForFieldName('name');
      if (nameNode) {
        const name = content.substring(nameNode.startIndex, nameNode.endIndex);
        const lineNumber = this.getLineNumber(content, node.startIndex);
        const text = content.substring(node.startIndex, node.endIndex).split('\n')[0] + '...';

        structure.functions.push({
          name,
          line: lineNumber,
          text
        });
      }
    });

    // Extract methods
    this.queryNodesByType(rootNode, 'method_definition', (node) => {
      const nameNode = node.childForFieldName('name');
      if (nameNode) {
        const name = content.substring(nameNode.startIndex, nameNode.endIndex);
        const lineNumber = this.getLineNumber(content, node.startIndex);
        const text = content.substring(node.startIndex, node.endIndex).split('\n')[0] + '...';

        structure.methods.push({
          name,
          line: lineNumber,
          text
        });
      }
    });
  }

  extractPythonStructure(rootNode, structure, content) {
    // Extract classes
    this.queryNodesByType(rootNode, 'class_definition', (node) => {
      const nameNode = node.childForFieldName('name');
      if (nameNode) {
        const name = content.substring(nameNode.startIndex, nameNode.endIndex);
        const lineNumber = this.getLineNumber(content, node.startIndex);
        const text = content.substring(node.startIndex, node.endIndex).split('\n')[0] + '...';

        structure.classes.push({
          name,
          line: lineNumber,
          text
        });
      }
    });

    // Extract functions
    this.queryNodesByType(rootNode, 'function_definition', (node) => {
      // Skip methods (functions inside classes)
      let parent = node.parent;
      let isMethod = false;
      while (parent) {
        if (parent.type === 'class_definition') {
          isMethod = true;
          break;
        }
        parent = parent.parent;
      }

      if (!isMethod) {
        const nameNode = node.childForFieldName('name');
        if (nameNode) {
          const name = content.substring(nameNode.startIndex, nameNode.endIndex);
          const lineNumber = this.getLineNumber(content, node.startIndex);
          const text = content.substring(node.startIndex, node.endIndex).split('\n')[0] + '...';

          structure.functions.push({
            name,
            line: lineNumber,
            text
          });
        }
      } else {
        // It's a method
        const nameNode = node.childForFieldName('name');
        if (nameNode) {
          const name = content.substring(nameNode.startIndex, nameNode.endIndex);
          const lineNumber = this.getLineNumber(content, node.startIndex);
          const text = content.substring(node.startIndex, node.endIndex).split('\n')[0] + '...';

          structure.methods.push({
            name,
            line: lineNumber,
            text
          });
        }
      }
    });
  }

  extractJavaStructure(rootNode, structure, content) {
    // Extract classes
    this.queryNodesByType(rootNode, 'class_declaration', (node) => {
      const nameNode = node.childForFieldName('name');
      if (nameNode) {
        const name = content.substring(nameNode.startIndex, nameNode.endIndex);
        const lineNumber = this.getLineNumber(content, node.startIndex);
        const text = content.substring(node.startIndex, Math.min(node.startIndex + 100, node.endIndex)).split('\n')[0] + '...';

        structure.classes.push({
          name,
          line: lineNumber,
          text
        });
      }
    });

    // Extract methods
    this.queryNodesByType(rootNode, 'method_declaration', (node) => {
      const nameNode = node.childForFieldName('name');
      if (nameNode) {
        const name = content.substring(nameNode.startIndex, nameNode.endIndex);
        const lineNumber = this.getLineNumber(content, node.startIndex);
        const text = content.substring(node.startIndex, Math.min(node.startIndex + 100, node.endIndex)).split('\n')[0] + '...';

        structure.methods.push({
          name,
          line: lineNumber,
          text
        });
      }
    });
  }

  extractGoStructure(rootNode, structure, content) {
    // Extract structs (similar to classes)
    this.queryNodesByType(rootNode, 'type_declaration', (node) => {
      const specNode = node.childForFieldName('type');
      if (specNode && specNode.type === 'type_spec' && specNode.childForFieldName('type').type === 'struct_type') {
        const nameNode = specNode.childForFieldName('name');
        if (nameNode) {
          const name = content.substring(nameNode.startIndex, nameNode.endIndex);
          const lineNumber = this.getLineNumber(content, node.startIndex);
          const text = content.substring(node.startIndex, Math.min(node.startIndex + 100, node.endIndex)).split('\n')[0] + '...';

          structure.classes.push({
            name,
            line: lineNumber,
            text
          });
        }
      }
    });

    // Extract functions
    this.queryNodesByType(rootNode, 'function_declaration', (node) => {
      const nameNode = node.childForFieldName('name');
      if (nameNode) {
        const name = content.substring(nameNode.startIndex, nameNode.endIndex);
        const lineNumber = this.getLineNumber(content, node.startIndex);
        const text = content.substring(node.startIndex, Math.min(node.startIndex + 100, node.endIndex)).split('\n')[0] + '...';

        // Check if it's a method (has a receiver)
        const receiverNode = node.childForFieldName('receiver');
        if (receiverNode) {
          structure.methods.push({
            name,
            line: lineNumber,
            text
          });
        } else {
          structure.functions.push({
            name,
            line: lineNumber,
            text
          });
        }
      }
    });
  }

  extractGenericStructure(rootNode, structure, content) {
    // Try to extract common patterns across languages

    // Look for class-like structures
    ['class_declaration', 'class_definition', 'struct_declaration', 'interface_declaration'].forEach(type => {
      this.queryNodesByType(rootNode, type, (node) => {
        // Try to find the name in various ways
        let name = null;
        let nameNode = node.childForFieldName('name');

        if (nameNode) {
          name = content.substring(nameNode.startIndex, nameNode.endIndex);
        } else {
          // Try to find a name by looking at children with 'identifier' type
          for (let i = 0; i < node.childCount; i++) {
            const child = node.child(i);
            if (child.type === 'identifier') {
              name = content.substring(child.startIndex, child.endIndex);
              break;
            }
          }
        }

        if (name) {
          const lineNumber = this.getLineNumber(content, node.startIndex);
          const text = content.substring(node.startIndex, Math.min(node.startIndex + 100, node.endIndex)).split('\n')[0] + '...';

          structure.classes.push({
            name,
            line: lineNumber,
            text
          });
        }
      });
    });

    // Look for function-like structures
    ['function_declaration', 'function_definition', 'method_declaration', 'method_definition'].forEach(type => {
      this.queryNodesByType(rootNode, type, (node) => {
        // Try to find the name in various ways
        let name = null;
        let nameNode = node.childForFieldName('name');

        if (nameNode) {
          name = content.substring(nameNode.startIndex, nameNode.endIndex);
        } else {
          // Try to find a name by looking at children with 'identifier' type
          for (let i = 0; i < node.childCount; i++) {
            const child = node.child(i);
            if (child.type === 'identifier') {
              name = content.substring(child.startIndex, child.endIndex);
              break;
            }
          }
        }

        if (name) {
          const lineNumber = this.getLineNumber(content, node.startIndex);
          const text = content.substring(node.startIndex, Math.min(node.startIndex + 100, node.endIndex)).split('\n')[0] + '...';

          // Determine if it's a method or function
          let isMethod = false;
          let parent = node.parent;
          while (parent) {
            if (parent.type.includes('class') || parent.type.includes('struct') || parent.type.includes('interface')) {
              isMethod = true;
              break;
            }
            parent = parent.parent;
          }

          if (isMethod) {
            structure.methods.push({
              name,
              line: lineNumber,
              text
            });
          } else {
            structure.functions.push({
              name,
              line: lineNumber,
              text
            });
          }
        }
      });
    });
  }

  queryNodesByType(node, type, callback) {
    if (node.type === type) {
      callback(node);
    }

    for (let i = 0; i < node.childCount; i++) {
      this.queryNodesByType(node.child(i), type, callback);
    }
  }

  getLineNumber(content, index) {
    // Count newlines up to the index
    const textUpToIndex = content.substring(0, index);
    return (textUpToIndex.match(/\n/g) || []).length + 1;
  }

  calculateMetrics(language, content, structure) {
    const lines = content.split('\n');

    // Count comment lines based on language
    let commentLines = 0;
    let inBlockComment = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      if (language === 'javascript' || language === 'typescript' || language === 'java' ||
          language === 'c' || language === 'cpp' || language === 'csharp') {
        // Check for block comments
        if (inBlockComment) {
          commentLines++;
          if (line.includes('*/')) {
            inBlockComment = false;
          }
        } else if (line.startsWith('//')) {
          commentLines++;
        } else if (line.startsWith('/*')) {
          commentLines++;
          if (!line.includes('*/')) {
            inBlockComment = true;
          }
        } else if (line.startsWith('*') && line.endsWith('*/')) {
          commentLines++;
          inBlockComment = false;
        } else if (line.startsWith('*')) {
          commentLines++;
        }
      } else if (language === 'python') {
        // Check for Python comments
        if (line.startsWith('#')) {
          commentLines++;
        } else if (line.startsWith('"""') || line.startsWith("'''")) {
          commentLines++;
          // Check if the docstring ends on the same line
          if ((line.startsWith('"""') && line.endsWith('"""') && line.length > 3) ||
              (line.startsWith("'''") && line.endsWith("'''") && line.length > 3)) {
            // Single line docstring
          } else {
            // Multi-line docstring - find the end
            const docStringDelimiter = line.startsWith('"""') ? '"""' : "'''";
            let j = i + 1;
            while (j < lines.length) {
              commentLines++;
              if (lines[j].trim().endsWith(docStringDelimiter)) {
                break;
              }
              j++;
            }
            i = j; // Skip to the end of the docstring
          }
        }
      } else if (language === 'go') {
        // Check for Go comments
        if (line.startsWith('//')) {
          commentLines++;
        } else if (line.startsWith('/*')) {
          commentLines++;
          if (!line.includes('*/')) {
            inBlockComment = true;
          }
        } else if (inBlockComment) {
          commentLines++;
          if (line.includes('*/')) {
            inBlockComment = false;
          }
        }
      }
    }

    // Calculate cyclomatic complexity
    let complexity = 1; // Base complexity

    // Define complexity patterns based on language
    const complexityPatterns = [];

    if (language === 'javascript' || language === 'typescript' || language === 'java' ||
        language === 'c' || language === 'cpp' || language === 'csharp') {
      complexityPatterns.push(
        /if\s*\(/g,
        /else\s+if/g,
        /else/g,
        /for\s*\(/g,
        /while\s*\(/g,
        /switch\s*\(/g,
        /case\s+/g,
        /catch\s*\(/g,
        /\?\s*/g,
        /&&/g,
        /\|\|/g
      );
    } else if (language === 'python') {
      complexityPatterns.push(
        /if\s+/g,
        /elif\s+/g,
        /else:/g,
        /for\s+/g,
        /while\s+/g,
        /except\s+/g,
        /and\s+/g,
        /or\s+/g
      );
    } else if (language === 'go') {
      complexityPatterns.push(
        /if\s+/g,
        /else\s+if/g,
        /else\s*{/g,
        /for\s+/g,
        /switch\s+/g,
        /case\s+/g,
        /&&/g,
        /\|\|/g
      );
    }

    // Calculate complexity
    complexityPatterns.forEach(pattern => {
      const matches = content.match(pattern) || [];
      complexity += matches.length;
    });

    // Calculate additional metrics
    const linesOfCode = lines.length;
    const commentRatio = commentLines / (linesOfCode || 1);

    // Calculate code duplication (simplified)
    const duplicationScore = this.calculateDuplicationScore(content);

    return {
      lineCount: linesOfCode,
      commentCount: commentLines,
      commentRatio: commentRatio,
      cyclomaticComplexity: complexity,
      duplicationScore: duplicationScore,
      classCount: structure.classes.length,
      functionCount: structure.functions.length,
      methodCount: structure.methods.length
    };
  }

  calculateDuplicationScore(content) {
    // Simplified duplication detection
    // In a real implementation, we would use a more sophisticated algorithm

    // Split content into lines and normalize
    const lines = content.split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0 && !line.startsWith('//') && !line.startsWith('#'));

    // Count duplicated lines
    const lineMap = new Map();
    let duplicatedLines = 0;

    lines.forEach(line => {
      if (line.length > 10) { // Only consider non-trivial lines
        const count = lineMap.get(line) || 0;
        if (count > 0) {
          duplicatedLines++;
        }
        lineMap.set(line, count + 1);
      }
    });

    // Calculate duplication score (0-100)
    return Math.min(100, Math.round((duplicatedLines / (lines.length || 1)) * 100));
  }

  async analyzeFiles(files) {
    if (!this.initialized) {
      await this.initialize();
    }

    const results = [];

    // Process files in batches to avoid memory issues
    const batchSize = 10;
    for (let i = 0; i < files.length; i += batchSize) {
      const batch = files.slice(i, i + batchSize);

      // Process batch in parallel
      const batchResults = await Promise.all(
        batch.map(file => this.analyzeFile(file.path, file.content))
      );

      results.push(...batchResults);

      // Log progress
      console.log(`Analyzed ${Math.min(i + batchSize, files.length)} of ${files.length} files`);
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
      averageDuplicationScore: 0,
      commentRatio: 0,
      structureSummary: {
        classes: 0,
        functions: 0,
        methods: 0
      },
      complexityDistribution: {
        low: 0,    // 1-10
        medium: 0, // 11-20
        high: 0,   // 21-50
        veryHigh: 0 // 50+
      },
      largestFiles: [],
      mostComplexFiles: []
    };

    // Calculate aggregates
    let successfulAnalyses = 0;
    let totalComplexity = 0;
    let totalDuplicationScore = 0;
    let totalCommentRatio = 0;

    // Collect file metrics for sorting
    const fileMetrics = [];

    analysisResults.forEach(result => {
      if (!result.success) return;

      successfulAnalyses++;

      // Count languages
      overview.languageBreakdown[result.language] = (overview.languageBreakdown[result.language] || 0) + 1;

      // Sum lines
      if (result.metrics && result.metrics.lineCount) {
        overview.totalLines += result.metrics.lineCount;

        // Add to file metrics for sorting
        fileMetrics.push({
          path: result.path,
          lineCount: result.metrics.lineCount,
          complexity: result.metrics.cyclomaticComplexity || 0,
          language: result.language
        });
      }

      // Sum complexity and categorize
      if (result.metrics && result.metrics.cyclomaticComplexity) {
        const complexity = result.metrics.cyclomaticComplexity;
        totalComplexity += complexity;

        // Categorize complexity
        if (complexity <= 10) {
          overview.complexityDistribution.low++;
        } else if (complexity <= 20) {
          overview.complexityDistribution.medium++;
        } else if (complexity <= 50) {
          overview.complexityDistribution.high++;
        } else {
          overview.complexityDistribution.veryHigh++;
        }
      }

      // Sum duplication score
      if (result.metrics && result.metrics.duplicationScore !== undefined) {
        totalDuplicationScore += result.metrics.duplicationScore;
      }

      // Sum comment ratio
      if (result.metrics && result.metrics.commentRatio !== undefined) {
        totalCommentRatio += result.metrics.commentRatio;
      }

      // Sum structure elements
      if (result.structure) {
        if (result.structure.classes) {
          overview.structureSummary.classes += result.structure.classes.length || 0;
        }
        if (result.structure.functions) {
          overview.structureSummary.functions += result.structure.functions.length || 0;
        }
        if (result.structure.methods) {
          overview.structureSummary.methods += result.structure.methods.length || 0;
        }
      }
    });

    // Calculate averages
    if (successfulAnalyses > 0) {
      overview.averageComplexity = totalComplexity / successfulAnalyses;
      overview.averageDuplicationScore = totalDuplicationScore / successfulAnalyses;
      overview.commentRatio = totalCommentRatio / successfulAnalyses;
    }

    // Find largest files
    fileMetrics.sort((a, b) => b.lineCount - a.lineCount);
    overview.largestFiles = fileMetrics.slice(0, 10).map(file => ({
      path: file.path,
      lineCount: file.lineCount,
      language: file.language
    }));

    // Find most complex files
    fileMetrics.sort((a, b) => b.complexity - a.complexity);
    overview.mostComplexFiles = fileMetrics.slice(0, 10).map(file => ({
      path: file.path,
      complexity: file.complexity,
      language: file.language
    }));

    return overview;
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
      'cs': 'csharp',
      'php': 'php',
      'swift': 'swift',
      'kt': 'kotlin',
      'json': 'json',
      'md': 'markdown',
      'yml': 'yaml',
      'yaml': 'yaml',
      'html': 'html',
      'css': 'css',
      'scss': 'scss',
      'less': 'less',
      'sql': 'sql',
      'sh': 'bash',
      'bash': 'bash',
      'xml': 'xml',
      'vue': 'vue',
      'svelte': 'svelte',
      'dart': 'dart',
      'ex': 'elixir',
      'exs': 'elixir',
      'elm': 'elm',
      'clj': 'clojure',
      'hs': 'haskell'
    };

    return extensionMap[ext] || null;
  }

  mockStructure(language, content) {
    // Mock implementation that returns a basic structure
    // This is used as a fallback when Tree-sitter parsing fails

    const structure = {
      classes: [],
      functions: [],
      methods: []
    };

    // Count some typical patterns in the code to create a mock structure
    if (language === 'markdown') {
      // Extract headings as "classes"
      const headingMatches = content.match(/^#+\s+(.+)$/gm) || [];
      headingMatches.forEach((match, index) => {
        const level = match.match(/^#+/)[0].length;
        const name = match.replace(/^#+\s+/, '');
        const lineNumber = this.getLineNumberForMatch(content, match, index);
        structure.classes.push({
          name: `H${level}: ${name}`,
          line: lineNumber,
          text: match
        });
      });

      // Extract code blocks as "functions"
      const codeBlockMatches = content.match(/```[\s\S]+?```/g) || [];
      codeBlockMatches.forEach((match, index) => {
        const language = match.match(/```(\w*)/)[1] || 'text';
        const lineNumber = this.getLineNumberForMatch(content, match, index);
        structure.functions.push({
          name: `Code Block (${language})`,
          line: lineNumber,
          text: match.split('\n')[0] + '...'
        });
      });

      // Extract links as "methods"
      const linkMatches = content.match(/\[([^\]]+)\]\(([^)]+)\)/g) || [];
      linkMatches.forEach((match, index) => {
        const text = match.match(/\[([^\]]+)\]/)[1];
        const url = match.match(/\]\(([^)]+)\)/)[1];
        const lineNumber = this.getLineNumberForMatch(content, match, index);
        structure.methods.push({
          name: `Link: ${text}`,
          line: lineNumber,
          text: `${text} -> ${url}`
        });
      });
    } else if (language === 'javascript' || language === 'typescript') {
      // Match class declarations
      const classMatches = content.match(/class\s+(\w+)/g) || [];
      classMatches.forEach((match, index) => {
        const name = match.replace('class ', '');
        const lineNumber = this.getLineNumberForMatch(content, match, index);
        structure.classes.push({
          name,
          line: lineNumber,
          text: match
        });
      });

      // Match function declarations
      const functionMatches = content.match(/function\s+(\w+)/g) || [];
      functionMatches.forEach((match, index) => {
        const name = match.replace('function ', '');
        const lineNumber = this.getLineNumberForMatch(content, match, index);
        structure.functions.push({
          name,
          line: lineNumber,
          text: match
        });
      });

      // Match method declarations
      const methodMatches = content.match(/(\w+)\s*\([^)]*\)\s*{/g) || [];
      methodMatches.forEach((match, index) => {
        const name = match.split('(')[0].trim();
        if (name !== 'if' && name !== 'for' && name !== 'while' && name !== 'function') {
          const lineNumber = this.getLineNumberForMatch(content, match, index);
          structure.methods.push({
            name,
            line: lineNumber,
            text: match
          });
        }
      });
    } else if (language === 'python') {
      // Match class declarations
      const classMatches = content.match(/class\s+(\w+)/g) || [];
      classMatches.forEach((match, index) => {
        const name = match.replace('class ', '');
        const lineNumber = this.getLineNumberForMatch(content, match, index);
        structure.classes.push({
          name,
          line: lineNumber,
          text: match
        });
      });

      // Match function declarations
      const functionMatches = content.match(/def\s+(\w+)/g) || [];
      functionMatches.forEach((match, index) => {
        const name = match.replace('def ', '');
        const lineNumber = this.getLineNumberForMatch(content, match, index);
        structure.functions.push({
          name,
          line: lineNumber,
          text: match
        });
      });
    } else if (language === 'java') {
      // Match class declarations
      const classMatches = content.match(/class\s+(\w+)/g) || [];
      classMatches.forEach((match, index) => {
        const name = match.replace('class ', '');
        const lineNumber = this.getLineNumberForMatch(content, match, index);
        structure.classes.push({
          name,
          line: lineNumber,
          text: match
        });
      });

      // Match method declarations (simplified)
      const methodMatches = content.match(/(\w+)\s+(\w+)\s*\([^)]*\)\s*{/g) || [];
      methodMatches.forEach((match, index) => {
        const parts = match.split(/\s+/);
        if (parts.length >= 2) {
          const name = parts[1].split('(')[0].trim();
          const lineNumber = this.getLineNumberForMatch(content, match, index);
          structure.methods.push({
            name,
            line: lineNumber,
            text: match
          });
        }
      });
    }

    return structure;
  }

  getLineNumberForMatch(content, match, fallbackIndex) {
    // Find the line number for a regex match
    const index = content.indexOf(match);
    if (index === -1) return fallbackIndex + 1;

    return this.getLineNumber(content, index);
  }
}

module.exports = CodeAnalysisEngine;