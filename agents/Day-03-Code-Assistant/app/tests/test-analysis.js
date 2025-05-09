// Test script for analyzing a limited number of files
const RepositoryAnalysisAgent = require('../src/app');
const path = require('path');
const fs = require('fs');

async function testAnalysis() {
  console.log('Starting limited file analysis test...');
  
  // Initialize agent
  const agent = new RepositoryAnalysisAgent();
  
  try {
    // Initialize components
    await agent.initialize();
    
    // Use an already cloned repository
    const repoPath = path.join(process.cwd(), 'repos/digi-persona');
    
    // Check if repository exists
    if (!fs.existsSync(repoPath)) {
      console.error(`Repository not found at ${repoPath}`);
      console.log('Please run the full analysis first to clone the repository, or specify a different path.');
      process.exit(1);
    }
    
    // Define files to analyze (just 3 files)
    const filePaths = [
      'app/main.py',                          // Python main file
      'app/api/endpoints/personas.py',        // Python API endpoint
      'frontend/src/components/ui/button.tsx' // TypeScript React component
    ];
    
    // Read file contents
    console.log('Reading files...');
    const files = [];
    
    for (const filePath of filePaths) {
      try {
        const fullPath = path.join(repoPath, filePath);
        const content = fs.readFileSync(fullPath, 'utf8');
        files.push({
          path: filePath,
          content: content
        });
        console.log(`Read file: ${filePath} (${content.length} bytes)`);
      } catch (error) {
        console.warn(`Could not read file ${filePath}: ${error.message}`);
      }
    }
    
    if (files.length === 0) {
      console.error('No files could be read. Exiting.');
      process.exit(1);
    }
    
    // Analyze files
    console.log('\nAnalyzing files...');
    const analysisResults = await agent.codeAnalysis.analyzeFiles(files);
    
    // Repository info
    const repositoryInfo = {
      name: 'rakeshgangwar/digi-persona',
      description: 'A platform for creating and managing multiple virtual personas with social media presence powered by AI',
      url: 'https://github.com/rakeshgangwar/digi-persona'
    };
    
    // AI analysis
    console.log('\nPerforming AI analysis...');
    const fileAnalysisResults = await agent.aiAnalysis.analyzeMultipleFiles(files, analysisResults);
    
    // Only do repository analysis if we have file analysis results
    let repositoryAnalysisResult = null;
    if (fileAnalysisResults.some(r => r.success)) {
      console.log('\nPerforming repository analysis...');
      repositoryAnalysisResult = await agent.aiAnalysis.analyzeRepository(repositoryInfo, analysisResults);
    }
    
    // Prioritize findings
    const prioritizedFindings = agent.aiAnalysis.prioritizeFindings(fileAnalysisResults, repositoryAnalysisResult || { success: false });
    
    // Output results
    console.log('\nAnalysis Results:');
    console.log(`- Files Analyzed: ${files.length}`);
    console.log(`- Total Findings: ${prioritizedFindings.length}`);
    
    if (prioritizedFindings.length > 0) {
      console.log('\nFindings:');
      prioritizedFindings.forEach((finding, index) => {
        console.log(`\n${index + 1}. ${finding.title} (${finding.priority})`);
        console.log(`   Source: ${finding.source}`);
        if (finding.source === 'file') {
          console.log(`   File: ${finding.filePath}`);
          console.log(`   Location: ${finding.location}`);
        } else {
          console.log(`   Area: ${finding.area}`);
        }
        console.log(`   Description: ${finding.description.substring(0, 100)}...`);
        console.log(`   Suggestion: ${finding.suggestion}`);
      });
    } else {
      console.log('\nNo findings were generated.');
    }
    
    // Save results to file
    const outputPath = 'test-analysis-results.json';
    fs.writeFileSync(outputPath, JSON.stringify({
      repositoryInfo,
      files: files.map(f => f.path),
      findings: prioritizedFindings
    }, null, 2));
    console.log(`\nResults saved to ${outputPath}`);
    
  } catch (error) {
    console.error('Error:', error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Run the test
testAnalysis();
