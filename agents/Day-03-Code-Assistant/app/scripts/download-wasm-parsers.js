/**
 * Script to download pre-built Tree-sitter WASM parsers
 */

const fs = require('fs');
const fsPromises = fs.promises;
const path = require('path');
const https = require('https');
const { promisify } = require('util');
const stream = require('stream');
const pipeline = promisify(stream.pipeline);

const PARSERS_DIR = path.join(__dirname, '..', 'parsers');

// List of parsers to download from CDN
const PARSERS = [
  {
    name: 'javascript',
    url: 'https://github.com/tree-sitter/tree-sitter-javascript/releases/download/v0.23.1/tree-sitter-javascript.wasm'
  },
  {
    name: 'typescript',
    url: 'https://github.com/tree-sitter/tree-sitter-typescript/releases/download/v0.23.2/tree-sitter-typescript.wasm'
  },
  {
    name: 'tsx',
    url: 'https://github.com/tree-sitter/tree-sitter-typescript/releases/download/v0.23.2/tree-sitter-tsx.wasm'
  },
  {
    name: 'python',
    url: 'https://github.com/tree-sitter/tree-sitter-python/releases/download/v0.23.6/tree-sitter-python.wasm'
  },
  {
    name: 'java',
    url: 'https://github.com/tree-sitter/tree-sitter-java/releases/download/v0.23.5/tree-sitter-java.wasm'
  },
  {
    name: 'go',
    url: 'https://github.com/tree-sitter/tree-sitter-go/releases/download/v0.23.4/tree-sitter-go.wasm'
  },
  {
    name: 'ruby',
    url: 'https://github.com/tree-sitter/tree-sitter-ruby/releases/download/v0.23.1/tree-sitter-ruby.wasm'
  },
  {
    name: 'c',
    url: 'https://github.com/tree-sitter/tree-sitter-c/releases/download/v0.23.5/tree-sitter-c.wasm'
  },
  {
    name: 'cpp',
    url: 'https://github.com/tree-sitter/tree-sitter-cpp/releases/download/v0.23.4/tree-sitter-cpp.wasm'
  },
  {
    name: 'c_sharp',
    url: 'https://github.com/tree-sitter/tree-sitter-c-sharp/releases/download/v0.23.1/tree-sitter-c_sharp.wasm'
  },
  {
    name: 'rust',
    url: 'https://github.com/tree-sitter/tree-sitter-rust/releases/download/v0.24.0/tree-sitter-rust.wasm'
  }
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

async function downloadParsers() {
  try {
    // Create parsers directory
    await fsPromises.mkdir(PARSERS_DIR, { recursive: true });

    // Download each parser
    const results = [];
    for (const parser of PARSERS) {
      const dest = path.join(PARSERS_DIR, `tree-sitter-${parser.name}.wasm`);

      try {
        console.log(`Downloading ${parser.name} parser from ${parser.url}...`);
        await downloadFile(parser.url, dest);
        console.log(`Successfully downloaded ${parser.name} parser to ${dest}`);
        results.push(true);
      } catch (error) {
        console.error(`Error downloading ${parser.name} parser:`, error.message);
        results.push(false);
      }
    }

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
