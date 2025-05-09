// Configuration Manager Component
// This component manages user preferences, authentication credentials, and analysis settings

const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');
const crypto = require('crypto');
const os = require('os');

class ConfigurationManager {
  constructor(options = {}) {
    this.configPath = options.configPath || path.join(process.cwd(), 'config');
    this.configFile = options.configFile || 'default.yaml';
    this.credentialsFile = options.credentialsFile || '.credentials.yaml';
    this.profileName = options.profile || 'default';
    this.config = null;
    this.credentials = null;
  }
  
  async initialize() {
    // Load configuration
    await this.loadConfiguration();
    
    // Load credentials
    await this.loadCredentials();
    
    // Apply environment variables
    this.applyEnvironmentVariables();
    
    // Validate configuration
    this.validateConfiguration();
    
    return {
      config: this.config,
      hasCredentials: !!this.credentials
    };
  }
  
  async loadConfiguration() {
    const configFilePath = path.join(this.configPath, this.configFile);
    
    try {
      // Load configuration file
      const fileContent = await fs.readFile(configFilePath, 'utf8');
      const fileExt = path.extname(configFilePath).toLowerCase();
      
      // Parse based on file extension
      if (fileExt === '.json') {
        this.config = JSON.parse(fileContent);
      } else if (fileExt === '.yaml' || fileExt === '.yml') {
        this.config = yaml.load(fileContent);
      } else {
        throw new Error(`Unsupported configuration file format: ${fileExt}`);
      }
    } catch (error) {
      console.warn(`Could not load configuration file: ${error.message}`);
      this.config = this.createDefaultConfig();
      await this.saveConfiguration();
    }
    
    // Apply profile if specified
    if (this.profileName !== 'default' && this.config.profiles && this.config.profiles[this.profileName]) {
      this.config = {
        ...this.config,
        ...this.config.profiles[this.profileName]
      };
    }
    
    return this.config;
  }
  
  async saveConfiguration() {
    const configFilePath = path.join(this.configPath, this.configFile);
    
    try {
      const fileExt = path.extname(configFilePath).toLowerCase();
      let fileContent;
      
      // Serialize based on file extension
      if (fileExt === '.json') {
        fileContent = JSON.stringify(this.config, null, 2);
      } else if (fileExt === '.yaml' || fileExt === '.yml') {
        fileContent = yaml.dump(this.config);
      } else {
        throw new Error(`Unsupported configuration file format: ${fileExt}`);
      }
      
      // Ensure directory exists
      await fs.mkdir(path.dirname(configFilePath), { recursive: true });
      
      // Write file
      await fs.writeFile(configFilePath, fileContent, 'utf8');
      return true;
    } catch (error) {
      console.error(`Error saving configuration file: ${error.message}`);
      return false;
    }
  }
  
  async loadCredentials() {
    const credentialsFilePath = path.join(this.configPath, this.credentialsFile);
    
    try {
      const fileContent = await fs.readFile(credentialsFilePath, 'utf8');
      const fileExt = path.extname(credentialsFilePath).toLowerCase();
      
      // Parse based on file extension
      if (fileExt === '.json') {
        this.credentials = JSON.parse(fileContent);
      } else if (fileExt === '.yaml' || fileExt === '.yml') {
        this.credentials = yaml.load(fileContent);
      } else {
        throw new Error(`Unsupported credentials file format: ${fileExt}`);
      }
      
      // Decrypt credentials if needed
      
      return this.credentials;
    } catch (error) {
      console.warn(`Could not load credentials file: ${error.message}`);
      this.credentials = null;
      return null;
    }
  }
  
