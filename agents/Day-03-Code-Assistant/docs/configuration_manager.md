# Configuration Manager

This document provides implementation details for the Configuration Manager of the Repository Analysis and Issue Creation Agent. This component is responsible for managing user preferences, authentication credentials, and analysis settings.

## Table of Contents

1. [Overview](#overview)
2. [Key Responsibilities](#key-responsibilities)
3. [Implementation Details](#implementation-details)
4. [Code Examples](#code-examples)
5. [Best Practices](#best-practices)
6. [Integration Points](#integration-points)

## Overview

The Configuration Manager serves as the central component for managing all configuration settings for the Repository Analysis and Issue Creation Agent. It handles loading and validating configuration files, managing sensitive credentials, and providing configuration values to other components. This ensures that the agent's behavior can be customized to meet specific requirements without code changes.

## Key Responsibilities

- **Configuration Loading**: Load and parse configuration files
- **Credential Management**: Securely store and provide access to authentication credentials
- **Validation**: Validate configuration values and provide sensible defaults
- **Environment Integration**: Support environment variables for configuration
- **Configuration Updates**: Allow runtime updates to configuration
- **Profile Management**: Support multiple configuration profiles

## Implementation Details

### Configuration Loading

First, we need to implement configuration loading from files:

```javascript
const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');

class ConfigurationLoader {
  async loadConfigFile(filePath) {
    try {
      const fileContent = await fs.readFile(filePath, 'utf8');
      const fileExt = path.extname(filePath).toLowerCase();
      
      // Parse based on file extension
      if (fileExt === '.json') {
        return JSON.parse(fileContent);
      } else if (fileExt === '.yaml' || fileExt === '.yml') {
        return yaml.load(fileContent);
      } else {
        throw new Error(`Unsupported configuration file format: ${fileExt}`);
      }
    } catch (error) {
      console.error(`Error loading configuration file: ${error.message}`);
      return null;
    }
  }
  
  async saveConfigFile(filePath, config) {
    try {
      const fileExt = path.extname(filePath).toLowerCase();
      let fileContent;
      
      // Serialize based on file extension
      if (fileExt === '.json') {
        fileContent = JSON.stringify(config, null, 2);
      } else if (fileExt === '.yaml' || fileExt === '.yml') {
        fileContent = yaml.dump(config);
      } else {
        throw new Error(`Unsupported configuration file format: ${fileExt}`);
      }
      
      // Ensure directory exists
      const dirPath = path.dirname(filePath);
      await fs.mkdir(dirPath, { recursive: true });
      
      // Write file
      await fs.writeFile(filePath, fileContent, 'utf8');
      return true;
    } catch (error) {
      console.error(`Error saving configuration file: ${error.message}`);
      return false;
    }
  }
}
```

### Credential Management

Next, we need to implement secure credential management:

```javascript
const crypto = require('crypto');
const os = require('os');

class CredentialManager {
  constructor(encryptionKey = null) {
    // Use provided key or generate one based on machine-specific information
    this.encryptionKey = encryptionKey || this.generateEncryptionKey();
  }
  
  generateEncryptionKey() {
    // Generate a deterministic but machine-specific key
    const machineId = this.getMachineId();
    return crypto.createHash('sha256').update(machineId).digest('hex');
  }
  
  getMachineId() {
    // Create a unique identifier based on machine information
    const hostname = os.hostname();
    const username = os.userInfo().username;
    const platform = os.platform();
    const cpus = os.cpus().map(cpu => cpu.model).join('');
    
    return `${hostname}-${username}-${platform}-${cpus}`;
  }
  
  encrypt(text) {
    try {
      const iv = crypto.randomBytes(16);
      const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(this.encryptionKey.slice(0, 32)), iv);
      
      let encrypted = cipher.update(text, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      return `${iv.toString('hex')}:${encrypted}`;
    } catch (error) {
      console.error('Encryption error:', error.message);
      return null;
    }
  }
  
  decrypt(encryptedText) {
    try {
      const parts = encryptedText.split(':');
      if (parts.length !== 2) {
        throw new Error('Invalid encrypted text format');
      }
      
      const iv = Buffer.from(parts[0], 'hex');
      const encrypted = parts[1];
      
      const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(this.encryptionKey.slice(0, 32)), iv);
      
      let decrypted = decipher.update(encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return decrypted;
    } catch (error) {
      console.error('Decryption error:', error.message);
      return null;
    }
  }
  
  async saveCredentials(credentials, filePath) {
    // Encrypt each credential
    const encryptedCredentials = {};
    
    for (const [key, value] of Object.entries(credentials)) {
      encryptedCredentials[key] = this.encrypt(value);
    }
    
    // Save to file
    const configLoader = new ConfigurationLoader();
    return await configLoader.saveConfigFile(filePath, encryptedCredentials);
  }
  
  async loadCredentials(filePath) {
    // Load from file
    const configLoader = new ConfigurationLoader();
    const encryptedCredentials = await configLoader.loadConfigFile(filePath);
    
    if (!encryptedCredentials) {
      return null;
    }
    
    // Decrypt each credential
    const credentials = {};
    
    for (const [key, value] of Object.entries(encryptedCredentials)) {
      credentials[key] = this.decrypt(value);
    }
    
    return credentials;
  }
}
```

### Configuration Validation

Now, we need to implement configuration validation:

```javascript
class ConfigurationValidator {
  validateRepositoryConfig(config) {
    const validatedConfig = {
      owner: config.owner,
      repo: config.repo,
      branch: config.branch || 'main',
      depth: config.depth || 1,
      includePatterns: config.includePatterns || ['**/*'],
      excludePatterns: config.excludePatterns || [
        'node_modules/**',
        '.git/**',
        'dist/**',
        'build/**',
        '**/*.min.js',
        '**/*.bundle.js'
      ]
    };
    
    // Validate required fields
    if (!validatedConfig.owner || !validatedConfig.repo) {
      throw new Error('Repository owner and name are required');
    }
    
    return validatedConfig;
  }
  
  validateAnalysisConfig(config) {
    const validatedConfig = {
      maxFilesToAnalyze: config.maxFilesToAnalyze || 100,
      maxFileSizeKB: config.maxFileSizeKB || 1000,
      includeLanguages: config.includeLanguages || ['javascript', 'typescript', 'python', 'java', 'go', 'ruby', 'c', 'cpp', 'csharp'],
      excludeLanguages: config.excludeLanguages || [],
      analysisDepth: config.analysisDepth || 'medium',
      enabledAnalyzers: config.enabledAnalyzers || ['structure', 'complexity', 'duplication', 'security', 'performance']
    };
    
    // Validate analysis depth
    if (!['light', 'medium', 'deep'].includes(validatedConfig.analysisDepth)) {
      validatedConfig.analysisDepth = 'medium';
    }
    
    return validatedConfig;
  }
  
  validateAIConfig(config) {
    const validatedConfig = {
      provider: config.provider || 'openai',
      model: config.model || 'gpt-4',
      temperature: config.temperature !== undefined ? config.temperature : 0.2,
      maxTokens: config.maxTokens || 2000,
      promptTemplate: config.promptTemplate || 'default'
    };
    
    // Validate temperature
    if (validatedConfig.temperature < 0 || validatedConfig.temperature > 1) {
      validatedConfig.temperature = 0.2;
    }
    
    return validatedConfig;
  }
  
  validateIssueConfig(config) {
    const validatedConfig = {
      createIssues: config.createIssues !== undefined ? config.createIssues : true,
      maxIssuesToCreate: config.maxIssuesToCreate || 10,
      labelPrefix: config.labelPrefix || 'ai-analysis',
      priorityThreshold: config.priorityThreshold || 'Low',
      issueTemplate: config.issueTemplate || 'default',
      dryRun: config.dryRun !== undefined ? config.dryRun : false
    };
    
    // Validate priority threshold
    const validPriorities = ['Critical', 'High', 'Medium', 'Low'];
    if (!validPriorities.includes(validatedConfig.priorityThreshold)) {
      validatedConfig.priorityThreshold = 'Low';
    }
    
    return validatedConfig;
  }
}
```

### Environment Integration

We also need to support environment variables for configuration:

```javascript
class EnvironmentManager {
  loadFromEnvironment() {
    const config = {
      repository: {},
      analysis: {},
      ai: {},
      issue: {},
      credentials: {}
    };
    
    // Repository configuration
    if (process.env.REPO_OWNER) config.repository.owner = process.env.REPO_OWNER;
    if (process.env.REPO_NAME) config.repository.repo = process.env.REPO_NAME;
    if (process.env.REPO_BRANCH) config.repository.branch = process.env.REPO_BRANCH;
    
    // Analysis configuration
    if (process.env.ANALYSIS_MAX_FILES) config.analysis.maxFilesToAnalyze = parseInt(process.env.ANALYSIS_MAX_FILES, 10);
    if (process.env.ANALYSIS_MAX_FILE_SIZE) config.analysis.maxFileSizeKB = parseInt(process.env.ANALYSIS_MAX_FILE_SIZE, 10);
    if (process.env.ANALYSIS_DEPTH) config.analysis.analysisDepth = process.env.ANALYSIS_DEPTH;
    
    // AI configuration
    if (process.env.AI_PROVIDER) config.ai.provider = process.env.AI_PROVIDER;
    if (process.env.AI_MODEL) config.ai.model = process.env.AI_MODEL;
    if (process.env.AI_TEMPERATURE) config.ai.temperature = parseFloat(process.env.AI_TEMPERATURE);
    
    // Issue configuration
    if (process.env.ISSUE_CREATE === 'true') config.issue.createIssues = true;
    if (process.env.ISSUE_CREATE === 'false') config.issue.createIssues = false;
    if (process.env.ISSUE_MAX) config.issue.maxIssuesToCreate = parseInt(process.env.ISSUE_MAX, 10);
    if (process.env.ISSUE_PRIORITY) config.issue.priorityThreshold = process.env.ISSUE_PRIORITY;
    if (process.env.ISSUE_DRY_RUN === 'true') config.issue.dryRun = true;
    
    // Credentials
    if (process.env.GITHUB_TOKEN) config.credentials.githubToken = process.env.GITHUB_TOKEN;
    if (process.env.OPENAI_API_KEY) config.credentials.openaiApiKey = process.env.OPENAI_API_KEY;
    
    return config;
  }
}
```

## Code Examples

### Complete Configuration Manager

Here's a more complete example of a Configuration Manager that combines the above components:

```javascript
// configurationManager.js
const path = require('path');
const ConfigurationLoader = require('./ConfigurationLoader');
const CredentialManager = require('./CredentialManager');
const ConfigurationValidator = require('./ConfigurationValidator');
const EnvironmentManager = require('./EnvironmentManager');

class ConfigurationManager {
  constructor(options = {}) {
    this.configPath = options.configPath || path.join(process.cwd(), 'config');
    this.configFile = options.configFile || 'config.yaml';
    this.credentialsFile = options.credentialsFile || 'credentials.yaml';
    this.profileName = options.profile || 'default';
    
    this.configLoader = new ConfigurationLoader();
    this.credentialManager = new CredentialManager(options.encryptionKey);
    this.configValidator = new ConfigurationValidator();
    this.environmentManager = new EnvironmentManager();
    
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
    
    // Load configuration file
    this.config = await this.configLoader.loadConfigFile(configFilePath);
    
    // If no configuration found, create default
    if (!this.config) {
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
    return await this.configLoader.saveConfigFile(configFilePath, this.config);
  }
  
  async loadCredentials() {
    const credentialsFilePath = path.join(this.configPath, this.credentialsFile);
    this.credentials = await this.credentialManager.loadCredentials(credentialsFilePath);
    return this.credentials;
  }
  
  async saveCredentials(credentials) {
    const credentialsFilePath = path.join(this.configPath, this.credentialsFile);
    this.credentials = credentials;
    return await this.credentialManager.saveCredentials(credentials, credentialsFilePath);
  }
  
  applyEnvironmentVariables() {
    const envConfig = this.environmentManager.loadFromEnvironment();
    
    // Merge environment variables into configuration
    this.config = {
      ...this.config,
      repository: { ...this.config.repository, ...envConfig.repository },
      analysis: { ...this.config.analysis, ...envConfig.analysis },
      ai: { ...this.config.ai, ...envConfig.ai },
      issue: { ...this.config.issue, ...envConfig.issue }
    };
    
    // Merge credentials
    if (!this.credentials) {
      this.credentials = {};
    }
    
    this.credentials = {
      ...this.credentials,
      ...envConfig.credentials
    };
  }
  
  validateConfiguration() {
    // Validate each section of the configuration
    this.config.repository = this.configValidator.validateRepositoryConfig(this.config.repository || {});
    this.config.analysis = this.configValidator.validateAnalysisConfig(this.config.analysis || {});
    this.config.ai = this.configValidator.validateAIConfig(this.config.ai || {});
    this.config.issue = this.configValidator.validateIssueConfig(this.config.issue || {});
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
  
  updateConfig(section, updates) {
    if (!this.config[section]) {
      this.config[section] = {};
    }
    
    this.config[section] = {
      ...this.config[section],
      ...updates
    };
    
    // Re-validate the updated section
    switch (section) {
      case 'repository':
        this.config.repository = this.configValidator.validateRepositoryConfig(this.config.repository);
        break;
      case 'analysis':
        this.config.analysis = this.configValidator.validateAnalysisConfig(this.config.analysis);
        break;
      case 'ai':
        this.config.ai = this.configValidator.validateAIConfig(this.config.ai);
        break;
      case 'issue':
        this.config.issue = this.configValidator.validateIssueConfig(this.config.issue);
        break;
    }
    
    return this.config[section];
  }
}

module.exports = ConfigurationManager;
```

## Best Practices

1. **Secure Credential Storage**: Store credentials securely using encryption
2. **Environment Variable Support**: Support configuration via environment variables for CI/CD integration
3. **Validation**: Validate all configuration values and provide sensible defaults
4. **Multiple Profiles**: Support multiple configuration profiles for different use cases
5. **Separation of Concerns**: Keep configuration separate from code
6. **Documentation**: Document all configuration options and their effects
7. **Graceful Degradation**: Handle missing or invalid configuration gracefully

## Integration Points

The Configuration Manager interfaces with:

1. **Repository Access Layer**: Provides repository access settings
2. **Code Analysis Engine**: Provides analysis settings
3. **AI Analysis Coordinator**: Provides AI model settings
4. **Issue Management System**: Provides issue creation settings

By implementing a robust Configuration Manager, the agent will be highly configurable and adaptable to different environments and use cases, without requiring code changes.
