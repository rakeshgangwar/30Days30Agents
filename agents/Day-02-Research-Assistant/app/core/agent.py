"""Main Research Assistant agent implementation."""

import os
from typing import Dict, List, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI

from core.config import (
    get_llm_config, get_search_config, validate_config,
    OPENAI_API_KEY, GOOGLE_GEMINI_API_KEY, EXA_API_KEY, SERPAPI_API_KEY,
    CACHE_DIR, RESEARCH_DB_DIR
)
from components.input_processing import QueryAnalyzer, SearchQueryFormulator
from components.research_workflow import ResearchStrategyPlanner
from components.knowledge_processing import ResearchRepository, InformationSynthesizer, SourceEvaluator, CitationFormatter
from components.output_formatting import ResearchSummaryGenerator, KeyFindingsExtractor, ResearchReportGenerator
from components.error_handling import SearchFailureHandler, ContentAccessRetrier, FallbackInformationSources, ErrorLogger
from tools.search_tools import WebSearchTool
from tools.browsing_tools import WebBrowsingTool, ContentExtractionTool, DocumentCache
from tools.document_loaders import DocumentLoaderManager
from core.langgraph_workflow import ResearchGraph


class ResearchAssistant:
    """
    Main Research Assistant agent that coordinates all components.

    This is the top-level class that initializes all components
    and provides the main interface for conducting research.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Research Assistant.

        Args:
            model_name: Optional model name override
        """
        # Initialize configuration
        validate_config()

        # Set up the LLMs for different phases
        self.analysis_llm = self._initialize_llm(model_name, phase="analysis")
        self.synthesis_llm = self._initialize_llm(model_name, phase="synthesis")

        # For backward compatibility, set self.llm to the analysis LLM
        self.llm = self.analysis_llm

        # Set up the research components
        self.document_cache = DocumentCache(CACHE_DIR)
        self.search_tool = self._initialize_search_tool()
        self.browsing_tool = WebBrowsingTool(use_playwright=True, cache_dir=CACHE_DIR)
        self.extraction_tool = ContentExtractionTool(self.analysis_llm)  # Use analysis LLM for extraction
        self.document_loader = DocumentLoaderManager(cache_dir=CACHE_DIR)

        # Initialize the repository
        self.repository = self._initialize_repository()

        # Initialize error handling components
        self.error_logger = ErrorLogger(os.path.join(CACHE_DIR, "research_errors.log"))
        self.search_failure_handler = SearchFailureHandler()
        self.content_retrier = ContentAccessRetrier()
        self.fallback_sources = FallbackInformationSources()

        # Initialize processing components for analysis phase
        self.query_analyzer = QueryAnalyzer(self.analysis_llm)
        self.search_query_formulator = SearchQueryFormulator(self.analysis_llm)
        self.strategy_planner = ResearchStrategyPlanner(self.analysis_llm)

        # Initialize processing components for synthesis phase
        self.synthesizer = InformationSynthesizer(self.synthesis_llm)
        self.source_evaluator = SourceEvaluator(self.analysis_llm)  # Analysis LLM is sufficient for evaluation
        self.citation_formatter = CitationFormatter()

        # Initialize output formatting components with synthesis LLM
        self.summary_generator = ResearchSummaryGenerator(self.synthesis_llm)
        self.findings_extractor = KeyFindingsExtractor(self.synthesis_llm)
        self.report_generator = ResearchReportGenerator(
            self.summary_generator,
            self.findings_extractor,
            self.citation_formatter
        )

        # Create the evaluator with analysis LLM
        self.evaluator = ResearchEvaluator(self.analysis_llm)

        # Initialize the workflow
        self.workflow = self._initialize_workflow()

    def _initialize_llm(self, model_name: Optional[str] = None, phase: str = "analysis"):
        """
        Initialize the language model based on available API keys and research phase.

        Args:
            model_name: Optional model name override
            phase: Research phase ("analysis" or "synthesis")

        Returns:
            Initialized language model
        """
        llm_config = get_llm_config(phase=phase)
        provider = llm_config["provider"]

        if model_name:
            # Override the model name if provided
            llm_config["model"] = model_name

        # Log which model is being initialized
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Initializing {phase} LLM: {provider} - {llm_config['model']}")

        if provider == "openai" and OPENAI_API_KEY:
            return ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model_name=llm_config["model"],
                temperature=0.1
            )
        elif provider == "gemini" and GOOGLE_GEMINI_API_KEY:
            return ChatGoogleGenerativeAI(
                api_key=GOOGLE_GEMINI_API_KEY,
                model=llm_config["model"],
                temperature=0.1
            )
        else:
            # Fallback to local Ollama if no API keys are available
            try:
                logger.info("No API keys available, falling back to Ollama (llama3)")
                return Ollama(model="llama3")
            except Exception as e:
                raise ValueError(f"Could not initialize any LLM: {e}")

    def _initialize_search_tool(self):
        """
        Initialize the search tool based on available API keys.

        Returns:
            Initialized search tool
        """
        search_config = get_search_config()

        if search_config["engine"] == "exa" and EXA_API_KEY:
            return WebSearchTool(api_key=EXA_API_KEY, search_engine="exa")
        elif SERPAPI_API_KEY:
            return WebSearchTool(api_key=SERPAPI_API_KEY, search_engine="serpapi")
        else:
            raise ValueError("No valid search API key found")

    def _initialize_repository(self):
        """
        Initialize the research repository.

        Returns:
            Initialized repository
        """
        try:
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

            return ResearchRepository(
                embedding_model=embeddings,
                persist_directory=RESEARCH_DB_DIR
            )
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            print("Using repository without embeddings")
            return ResearchRepository(persist_directory=RESEARCH_DB_DIR)

    def _initialize_workflow(self):
        """
        Initialize the research workflow.

        Returns:
            Initialized workflow
        """
        return ResearchGraph(
            query_analyzer=self.query_analyzer,
            search_query_formulator=self.search_query_formulator,
            strategy_planner=self.strategy_planner,
            search_tool=self.search_tool,
            browsing_tool=self.browsing_tool,
            extraction_tool=self.extraction_tool,
            synthesizer=self.synthesizer,
            report_generator=self.report_generator,
            evaluator=self.evaluator,
            error_logger=self.error_logger,
            document_loader=self.document_loader
        )

    def research(
        self, query: str, max_iterations: int = 50, return_intermediate_steps: bool = False,
        research_depth: str = None
    ) -> Dict[str, Any]:
        """
        Conduct research on a query.

        Args:
            query: The research query
            max_iterations: Maximum number of iterations (default increased to 50)
            return_intermediate_steps: Whether to return intermediate steps
            research_depth: Depth of research (light, medium, deep)

        Returns:
            Research results
        """
        # Use default research depth from config if not specified
        from core.config import DEFAULT_RESEARCH_DEPTH
        if research_depth is None:
            research_depth = DEFAULT_RESEARCH_DEPTH

        # Normalize research depth to lowercase
        research_depth = research_depth.lower()

        try:
            # Run the workflow with increased recursion limit
            # Pass the research depth to the workflow
            result = self.workflow.run(
                query,
                max_iterations=max_iterations,
                research_depth=research_depth
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in research workflow: {e}")

            # Return a minimal result on error
            return {
                "query": query,
                "report": {
                    "title": f"Research on: {query}",
                    "report_text": f"## Error during research\n\nAn error occurred while researching '{query}':\n\n```\n{str(e)}\n```\n\nPlease try again with a more specific query or check the logs for details."
                },
                "sources": [],
                "metadata": {
                    "error": str(e)
                }
            }

        # Extract the final report
        final_report = result.get("final_report", {})

        # Calculate some metrics
        start_time = result.get("start_time", "")
        end_time = result.get("last_updated", "")

        research_result = {
            "query": query,
            "report": final_report,
            "sources": [
                {"url": item["url"], "title": item["title"]}
                for item in result.get("extracted_content", [])
            ],
            "metadata": {
                "source_count": len(result.get("extracted_content", [])),
                "start_time": start_time,
                "end_time": end_time,
                "error_count": len(result.get("errors", []))
            }
        }

        if return_intermediate_steps:
            # Include the intermediate state for debugging
            research_result["intermediate_steps"] = {
                "analysis": result.get("analysis", {}),
                "strategy": result.get("strategy", {}),
                "search_queries": result.get("search_queries", []),
                "errors": result.get("errors", [])
            }

        return research_result


class ResearchEvaluator:
    """
    Evaluates research progress and information sufficiency.

    This component determines when enough information has been
    gathered to satisfy the research query.
    """

    def __init__(self, llm):
        """
        Initialize the ResearchEvaluator.

        Args:
            llm: Language model for evaluation
        """
        self.llm = llm

    def check_information_sufficiency(
        self, extracted_content: List[Dict[str, Any]], query: str, query_analysis: Dict[str, Any]
    ) -> bool:
        """
        Check if the gathered information is sufficient to answer the query.

        Args:
            extracted_content: Extracted content from sources
            query: Original research query
            query_analysis: Analysis of the query

        Returns:
            Whether the information is sufficient
        """
        # If there are no sources, information is not sufficient
        if not extracted_content:
            return False

        # If we have many sources, assume it's sufficient
        if len(extracted_content) >= 5:
            return True

        # For fewer sources, check coverage
        try:
            # Extract topics from analysis
            topics = query_analysis.get("topics", [])

            # If there are no topics, extract them from the query
            if not topics:
                topics = [query]

            # Check if each topic is covered in the extracted content
            topic_coverage = {}

            for topic in topics:
                topic_str = topic.lower() if isinstance(topic, str) else str(topic).lower()
                covered = False
                for item in extracted_content:
                    extracted_text = item.get("extracted_text", "")
                    extracted_text_str = (
                        extracted_text.lower() if isinstance(extracted_text, str)
                        else str(extracted_text).lower()
                    )
                    if topic_str in extracted_text_str:
                        covered = True
                        break

                topic_coverage[topic_str] = covered

            # Calculate the coverage percentage
            coverage_percentage = sum(1 for covered in topic_coverage.values() if covered) / len(topic_coverage)

            # If coverage is high, information is sufficient
            return coverage_percentage >= 0.7
        except Exception as e:
            print(f"Error checking information sufficiency: {e}")
            # Default to true if we have at least one source
            return len(extracted_content) > 0