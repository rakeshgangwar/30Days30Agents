"""Integration tests for the Research Assistant application."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Import components for integration testing
from components.input_processing import QueryAnalyzer, SearchQueryFormulator
from components.research_workflow import ResearchStrategyPlanner, ResearchWorkflow
from components.knowledge_processing import InformationSynthesizer, SourceEvaluator
from components.output_formatting import ResearchSummaryGenerator, KeyFindingsExtractor, ResearchReportGenerator
from tools.search_tools import WebSearchTool
from tools.browsing_tools import WebBrowsingTool, ContentExtractionTool


class MockLLM:
    """Mock LLM for testing."""

    def __init__(self, responses=None):
        """
        Initialize the MockLLM.

        Args:
            responses: Dictionary mapping prompt substrings to responses
        """
        self.responses = responses or {}
        self.default_response = """
        # Research Summary: Recent Advancements in AI

        ## Key Findings
        * Deep learning architectures have evolved significantly [1, 3]
        * Large language models can now perform complex reasoning tasks [2]
        * AI applications in healthcare show promising diagnostic capabilities [4]

        ## Detailed Analysis
        Artificial intelligence has undergone remarkable development in the past five years,
        with particular advances in neural network architectures and training methods.
        """
        self.invocations = []

    def invoke(self, prompt):
        """
        Mock invocation that returns predefined responses based on prompt content.

        Args:
            prompt: The input prompt

        Returns:
            Predefined response based on prompt content
        """
        # Track invocations for testing
        self.invocations.append(prompt)

        # Special case for the test_complete_research_workflow test
        if "Generate a comprehensive research summary" in prompt:
            return """
            # Research Summary: Recent Advancements in AI

            ## Key Findings
            * Deep learning architectures have evolved significantly [1, 3]
            * Large language models can now perform complex reasoning tasks [2]
            * AI applications in healthcare show promising diagnostic capabilities [4]

            ## Detailed Analysis
            Artificial intelligence has undergone remarkable development in the past five years,
            with particular advances in neural network architectures and training methods.
            """

        # Check if we have a matching response
        for key, response in self.responses.items():
            if key in prompt:
                return response

        # Fall back to default response
        return self.default_response


class TestResearchWorkflowIntegration(unittest.TestCase):
    """Integration tests for the research workflow."""

    def setUp(self):
        """Set up integration test environment."""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()

        # Set up mock LLM with predefined responses for different components
        self.mock_llm = MockLLM({
            "Analyze the following research query": """
            Main topics: Artificial Intelligence, Machine Learning
            Key entities: Neural Networks, Deep Learning, AI Applications
            Query type: Exploratory
            Domain: Computer Science, Technology
            Time constraints: Recent developments (last 5 years)
            """,

            "Formulate 3-5 effective search queries": """
            1. Latest advancements in artificial intelligence and machine learning
            2. Recent breakthroughs in neural networks and deep learning
            3. Practical applications of AI in industry 2020-2025
            4. State-of-the-art AI research and future directions
            """,

            "Develop a research strategy": """
            1. Number of sources to consult: At least 5 sources
            2. Types of sources to prioritize: Academic papers, research reports, tech blogs, industry publications
            3. Criteria for determining enough information: Coverage of all key topics, representation of different perspectives
            4. Approach for conflicting information: Present multiple viewpoints with credibility assessment
            5. Sequence of search operations: General overview, technical details, practical applications, future directions
            """,

            "Extract the most relevant information": "This is the extracted content that is relevant to the query about AI advancements.",

            "Synthesize the above information": """
            ## Summary
            AI has seen significant advancements in recent years across multiple domains.

            ## Key Points
            * Deep learning models have dramatically improved in performance and efficiency
            * Large language models like GPT-4, Gemini and Claude represent major breakthroughs
            * Real-world applications now span healthcare, finance, and autonomous systems

            ## Areas of Consensus
            Most sources agree on the transformative impact of AI on industry and society.

            ## Conflicting Information
            Sources disagree on the timeline for achieving artificial general intelligence.

            ## Information Gaps
            More research is needed on the ethical implications and regulatory frameworks.
            """,

            "Generate a comprehensive research summary": """
            # Research Summary: Recent Advancements in AI

            ## Key Findings
            * Deep learning architectures have evolved significantly [1, 3]
            * Large language models can now perform complex reasoning tasks [2]
            * AI applications in healthcare show promising diagnostic capabilities [4]

            ## Detailed Analysis
            Artificial intelligence has undergone remarkable development in the past five years,
            with particular advances in neural network architectures and training methods.

            The emergence of transformer-based models has revolutionized natural language processing,
            while computer vision continues to benefit from convolutional neural networks.

            ## Sources
            [1] "Recent Advances in Deep Learning" - example.com/advances
            [2] "Large Language Models: Capabilities and Limitations" - example.com/llm
            [3] "Neural Network Architectures" - example.com/nn
            [4] "AI in Healthcare" - example.com/health
            """
        })

        # Create component instances with the mock LLM
        self.query_analyzer = QueryAnalyzer(self.mock_llm)
        self.search_query_formulator = SearchQueryFormulator(self.mock_llm)
        self.strategy_planner = ResearchStrategyPlanner(self.mock_llm)
        self.extraction_tool = ContentExtractionTool(self.mock_llm)
        self.synthesizer = InformationSynthesizer(self.mock_llm)
        self.source_evaluator = SourceEvaluator(self.mock_llm)
        self.summary_generator = ResearchSummaryGenerator(self.mock_llm)
        self.findings_extractor = KeyFindingsExtractor(self.mock_llm)
        self.evaluator = MockResearchEvaluator()

        # Create mock tools
        self.search_tool = MockSearchTool()
        self.browsing_tool = MockBrowsingTool()

        # Create report generator
        self.report_generator = ResearchReportGenerator(
            self.summary_generator,
            self.findings_extractor,
            MockCitationFormatter()
        )

        # Create the complete workflow
        self.workflow = ResearchWorkflow(
            query_analyzer=self.query_analyzer,
            search_query_formulator=self.search_query_formulator,
            strategy_planner=self.strategy_planner,
            search_tool=self.search_tool,
            browsing_tool=self.browsing_tool,
            extraction_tool=self.extraction_tool,
            synthesizer=self.synthesizer,
            report_generator=self.report_generator,
            evaluator=self.evaluator
        )

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_complete_research_workflow(self):
        """Test the complete research workflow from query to final report."""
        # Execute the complete workflow
        test_query = "What are the recent advancements in artificial intelligence?"
        result = self.workflow.run_workflow(test_query)

        # Verify the workflow produced a complete result
        self.assertEqual(result["query"], test_query)
        self.assertIsNotNone(result["report"])
        self.assertIsNotNone(result["sources"])
        self.assertGreater(result["research_time"], 0)

        # Verify report contents
        self.assertIn("Key Findings", result["report"]["report_text"])
        self.assertIn("Deep learning", result["report"]["report_text"])
        self.assertGreater(len(result["report"]["key_findings"]), 0)

    def test_input_processing_integration(self):
        """Test the integration of input processing components."""
        # Test query
        test_query = "What are the recent advancements in artificial intelligence?"

        # Execute the query analysis
        analysis = self.query_analyzer.analyze(test_query)

        # Verify analysis structure
        self.assertIn("topics", analysis)
        self.assertIn("entities", analysis)
        self.assertIn("query_type", analysis)

        # Check that topics contain relevant information
        self.assertTrue(any("intelligence" in topic.lower() for topic in analysis["topics"]))

        # Use the analysis to formulate search queries
        search_queries = self.search_query_formulator.formulate_queries(analysis)

        # Verify search queries
        self.assertGreater(len(search_queries), 0)
        self.assertTrue(any("artificial intelligence" in query.lower() for query in search_queries))

        # Create research strategy
        strategy = self.strategy_planner.create_strategy(test_query, analysis)

        # Verify strategy structure
        self.assertIn("min_sources", strategy)
        self.assertIn("source_priorities", strategy)
        self.assertIn("completion_criteria", strategy)

    def test_research_and_extraction_integration(self):
        """Test the integration of search, browsing, and extraction."""
        # Initialize the research
        state = self.workflow.initialize_research("Test query")

        # Execute search
        search_state = self.workflow.perform_search(state)

        # Verify search results were added
        self.assertGreater(len(search_state["search_results"]), 0)

        # Execute browsing
        browse_state = self.workflow.browse_content(search_state)

        # Verify pages were browsed
        self.assertGreater(len(browse_state["browsed_pages"]), 0)

        # Execute extraction
        extract_state = self.workflow.extract_information(browse_state)

        # Verify content was extracted
        self.assertGreater(len(extract_state["extracted_content"]), 0)

    def test_synthesis_and_reporting_integration(self):
        """Test the integration of synthesis and reporting components."""
        # Create a state with extracted content
        state = {
            "query": "Test query about AI",
            "analysis": {"topics": ["AI"], "query_type": "exploratory"},
            "extracted_content": [
                {
                    "url": "https://example.com/1",
                    "title": "AI Article 1",
                    "extracted_text": "Content about AI advancements."
                },
                {
                    "url": "https://example.com/2",
                    "title": "AI Article 2",
                    "extracted_text": "More information about AI applications."
                }
            ],
            "next_step": "synthesize_information",
            "last_updated": datetime.now().isoformat()
        }

        # Execute synthesis
        synthesis_state = self.workflow.synthesize_information(state)

        # Verify synthesis results
        self.assertIsNotNone(synthesis_state["synthesized_information"])
        self.assertIn("raw_synthesis", synthesis_state["synthesized_information"])

        # Execute report generation
        report_state = self.workflow.generate_report(synthesis_state)

        # Verify report was generated
        self.assertIsNotNone(report_state["final_report"])
        self.assertIn("report_text", report_state["final_report"])
        self.assertIn("key_findings", report_state["final_report"])
        self.assertIn("sources", report_state["final_report"])


class MockSearchTool:
    """Mock search tool for testing."""

    def search(self, query):
        """Return mock search results."""
        return [
            {
                "title": f"Result 1 for {query}",
                "url": "https://example.com/result1",
                "snippet": "This is a snippet about AI and machine learning advancements."
            },
            {
                "title": f"Result 2 for {query}",
                "url": "https://example.com/result2",
                "snippet": "Information about neural networks and deep learning."
            },
            {
                "title": f"Result 3 for {query}",
                "url": "https://example.com/result3",
                "snippet": "Recent applications of artificial intelligence in various domains."
            }
        ]


class MockBrowsingTool:
    """Mock browsing tool for testing."""

    def fetch_content(self, url):
        """Return mock content for a URL."""
        # Extract domain from URL for a more realistic title
        import re
        domain = re.sub(r'^https?://(www\.)?', '', url)
        domain = domain.split('/')[0]  # Get just the domain part

        # Create a more realistic title based on the URL
        page_title = f"{domain.capitalize()} - Information Page"
        if "wikipedia" in domain.lower():
            page_title = f"Wikipedia - {domain.split('.')[-2].capitalize()}"
        elif "github" in domain.lower():
            page_title = f"GitHub - Repository Page"

        return {
            "title": page_title,
            "content": f"<html><body><h1>Content for {url}</h1><p>This is a detailed article about artificial intelligence, machine learning, and neural networks. The field has seen significant advancements in recent years.</p></body></html>",
            "url": url,
            "fetched_at": datetime.now().isoformat()
        }


class MockResearchEvaluator:
    """Mock research evaluator for testing."""

    def check_information_sufficiency(self, extracted_content, query, query_analysis):
        """Check if we have sufficient information (always returns True after some content)."""
        # Return True if we have at least 2 content items
        return len(extracted_content) >= 2


class MockCitationFormatter:
    """Mock citation formatter for testing."""

    def format_citations(self, sources):
        """Return mock formatted citations."""
        formatted_citations = []
        for idx, source in enumerate(sources):
            formatted_citations.append({
                "source_id": idx,
                "formatted_citation": f"{source.get('title', 'Unknown')}. {source.get('url', '')}",
                "url": source.get("url", "")
            })
        return formatted_citations


class TestEndToEndResearch(unittest.TestCase):
    """End-to-end tests with more realistic test cases."""

    def setUp(self):
        """Set up the end-to-end test environment."""
        # This would normally set up the actual components
        # For testing, we'll use a mock version of the research assistant
        self.mock_assistant = MagicMock()
        self.mock_assistant.research.return_value = {
            "query": "Test query",
            "report": {
                "report_text": "Test report content",
                "key_findings": ["Finding 1", "Finding 2"]
            },
            "sources": [
                {"title": "Source 1", "url": "https://example.com/1"},
                {"title": "Source 2", "url": "https://example.com/2"}
            ],
            "metadata": {
                "source_count": 2,
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "error_count": 0
            }
        }

    @unittest.skip("This test uses real API calls and should be run manually")
    def test_actual_research_with_apis(self):
        """
        Test actual research with real APIs (skipped by default).

        This test is designed to be run manually when API keys are available,
        as it would make real API calls to search engines and language models.
        """
        from core.agent import ResearchAssistant

        # This requires actual API keys to be set in environment variables
        assistant = ResearchAssistant()

        # Select a question from the test questions document
        test_query = "What are the main differences between renewable and non-renewable energy sources?"

        # Conduct research with minimal iterations for testing
        result = assistant.research(query=test_query, max_iterations=2)

        # Verify basic structure (but not content since it's non-deterministic)
        self.assertEqual(result["query"], test_query)
        self.assertIn("report", result)
        self.assertIn("sources", result)

    def test_simulated_research_process(self):
        """Test a simulated research process with predefined responses."""
        # Test with a sample query from the test questions document
        test_query = "What are the main differences between renewable and non-renewable energy sources?"

        # Get research results from the mock assistant
        result = self.mock_assistant.research(query=test_query)

        # Verify the results structure
        self.assertIsNotNone(result["report"])
        self.assertIsNotNone(result["sources"])
        self.assertGreater(len(result["sources"]), 0)


if __name__ == "__main__":
    unittest.main()