"""Research workflow components for the Research Assistant."""

from datetime import datetime
import logging
from typing import Dict, List, Any, TypedDict, Optional

# Configure logging
logger = logging.getLogger("research_workflow")

class ResearchStrategyPlanner:
    """
    Plans and determines the overall research approach based on the query.

    This component determines how research should be conducted, including
    the number of sources, types of sources to prioritize, and criteria for
    determining when enough information has been gathered.
    """

    def __init__(self, llm):
        """
        Initialize the ResearchStrategyPlanner.

        Args:
            llm: Language model for strategy planning
        """
        self.llm = llm
        self.prompt_template = """
        Based on the query: "{query}"
        And the analysis: {analysis}

        Develop a research strategy that includes:
        1. The number of sources to consult (minimum)
        2. Types of sources to prioritize
        3. Criteria for determining when enough information has been gathered
        4. Approach for handling conflicting information
        5. Sequence of search operations to perform
        """

    def create_strategy(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a research strategy based on the query and its analysis.

        Args:
            query: The original research query
            analysis: Analysis of the research query

        Returns:
            Dictionary containing the research strategy
        """
        # Convert analysis dict to a readable string format
        analysis_str = "\n".join([f"{k}: {v}" for k, v in analysis.items()])

        response = self.llm.invoke(self.prompt_template.format(
            query=query,
            analysis=analysis_str
        ))

        # Parse the response to extract a structured research strategy
        return self._parse_strategy_response(response, query, analysis)

    def _parse_strategy_response(
        self, response, query: str, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured strategy.

        Args:
            response: Raw LLM response (string or AIMessage)
            query: The original query
            analysis: The query analysis

        Returns:
            Dictionary with structured strategy
        """
        # Convert AIMessage to string if needed
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)

        lines = response_text.strip().split('\n')

        # Default strategy values
        strategy = {
            "min_sources": 3,
            "source_priorities": ["academic", "news", "reference"],
            "completion_criteria": {
                "min_sources_gathered": 3,
                "coverage_of_topics": 0.7,  # 70% coverage
                "information_diversity": True
            },
            "conflict_resolution": "majority_view_with_alternatives",
            "search_sequence": ["general", "specific", "academic", "recent"],
            "time_allocation": {
                "search": 0.3,  # 30% of time
                "browse": 0.4,  # 40% of time
                "synthesize": 0.3  # 30% of time
            }
        }

        # Parse the response to update the strategy
        for line in lines:
            line = line.strip().lower()

            if "sources" in line and "consult" in line and any(c.isdigit() for c in line):
                # Extract number of sources
                for word in line.split():
                    if word.isdigit():
                        strategy["min_sources"] = int(word)
                        break

            elif "prioritize" in line or "sources" in line and ":" in line:
                # Extract source priorities
                priorities = []
                if ":" in line:
                    sources_text = line.split(":", 1)[1]
                    for source_type in ["academic", "news", "blog", "reference", "primary", "secondary", "expert", "opinion"]:
                        if source_type in sources_text:
                            priorities.append(source_type)

                if priorities:
                    strategy["source_priorities"] = priorities

            elif "criteria" in line or "enough" in line or "sufficient" in line:
                # Parse completion criteria
                if "coverage" in line and any(c.isdigit() for c in line):
                    for word in line.split():
                        if word.replace('.', '').isdigit():
                            strategy["completion_criteria"]["coverage_of_topics"] = float(word)
                            break

            elif "conflict" in line or "disagreement" in line or "contradict" in line:
                # Parse conflict resolution approach
                if "highlight" in line or "present both" in line or "all views" in line:
                    strategy["conflict_resolution"] = "present_all_perspectives"
                elif "expert" in line or "authoritative" in line:
                    strategy["conflict_resolution"] = "prefer_expert_sources"
                elif "recent" in line or "latest" in line:
                    strategy["conflict_resolution"] = "prefer_recent_sources"

            elif "sequence" in line or "order" in line or "steps" in line:
                # Parse search sequence
                if ":" in line:
                    sequence_text = line.split(":", 1)[1]
                    sequence = [s.strip() for s in sequence_text.split(",")]
                    if sequence:
                        strategy["search_sequence"] = sequence

        # Add query-specific considerations based on analysis
        if analysis.get("query_type") == "factual":
            strategy["source_priorities"] = ["academic", "reference", "official", "news"]
            strategy["completion_criteria"]["fact_verification"] = True

        elif analysis.get("query_type") == "comparative":
            strategy["completion_criteria"]["comparison_coverage"] = True
            strategy["conflict_resolution"] = "present_all_perspectives"

        elif analysis.get("query_type") == "exploratory":
            strategy["completion_criteria"]["breadth_over_depth"] = True
            strategy["min_sources"] = max(strategy["min_sources"], 5)  # More sources for exploratory

        if analysis.get("time_constraints"):
            strategy["time_constraint"] = analysis["time_constraints"]
            if "recent" in analysis.get("time_constraints", "").lower():
                strategy["recency_filter"] = "last_3_years"

        return strategy


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


