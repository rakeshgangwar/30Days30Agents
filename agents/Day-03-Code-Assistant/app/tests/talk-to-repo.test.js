/**
 * Test script for the "Talk to Your Repository" feature
 */

const RepositoryAnalysisAgent = require('../src/app');
const path = require('path');
const assert = require('assert');

// Test configuration
const TEST_REPO_PATH = path.join(__dirname, '..');
const TEST_QUESTIONS = [
  'What is this repository about?',
  'What are the main components of this application?',
  'How is the CLI interface implemented?'
];

async function runTest() {
  console.log('Testing "Talk to Your Repository" feature...');
  
  try {
    // Initialize agent
    console.log('Initializing agent...');
    const agent = new RepositoryAnalysisAgent();
    await agent.initialize();
    
    // Start conversation with local repository
    console.log(`Starting conversation with repository at ${TEST_REPO_PATH}...`);
    const sessionResult = await agent.startConversation(TEST_REPO_PATH, {
      generateSummary: true
    });
    
    assert(sessionResult.success, 'Failed to start conversation');
    console.log(`Conversation started with session ID: ${sessionResult.sessionId}`);
    
    // Ask test questions
    for (const question of TEST_QUESTIONS) {
      console.log(`\nAsking: "${question}"`);
      const response = await agent.askQuestion(sessionResult.sessionId, question);
      
      assert(response.success, `Failed to get response for question: ${question}`);
      console.log(`Response: ${response.response.substring(0, 100)}...`);
    }
    
    console.log('\nAll tests passed!');
  } catch (error) {
    console.error('Test failed:', error.message);
    process.exit(1);
  }
}

// Run the test
runTest().catch(error => {
  console.error('Unhandled error:', error);
  process.exit(1);
});
