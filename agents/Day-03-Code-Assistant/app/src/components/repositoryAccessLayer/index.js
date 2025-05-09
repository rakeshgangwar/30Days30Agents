// Repository Access Layer Component
// This component handles cloning, accessing, and navigating repository files

const simpleGit = require('simple-git');
const fs = require('fs').promises;
const path = require('path');
const glob = require('glob');
const { isBinaryFile } = require('isbinaryfile');
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
  
  listRepositoryFiles(repoPath, options = {}) {
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
  
  async readFileContent(filePath) {
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
}

module.exports = RepositoryAccessLayer;