class ResearchWorkflow:
    """
    Manages the overall research workflow and state transitions.

    This component orchestrates the different stages of the research process,
    from search to browsing to information extraction to synthesis.
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
        document_loader=None
    ):
        """
        Initialize the ResearchWorkflow.

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
        self.document_loader = document_loader

    def initialize_research(self, query: str) -> ResearchState:
        """
        Initialize the research workflow with a query.

        Args:
            query: The research query

        Returns:
            Initial research state
        """
        # Analyze the query
        analysis = self.query_analyzer.analyze(query)

        # Formulate search queries
        search_queries = self.search_query_formulator.formulate_queries(analysis)

        # Create research strategy
        strategy = self.strategy_planner.create_strategy(query, analysis)

        # Initialize the research state
        current_time = datetime.now().isoformat()

        return {
            "query": query,
            "analysis": analysis,
            "strategy": strategy,
            "search_queries": search_queries,
            "current_query_index": 0,
            "search_results": [],
            "browsed_pages": [],
            "extracted_content": [],
            "synthesized_information": None,
            "research_complete": False,
            "next_step": "perform_search",
            "final_report": None,
            "start_time": current_time,
            "last_updated": current_time
        }

    def perform_search(self, state: ResearchState) -> ResearchState:
        """
        Execute the current search query and update results.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        current_query = state["search_queries"][state["current_query_index"]]
        search_results = self.search_tool.search(current_query)

        # Filter out already seen results
        seen_urls = {result["url"] for result in state["search_results"]}
        new_results = [result for result in search_results if result["url"] not in seen_urls]

        updated_results = state["search_results"] + new_results

        return {
            **state,
            "search_results": updated_results,
            "next_step": "browse_content",
            "last_updated": datetime.now().isoformat()
        }

    def browse_content(self, state: ResearchState) -> ResearchState:
        """
        Browse and fetch content from search results.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        # Get URLs that haven't been browsed yet
        new_urls = [
            result["url"] for result in state["search_results"]
            if not any(bp["url"] == result["url"] for bp in state["browsed_pages"])
        ]

        # Browse top N unvisited pages
        browsed_pages = []
        for url in new_urls[:3]:  # Process 3 at a time
            try:
                page_content = self.browsing_tool.fetch_content(url)
                browsed_pages.append({
                    "url": url,
                    "title": page_content.get("title", ""),
                    "content": page_content.get("content", ""),
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                # Log the error but continue with other URLs
                print(f"Error browsing {url}: {e}")

        updated_browsed_pages = state["browsed_pages"] + browsed_pages

        return {
            **state,
            "browsed_pages": updated_browsed_pages,
            "next_step": "extract_information",
            "last_updated": datetime.now().isoformat()
        }

    def extract_information(self, state: ResearchState) -> ResearchState:
        """
        Extract relevant information from browsed pages.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        # Get pages that haven't been extracted yet
        new_pages = [
            page for page in state["browsed_pages"]
            if not any(ec["url"] == page["url"] for ec in state["extracted_content"])
        ]

        logger.info(f"Extracting information from {len(new_pages)} new pages")

        extracted_content = []
        for page in new_pages:
            try:
                logger.info(f"Extracting content from page: {page['url']}")

                # Skip pages with empty content
                if not page.get("content"):
                    logger.warning(f"Skipping page with empty content: {page['url']}")
                    continue

                extracted = self.extraction_tool.extract_relevant_content(
                    page["content"],
                    state["query"]
                )

                # Handle AIMessage objects - convert to string if needed
                if hasattr(extracted, 'content'):
                    logger.info(f"Converting AIMessage to string for {page['url']}")
                    extracted_text = extracted.content
                else:
                    extracted_text = str(extracted)

                if extracted_text:
                    logger.info(f"Successfully extracted content from {page['url']} ({len(extracted_text)} chars)")
                    extracted_content.append({
                        "url": page["url"],
                        "title": page["title"],
                        "extracted_text": extracted_text,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.warning(f"No content extracted from {page['url']}")
            except Exception as e:
                error_msg = f"Error extracting content from {page['url']}: {e}"
                logger.error(error_msg)
                if hasattr(self, 'error_logger'):
                    self.error_logger.log_error(e, f"extract_information_url: {page['url']}")

        updated_extracted_content = state["extracted_content"] + extracted_content
        logger.info(f"Total extracted content items: {len(updated_extracted_content)}")

        return {
            **state,
            "extracted_content": updated_extracted_content,
            "next_step": "evaluate_progress",
            "last_updated": datetime.now().isoformat()
        }

    def evaluate_progress(self, state: ResearchState) -> ResearchState:
        """
        Determine if enough research has been done or if more is needed.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        # Check if we've satisfied the research strategy criteria

        # 1. Have we reached minimum number of sources?
        sources_gathered = len(state["extracted_content"])
        min_sources = state["strategy"]["min_sources"]

        # 2. Have we searched all queries?
        all_queries_searched = state["current_query_index"] >= len(state["search_queries"]) - 1

        # 3. Do we have sufficient information coverage?
        information_sufficient = self.evaluator.check_information_sufficiency(
            state["extracted_content"],
            state["query"],
            state["analysis"]
        )

        if (sources_gathered >= min_sources and information_sufficient) or \
           (all_queries_searched and sources_gathered > 0):
            return {
                **state,
                "research_complete": True,
                "next_step": "synthesize_information",
                "last_updated": datetime.now().isoformat()
            }
        else:
            # More research needed
            return {
                **state,
                "current_query_index": (state["current_query_index"] + 1) % len(state["search_queries"]),
                "next_step": "perform_search",
                "last_updated": datetime.now().isoformat()
            }

    def synthesize_information(self, state: ResearchState) -> ResearchState:
        """
        Synthesize the extracted information into a coherent summary.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        synthesized = self.synthesizer.synthesize(
            state["extracted_content"],
            state["query"],
            state["analysis"]
        )

        return {
            **state,
            "synthesized_information": synthesized,
            "next_step": "generate_report",
            "last_updated": datetime.now().isoformat()
        }

    def generate_report(self, state: ResearchState) -> ResearchState:
        """
        Generate the final research report.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        report = self.report_generator.generate(
            state["synthesized_information"],
            state["extracted_content"],
            state["query"]
        )

        return {
            **state,
            "final_report": report,
            "next_step": "end",
            "last_updated": datetime.now().isoformat()
        }

    def load_documents_from_sources(self, state: ResearchState) -> ResearchState:
        """
        Load documents from various sources based on the research query.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        # If document loader is not available, skip this step
        if not self.document_loader:
            logger.info("Document loader not available, skipping document loading step")
            return state

        query = state["query"]
        logger.info(f"Loading documents for query: '{query}'")

        # Determine which document sources to use based on the query analysis
        query_type = state["analysis"].get("query_type", "")
        domain = state["analysis"].get("domain", "")

        logger.info(f"Query type: {query_type}, Domain: {domain}")

        loaded_documents = []

        # For academic or scientific queries, use Arxiv and PubMed
        if query_type in ["factual", "academic", "scientific"] or domain in ["science", "medicine", "research"]:
            logger.info("Using academic sources (Arxiv) for this query")
            # Load from Arxiv
            arxiv_docs = self.document_loader.load_from_arxiv(query, max_docs=3)
            loaded_documents.extend(arxiv_docs)
            logger.info(f"Loaded {len(arxiv_docs)} documents from Arxiv")

            # Load from PubMed for medical/biological topics
            if domain in ["medicine", "biology", "health"]:
                logger.info("Using medical sources (PubMed) for this query")
                pubmed_docs = self.document_loader.load_from_pubmed(query, max_docs=3)
                loaded_documents.extend(pubmed_docs)
                logger.info(f"Loaded {len(pubmed_docs)} documents from PubMed")

        # For general knowledge queries, use Wikipedia
        if query_type in ["factual", "exploratory", "general"]:
            logger.info("Using encyclopedic sources (Wikipedia) for this query")
            wiki_docs = self.document_loader.load_from_wikipedia(query, max_docs=2)
            loaded_documents.extend(wiki_docs)
            logger.info(f"Loaded {len(wiki_docs)} documents from Wikipedia")

        # For all queries, load from web search results
        logger.info("Loading content from web search results")
        web_docs_count = 0
        for result in state["search_results"][:5]:  # Process top 5 search results
            url = result.get("url", "")
            if url:
                # Use Playwright for JavaScript-heavy sites
                use_playwright = any(js_site in url for js_site in [
                    "twitter.com", "linkedin.com", "facebook.com",
                    "instagram.com", "app.", "dashboard."
                ])
                web_docs = self.document_loader.load_from_web(url, use_playwright=use_playwright)
                loaded_documents.extend(web_docs)
                web_docs_count += len(web_docs)

        logger.info(f"Loaded {web_docs_count} documents from web search results")

        # Chunk the documents for better processing
        logger.info(f"Chunking {len(loaded_documents)} documents")
        chunked_documents = self.document_loader.chunk_documents(loaded_documents)
        logger.info(f"Created {len(chunked_documents)} chunks")

        # Add to browsed pages
        browsed_pages = state["browsed_pages"]
        added_count = 0
        for doc in loaded_documents:
            source_type = doc.get("source_type", "")
            url = doc.get("url", "")

            # Only add if not already in browsed pages
            if not any(bp["url"] == url for bp in browsed_pages):
                browsed_pages.append({
                    "url": url,
                    "title": doc.get("metadata", {}).get("title", f"{source_type.capitalize()} Document"),
                    "content": doc.get("content", ""),
                    "source_type": source_type,
                    "timestamp": datetime.now().isoformat()
                })
                added_count += 1

        logger.info(f"Added {added_count} new documents to browsed pages")
        logger.info(f"Total browsed pages: {len(browsed_pages)}")

        return {
            **state,
            "browsed_pages": browsed_pages,
            "next_step": "extract_information",
            "last_updated": datetime.now().isoformat()
        }

    def run_step(self, state: ResearchState) -> ResearchState:
        """
        Run the next step in the research workflow.

        Args:
            state: Current research state

        Returns:
            Updated research state
        """
        next_step = state["next_step"]
        logger.info(f"Running workflow step: {next_step}")

        if next_step == "perform_search":
            return self.perform_search(state)
        elif next_step == "browse_content":
            # First use traditional browsing
            logger.info("Starting traditional web browsing")
            browsed_state = self.browse_content(state)

            # Then enhance with document loaders if available
            if self.document_loader:
                logger.info("Enhancing with document loaders")
                enhanced_state = self.load_documents_from_sources(browsed_state)
                logger.info("Document loading complete")
                return enhanced_state
            return browsed_state
        elif next_step == "extract_information":
            return self.extract_information(state)
        elif next_step == "evaluate_progress":
            return self.evaluate_progress(state)
        elif next_step == "synthesize_information":
            return self.synthesize_information(state)
        elif next_step == "generate_report":
            return self.generate_report(state)
        else:
            # End or unknown step
            logger.info(f"Unknown or end step: {next_step}")
            return state

    def run_workflow(self, query: str) -> Dict[str, Any]:
        """
        Run the complete research workflow from query to final report.

        Args:
            query: The research query

        Returns:
            Dictionary with the final research report and metadata
        """
        state = self.initialize_research(query)

        while state["next_step"] != "end":
            state = self.run_step(state)

        return {
            "query": state["query"],
            "report": state["final_report"],
            "sources": [
                {"url": item["url"], "title": item["title"]}
                for item in state["extracted_content"]
            ],
            "research_time": self._calculate_research_time(state)
        }

    def _calculate_research_time(self, state: ResearchState) -> float:
        """
        Calculate the total research time in seconds.

        Args:
            state: Research state

        Returns:
            Research time in seconds
        """
        start_time = datetime.fromisoformat(state["start_time"])
        end_time = datetime.fromisoformat(state["last_updated"])

        return (end_time - start_time).total_seconds()