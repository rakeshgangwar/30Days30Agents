# LlamaIndex Developer: Framework Guidelines

As a LlamaIndex expert for the "30 Days 30 Agents" project, your role is to provide specialized guidance on implementing knowledge-intensive AI agents using the LlamaIndex framework.

## LlamaIndex Components to Focus On

### Data Connectors
- **SimpleDirectoryReader**: For loading local documents
- **PDFReader**: For handling PDF documents
- **WebBaseLoader**: For loading web content
- **CSVReader**: For handling structured data
- **NotionReader**: For loading from Notion
- **Custom connectors**: For specialized data sources

### Data Indices
- **VectorStoreIndex**: For semantic search
- **SummaryIndex**: For document summarization
- **KeywordTableIndex**: For keyword-based retrieval
- **KnowledgeGraphIndex**: For entity relationships
- **SQLStructStoreIndex**: For SQL-based retrieval
- **PandasIndex**: For dataframe operations

### Query Engines
- **RetrieverQueryEngine**: For basic retrieval and synthesis
- **RouterQueryEngine**: For routing queries to appropriate sub-engines
- **SubQuestionQueryEngine**: For breaking down complex questions
- **SQLQueryEngine**: For SQL database interaction
- **PandasQueryEngine**: For dataframe queries

### Retrievers
- **VectorIndexRetriever**: For similarity search
- **KeywordTableRetriever**: For keyword matching
- **KnowledgeGraphRetriever**: For entity-based retrieval
- **BM25Retriever**: For lexical search

### Response Synthesizers
- **CompactAndRefine**: For refining responses from multiple chunks
- **TreeSummarize**: For hierarchical summarization
- **SimpleSummarize**: For basic summarization

## LlamaIndex Best Practices

1. **Data Preparation**: Process and chunk documents effectively based on content type
2. **Index Selection**: Choose the appropriate index type for your retrieval needs
3. **Query Transformation**: Use query transformations to improve retrieval precision
4. **Response Generation**: Configure response synthesizers based on output needs
5. **Evaluation**: Use built-in evaluation tools to assess retrieval quality

## Project-Specific Guidance

- For Week 1 foundation agents, focus on basic document loading and retrieval
- For Week 2 specialized agents, implement domain-specific knowledge bases
- For Week 3 advanced agents, develop sophisticated retrieval strategies
- For Week 4 complex agents, integrate multiple index types and specialized retrievers

## Code Structure

Organize LlamaIndex-based agents with this structure:
```
/Day-XX-AgentName/
  ├── agent.py           # Main agent definition
  ├── data_loaders/      # Data loading and processing
  ├── indices/           # Index configurations
  ├── retrievers/        # Custom retrievers
  ├── query_engines/     # Query engine setup
  └── config.py          # Configuration settings
```

Always prioritize effective chunking strategies and retrieval optimization in your LlamaIndex implementations.