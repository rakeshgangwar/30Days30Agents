/**
 * Integration tests for the flow from Repository Access Layer to Code Analysis Engine
 */

const RepositoryAccessLayer = require('../../../src/components/repositoryAccessLayer');
const CodeAnalysisEngine = require('../../../src/components/codeAnalysisEngine');
const path = require('path');
const mock = require('mock-fs');

describe('Repository to Analysis Integration', () => {
  // Setup and teardown
  beforeEach(() => {
    // Setup mock file system with sample repository
    mock({
      'repos/test-repo': {
        'src': {
          'app.js': `
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(3000, () => {
  console.log('Server started on port 3000');
});
          `,
          'utils': {
            'helper.js': `
function formatDate(date) {
  const month = date.getMonth() + 1;
  const day = date.getDate();
  return \`\${date.getFullYear()}-\${month < 10 ? '0' + month : month}-\${day < 10 ? '0' + day : day}\`;
}

function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

module.exports = {
  formatDate,
  calculateTotal
};
            `
          }
        },
        'package.json': `
{
  "name": "test-repo",
  "version": "1.0.0",
  "description": "Test repository for integration tests",
  "main": "src/app.js",
  "scripts": {
    "start": "node src/app.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.17.1"
  }
}
        `
      }
    });
  });

  afterEach(() => {
    // Restore real file system
    mock.restore();
  });

  // Tests
  test('should successfully read and analyze repository files', async () => {
    // Arrange
    const repoPath = path.resolve('repos/test-repo');
    const repositoryAccess = new RepositoryAccessLayer({
      workDir: path.resolve('repos')
    });
    const codeAnalysis = new CodeAnalysisEngine();
    await codeAnalysis.initialize();

    // Act
    // 1. List repository files
    const files = await repositoryAccess.listRepositoryFiles(repoPath);
    
    // 2. Read file contents
    const fileContents = [];
    for (const filePath of files) {
      const content = await repositoryAccess.readFileContent(filePath);
      if (content.success) {
        fileContents.push({
          path: filePath,
          content: content.content
        });
      }
    }
    
    // 3. Analyze files
    const analysisResults = await codeAnalysis.analyzeFiles(fileContents);
    
    // Assert
    expect(files.length).toBeGreaterThan(0);
    expect(fileContents.length).toBeGreaterThan(0);
    expect(analysisResults.length).toBe(fileContents.length);
    
    // Check that analysis results contain expected data
    const jsFiles = analysisResults.filter(r => r.language === 'javascript');
    expect(jsFiles.length).toBeGreaterThan(0);
    
    // At least one file should have structure information
    const filesWithStructure = analysisResults.filter(r => r.success && r.structure && 
      (r.structure.functions.length > 0 || r.structure.classes.length > 0 || r.structure.methods.length > 0));
    expect(filesWithStructure.length).toBeGreaterThan(0);
    
    // Package.json should be successfully analyzed
    const packageJsonResult = analysisResults.find(r => r.path.includes('package.json'));
    expect(packageJsonResult).toBeDefined();
    expect(packageJsonResult.success).toBe(true);
  });

  test('should generate a codebase overview', async () => {
    // Arrange
    const repoPath = path.resolve('repos/test-repo');
    const repositoryAccess = new RepositoryAccessLayer({
      workDir: path.resolve('repos')
    });
    const codeAnalysis = new CodeAnalysisEngine();
    await codeAnalysis.initialize();

    // Act
    // 1. List and read files
    const files = await repositoryAccess.listRepositoryFiles(repoPath);
    const fileContents = [];
    for (const filePath of files) {
      const content = await repositoryAccess.readFileContent(filePath);
      if (content.success) {
        fileContents.push({
          path: filePath,
          content: content.content
        });
      }
    }
    
    // 2. Analyze files
    const analysisResults = await codeAnalysis.analyzeFiles(fileContents);
    
    // 3. Generate overview
    const overview = codeAnalysis.generateCodebaseOverview(analysisResults);
    
    // Assert
    expect(overview).toBeDefined();
    expect(overview.fileCount).toBe(analysisResults.length);
    expect(overview.languageBreakdown).toBeDefined();
    expect(overview.languageBreakdown.javascript).toBeGreaterThan(0);
    expect(overview.totalLines).toBeGreaterThan(0);
    expect(overview.structureSummary).toBeDefined();
  });
});