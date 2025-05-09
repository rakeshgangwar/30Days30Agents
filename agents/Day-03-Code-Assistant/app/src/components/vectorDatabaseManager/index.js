/**
 * Vector Database Manager
 *
 * This component manages a vector database for semantic code search,
 * allowing for more accurate retrieval of relevant code snippets.
 */

const path = require('path');
const fs = require('fs').promises;
const { OpenAI } = require('openai');
const hnswlib = require('hnswlib-node');

class VectorDatabaseManager {
  constructor(options = {}) {
    this.options = {
      storagePath: options.storagePath || path.join(process.cwd(), 'storage', 'vector-db'),
      embeddingsModel: options.embeddingsModel || 'text-embedding-3-small',
      dimensions: options.dimensions || 1536,
      maxConnections: options.maxConnections || 16,
      ...options
    };

    this.openaiApiKey = options.openaiApiKey;
    this.openai = null;
    this.vectorStores = new Map();
    this.documents = new Map(); // Store documents by ID for retrieval
    this.initialized = false;
  }

  /**
   * Initialize the vector database manager
   * @returns {Promise<boolean>} - Success status
   */
  async initialize() {
    if (this.initialized) return true;

    try {
      // Create storage directory if it doesn't exist
      await fs.mkdir(this.options.storagePath, { recursive: true });

      // Initialize OpenAI client
      this.openai = new OpenAI({
        apiKey: this.openaiApiKey
      });

      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize VectorDatabaseManager:', error.message);
      return false;
    }
  }

  /**
   * Create embeddings for texts using OpenAI API
   * @param {string[]} texts - Array of texts to embed
   * @returns {Promise<number[][]>} - Array of embeddings
   */
  async createEmbeddings(texts) {
    if (!this.openai) {
      throw new Error('OpenAI client not initialized');
    }

    // Handle empty input
    if (!texts || texts.length === 0) {
      return [];
    }

    // Ensure texts are strings and not empty
    const validTexts = texts
      .filter(text => text && typeof text === 'string' && text.trim().length > 0)
      .map(text => text.trim());

    // If no valid texts, return empty array
    if (validTexts.length === 0) {
      return [];
    }

    try {
      const response = await this.openai.embeddings.create({
        model: this.options.embeddingsModel,
        input: validTexts
      });

      return response.data.map(item => item.embedding);
    } catch (error) {
      console.error('Error creating embeddings:', error.message);
      throw error;
    }
  }

  /**
   * Get or create a vector store for a repository
   * @param {string} repoId - Repository identifier
   * @returns {Promise<Object>} - Vector store and documents
   */
  async getVectorStore(repoId) {
    if (!this.initialized) {
      await this.initialize();
    }

    // Check if vector store already exists in memory
    if (this.vectorStores.has(repoId)) {
      return {
        index: this.vectorStores.get(repoId),
        documents: this.documents.get(repoId) || []
      };
    }

    // Check if vector store exists on disk
    const vectorStorePath = path.join(this.options.storagePath, repoId);
    const indexPath = path.join(vectorStorePath, 'index.bin');
    const documentsPath = path.join(vectorStorePath, 'documents.json');

    try {
      // Check if files exist
      await fs.access(indexPath);
      await fs.access(documentsPath);

      // Load index from disk
      const index = new hnswlib.HierarchicalNSW('cosine', this.options.dimensions);
      index.readIndex(indexPath);

      // Load documents from disk
      const documentsJson = await fs.readFile(documentsPath, 'utf8');
      const documents = JSON.parse(documentsJson);

      // Store in memory
      this.vectorStores.set(repoId, index);
      this.documents.set(repoId, documents);

      console.log(`Loaded existing vector store for ${repoId} with ${documents.length} documents`);

      return {
        index,
        documents
      };
    } catch (error) {
      // Create new vector store
      console.log(`Creating new vector store for ${repoId}`);

      // Create directory
      await fs.mkdir(vectorStorePath, { recursive: true });

      // Create new index
      const index = new hnswlib.HierarchicalNSW('cosine', this.options.dimensions);

      // Initialize with max elements (can be increased later)
      index.initIndex(1000, this.options.maxConnections, 100, 200);

      // Store in memory
      this.vectorStores.set(repoId, index);
      this.documents.set(repoId, []);

      return {
        index,
        documents: []
      };
    }
  }

