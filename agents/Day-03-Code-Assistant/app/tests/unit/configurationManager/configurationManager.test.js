/**
 * Unit tests for Configuration Manager component
 */

const ConfigurationManager = require('../../../src/components/configurationManager');
const path = require('path');
const fs = require('fs');
const mock = require('mock-fs');

describe('Configuration Manager', () => {
  // Setup and teardown
  beforeEach(() => {
    // Setup mock file system
    mock({
      'config': {
        'config.yaml': `
repository:
  owner: "test-owner"
  repo: "test-repo"
  branch: "main"
analysis:
  maxFilesToAnalyze: 50
`,
        'credentials.yaml': '# This file would contain encrypted credentials'
      }
    });
  });

  afterEach(() => {
    // Restore real file system
    mock.restore();
  });

  // Tests
  test('should load configuration file', async () => {
    // Arrange
    const configManager = new ConfigurationManager({
      configPath: 'config',
      configFile: 'config.yaml'
    });

    // Act
    await configManager.initialize();
    const config = configManager.getConfig();

    // Assert
    expect(config).toBeDefined();
    expect(config.repository).toBeDefined();
    expect(config.repository.owner).toBe('test-owner');
    expect(config.repository.repo).toBe('test-repo');
  });

  test('should create default configuration if file does not exist', async () => {
    // Arrange
    mock.restore();
    mock({
      'empty-config': {}
    });

    const configManager = new ConfigurationManager({
      configPath: 'empty-config',
      configFile: 'new-config.yaml'
    });

    // Act
    await configManager.initialize();
    const config = configManager.getConfig();

    // Assert
    expect(config).toBeDefined();
    expect(config.repository).toBeDefined();
    expect(config.analysis).toBeDefined();
    expect(config.ai).toBeDefined();
    expect(config.issue).toBeDefined();
  });

  test('should apply environment variables to configuration', async () => {
    // Arrange
    process.env.REPO_OWNER = 'env-owner';
    process.env.REPO_NAME = 'env-repo';
    
    const configManager = new ConfigurationManager({
      configPath: 'config',
      configFile: 'config.yaml'
    });

    // Act
    await configManager.initialize();
    const config = configManager.getConfig();

    // Assert
    expect(config.repository.owner).toBe('env-owner');
    expect(config.repository.repo).toBe('env-repo');

    // Cleanup
    delete process.env.REPO_OWNER;
    delete process.env.REPO_NAME;
  });

  test('should validate configuration values', async () => {
    // Arrange
    mock.restore();
    mock({
      'invalid-config': {
        'config.yaml': `
repository:
  owner: "test-owner"
  repo: "test-repo"
analysis:
  analysisDepth: "invalid-depth"
ai:
  temperature: 2.5
`
      }
    });

    const configManager = new ConfigurationManager({
      configPath: 'invalid-config',
      configFile: 'config.yaml'
    });

    // Act
    await configManager.initialize();
    const config = configManager.getConfig();

    // Assert
    expect(config.analysis.analysisDepth).toBe('medium'); // Fallback to default
    expect(config.ai.temperature).toBe(0.2); // Fallback to default
  });
});