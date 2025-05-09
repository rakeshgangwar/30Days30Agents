/**
 * Test script for GitHub API integration
 * 
 * This script tests the GitHub API integration in the IssueManagementSystem component
 */

require('dotenv').config();
const IssueManagementSystem = require('../src/components/issueManagementSystem');
const StorageManager = require('../src/components/storageManager');

// Check if GitHub token is available
if (!process.env.GITHUB_TOKEN) {
  console.error('Error: GITHUB_TOKEN environment variable is not set');
  console.log('Please set the GITHUB_TOKEN environment variable in your .env file');
  process.exit(1);
}

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
  github: {
    token: process.env.GITHUB_TOKEN
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
    title: 'Potential performance issue',
    description: 'The loop implementation could be optimized for better performance.',
    location: 'Line 20-25',
    suggestion: 'Consider using a more efficient algorithm or caching results.',
    priority: 'Low',
    source: 'file',
    filePath: 'src/utils.js'
  },
  {
    title: 'Security vulnerability',
    description: 'Potential SQL injection vulnerability in database query.',
    location: 'Line 45-50',
    suggestion: 'Use parameterized queries or prepared statements.',
    priority: 'Critical',
    source: 'file',
    filePath: 'src/database.js'
  }
];

// Test the IssueManagementSystem
async function testIssueManagementSystem() {
  console.log('Testing IssueManagementSystem...');
  
  try {
    // Initialize the StorageManager
    await storageManager.initialize();
    
    // Test issue creation
    console.log('Testing issue creation...');
    
    // Replace with your own repository owner and name
    const owner = 'test-owner';
    const repo = 'test-repo';
    
    const result = await issueManagementSystem.createIssuesFromFindings(owner, repo, sampleFindings, {
      limit: 2
    });
    
    console.log('Issue creation result:');
    console.log(JSON.stringify(result.summary, null, 2));
    
    if (result.success) {
      console.log('✅ Issue creation test successful');
      
      // Log created issues
      console.log('\nCreated issues:');
      result.results.forEach((issueResult, index) => {
        if (issueResult.success) {
          console.log(`Issue ${index + 1}:`);
          console.log(`  Title: ${issueResult.finding.title}`);
          console.log(`  Priority: ${issueResult.finding.priority}`);
          if (issueResult.dryRun) {
            console.log('  (Dry run - no actual issue created)');
          } else {
            console.log(`  Issue #: ${issueResult.issueNumber}`);
            console.log(`  URL: ${issueResult.issueUrl}`);
          }
        } else {
          console.log(`Issue ${index + 1} (Failed):`);
          console.log(`  Title: ${issueResult.finding.title}`);
          console.log(`  Error: ${issueResult.error || 'Unknown error'}`);
          if (issueResult.isDuplicate) {
            console.log('  (Duplicate issue detected)');
          }
        }
        console.log('');
      });
    } else {
      console.error('❌ Issue creation test failed:', result.error);
    }
    
    console.log('\nTest completed successfully');
  } catch (error) {
    console.error('Error during test:', error.message);
    process.exit(1);
  }
}

// Run the test
testIssueManagementSystem();
