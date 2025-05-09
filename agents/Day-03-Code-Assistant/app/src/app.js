/**
 * Repository Analysis and Issue Creation Agent
 *
 * Main application class that integrates all components together
 */

const path = require('path');
const ConfigurationManager = require('./components/configurationManager');
const RepositoryAccessLayer = require('./components/repositoryAccessLayer');
const CodeAnalysisEngine = require('./components/codeAnalysisEngine');
const AIAnalysisCoordinator = require('./components/aiAnalysisCoordinator');
const IssueManagementSystem = require('./components/issueManagementSystem');
const StorageManager = require('./components/storageManager');
const RepoConversationManager = require('./components/repoConversationManager');
const VectorDatabaseManager = require('./components/vectorDatabaseManager');

class RepositoryAnalysisAgent {
  constructor(options = {}) {
    this.options = options;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;

    // Initialize configuration manager
    this.configManager = new ConfigurationManager(this.options.config);
    const configResult = await this.configManager.initialize();

    if (!configResult.hasCredentials) {
      throw new Error('No credentials found. Please configure credentials first.');
    }

    // Initialize storage manager
    this.storageManager = new StorageManager(this.options.storage);
    await this.storageManager.initialize();

    // Initialize repository access layer
    this.repositoryAccess = new RepositoryAccessLayer(this.configManager.getConfig().repository);

    // Initialize code analysis engine
    this.codeAnalysis = new CodeAnalysisEngine();
    await this.codeAnalysis.initialize();

    // Initialize AI analysis coordinator
    const aiConfig = {
      ...this.configManager.getConfig().ai,
      openai: {
        apiKey: this.configManager.getCredentials().openaiApiKey
      }
    };
    this.aiAnalysis = new AIAnalysisCoordinator(aiConfig);

    // Initialize issue management system
    const issueConfig = {
      ...this.configManager.getConfig().issue,
      github: {
        token: this.configManager.getCredentials().githubToken
      }
    };
    this.issueManagement = new IssueManagementSystem(issueConfig, this.storageManager);

    // Initialize vector database manager
    this.vectorDatabase = new VectorDatabaseManager({
      openaiApiKey: this.configManager.getCredentials().openaiApiKey,
      storagePath: this.options.vectorDbPath || path.join(process.cwd(), 'storage', 'vector-db')
    });
    await this.vectorDatabase.initialize();

    // Initialize repository conversation manager
    this.conversationManager = new RepoConversationManager({
      repositoryAccess: this.repositoryAccess,
      codeAnalysis: this.codeAnalysis,
      aiAnalysis: this.aiAnalysis,
      vectorDatabase: this.vectorDatabase,
      historyPath: this.options.conversationHistoryPath || path.join(process.cwd(), 'storage', 'conversations')
    });
    await this.conversationManager.initialize();

    this.initialized = true;
    return true;
  }