  /**
   * Add code snippets to the vector database
   * @param {string} repoId - Repository identifier
   * @param {Array<Object>} snippets - Code snippets to add
   * @returns {Promise<Object>} - Result
   */
  async addCodeSnippets(repoId, snippets) {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // Handle empty snippets array
      if (!snippets || snippets.length === 0) {
        return {
          success: true,
          count: 0
        };
      }

      // Get or create vector store
      const { index, documents } = await this.getVectorStore(repoId);

      // Filter out snippets with empty content
      const validSnippets = snippets.filter(snippet =>
        snippet &&
        snippet.content &&
        typeof snippet.content === 'string' &&
        snippet.content.trim().length > 0
      );

      if (validSnippets.length === 0) {
        return {
          success: true,
          count: 0
        };
      }

      // Convert snippets to documents
      const newDocuments = validSnippets.map(snippet => ({
        content: snippet.content,
        metadata: {
          filePath: snippet.filePath || 'unknown',
          startLine: snippet.startLine || 0,
          endLine: snippet.endLine || 0,
          type: snippet.type || 'code',
          name: snippet.name || '',
          language: snippet.language || 'unknown'
        }
      }));

      // Create embeddings for new documents
      const texts = newDocuments.map(doc => doc.content);
      const embeddings = await this.createEmbeddings(texts);

      // If no embeddings were created, return
      if (embeddings.length === 0) {
        return {
          success: true,
          count: 0
        };
      }

      // Add embeddings to index
      const startIndex = documents.length;
      for (let i = 0; i < embeddings.length; i++) {
        index.addPoint(embeddings[i], startIndex + i);
      }

      // Add documents to collection
      const updatedDocuments = [...documents, ...newDocuments];
      this.documents.set(repoId, updatedDocuments);

      // Save to disk
      const vectorStorePath = path.join(this.options.storagePath, repoId);
      const indexPath = path.join(vectorStorePath, 'index.bin');
      const documentsPath = path.join(vectorStorePath, 'documents.json');

      // Save index
      index.writeIndex(indexPath);

      // Save documents
      await fs.writeFile(documentsPath, JSON.stringify(updatedDocuments));

      return {
        success: true,
        count: newDocuments.length
      };
    } catch (error) {
      console.error('Failed to add code snippets:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Search for similar code snippets
   * @param {string} repoId - Repository identifier
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @returns {Promise<Object>} - Search results
   */
  async searchSimilarCode(repoId, query, options = {}) {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // Get vector store
      const { index, documents } = await this.getVectorStore(repoId);

      // If no documents, return empty results
      if (documents.length === 0) {
        return {
          success: true,
          results: []
        };
      }

      // Create embedding for query
      const [queryEmbedding] = await this.createEmbeddings([query]);

      // Set default limit
      const k = Math.min(options.limit || 5, documents.length);

      // Perform search
      const searchResults = index.searchKnn(queryEmbedding, k);

      // Map results to documents
      const results = searchResults.neighbors.map((docIndex, i) => {
        const document = documents[docIndex];
        return {
          content: document.content,
          filePath: document.metadata.filePath,
          startLine: document.metadata.startLine,
          endLine: document.metadata.endLine,
          type: document.metadata.type,
          name: document.metadata.name,
          language: document.metadata.language,
          score: searchResults.distances[i]
        };
      });

      // Filter results if needed
      let filteredResults = results;
      if (options.filter) {
        filteredResults = results.filter(result => {
          for (const [key, value] of Object.entries(options.filter)) {
            if (result[key] !== value) {
              return false;
            }
          }
          return true;
        });
      }

      return {
        success: true,
        results: filteredResults
      };
    } catch (error) {
      console.error('Failed to search similar code:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Extract code snippets from files
   * @param {Array<Object>} files - Files to extract snippets from
   * @param {Array<Object>} analysisResults - Analysis results
   * @returns {Array<Object>} - Code snippets
   */
  extractCodeSnippets(files, analysisResults) {
    const snippets = [];

    for (const file of files) {
      // Find analysis result for this file
      const analysisResult = analysisResults.find(r => r.path === file.path);
      if (!analysisResult || !analysisResult.success) continue;

      const language = analysisResult.language || 'unknown';
      const content = file.content;

      // Add whole file as a snippet
      snippets.push({
        filePath: file.path,
        content: content,
        type: 'file',
        name: path.basename(file.path),
        language
      });

      // Extract classes
      if (analysisResult.structure && analysisResult.structure.classes) {
        for (const cls of analysisResult.structure.classes) {
          if (!cls.line) continue;

          // Extract class content
          const lines = content.split('\n');
          const classContent = lines.slice(cls.line - 1, cls.line + 20).join('\n');

          snippets.push({
            filePath: file.path,
            content: classContent,
            startLine: cls.line,
            endLine: cls.line + 20,
            type: 'class',
            name: cls.name,
            language
          });
        }
      }

      // Extract functions
      if (analysisResult.structure && analysisResult.structure.functions) {
        for (const func of analysisResult.structure.functions) {
          if (!func.line) continue;

          // Extract function content
          const lines = content.split('\n');
          const functionContent = lines.slice(func.line - 1, func.line + 15).join('\n');

          snippets.push({
            filePath: file.path,
            content: functionContent,
            startLine: func.line,
            endLine: func.line + 15,
            type: 'function',
            name: func.name,
            language
          });
        }
      }
    }

    return snippets;
  }

  /**
   * Index a repository
   * @param {string} repoId - Repository identifier
   * @param {string} repoPath - Path to the repository
   * @param {Object} repositoryAccess - Repository access layer
   * @param {Object} codeAnalysis - Code analysis engine
   * @returns {Promise<Object>} - Result
   */
  async indexRepository(repoId, repoPath, repositoryAccess, codeAnalysis) {
    try {
      console.log(`Indexing repository ${repoId}...`);

      // Check if repository path exists
      try {
        const stats = await fs.stat(repoPath);
        if (!stats.isDirectory()) {
          console.error(`Error: ${repoPath} is not a directory`);
          return {
            success: false,
            error: `${repoPath} is not a directory`
          };
        }
      } catch (error) {
        console.error(`Error: ${repoPath} does not exist`);
        return {
          success: false,
          error: `${repoPath} does not exist`
        };
      }

      // List files
      const files = await repositoryAccess.listRepositoryFiles(repoPath);

      // Check if there are any files
      if (!files || files.length === 0) {
        console.log('No files found in repository');
        return {
          success: true,
          snippetsCount: 0,
          filesCount: 0
        };
      }

      // Limit to a reasonable number of files
      const maxFiles = 100;
      const sampleFiles = files.slice(0, maxFiles);

      console.log(`Reading ${sampleFiles.length}/${files.length} files...`);

      // Read file contents
      const fileContents = [];
      for (const filePath of sampleFiles) {
        try {
          const content = await repositoryAccess.readFileContent(filePath);
          if (content.success) {
            fileContents.push({
              path: filePath,
              content: content.content
            });
          }
        } catch (error) {
          console.error(`Error reading file ${filePath}: ${error.message}`);
        }
      }

      // Check if any files were read successfully
      if (fileContents.length === 0) {
        console.log('No file contents could be read');
        return {
          success: true,
          snippetsCount: 0,
          filesCount: 0
        };
      }

      // Analyze files
      console.log('Analyzing files...');
      const analysisResults = await codeAnalysis.analyzeFiles(fileContents);

      // Extract code snippets
      console.log('Extracting code snippets...');
      const snippets = this.extractCodeSnippets(fileContents, analysisResults);

      // Check if any snippets were extracted
      if (snippets.length === 0) {
        console.log('No code snippets could be extracted');
        return {
          success: true,
          snippetsCount: 0,
          filesCount: fileContents.length
        };
      }

      // Add snippets to vector database
      console.log(`Adding ${snippets.length} snippets to vector database...`);
      const result = await this.addCodeSnippets(repoId, snippets);

      console.log(`Indexed ${result.count} snippets for repository ${repoId}`);

      return {
        success: true,
        snippetsCount: result.count,
        filesCount: fileContents.length
      };
    } catch (error) {
      console.error('Failed to index repository:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Clear the vector database for a repository
   * @param {string} repoId - Repository identifier
   * @returns {Promise<Object>} - Result
   */
  async clearRepository(repoId) {
    try {
      // Remove from memory
      this.vectorStores.delete(repoId);

      // Remove from disk
      const vectorStorePath = path.join(this.options.storagePath, repoId);
      await fs.rm(vectorStorePath, { recursive: true, force: true });

      return {
        success: true
      };
    } catch (error) {
      console.error('Failed to clear repository:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }
}

module.exports = VectorDatabaseManager;
