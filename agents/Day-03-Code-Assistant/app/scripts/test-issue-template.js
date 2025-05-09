/**
 * Test script for issue template functionality
 * 
 * This script tests the issue template functionality in the IssueManagementSystem component
 */

require('dotenv').config();
const IssueManagementSystem = require('../src/components/issueManagementSystem');
const StorageManager = require('../src/components/storageManager');
const path = require('path');

// Initialize the StorageManager
const storageManager = new StorageManager({
  storagePath: './storage/test'
});

// Initialize the IssueManagementSystem
const issueManagementSystem = new IssueManagementSystem({
  createIssues: true,
  maxIssuesToCreate: 2,
  labelPrefix: 'test-ai-analysis',
  priorityThreshold: 'Low',
  dryRun: true, // Set to true for testing to avoid creating actual issues
  templatePath: path.join(process.cwd(), 'templates'), // Path to templates directory
  github: {
    token: process.env.GITHUB_TOKEN || 'dummy-token'
  }
}, storageManager);

// Sample findings for testing
const sampleFindings = [
  {
    title: 'Missing error handling',
    description: 'This code does not have proper error handling, which could lead to unhandled exceptions.',
    location: 'Line 10-15',
    suggestion: 'Add try/catch blocks or error handling middleware.',
    priority: 'Medium',
    source: 'file',
    filePath: 'src/app.js'
  },
  {
    title: 'Repository structure needs improvement',
    description: 'The repository structure is not following best practices, making it difficult to navigate and maintain.',
    area: 'Repository Structure',
    suggestion: 'Reorganize the repository according to standard project structure.',
    priority: 'Low',
    source: 'repository'
  }
];

// Test the issue template functionality
async function testIssueTemplate() {
  console.log('Testing issue template functionality...');
  
  try {
    // Initialize the StorageManager
    await storageManager.initialize();
    
    // Wait for the template to load
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Test file issue formatting
    console.log('\nTesting file issue formatting...');
    const fileIssue = sampleFindings[0];
    const fileIssueBody = issueManagementSystem.createFileIssueBody(fileIssue);
    console.log('File Issue Body:');
    console.log('-----------------------------------');
    console.log(fileIssueBody);
    console.log('-----------------------------------');
    
    // Test repository issue formatting
    console.log('\nTesting repository issue formatting...');
    const repoIssue = sampleFindings[1];
    const repoIssueBody = issueManagementSystem.createRepositoryIssueBody(repoIssue);
    console.log('Repository Issue Body:');
    console.log('-----------------------------------');
    console.log(repoIssueBody);
    console.log('-----------------------------------');
    
    // Verify that the template is being used
    if (fileIssueBody.includes('Issue Description') && 
        fileIssueBody.includes('Location') && 
        fileIssueBody.includes('Suggested Solution') && 
        fileIssueBody.includes('Priority')) {
      console.log('\n✅ Issue template is being used correctly for file issues');
    } else {
      console.error('\n❌ Issue template is not being applied correctly for file issues');
    }
    
    if (repoIssueBody.includes('Issue Description') && 
        repoIssueBody.includes('Location') && 
        repoIssueBody.includes('Suggested Solution') && 
        repoIssueBody.includes('Priority')) {
      console.log('✅ Issue template is being used correctly for repository issues');
    } else {
      console.error('❌ Issue template is not being applied correctly for repository issues');
    }
    
    console.log('\nTest completed successfully');
  } catch (error) {
    console.error('Error during test:', error.message);
    process.exit(1);
  }
}

// Run the test
testIssueTemplate();
