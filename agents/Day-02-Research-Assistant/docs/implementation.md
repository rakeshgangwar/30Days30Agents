# Day 2: Research Assistant - Implementation Documentation

## 1. Overview

The Research Assistant is a comprehensive agent designed to conduct web research on user-specified topics, synthesize information from multiple sources, and provide summarized findings with citations. It employs an iterative research process to ensure thorough coverage and high-quality information synthesis.

## 2. Architecture

The Research Assistant follows a modular architecture built around a LangGraph workflow. The architecture consists of several key components:

### 2.1 Core Components

- **Agent Core**: Coordinates all components and manages the research workflow
- **LangGraph Workflow**: Orchestrates the research process through a state machine
- **Tool Integration**: Provides access to search engines, web browsing, and content extraction
- **Knowledge Processing**: Manages information storage, retrieval, and synthesis
- **Output Formatting**: Generates research reports with proper citations

### 2.2 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Research Assistant                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                               │                                 │
│  ┌─────────────────┐    ┌─────▼────────┐    ┌────────────────┐  │
│  │ Input Processing│◄───┤  Agent Core  ├───►│Output Formatting│  │
│  └────────┬────────┘    └──────┬───────┘    └────────┬───────┘  │
│           │                    │                     │          │
│  ┌────────▼────────┐    ┌──────▼───────┐    ┌────────▼───────┐  │
│  │Research Workflow│◄───┤Tool Integration├──►│Knowledge Process│ │
│  └─────────────────┘    └────────────────┘   └────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 3. Implementation Details

### 3.1 Core Agent (`core/agent.py`)

The `ResearchAssistant` class serves as the main entry point and coordinates all components:

```python
class ResearchAssistant:
    def __init__(self, model_name: Optional[str] = None):
        # Initialize LLMs for different phases
        self.analysis_llm = self._initialize_llm(model_name, phase="analysis")
        self.synthesis_llm = self._initialize_llm(model_name, phase="synthesis")
        
        # Initialize components
        self.query_analyzer = QueryAnalyzer(self.analysis_llm)
        self.search_query_formulator = SearchQueryFormulator(self.analysis_llm)
        self.strategy_planner = ResearchStrategyPlanner(self.analysis_llm)
        self.synthesizer = InformationSynthesizer(self.synthesis_llm)
        self.source_evaluator = SourceEvaluator(self.analysis_llm)
        self.citation_formatter = CitationFormatter()
        self.summary_generator = ResearchSummaryGenerator(self.synthesis_llm)
        self.findings_extractor = KeyFindingsExtractor(self.synthesis_llm)
        self.report_generator = ResearchReportGenerator(...)
        
        # Initialize workflow
        self.workflow = self._initialize_workflow()
        
    def research(self, query: str, max_iterations: int = 50, 
                return_intermediate_steps: bool = False,
                research_depth: str = None) -> Dict[str, Any]:
        # Main research method
        ...
```

### 3.2 LangGraph Workflow (`core/langgraph_workflow.py`)

The research workflow is implemented as a LangGraph state machine:

```python
class ResearchGraph:
    def __init__(self, research_assistant):
        self.research_assistant = research_assistant
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        # Create the StateGraph with ResearchState
        research_graph = StateGraph(ResearchState)
        
        # Add nodes for each step in the workflow
        research_graph.add_node("analyze_query", self.analyze_query)
        research_graph.add_node("perform_search", self.perform_search)
        research_graph.add_node("browse_content", self.browse_content)
        research_graph.add_node("extract_information", self.extract_information)
        research_graph.add_node("evaluate_progress", self.evaluate_progress)
        research_graph.add_node("synthesize_information", self.synthesize_information)
        research_graph.add_node("generate_report", self.generate_report)
        
        # Define edges between nodes
        research_graph.add_edge("analyze_query", "perform_search")
        research_graph.add_conditional_edges(...)
        
        return research_graph.compile()
```

### 3.3 Input Processing (`components/input_processing.py`)

Handles the initial analysis of research queries:

- `QueryAnalyzer`: Breaks down research queries into structured elements
- `SearchQueryFormulator`: Creates effective search queries from the analysis

### 3.4 Research Workflow (`components/research_workflow.py`)

Manages the research strategy and execution:

- `ResearchStrategyPlanner`: Determines the research approach based on query analysis
- `ResearchEvaluator`: Assesses research progress and determines when sufficient information has been gathered

### 3.5 Tool Integration

#### 3.5.1 Search Tools (`tools/search_tools.py`)