  async analyzeRepository(owner, repo, options = {}) {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // Step 1: Clone repository
      console.log(`Cloning repository ${owner}/${repo}...`);
      const repoResult = await this.repositoryAccess.cloneRepository(`https://github.com/${owner}/${repo}.git`);

      if (!repoResult.success) {
        throw new Error(`Failed to clone repository: ${repoResult.error}`);
      }

      // Step 2: List files
      console.log('Listing repository files...');
      const files = await this.repositoryAccess.listRepositoryFiles(repoResult.path);

      // Step 3: Read file contents
      console.log(`Reading ${files.length} files...`);
      const fileContents = [];

      for (const filePath of files) {
        const content = await this.repositoryAccess.readFileContent(filePath);
        if (content.success) {
          fileContents.push({
            path: filePath,
            content: content.content
          });
        }
      }

      // Step 4: Analyze code
      console.log('Analyzing code...');
      const analysisResults = await this.codeAnalysis.analyzeFiles(fileContents);

      // Step 5: Generate repository info
      const repositoryInfo = {
        name: `${owner}/${repo}`,
        description: options.description || `Repository ${owner}/${repo}`,
        url: `https://github.com/${owner}/${repo}`
      };

      // Step 6: AI analysis
      console.log('Performing AI analysis...');
      const fileAnalysisResults = await this.aiAnalysis.analyzeMultipleFiles(fileContents, analysisResults);
      const repositoryAnalysisResult = await this.aiAnalysis.analyzeRepository(repositoryInfo, analysisResults);

      // Step 7: Prioritize findings
      const prioritizedFindings = this.aiAnalysis.prioritizeFindings(fileAnalysisResults, repositoryAnalysisResult);

      // Step 8: Create issues
      if (this.configManager.getConfig().issue.createIssues && !options.dryRun) {
        console.log('Creating GitHub issues...');
        const issueResults = await this.issueManagement.createIssuesFromFindings(owner, repo, prioritizedFindings, {
          limit: this.configManager.getConfig().issue.maxIssuesToCreate,
          skipLowPriority: this.configManager.getConfig().issue.priorityThreshold !== 'Low'
        });

        console.log(`Created ${issueResults.summary.created} issues.`);
      } else {
        console.log('Dry run mode - no issues created.');
      }

      // Step 9: Generate report
      const report = this.generateReport(repositoryInfo, analysisResults, prioritizedFindings);

      return {
        success: true,
        repositoryInfo,
        analysisResults,
        findings: prioritizedFindings,
        report
      };
    } catch (error) {
      console.error('Error analyzing repository:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  generateReport(repositoryInfo, analysisResults, findings) {
    // Generate a summary report
    const successfulAnalyses = analysisResults.filter(r => r.success).length;
    const totalFiles = analysisResults.length;

    // Count findings by priority
    const findingsByPriority = {
      Critical: findings.filter(f => f.priority === 'Critical').length,
      High: findings.filter(f => f.priority === 'High').length,
      Medium: findings.filter(f => f.priority === 'Medium').length,
      Low: findings.filter(f => f.priority === 'Low').length
    };

    // Count findings by type
    const findingsByType = {};
    findings.forEach(finding => {
      const type = this.detectFindingType(finding);
      findingsByType[type] = (findingsByType[type] || 0) + 1;
    });

    return {
      repository: repositoryInfo.name,
      timestamp: new Date().toISOString(),
      summary: {
        totalFiles,
        analyzedFiles: successfulAnalyses,
        totalFindings: findings.length,
        findingsByPriority,
        findingsByType
      },
      topFindings: findings.slice(0, 5).map(f => ({
        title: f.title,
        priority: f.priority,
        source: f.source
      }))
    };
  }

  detectFindingType(finding) {
    const title = finding.title.toLowerCase();
    const description = finding.description.toLowerCase();

    if (title.includes('bug') || description.includes('bug') ||
        title.includes('error') || description.includes('error')) {
      return 'Bug';
    } else if (title.includes('security') || description.includes('security') ||
               title.includes('vulnerability') || description.includes('vulnerability')) {
      return 'Security';
    } else if (title.includes('performance') || description.includes('performance')) {
      return 'Performance';
    } else if (title.includes('documentation') || description.includes('documentation')) {
      return 'Documentation';
    } else if (title.includes('refactor') || description.includes('refactor') ||
               title.includes('code smell') || description.includes('code smell')) {
      return 'Refactoring';
    } else if (title.includes('feature') || description.includes('feature') ||
               title.includes('enhancement') || description.includes('enhancement')) {
      return 'Enhancement';
    } else {
      return 'Other';
    }
  }

  /**
   * Start a conversation with a local repository
   * @param {string} repoPath - Path to the repository
   * @param {Object} options - Conversation options
   * @returns {Object} - Conversation session
   */
  async startConversation(repoPath, options = {}) {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // Start conversation
      const result = await this.conversationManager.startConversation(repoPath, {
        generateSummary: options.generateSummary !== false
      });

      return result;
    } catch (error) {
      console.error('Error starting conversation:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Ask a question about the repository
   * @param {string} sessionId - Conversation session ID
   * @param {string} question - User's question
   * @returns {Object} - Response
   */
  async askQuestion(sessionId, question) {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // Process question
      const result = await this.conversationManager.askQuestion(sessionId, question);

      return result;
    } catch (error) {
      console.error('Error processing question:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Start an interactive CLI conversation with a repository
   * @param {string} sessionId - Conversation session ID
   */
  async startInteractiveSession(sessionId) {
    if (!this.initialized) {
      await this.initialize();
    }

    await this.conversationManager.startInteractiveSession(sessionId);
  }

  /**
   * Clone a repository and start a conversation with it
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @param {Object} options - Conversation options
   * @returns {Object} - Conversation session
   */
  async cloneAndStartConversation(owner, repo, options = {}) {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // Clone repository
      console.log(`Cloning repository ${owner}/${repo}...`);
      const repoResult = await this.repositoryAccess.cloneRepository(`https://github.com/${owner}/${repo}.git`);

      if (!repoResult.success) {
        throw new Error(`Failed to clone repository: ${repoResult.error}`);
      }

      // Start conversation
      const result = await this.startConversation(repoResult.path, options);

      return result;
    } catch (error) {
      console.error('Error cloning and starting conversation:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }
}

module.exports = RepositoryAnalysisAgent;