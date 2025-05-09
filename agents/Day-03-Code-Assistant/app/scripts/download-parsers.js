/**
 * Script to download Tree-sitter parsers
 */

const fs = require('fs').promises;
const path = require('path');
const https = require('https');
const { promisify } = require('util');
const stream = require('stream');
const pipeline = promisify(stream.pipeline);
const { execSync } = require('child_process');

const PARSERS_DIR = path.join(__dirname, '..', 'parsers');
const TEMP_DIR = path.join(__dirname, '..', 'temp');

// List of parsers to download
const PARSERS = [
  { name: 'javascript', repo: 'https://github.com/tree-sitter/tree-sitter-javascript' },
  { name: 'typescript', repo: 'https://github.com/tree-sitter/tree-sitter-typescript' },
  { name: 'python', repo: 'https://github.com/tree-sitter/tree-sitter-python' },
  { name: 'java', repo: 'https://github.com/tree-sitter/tree-sitter-java' },
  { name: 'go', repo: 'https://github.com/tree-sitter/tree-sitter-go' },
  { name: 'ruby', repo: 'https://github.com/tree-sitter/tree-sitter-ruby' },
  { name: 'c', repo: 'https://github.com/tree-sitter/tree-sitter-c' },
  { name: 'cpp', repo: 'https://github.com/tree-sitter/tree-sitter-cpp' },
  { name: 'c-sharp', repo: 'https://github.com/tree-sitter/tree-sitter-c-sharp' },
  { name: 'php', repo: 'https://github.com/tree-sitter/tree-sitter-php' },
  { name: 'rust', repo: 'https://github.com/tree-sitter/tree-sitter-rust' }
];

async function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download ${url}: ${response.statusCode}`));
        return;
      }
      pipeline(response, file)
        .then(() => resolve())
        .catch(reject);
    }).on('error', reject);
  });
}

async function cloneAndBuildParser(parser) {
  const repoDir = path.join(TEMP_DIR, `tree-sitter-${parser.name}`);
  const wasmFile = path.join(PARSERS_DIR, `tree-sitter-${parser.name}.wasm`);
  
  try {
    // Clone repository
    console.log(`Cloning ${parser.name} parser repository...`);
    execSync(`git clone ${parser.repo} ${repoDir}`, { stdio: 'inherit' });
    
    // Build WASM
    console.log(`Building ${parser.name} parser...`);
    process.chdir(repoDir);
    
    // Special handling for TypeScript which has multiple parsers
    if (parser.name === 'typescript') {
      // Build TypeScript parser
      process.chdir(path.join(repoDir, 'typescript'));
      execSync('npx tree-sitter build-wasm', { stdio: 'inherit' });
      await fs.copyFile('tree-sitter-typescript.wasm', wasmFile);
      
      // Build TSX parser
      process.chdir(path.join(repoDir, 'tsx'));
      execSync('npx tree-sitter build-wasm', { stdio: 'inherit' });
      await fs.copyFile('tree-sitter-tsx.wasm', path.join(PARSERS_DIR, 'tree-sitter-tsx.wasm'));
    } else {
      execSync('npx tree-sitter build-wasm', { stdio: 'inherit' });
      await fs.copyFile(`tree-sitter-${parser.name}.wasm`, wasmFile);
    }
    
    console.log(`Successfully built ${parser.name} parser`);
    return true;
  } catch (error) {
    console.error(`Error building ${parser.name} parser:`, error.message);
    return false;
  }
}

async function downloadParsers() {
  try {
    // Create directories
    await fs.mkdir(PARSERS_DIR, { recursive: true });
    await fs.mkdir(TEMP_DIR, { recursive: true });
    
    // Check if tree-sitter CLI is installed
    try {
      execSync('npx tree-sitter --help', { stdio: 'ignore' });
      console.log('Tree-sitter CLI is available');
    } catch (error) {
      console.log('Installing tree-sitter CLI...');
      execSync('npm install -g tree-sitter-cli', { stdio: 'inherit' });
    }
    
    // Clone and build each parser
    const results = [];
    for (const parser of PARSERS) {
      results.push(await cloneAndBuildParser(parser));
    }
    
    // Clean up
    console.log('Cleaning up temporary files...');
    await fs.rm(TEMP_DIR, { recursive: true, force: true });
    
    // Summary
    const successful = results.filter(r => r).length;
    console.log(`\nDownloaded ${successful} of ${PARSERS.length} parsers successfully!`);
    console.log(`Parser files are located in: ${PARSERS_DIR}`);
  } catch (error) {
    console.error('Error downloading parsers:', error);
  }
}

// Run the download
downloadParsers();
