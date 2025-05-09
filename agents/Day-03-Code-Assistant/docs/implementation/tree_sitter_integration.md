# Tree-sitter Integration

This document provides information about integrating Tree-sitter for code parsing and analysis in the Repository Analysis and Issue Creation Agent.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Supported Languages](#supported-languages)
4. [Usage](#usage)
5. [Queries](#queries)
6. [Fallback Mechanisms](#fallback-mechanisms)
7. [Resources](#resources)

## Overview

Tree-sitter is a parser generator tool and an incremental parsing library. It can build a concrete syntax tree for a source file and efficiently update the syntax tree as the source file is edited. We use Tree-sitter to parse code files and extract their structure for analysis.

## Installation

### Prerequisites

- Node.js 14 or higher
- npm or yarn

### Installing Tree-sitter

Tree-sitter is included as a dependency in the project's `package.json` file:

```json
"dependencies": {
  "web-tree-sitter": "^0.20.7"
}
```

### Installing Language Parsers

Tree-sitter requires language-specific parsers for each supported language. These parsers are WebAssembly (WASM) files that need to be downloaded and placed in the `parsers` directory.

You can download the parsers manually from the official repositories:

1. Visit the [List of parsers](https://github.com/tree-sitter/tree-sitter/wiki/List-of-parsers) on the Tree-sitter wiki
2. Clone the repository for each language you want to support
3. Build the WASM file for each language
4. Place the WASM files in the `parsers` directory

Alternatively, you can use the provided script to download and install the parsers:

```bash
# From the project root directory
node scripts/download-parsers.js
```

## Supported Languages

The agent currently supports the following languages:

| Language   | Parser Repository                                   | File Extensions       |
|------------|-----------------------------------------------------|------------------------|
| JavaScript | https://github.com/tree-sitter/tree-sitter-javascript | .js                   |
| TypeScript | https://github.com/tree-sitter/tree-sitter-typescript | .ts, .tsx             |
| Python     | https://github.com/tree-sitter/tree-sitter-python     | .py                   |
| Java       | https://github.com/tree-sitter/tree-sitter-java       | .java                 |
| Go         | https://github.com/tree-sitter/tree-sitter-go         | .go                   |
| Ruby       | https://github.com/tree-sitter/tree-sitter-ruby       | .rb                   |
| C++        | https://github.com/tree-sitter/tree-sitter-cpp        | .cpp, .hpp, .cc, .h   |
| C#         | https://github.com/tree-sitter/tree-sitter-c-sharp    | .cs                   |

## Usage

### Initializing Tree-sitter

```javascript
const Parser = require('web-tree-sitter');

async function initializeParser() {
  await Parser.init();
  
  // Load language parsers
  const javascriptParser = await loadLanguage('javascript');
  const pythonParser = await loadLanguage('python');
  // Load other languages as needed
  
  return {
    javascript: javascriptParser,
    python: pythonParser,
    // Other languages
  };
}

async function loadLanguage(language) {
  const parser = new Parser();
  const langPath = path.join(__dirname, `parsers/tree-sitter-${language}.wasm`);
  const lang = await Parser.Language.load(langPath);
  parser.setLanguage(lang);
  return parser;
}
```

### Parsing a File

```javascript
function parseFile(parser, content) {
  try {
    const tree = parser.parse(content);
    return {
      success: true,
      tree
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}
```

### Extracting Structure

```javascript
function extractStructure(tree, content) {
  const structure = {
    classes: [],
    functions: [],
    methods: []
  };
  
  // Extract classes
  const classNodes = findNodes(tree.rootNode, 'class_definition');
  for (const node of classNodes) {
    structure.classes.push({
      name: getNodeText(node.childForFieldName('name'), content),
      start: node.startPosition,
      end: node.endPosition
    });
  }
  
  // Extract functions
  const functionNodes = findNodes(tree.rootNode, 'function_definition');
  for (const node of functionNodes) {
    structure.functions.push({
      name: getNodeText(node.childForFieldName('name'), content),
      start: node.startPosition,
      end: node.endPosition
    });
  }
  
  return structure;
}

function findNodes(node, type) {
  const nodes = [];
  
  if (node.type === type) {
    nodes.push(node);
  }
  
  for (let i = 0; i < node.childCount; i++) {
    const child = node.child(i);
    nodes.push(...findNodes(child, type));
  }
  
  return nodes;
}

function getNodeText(node, content) {
  if (!node) return '';
  return content.substring(node.startIndex, node.endIndex);
}
```

## Queries

Tree-sitter provides a query language that allows you to search for patterns in the syntax tree. This is useful for extracting specific structures from code files.

### Example Query for JavaScript Classes

```javascript
const query = `
(class_declaration
  name: (identifier) @class.name
  body: (class_body) @class.body)
`;

function executeQuery(tree, query, content) {
  const queryInstance = tree.getLanguage().query(query);
  const matches = queryInstance.matches(tree.rootNode);
  
  return matches.map(match => {
    const result = {};
    
    for (const capture of match.captures) {
      const name = capture.name;
      const node = capture.node;
      result[name] = content.substring(node.startIndex, node.endIndex);
    }
    
    return result;
  });
}
```

## Fallback Mechanisms

In case Tree-sitter fails to parse a file or a language parser is not available, the agent provides fallback mechanisms:

1. **Regex-based Parsing**: Uses regular expressions to extract basic structure
2. **Language Detection**: Falls back to simpler language detection based on file extensions
3. **Mock Analysis**: Provides mock analysis results for unsupported languages

## Resources

- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Tree-sitter GitHub Repository](https://github.com/tree-sitter/tree-sitter)
- [List of Tree-sitter Parsers](https://github.com/tree-sitter/tree-sitter/wiki/List-of-parsers)
- [Tree-sitter Query Language Documentation](https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax)
- [web-tree-sitter NPM Package](https://www.npmjs.com/package/web-tree-sitter)