- `WebSearchTool`: Abstracts different search engines (Exa, SerpAPI)
- `SearchHistory`: Tracks search history to prevent redundant searches

#### 3.5.2 Browsing Tools (`tools/browsing_tools.py`)

- `WebBrowsingTool`: Fetches content from web pages
- `ContentExtractionTool`: Extracts relevant information from web content
- `DocumentCache`: Caches web pages to minimize redundant requests

#### 3.5.3 Document Loaders (`tools/document_loaders.py`)

- `DocumentLoaderManager`: Provides a unified interface for loading documents from different sources and formats

### 3.6 Knowledge Processing (`components/knowledge_processing.py`)

- `ResearchRepository`: Stores and organizes research findings
- `InformationSynthesizer`: Combines information from multiple sources
- `SourceEvaluator`: Assesses source credibility
- `CitationFormatter`: Standardizes source references

### 3.7 Output Formatting (`components/output_formatting.py`)

- `ResearchSummaryGenerator`: Creates a structured summary of research findings
- `KeyFindingsExtractor`: Identifies and extracts key findings from research
- `ResearchReportGenerator`: Generates the final research report

### 3.8 Error Handling (`components/error_handling.py`)

- `SearchFailureHandler`: Manages search API errors
- `ContentAccessRetrier`: Handles website access issues
- `FallbackInformationSources`: Provides alternative sources when primary sources fail
- `ErrorLogger`: Logs errors for debugging and improvement

## 4. User Interfaces

### 4.1 Streamlit Interface (`interface/streamlit_app.py`)

The primary user interface is implemented using Streamlit:

- Provides a web-based interface for entering research queries
- Allows configuration of research parameters (depth, etc.)
- Displays research results with proper formatting
- Shows research history for previous queries

### 4.2 Command Line Interface (`main.py`)

A CLI is provided for programmatic use:

```bash
# Basic usage
python main.py research "What is quantum computing?"

# Save results to a file
python main.py research "History of AI" --output research_results.md

# Use specific models
python main.py research "Quantum computing" --analysis-model gpt-4o-mini --synthesis-model gpt-4o
```

## 5. Configuration (`core/config.py`)

The Research Assistant uses a centralized configuration system:

- API keys for various services (OpenAI, Exa, Google Gemini)
- Model selection for different phases (analysis, synthesis)
- Research parameters (depth, sources, etc.)
- Web browsing configuration
- Vector store settings

## 6. Research Process Flow

1. **Query Analysis**: The user's research query is analyzed to identify key topics, entities, and characteristics.
2. **Search Query Formulation**: Multiple search queries are created to ensure comprehensive coverage.
3. **Web Search**: Search queries are executed using the configured search engine.
4. **Content Browsing**: Relevant web pages are accessed and their content retrieved.
5. **Information Extraction**: Key information is extracted from the web content.
6. **Progress Evaluation**: Research progress is evaluated against completion criteria.
7. **Information Synthesis**: Information from multiple sources is combined and synthesized.
8. **Report Generation**: A final research report is generated with proper citations.

## 7. Model Usage

The Research Assistant uses different models for different phases:

- **Analysis Phase**: Uses smaller, cheaper models (e.g., GPT-4o-mini, Gemini-2.0-flash) for query analysis, search formulation, and content extraction.
- **Synthesis Phase**: Uses more powerful models (e.g., GPT-4o, Gemini-2.5-pro) for information synthesis and report generation.

This approach optimizes for both cost and quality, using more expensive models only where they provide the most value.

## 8. Research Depth Configuration

The Research Assistant supports different research depths:

- **Light**: Quick research with fewer sources (5 pages)
- **Medium**: Balanced research with moderate sources (10 pages)
- **Deep**: Comprehensive research with many sources (20 pages)

## 9. Future Enhancements

- **Specialized Domain Research**: Add domain-specific models and tools for fields like medical, legal, or scientific research.
- **Multimedia Content Analysis**: Extract information from images, charts, and videos in research sources.
- **Interactive Research**: Allow users to guide the research process with feedback and additional queries.
- **Source Language Translation**: Automatically translate foreign language sources for comprehensive research.
- **Fact Verification**: Cross-reference facts across multiple sources for validation.
- **Knowledge Graph Construction**: Build a connected graph of entities and relationships from research.

## 10. Conclusion

The Research Assistant provides a powerful, flexible framework for conducting comprehensive web research. Its modular architecture allows for easy extension and customization, while its use of LangGraph provides a clear, structured workflow for the research process.
