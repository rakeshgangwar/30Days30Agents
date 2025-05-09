/**
 * Test script for enhanced components
 */

const CodeAnalysisEngine = require('./components/codeAnalysisEngine');
const AIAnalysisCoordinator = require('./components/aiAnalysisCoordinator');
const fs = require('fs').promises;
const path = require('path');

async function testCodeAnalysisEngine() {
  console.log('\n--- Testing CodeAnalysisEngine ---');
  
  // Initialize engine
  const engine = new CodeAnalysisEngine();
  await engine.initialize();
  
  // Test file analysis
  const testFilePath = path.join(__dirname, 'components/codeAnalysisEngine/index.js');
  
  try {
    const content = await fs.readFile(testFilePath, 'utf8');
    console.log(`Analyzing file: ${testFilePath}`);
    
    const result = await engine.analyzeFile(testFilePath, content);
    
    if (result.success) {
      console.log('File analysis successful');
      console.log(`Language: ${result.language}`);
      console.log(`Structure: ${result.structure.classes.length} classes, ${result.structure.functions.length} functions, ${result.structure.methods.length} methods`);
      console.log(`Metrics: ${result.metrics.lineCount} lines, ${result.metrics.cyclomaticComplexity} complexity`);
    } else {
      console.error('File analysis failed:', result.error);
    }
  } catch (error) {
    console.error('Error testing CodeAnalysisEngine:', error.message);
  }
}

async function testAIAnalysisCoordinator() {
  console.log('\n--- Testing AIAnalysisCoordinator ---');
  
  // Initialize coordinator
  const coordinator = new AIAnalysisCoordinator({
    // Use mock responses for testing
    openai: { apiKey: 'test-key' }
  });
  
  // Test file analysis
  const testFilePath = path.join(__dirname, 'components/aiAnalysisCoordinator/index.js');
  
  try {
    const content = await fs.readFile(testFilePath, 'utf8');
    
    // First analyze with CodeAnalysisEngine
    const engine = new CodeAnalysisEngine();
    await engine.initialize();
    
    const analysisResult = await engine.analyzeFile(testFilePath, content);
    
    if (analysisResult.success) {
      console.log('File analysis successful, now testing AI analysis');
      
      // Test AI analysis
      const file = {
        path: testFilePath,
        content: content
      };
      
      const aiResult = await coordinator.analyzeFile(file, analysisResult);
      
      if (aiResult.success) {
        console.log('AI analysis successful');
        console.log(`Found ${aiResult.findings.length} findings`);
        
        // Display first finding
        if (aiResult.findings.length > 0) {
          const finding = aiResult.findings[0];
          console.log(`Sample finding: ${finding.title} (${finding.priority})`);
          console.log(`Location: ${finding.location}`);
          console.log(`Suggestion: ${finding.suggestion}`);
        }
      } else {
        console.error('AI analysis failed:', aiResult.error);
      }
    } else {
      console.error('File analysis failed:', analysisResult.error);
    }
  } catch (error) {
    console.error('Error testing AIAnalysisCoordinator:', error.message);
  }
}

async function main() {
  console.log('Testing enhanced components...');
  
  try {
    await testCodeAnalysisEngine();
    await testAIAnalysisCoordinator();
    
    console.log('\nEnhanced components test completed successfully!');
  } catch (error) {
    console.error('Test failed:', error.message);
  }
}

// Run the tests
main().catch(error => {
  console.error('Unhandled error:', error);
  process.exit(1);
});
