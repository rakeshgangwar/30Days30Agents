"""LangGraph implementation of the research workflow."""

from datetime import datetime
from typing import Dict, List, Any, TypedDict, Optional, Annotated

from langgraph.graph import StateGraph, END


class ResearchState(TypedDict):
    """TypedDict for the research workflow state."""

    query: str
    analysis: Dict[str, Any]
    strategy: Dict[str, Any]
    search_queries: List[str]
    current_query_index: int
    search_results: List[Dict[str, Any]]
    browsed_pages: List[Dict[str, Any]]
    extracted_content: List[Dict[str, Any]]
    synthesized_information: Optional[Dict[str, Any]]
    research_complete: bool
    next_step: str
    final_report: Optional[str]
    start_time: str
    last_updated: str
    errors: List[Dict[str, Any]]
    research_depth: str


class ResearchGraph:
    """
    LangGraph implementation of the research workflow.

    This component uses LangGraph to create a state machine for the
    research process, managing state transitions and workflow logic.
    """

    def __init__(
        self,
        query_analyzer,
        search_query_formulator,
        strategy_planner,
        search_tool,
        browsing_tool,
        extraction_tool,
        synthesizer,
        report_generator,
        evaluator,
        error_logger,
        document_loader=None
    ):
        """
        Initialize the ResearchGraph.

        Args:
            query_analyzer: Component for analyzing queries
            search_query_formulator: Component for formulating search queries
            strategy_planner: Component for planning research strategy
            search_tool: Tool for web searching
            browsing_tool: Tool for web browsing
            extraction_tool: Tool for content extraction
            synthesizer: Component for synthesizing information
            report_generator: Component for generating reports
            evaluator: Component for evaluating research progress
            error_logger: Component for logging errors
            document_loader: Optional document loader manager
        """
        self.query_analyzer = query_analyzer
        self.search_query_formulator = search_query_formulator
        self.strategy_planner = strategy_planner
        self.search_tool = search_tool
        self.browsing_tool = browsing_tool
        self.extraction_tool = extraction_tool
        self.synthesizer = synthesizer
        self.report_generator = report_generator
        self.evaluator = evaluator
        self.error_logger = error_logger
        self.document_loader = document_loader

        # Create the LangGraph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.

        Returns:
            StateGraph for the research workflow
        """
        # Create the StateGraph with ResearchState
        research_graph = StateGraph(ResearchState)

        # Add nodes for each step in the research workflow
        research_graph.add_node("analyze_query", self.analyze_query)
        research_graph.add_node("perform_search", self.perform_search)
        research_graph.add_node("browse_content", self.browse_content)
        research_graph.add_node("extract_information", self.extract_information)
        research_graph.add_node("evaluate_progress", self.evaluate_progress)
        research_graph.add_node("synthesize_information", self.synthesize_information)
        research_graph.add_node("generate_report", self.generate_report)

        # Define the edge routing function
        def router(state: ResearchState) -> str:
            return state["next_step"]

        # Define the edges between nodes
        research_graph.add_edge("analyze_query", "perform_search")

        research_graph.add_conditional_edges(
            "perform_search",
            router,
            {
                "browse_content": "browse_content",
                "evaluate_progress": "evaluate_progress"  # Skip browsing if no results
            }
        )

        research_graph.add_conditional_edges(
            "browse_content",
            router,
            {
                "extract_information": "extract_information",
                "evaluate_progress": "evaluate_progress"  # Skip extraction if no content
            }
        )

        research_graph.add_conditional_edges(
            "extract_information",
            router,
            {
                "evaluate_progress": "evaluate_progress"
            }
        )

        research_graph.add_conditional_edges(
            "evaluate_progress",
            router,
            {
                "perform_search": "perform_search",
                "synthesize_information": "synthesize_information",
                "end": END
            }
        )

        research_graph.add_conditional_edges(
            "synthesize_information",
            router,
            {
                "generate_report": "generate_report",
                "evaluate_progress": "evaluate_progress"  # For additional research if needed
            }
        )

        research_graph.add_conditional_edges(
            "generate_report",
            router,
            {
                "end": END
            }
        )

        # Set the entry point
        research_graph.set_entry_point("analyze_query")

        return research_graph

    def analyze_query(self, state: ResearchState) -> ResearchState:
        """
        Analyze the research query and create initial research strategy.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        query = state["query"]

        # Log the research depth being used
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Analyzing query with research depth: {state.get('research_depth', 'medium')}")

        try:
            # Analyze the query
            analysis = self.query_analyzer.analyze(query)

            # Formulate search queries
            search_queries = self.search_query_formulator.formulate_queries(analysis)

            # Create research strategy (research_depth is accessed from state in _parse_strategy_response)
            strategy = self.strategy_planner.create_strategy(query, analysis)

            # Update the state
            return {
                **state,
                "analysis": analysis,
                "strategy": strategy,
                "search_queries": search_queries,
                "next_step": "perform_search",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            # Log the error
            self.error_logger.log_error(e, "analyze_query")

            # Return a minimal state to continue
            return {
                **state,
                "analysis": {"error": str(e)},
                "strategy": {"min_sources": 3},
                "search_queries": [query],
                "next_step": "perform_search",
                "last_updated": datetime.now().isoformat(),
                "errors": state.get("errors", []) + [{"step": "analyze_query", "error": str(e)}]
            }

    def perform_search(self, state: ResearchState) -> ResearchState:
        """
        Execute the current search query and update results.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        try:
            current_query = state["search_queries"][state["current_query_index"]]
            search_results = self.search_tool.search(current_query)

            # Filter out already seen results
            seen_urls = {result["url"] for result in state["search_results"]}
            new_results = [result for result in search_results if result["url"] not in seen_urls]

            updated_results = state["search_results"] + new_results

            # Determine next step based on results
            next_step = "browse_content" if new_results else "evaluate_progress"

            return {
                **state,
                "search_results": updated_results,
                "next_step": next_step,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            # Log the error
            self.error_logger.log_error(e, "perform_search")

            # Continue to evaluation even with error
            return {
                **state,
                "next_step": "evaluate_progress",
                "last_updated": datetime.now().isoformat(),
                "errors": state.get("errors", []) + [{"step": "perform_search", "error": str(e)}]
            }

    def browse_content(self, state: ResearchState) -> ResearchState:
        """
        Browse and fetch content from search results.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        try:
            # Get URLs that haven't been browsed yet
            new_urls = [
                result["url"] for result in state["search_results"]
                if not any(bp["url"] == result["url"] for bp in state["browsed_pages"])
            ]

            # Determine how many pages to browse based on research depth
            research_depth = state.get("research_depth", "medium")

            # Set pages to browse according to specified values
            if research_depth == "light":
                pages_to_browse = 5  # Light: 5 pages
            elif research_depth == "medium":
                pages_to_browse = 10  # Medium: 10 pages
            elif research_depth == "deep":
                pages_to_browse = 20  # Deep: 20 pages
            else:
                pages_to_browse = 10  # Default to medium if unknown depth

            # Browse top N unvisited pages
            browsed_pages = []
            for url in new_urls[:pages_to_browse]:
                try:
                    page_content = self.browsing_tool.fetch_content(url)
                    if page_content:
                        browsed_pages.append({
                            "url": url,
                            "title": page_content.get("title", ""),
                            "content": page_content.get("content", ""),
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    # Log the error but continue with other URLs
                    self.error_logger.log_error(e, f"browse_content_url: {url}")

            updated_browsed_pages = state["browsed_pages"] + browsed_pages

            # Use document loaders to enhance content if available
            if self.document_loader:
                try:
                    query = state["query"]
                    query_type = state["analysis"].get("query_type", "")
                    domain = state["analysis"].get("domain", "")

                    # Get research depth to adjust document loading
                    research_depth = state.get("research_depth", "medium")

                    # Set document limits based on research depth
                    arxiv_limit = 1  # Default for light
                    pubmed_limit = 1  # Default for light
                    wiki_limit = 1    # Default for light

                    if research_depth == "medium":
                        arxiv_limit = 3
                        pubmed_limit = 2
                        wiki_limit = 2
                    elif research_depth == "deep":
                        arxiv_limit = 5
                        pubmed_limit = 4
                        wiki_limit = 3

                    # For academic or scientific queries, use Arxiv and PubMed
                    if query_type in ["factual", "academic", "scientific"] or domain in ["science", "medicine", "research"]:
                        # Load from Arxiv
                        arxiv_docs = self.document_loader.load_from_arxiv(query, max_docs=arxiv_limit)

                        # Add to browsed pages
                        for doc in arxiv_docs:
                            url = doc.get("url", "")
                            if url and not any(bp["url"] == url for bp in updated_browsed_pages):
                                updated_browsed_pages.append({
                                    "url": url,
                                    "title": doc.get("metadata", {}).get("title", "Arxiv Document"),
                                    "content": doc.get("content", ""),
                                    "source_type": "arxiv",
                                    "timestamp": datetime.now().isoformat()
                                })

                        # Load from PubMed for medical/biological topics
                        if domain in ["medicine", "biology", "health"]:
                            pubmed_docs = self.document_loader.load_from_pubmed(query, max_docs=pubmed_limit)
                            for doc in pubmed_docs:
                                url = doc.get("url", "")
                                if url and not any(bp["url"] == url for bp in updated_browsed_pages):
                                    updated_browsed_pages.append({
                                        "url": url,
                                        "title": doc.get("metadata", {}).get("title", "PubMed Document"),
                                        "content": doc.get("content", ""),
                                        "source_type": "pubmed",
                                        "timestamp": datetime.now().isoformat()
                                    })

                    # For general knowledge queries, use Wikipedia
                    if query_type in ["factual", "exploratory", "general"]:
                        wiki_docs = self.document_loader.load_from_wikipedia(query, max_docs=wiki_limit)
                        for doc in wiki_docs:
                            url = doc.get("url", "")
                            if url and not any(bp["url"] == url for bp in updated_browsed_pages):
                                updated_browsed_pages.append({
                                    "url": url,
                                    "title": doc.get("metadata", {}).get("title", "Wikipedia Document"),
                                    "content": doc.get("content", ""),
                                    "source_type": "wikipedia",
                                    "timestamp": datetime.now().isoformat()
                                })
                except Exception as e:
                    # Log the error but continue with traditional browsing
                    self.error_logger.log_error(e, "document_loader_error")

            # Determine next step based on results
            next_step = "extract_information" if updated_browsed_pages else "evaluate_progress"

            return {
                **state,
                "browsed_pages": updated_browsed_pages,
                "next_step": next_step,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            # Log the error
            self.error_logger.log_error(e, "browse_content")

            # Continue to evaluation even with error
            return {
                **state,
                "next_step": "evaluate_progress",
                "last_updated": datetime.now().isoformat(),
                "errors": state.get("errors", []) + [{"step": "browse_content", "error": str(e)}]
            }

    def extract_information(self, state: ResearchState) -> ResearchState:
        """
        Extract relevant information from browsed pages.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        try:
            # Get pages that haven't been extracted yet
            new_pages = [
                page for page in state["browsed_pages"]
                if not any(ec["url"] == page["url"] for ec in state["extracted_content"])
            ]

            # Get research depth to adjust extraction parameters
            research_depth = state.get("research_depth", "medium")

            extracted_content = []
            for page in new_pages:
                try:
                    # For deep research, we'll extract more detailed content
                    if research_depth == "deep":
                        # Try to extract more comprehensive information
                        extracted = self.extraction_tool.extract_relevant_content(
                            page["content"],
                            state["query"],
                            detail_level="high"
                        )
                    elif research_depth == "light":
                        # For light research, extract just the essentials
                        extracted = self.extraction_tool.extract_relevant_content(
                            page["content"],
                            state["query"],
                            detail_level="low"
                        )
                    else:
                        # Medium depth (default)
                        extracted = self.extraction_tool.extract_relevant_content(
                            page["content"],
                            state["query"]
                        )

                    if extracted:
                        extracted_content.append({
                            "url": page["url"],
                            "title": page["title"],
                            "extracted_text": extracted,
                            "research_depth": research_depth,  # Store the depth used for extraction
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    # Log the error but continue with other pages
                    self.error_logger.log_error(e, f"extract_information_url: {page['url']}")

            updated_extracted_content = state["extracted_content"] + extracted_content

            return {
                **state,
                "extracted_content": updated_extracted_content,
                "next_step": "evaluate_progress",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            # Log the error
            self.error_logger.log_error(e, "extract_information")

            # Continue to evaluation even with error
            return {
                **state,
                "next_step": "evaluate_progress",
                "last_updated": datetime.now().isoformat(),
                "errors": state.get("errors", []) + [{"step": "extract_information", "error": str(e)}]
            }

    def evaluate_progress(self, state: ResearchState) -> ResearchState:
        """
        Determine if enough research has been done or if more is needed.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        try:
            # Check if we've satisfied the research strategy criteria

            # 1. Have we reached minimum number of sources?
            sources_gathered = len(state["extracted_content"])
            min_sources = state["strategy"].get("min_sources", 3)

            # Get research depth to adjust evaluation criteria
            research_depth = state.get("research_depth", "medium")

            # Adjust minimum sources based on research depth
            if research_depth == "light":
                # For light research, we can be more lenient
                min_sources = max(2, min_sources - 1)
            elif research_depth == "deep":
                # For deep research, we need more sources
                min_sources = max(5, min_sources)

            # 2. Have we searched all queries?
            all_queries_searched = state["current_query_index"] >= len(state["search_queries"]) - 1

            # 3. Do we have sufficient information coverage?
            information_sufficient = self.evaluator.check_information_sufficiency(
                state["extracted_content"],
                state["query"],
                state["analysis"]
            ) if sources_gathered > 0 else False

            # For deep research, we're more strict about information sufficiency
            if research_depth == "deep" and information_sufficient:
                # For deep research, we want more comprehensive coverage
                # Only consider it sufficient if we have more than the minimum sources
                information_sufficient = sources_gathered >= min_sources + 1

            # Handle different scenarios
            if sources_gathered == 0 and all_queries_searched:
                # No sources found at all - end research with error
                return {
                    **state,
                    "research_complete": True,
                    "next_step": "end",
                    "last_updated": datetime.now().isoformat(),
                    "errors": state.get("errors", []) + [{"step": "evaluate_progress", "error": "No sources found"}]
                }
            elif (sources_gathered >= min_sources and information_sufficient) or \
                 (all_queries_searched and sources_gathered > 0 and len(state.get("errors", [])) > 3):
                # Enough research done or we've tried all queries with some results
                return {
                    **state,
                    "research_complete": True,
                    "next_step": "synthesize_information",
                    "last_updated": datetime.now().isoformat()
                }
            else:
                # More research needed
                next_query_index = (state["current_query_index"] + 1) % len(state["search_queries"])
                return {
                    **state,
                    "current_query_index": next_query_index,
                    "next_step": "perform_search",
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            # Log the error
            self.error_logger.log_error(e, "evaluate_progress")

            # If we have any content, move to synthesis, otherwise try another search
            if len(state["extracted_content"]) > 0:
                return {
                    **state,
                    "research_complete": True,
                    "next_step": "synthesize_information",
                    "last_updated": datetime.now().isoformat(),
                    "errors": state.get("errors", []) + [{"step": "evaluate_progress", "error": str(e)}]
                }
            else:
                next_query_index = (state["current_query_index"] + 1) % len(state["search_queries"])
                return {
                    **state,
                    "current_query_index": next_query_index,
                    "next_step": "perform_search" if next_query_index != state["current_query_index"] else "end",
                    "last_updated": datetime.now().isoformat(),
                    "errors": state.get("errors", []) + [{"step": "evaluate_progress", "error": str(e)}]
                }

    def synthesize_information(self, state: ResearchState) -> ResearchState:
        """
        Synthesize the extracted information into a coherent summary.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        try:
            # Get research depth to adjust synthesis parameters
            research_depth = state.get("research_depth", "medium")

            # Pass research depth to the synthesizer
            synthesized = self.synthesizer.synthesize(
                state["extracted_content"],
                state["query"],
                state["analysis"],
                research_depth=research_depth  # Pass research depth to influence synthesis detail
            )

            return {
                **state,
                "synthesized_information": synthesized,
                "next_step": "generate_report",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            # Log the error
            self.error_logger.log_error(e, "synthesize_information")

            # Try to generate a report anyway with what we have
            return {
                **state,
                "synthesized_information": {
                    "raw_synthesis": f"Error synthesizing information: {str(e)}",
                    "sections": {"error": str(e)},
                    "source_count": len(state["extracted_content"]),
                    "query": state["query"]
                },
                "next_step": "generate_report",
                "last_updated": datetime.now().isoformat(),
                "errors": state.get("errors", []) + [{"step": "synthesize_information", "error": str(e)}]
            }

    def generate_report(self, state: ResearchState) -> ResearchState:
        """
        Generate the final research report.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        try:
            # Get research depth to adjust report generation
            research_depth = state.get("research_depth", "medium")

            # Pass research depth to the report generator
            report = self.report_generator.generate(
                state["synthesized_information"],
                state["extracted_content"],
                state["query"],
                research_depth=research_depth  # Pass research depth to influence report detail
            )

            return {
                **state,
                "final_report": report,
                "next_step": "end",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            # Log the error
            self.error_logger.log_error(e, "generate_report")

            # Create a minimal report with the error
            minimal_report = {
                "query": state["query"],
                "report_text": f"Error generating report: {str(e)}\n\nHere is the raw information that was gathered:\n\n" +
                              "\n\n".join([f"Source: {item['title']}\n{item['extracted_text']}" for item in state["extracted_content"]]),
                "key_findings": [],
                "sources": [{"title": s["title"], "url": s["url"]} for s in state["extracted_content"]],
                "metadata": {
                    "source_count": len(state["extracted_content"]),
                    "generated_at": datetime.now().isoformat(),
                    "error": str(e)
                }
            }

            return {
                **state,
                "final_report": minimal_report,
                "next_step": "end",
                "last_updated": datetime.now().isoformat(),
                "errors": state.get("errors", []) + [{"step": "generate_report", "error": str(e)}]
            }

    def initialize_state(self, query: str) -> ResearchState:
        """
        Initialize the research state with a query.

        Args:
            query: The research query

        Returns:
            Initial research state
        """
        current_time = datetime.now().isoformat()

        # Import default research depth from config
        from core.config import DEFAULT_RESEARCH_DEPTH

        return {
            "query": query,
            "analysis": {},
            "strategy": {},
            "search_queries": [query],  # Default to using the query itself
            "current_query_index": 0,
            "search_results": [],
            "browsed_pages": [],
            "extracted_content": [],
            "synthesized_information": None,
            "research_complete": False,
            "next_step": "analyze_query",
            "final_report": None,
            "start_time": current_time,
            "last_updated": current_time,
            "errors": [],
            "research_depth": DEFAULT_RESEARCH_DEPTH  # Default research depth
        }

    def run(self, query: str, max_iterations: int = 50, research_depth: str = "medium") -> Dict[str, Any]:
        """
        Run the research workflow from start to finish.

        Args:
            query: The research query
            max_iterations: Maximum number of iterations to prevent infinite loops (default: 50)
            research_depth: Depth of research (light, medium, deep) (default: medium)

        Returns:
            Final research state
        """
        # Initialize the research state with research depth
        state = self.initialize_state(query)

        # Add research depth to the state
        state["research_depth"] = research_depth

        # Compile the graph
        workflow = self.graph.compile()

        # Set a higher recursion limit to avoid errors
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Running research workflow with recursion_limit={max_iterations}, research_depth={research_depth}")

        # Run the workflow
        try:
            result = workflow.invoke(state, {"recursion_limit": max_iterations})
            return result
        except Exception as e:
            logger.error(f"Error in workflow execution: {e}")
            # Re-raise the exception to be handled by the caller
            raise