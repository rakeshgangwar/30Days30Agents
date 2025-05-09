# Repository Access Layer

This document provides implementation details for the Repository Access Layer of the Repository Analysis and Issue Creation Agent. This layer is responsible for accessing, cloning, and navigating through repository files.

## Table of Contents

1. [Overview](#overview)
2. [Key Responsibilities](#key-responsibilities)
3. [Implementation Details](#implementation-details)
4. [Code Examples](#code-examples)
5. [Best Practices](#best-practices)
6. [Integration Points](#integration-points)

## Overview

The Repository Access Layer serves as the foundation for the agent's ability to analyze code. It handles all interactions with the file system and Git repositories, providing a clean interface for other components to access repository contents without worrying about the underlying file operations.

## Key Responsibilities

- **Repository Cloning**: Clone repositories from GitHub or other Git providers
- **File System Navigation**: Traverse the repository's file structure efficiently
- **File Filtering**: Apply intelligent filtering to focus on relevant files
- **Content Reading**: Read file contents with appropriate encoding detection
- **Git Operations**: Perform Git operations like checking out branches or commits
- **Change Detection**: Identify changes between commits or branches

## Implementation Details

### Repository Cloning

For cloning repositories, we can use libraries like `simple-git` for Node.js or `GitPython` for Python. The implementation should:

1. Support both HTTPS and SSH authentication
2. Handle large repositories efficiently
3. Support shallow clones to minimize bandwidth and storage
4. Manage authentication securely

```javascript
// Example using simple-git in Node.js
const simpleGit = require('simple-git');
const fs = require('fs');
const path = require('path');

async function cloneRepository(repoUrl, targetDir, options = {}) {
  // Create target directory if it doesn't exist
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }
  
  const git = simpleGit();
  
  // Set default options
  const cloneOptions = {
    '--depth': options.depth || 1,  // Default to shallow clone
    '--single-branch': options.singleBranch !== false,
    '--branch': options.branch || 'main'
  };
  
  try {
    console.log(`Cloning ${repoUrl} to ${targetDir}...`);
    await git.clone(repoUrl, targetDir, cloneOptions);
    return { success: true, path: targetDir };
  } catch (error) {
    console.error(`Failed to clone repository: ${error.message}`);
    return { success: false, error: error.message };
  }
}
```

### File System Navigation

For traversing the repository, we can implement a breadth-first or depth-first traversal algorithm that respects common ignore patterns. Drawing inspiration from Cline's `listFiles` function:

```javascript
const path = require('path');
const glob = require('glob');

async function listRepositoryFiles(repoPath, options = {}) {
  // Default patterns to ignore
  const defaultIgnores = [
    'node_modules/**',
    '.git/**',
    'dist/**',
    'build/**',
    '**/*.min.js',
    '**/*.bundle.js',
    '**/vendor/**',
    '**/__pycache__/**',
    '**/venv/**',
    '**/env/**'
  ];
  
  // Combine default ignores with user-provided ignores
  const ignorePatterns = [...defaultIgnores, ...(options.ignore || [])];
  
  // Set up glob options
  const globOptions = {
    cwd: repoPath,
    ignore: ignorePatterns,
    nodir: options.filesOnly !== false,  // Default to files only
    dot: options.includeDotFiles === true,  // Default to excluding dot files
    absolute: true
  };
  
  // Use glob to find files
  return new Promise((resolve, reject) => {
    glob(options.pattern || '**/*', globOptions, (err, files) => {
      if (err) {
        reject(err);
      } else {
        resolve(files);
      }
    });
  });
}
```

### File Content Reading

When reading file contents, it's important to handle different encodings and file types correctly:

```javascript
const fs = require('fs').promises;
const isBinaryFile = require('is-binary-file').isBinaryFile;
const chardet = require('chardet');
const iconv = require('iconv-lite');

async function readFileContent(filePath) {
  try {
    // First check if it's a binary file
    const isBinary = await isBinaryFile(filePath);
    if (isBinary) {
      return { 
        success: false, 
        error: 'Binary file detected', 
        isBinary: true,
        path: filePath
      };
    }
    
    // Read file as buffer first to detect encoding
    const buffer = await fs.readFile(filePath);
    
    // Detect encoding
    const encoding = chardet.detect(buffer) || 'utf8';
    
    // Convert buffer to string using detected encoding
    const content = iconv.decode(buffer, encoding);
    
    return {
      success: true,
      content,
      encoding,
      path: filePath
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      path: filePath
    };
  }
}
```

## Code Examples

### Complete Repository Access Module

Here's a more complete example of a Repository Access module that combines the above functions:

```javascript
// repositoryAccess.js
const simpleGit = require('simple-git');
const fs = require('fs').promises;
const path = require('path');
const glob = require('glob');
const isBinaryFile = require('is-binary-file').isBinaryFile;
const chardet = require('chardet');
const iconv = require('iconv-lite');

class RepositoryAccessLayer {
  constructor(options = {}) {
    this.options = {
      workDir: options.workDir || path.join(process.cwd(), 'repos'),
      defaultBranch: options.defaultBranch || 'main',
      maxFileSize: options.maxFileSize || 1024 * 1024, // 1MB
      ...options
    };
    
    // Create working directory if it doesn't exist
    this.ensureWorkDir();
  }
  
  async ensureWorkDir() {
    try {
      await fs.mkdir(this.options.workDir, { recursive: true });
    } catch (error) {
      console.error(`Failed to create working directory: ${error.message}`);
    }
  }
  
  async cloneRepository(repoUrl, options = {}) {
    const repoName = this.getRepoNameFromUrl(repoUrl);
    const targetDir = path.join(this.options.workDir, repoName);
    
    // Check if repo already exists
    try {
      await fs.access(targetDir);
      // If we get here, the directory exists
      const git = simpleGit(targetDir);
      await git.pull(); // Update the repo
      return { success: true, path: targetDir, alreadyExists: true };
    } catch {
      // Directory doesn't exist, proceed with clone
    }
    
    // Clone options
    const cloneOptions = {
      depth: options.depth || 1,
      singleBranch: options.singleBranch !== false,
      branch: options.branch || this.options.defaultBranch
    };
    
    return await this._cloneRepo(repoUrl, targetDir, cloneOptions);
  }
  
  async _cloneRepo(repoUrl, targetDir, options) {
    const git = simpleGit();
    
    const cloneOptions = {
      '--depth': options.depth,
      '--single-branch': options.singleBranch,
      '--branch': options.branch
    };
    
    try {
      console.log(`Cloning ${repoUrl} to ${targetDir}...`);
      await git.clone(repoUrl, targetDir, cloneOptions);
      return { success: true, path: targetDir };
    } catch (error) {
      console.error(`Failed to clone repository: ${error.message}`);
      return { success: false, error: error.message };
    }
  }
  
  getRepoNameFromUrl(repoUrl) {
    // Extract repo name from URL
    const urlParts = repoUrl.split('/');
    let repoName = urlParts[urlParts.length - 1];
    
    // Remove .git extension if present
    if (repoName.endsWith('.git')) {
      repoName = repoName.slice(0, -4);
    }
    
    return repoName;
  }
  
  // Additional methods would be implemented here
}

module.exports = RepositoryAccessLayer;
```

## Best Practices

1. **Efficient File Traversal**: Use streaming or iterative approaches for large repositories
2. **Respect .gitignore**: Honor existing .gitignore files to avoid processing irrelevant files
3. **Encoding Detection**: Always detect file encoding before reading content
4. **Error Handling**: Implement robust error handling for file system operations
5. **Cleanup**: Properly clean up temporary repositories after analysis
6. **Rate Limiting**: Implement rate limiting for Git operations to avoid API rate limits
7. **Caching**: Cache repository contents when appropriate to improve performance

## Integration Points

The Repository Access Layer interfaces with:

1. **Code Analysis Engine**: Provides file contents for analysis
2. **Configuration Manager**: Receives filtering rules and repository settings
3. **External Git Providers**: Interacts with GitHub, GitLab, or other Git hosting services

By implementing a robust Repository Access Layer, the agent will have a solid foundation for accessing and analyzing code repositories efficiently and reliably.