  async saveCredentials(credentials) {
    const credentialsFilePath = path.join(this.configPath, this.credentialsFile);
    
    try {
      this.credentials = credentials;
      
      // Encrypt credentials if needed
      
      const fileExt = path.extname(credentialsFilePath).toLowerCase();
      let fileContent;
      
      // Serialize based on file extension
      if (fileExt === '.json') {
        fileContent = JSON.stringify(this.credentials, null, 2);
      } else if (fileExt === '.yaml' || fileExt === '.yml') {
        fileContent = yaml.dump(this.credentials);
      } else {
        throw new Error(`Unsupported credentials file format: ${fileExt}`);
      }
      
      // Ensure directory exists
      await fs.mkdir(path.dirname(credentialsFilePath), { recursive: true });
      
      // Write file
      await fs.writeFile(credentialsFilePath, fileContent, 'utf8');
      return true;
    } catch (error) {
      console.error(`Error saving credentials file: ${error.message}`);
      return false;
    }
  }
  
  applyEnvironmentVariables() {
    // Apply environment variables to configuration
    if (process.env.REPO_OWNER) {
      if (!this.config.repository) this.config.repository = {};
      this.config.repository.owner = process.env.REPO_OWNER;
    }
    
    if (process.env.REPO_NAME) {
      if (!this.config.repository) this.config.repository = {};
      this.config.repository.repo = process.env.REPO_NAME;
    }
    
    if (process.env.REPO_BRANCH) {
      if (!this.config.repository) this.config.repository = {};
      this.config.repository.branch = process.env.REPO_BRANCH;
    }
    
    // Apply environment variables to credentials
    if (!this.credentials) {
      this.credentials = {};
    }
    
    if (process.env.GITHUB_TOKEN) {
      this.credentials.githubToken = process.env.GITHUB_TOKEN;
    }
    
    if (process.env.OPENAI_API_KEY) {
      this.credentials.openaiApiKey = process.env.OPENAI_API_KEY;
    }
  }
  
  validateConfiguration() {
    // Validate repository configuration
    if (!this.config.repository) {
      this.config.repository = {};
    }
    
    if (!this.config.repository.branch) {
      this.config.repository.branch = 'main';
    }
    
    // Validate analysis configuration
    if (!this.config.analysis) {
      this.config.analysis = {};
    }
    
    if (!this.config.analysis.analysisDepth || 
        !['light', 'medium', 'deep'].includes(this.config.analysis.analysisDepth)) {
      this.config.analysis.analysisDepth = 'medium';
    }
    
    // Validate AI configuration
    if (!this.config.ai) {
      this.config.ai = {};
    }
    
    if (this.config.ai.temperature === undefined || 
        this.config.ai.temperature < 0 || 
        this.config.ai.temperature > 1) {
      this.config.ai.temperature = 0.2;
    }
    
    // Validate issue configuration
    if (!this.config.issue) {
      this.config.issue = {};
    }
  }
  
  createDefaultConfig() {
    return {
      repository: {
        owner: '',
        repo: '',
        branch: 'main',
        depth: 1,
        includePatterns: ['**/*'],
        excludePatterns: [
          'node_modules/**',
          '.git/**',
          'dist/**',
          'build/**',
          '**/*.min.js',
          '**/*.bundle.js'
        ]
      },
      analysis: {
        maxFilesToAnalyze: 100,
        maxFileSizeKB: 1000,
        includeLanguages: ['javascript', 'typescript', 'python', 'java', 'go', 'ruby', 'c', 'cpp', 'csharp'],
        excludeLanguages: [],
        analysisDepth: 'medium',
        enabledAnalyzers: ['structure', 'complexity', 'duplication', 'security', 'performance']
      },
      ai: {
        provider: 'openai',
        model: 'gpt-4',
        temperature: 0.2,
        maxTokens: 2000,
        promptTemplate: 'default'
      },
      issue: {
        createIssues: true,
        maxIssuesToCreate: 10,
        labelPrefix: 'ai-analysis',
        priorityThreshold: 'Low',
        issueTemplate: 'default',
        dryRun: false
      },
      profiles: {}
    };
  }
  
  getConfig() {
    return this.config;
  }
  
  getCredentials() {
    return this.credentials;
  }
}

module.exports = ConfigurationManager;