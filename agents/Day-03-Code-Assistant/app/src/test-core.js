/**
 * Test script for core infrastructure components
 *
 * This script tests the basic functionality of the core infrastructure components:
 * - ConfigurationManager
 * - StorageManager
 * - RepositoryAccessLayer
 */

const ConfigurationManager = require('./components/configurationManager');
const StorageManager = require('./components/storageManager');
const RepositoryAccessLayer = require('./components/repositoryAccessLayer');
const path = require('path');

async function testCoreInfrastructure() {
  console.log('Testing core infrastructure components...');

  try {
    // Test ConfigurationManager
    console.log('\n--- Testing ConfigurationManager ---');
    const configManager = new ConfigurationManager();
    const configResult = await configManager.initialize();

    console.log('Configuration loaded:', configResult.hasCredentials ? 'with credentials' : 'without credentials');
    console.log('Repository config:', configManager.getConfig().repository);
    console.log('AI config:', configManager.getConfig().ai);

    // Test StorageManager
    console.log('\n--- Testing StorageManager ---');
    const storageManager = new StorageManager({
      storagePath: path.join(process.cwd(), 'storage')
    });

    await storageManager.initialize();
    console.log('Storage initialized');

    // Save some test data
    const testData = {
      timestamp: new Date().toISOString(),
      message: 'Test data for core infrastructure'
    };

    await storageManager.saveData('test/core-infrastructure', testData);
    console.log('Test data saved');

    // Load the test data
    const loadedData = await storageManager.loadData('test/core-infrastructure');
    console.log('Loaded data:', loadedData);

    // Test RepositoryAccessLayer
    console.log('\n--- Testing RepositoryAccessLayer ---');
    const repoAccess = new RepositoryAccessLayer({
      workDir: path.join(process.cwd(), 'repos')
    });

    // Get repository details from configuration
    const repoConfig = configManager.getConfig().repository;

    // Check if repository owner and name are specified
    if (!repoConfig.owner || !repoConfig.repo) {
      console.log('Repository owner or name not specified in configuration.');
      console.log('Using default repository for testing: octokit/rest.js');

      repoConfig.owner = 'octokit';
      repoConfig.repo = 'rest.js';
    }

    const repoUrl = `https://github.com/${repoConfig.owner}/${repoConfig.repo}.git`;

    console.log(`Cloning repository: ${repoUrl}`);
    const cloneResult = await repoAccess.cloneRepository(repoUrl, {
      branch: repoConfig.branch,
      depth: repoConfig.depth || 1
    });

    if (cloneResult.success) {
      console.log('Repository cloned successfully:', cloneResult.path);

      // List files in the repository
      console.log('Listing repository files...');
      const files = await repoAccess.listRepositoryFiles(cloneResult.path, {
        pattern: '**/*.{js,jsx,ts,tsx,py,java,go,rb}',
        ignore: repoConfig.excludePatterns
      });

      console.log(`Found ${files.length} files`);

      // Read a few files
      if (files.length > 0) {
        console.log('\nReading sample files:');
        const sampleSize = Math.min(3, files.length);

        for (let i = 0; i < sampleSize; i++) {
          const filePath = files[i];
          const fileContent = await repoAccess.readFileContent(filePath);

          if (fileContent.success) {
            console.log(`- ${path.basename(filePath)}: ${fileContent.content.length} characters, encoding: ${fileContent.encoding}`);
          } else {
            console.log(`- ${path.basename(filePath)}: Error: ${fileContent.error}`);
          }
        }
      }
    } else {
      console.error('Failed to clone repository:', cloneResult.error);
    }

    console.log('\nCore infrastructure test completed successfully!');
  } catch (error) {
    console.error('Error testing core infrastructure:', error);
  }
}

// Run the test
testCoreInfrastructure();
