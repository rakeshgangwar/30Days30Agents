/**
 * Test script for OpenAI integration
 * 
 * This script tests the OpenAI integration in the AIAnalysisCoordinator component
 */

require('dotenv').config();
const AIAnalysisCoordinator = require('../src/components/aiAnalysisCoordinator');

// Check if OpenAI API key is available
if (!process.env.OPENAI_API_KEY) {
  console.error('Error: OPENAI_API_KEY environment variable is not set');
  console.log('Please set the OPENAI_API_KEY environment variable in your .env file');
  process.exit(1);
}

// Initialize the AIAnalysisCoordinator
const coordinator = new AIAnalysisCoordinator({
  provider: 'openai',
  model: 'gpt-3.5-turbo', // Using a cheaper model for testing
  openai: {
    apiKey: process.env.OPENAI_API_KEY
  }
});

// Sample file content for testing
const sampleFile = {
  path: 'sample.js',
  content: `
    function calculateSum(a, b) {
      return a + b;
    }
    
    function calculateProduct(a, b) {
      return a * b;
    }
    
    // Main function
    function main() {
      const num1 = 5;
      const num2 = 10;
      
      console.log('Sum:', calculateSum(num1, num2));
      console.log('Product:', calculateProduct(num1, num2));
    }
    
    main();
  `
};

// Sample analysis result for testing
const sampleAnalysisResult = {
  success: true,
  path: 'sample.js',
  language: 'javascript',
  structure: {
    classes: [],
    functions: [
      { name: 'calculateSum', start: 2, end: 4 },
      { name: 'calculateProduct', start: 6, end: 8 },
      { name: 'main', start: 11, end: 18 }
    ],
    methods: []
  },
  metrics: {
    lineCount: 20,
    commentCount: 1,
    commentRatio: 0.05,
    cyclomaticComplexity: 1,
    duplicationScore: 0.1,
    classCount: 0,
    functionCount: 3,
    methodCount: 0
  }
};

// Test the AIAnalysisCoordinator
async function testAIAnalysisCoordinator() {
  console.log('Testing AIAnalysisCoordinator...');
  
  try {
    // Test file analysis
    console.log('Testing file analysis...');
    const fileAnalysisResult = await coordinator.analyzeFile(sampleFile, sampleAnalysisResult);
    
    console.log('File analysis result:');
    console.log(JSON.stringify(fileAnalysisResult, null, 2));
    
    if (fileAnalysisResult.success) {
      console.log('✅ File analysis successful');
    } else {
      console.error('❌ File analysis failed:', fileAnalysisResult.error);
    }
    
    console.log('\nTest completed successfully');
  } catch (error) {
    console.error('Error during test:', error.message);
    process.exit(1);
  }
}

// Run the test
testAIAnalysisCoordinator();
