"""Tests for the research workflow components."""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from components.research_workflow import ResearchStrategyPlanner, ResearchWorkflow


class TestResearchStrategyPlanner(unittest.TestCase):
    """Tests for the ResearchStrategyPlanner class."""

    def setUp(self):
        """Set up test cases."""
        self.mock_llm = MagicMock()
        self.mock_llm.invoke.return_value = """
        Based on the query and analysis, here's a research strategy:

        1. Number of sources to consult: At least 5 sources should be consulted
        2. Types of sources to prioritize: Academic journals, reputable news sites, government reports
        3. Criteria for determining enough information: Coverage of all key aspects, representation of different perspectives
        4. Approach for conflicting information: Present all perspectives with credibility assessment
        5. Sequence of search operations: Start with broad overview, then specific aspects, then expert opinions
        """
        self.planner = ResearchStrategyPlanner(self.mock_llm)

    def test_create_strategy(self):
        """Test the create_strategy method."""
        query = "What are the environmental impacts of electric vehicles?"
        analysis = {
            "topics": ["Electric vehicles", "Environmental impact"],
            "entities": ["Carbon emissions", "Battery production", "Energy sources"],
            "query_type": "comparative",
            "domain": "environmental science",
            "time_constraints": "Current information"
        }

        result = self.planner.create_strategy(query, analysis)

        # Verify LLM was called with the correct prompt
        self.mock_llm.invoke.assert_called_once()
        args, _ = self.mock_llm.invoke.call_args
        self.assertIn(query, args[0])

        # Verify the results structure
        self.assertIn("min_sources", result)
        self.assertIn("source_priorities", result)
        self.assertIn("completion_criteria", result)
        self.assertIn("conflict_resolution", result)
        self.assertIn("search_sequence", result)

        # Check that strategy elements are populated
        self.assertIsInstance(result["min_sources"], int)
        self.assertIsInstance(result["source_priorities"], list)
        self.assertIsInstance(result["completion_criteria"], dict)
        self.assertIsInstance(result["conflict_resolution"], str)
        self.assertIsInstance(result["search_sequence"], list)

    def test_strategy_adaptation_to_query_type(self):
        """Test that strategy adapts to different query types."""
        query = "What are the environmental impacts of electric vehicles?"

        # Test with factual query
        factual_analysis = {
            "topics": ["Electric vehicles", "Environmental impact"],
            "entities": ["Carbon emissions", "Battery production"],
            "query_type": "factual",
            "domain": "environmental science"
        }

        factual_result = self.planner.create_strategy(query, factual_analysis)

        # Test with comparative query
        comparative_analysis = {
            "topics": ["Electric vehicles", "Environmental impact"],
            "entities": ["Carbon emissions", "Battery production"],
            "query_type": "comparative",
            "domain": "environmental science"
        }

        comparative_result = self.planner.create_strategy(query, comparative_analysis)

        # Test with exploratory query
        exploratory_analysis = {
            "topics": ["Electric vehicles", "Environmental impact"],
            "entities": ["Carbon emissions", "Battery production"],
            "query_type": "exploratory",
            "domain": "environmental science"
        }

        exploratory_result = self.planner.create_strategy(query, exploratory_analysis)

        # Verify that strategies differ based on query type
        # For this test, we rely on the query_type-specific logic in _parse_strategy_response
        if "completion_criteria" in factual_result and "completion_criteria" in comparative_result:
            self.assertNotEqual(
                factual_result.get("completion_criteria"),
                comparative_result.get("completion_criteria"),
                "Strategy should differ between factual and comparative queries"
            )

        if exploratory_result.get("min_sources") and factual_result.get("min_sources"):
            self.assertGreaterEqual(
                exploratory_result.get("min_sources", 0),
                factual_result.get("min_sources", 0),
                "Exploratory queries should have equal or more min_sources than factual queries"
            )


class TestResearchWorkflow(unittest.TestCase):
    """Tests for the ResearchWorkflow class."""

    def setUp(self):
        """Set up test cases."""
        # Create mock components
        self.mock_query_analyzer = MagicMock()
        self.mock_search_query_formulator = MagicMock()
        self.mock_strategy_planner = MagicMock()
        self.mock_search_tool = MagicMock()
        self.mock_browsing_tool = MagicMock()
        self.mock_extraction_tool = MagicMock()
        self.mock_synthesizer = MagicMock()
        self.mock_report_generator = MagicMock()
        self.mock_evaluator = MagicMock()

        # Set up mock responses
        self.mock_query_analyzer.analyze.return_value = {
            "topics": ["Test Topic"],
            "entities": ["Test Entity"],
            "query_type": "factual",
            "domain": "general",
            "time_constraints": None
        }

        self.mock_search_query_formulator.formulate_queries.return_value = [
            "test query 1",
            "test query 2"
        ]

        self.mock_strategy_planner.create_strategy.return_value = {
            "min_sources": 3,
            "source_priorities": ["academic", "news"],
            "completion_criteria": {"min_sources_gathered": 3},
            "conflict_resolution": "present_all_perspectives",
            "search_sequence": ["general", "specific"]
        }

        self.mock_search_tool.search.return_value = [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "snippet": "Test snippet 1"
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/2",
                "snippet": "Test snippet 2"
            }
        ]

        self.mock_browsing_tool.fetch_content.return_value = {
            "title": "Test Page",
            "content": "<html><body>Test content</body></html>",
            "url": "https://example.com/1"
        }

        self.mock_extraction_tool.extract_relevant_content.return_value = "Extracted relevant content"

        self.mock_evaluator.check_information_sufficiency.return_value = True

        self.mock_synthesizer.synthesize.return_value = {
            "raw_synthesis": "Synthesized information",
            "sections": {"summary": "Test summary"},
            "source_count": 2,
            "query": "test query"
        }

        self.mock_report_generator.generate.return_value = {
            "query": "test query",
            "report_text": "Test report",
            "key_findings": ["Finding 1", "Finding 2"],
            "sources": [{"title": "Test Source", "url": "https://example.com"}],
            "metadata": {"word_count": 100}
        }

        # Initialize the workflow
        self.workflow = ResearchWorkflow(
            query_analyzer=self.mock_query_analyzer,
            search_query_formulator=self.mock_search_query_formulator,
            strategy_planner=self.mock_strategy_planner,
            search_tool=self.mock_search_tool,
            browsing_tool=self.mock_browsing_tool,
            extraction_tool=self.mock_extraction_tool,
            synthesizer=self.mock_synthesizer,
            report_generator=self.mock_report_generator,
            evaluator=self.mock_evaluator
        )

    def test_initialize_research(self):
        """Test the initialize_research method."""
        query = "test research query"
        research_depth = "deep"  # Specify a research depth
        result = self.workflow.initialize_research(query, research_depth=research_depth)

        # Verify that components were called
        self.mock_query_analyzer.analyze.assert_called_once_with(query)
        self.mock_search_query_formulator.formulate_queries.assert_called_once()
        self.mock_strategy_planner.create_strategy.assert_called_once()

        # Verify the result structure
        self.assertEqual(result["query"], query)
        self.assertEqual(result["research_depth"], research_depth)  # Verify research_depth is in the result
        self.assertEqual(result["analysis"], self.mock_query_analyzer.analyze.return_value)
        self.assertEqual(result["strategy"], self.mock_strategy_planner.create_strategy.return_value)
        self.assertEqual(result["search_queries"], self.mock_search_query_formulator.formulate_queries.return_value)
        self.assertEqual(result["current_query_index"], 0)
        self.assertEqual(result["next_step"], "perform_search")
        self.assertFalse(result["research_complete"])
        self.assertIsNone(result["final_report"])

    def test_perform_search(self):
        """Test the perform_search method."""
        # Set up initial state
        state = {
            "query": "test query",
            "search_queries": ["test search query 1", "test search query 2"],
            "current_query_index": 0,
            "search_results": [],
            "next_step": "perform_search",
            "last_updated": datetime.now().isoformat()
        }

        result = self.workflow.perform_search(state)

        # Verify search was performed with the correct query
        self.mock_search_tool.search.assert_called_once_with("test search query 1")

        # Verify the result structure
        self.assertEqual(result["search_results"], self.mock_search_tool.search.return_value)
        self.assertEqual(result["next_step"], "browse_content")

    def test_browse_content(self):
        """Test the browse_content method."""
        # Set up initial state
        state = {
            "query": "test query",
            "search_results": [
                {"title": "Test Result", "url": "https://example.com/1", "snippet": "Test snippet"}
            ],
            "browsed_pages": [],
            "next_step": "browse_content",
            "last_updated": datetime.now().isoformat()
        }

        result = self.workflow.browse_content(state)

        # Verify browsing was performed with the correct URL
        self.mock_browsing_tool.fetch_content.assert_called_once_with("https://example.com/1")

        # Verify the result structure
        self.assertEqual(len(result["browsed_pages"]), 1)
        self.assertEqual(result["browsed_pages"][0]["url"], "https://example.com/1")
        self.assertEqual(result["next_step"], "extract_information")

    def test_extract_information(self):
        """Test the extract_information method."""
        # Set up initial state
        state = {
            "query": "test query",
            "browsed_pages": [
                {
                    "url": "https://example.com/1",
                    "title": "Test Page",
                    "content": "<html><body>Test content</body></html>",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "extracted_content": [],
            "next_step": "extract_information",
            "last_updated": datetime.now().isoformat()
        }

        result = self.workflow.extract_information(state)

        # Verify extraction was performed with the correct content and query
        self.mock_extraction_tool.extract_relevant_content.assert_called_once_with(
            "<html><body>Test content</body></html>",
            "test query"
        )

        # Verify the result structure
        self.assertEqual(len(result["extracted_content"]), 1)
        self.assertEqual(result["extracted_content"][0]["url"], "https://example.com/1")
        self.assertEqual(result["extracted_content"][0]["extracted_text"], "Extracted relevant content")
        self.assertEqual(result["next_step"], "evaluate_progress")

    def test_evaluate_progress_sufficient(self):
        """Test the evaluate_progress method when information is sufficient."""
        # Set up initial state
        state = {
            "query": "test query",
            "analysis": {"query_type": "factual"},
            "strategy": {"min_sources": 2},
            "search_queries": ["query 1", "query 2"],
            "current_query_index": 0,
            "extracted_content": [
                {"url": "https://example.com/1", "title": "Source 1", "extracted_text": "Content 1"},
                {"url": "https://example.com/2", "title": "Source 2", "extracted_text": "Content 2"}
            ],
            "next_step": "evaluate_progress",
            "last_updated": datetime.now().isoformat()
        }

        # Set the evaluator to return that information is sufficient
        self.mock_evaluator.check_information_sufficiency.return_value = True

        result = self.workflow.evaluate_progress(state)

        # Verify evaluation was performed
        self.mock_evaluator.check_information_sufficiency.assert_called_once()

        # Verify the result structure for sufficient information
        self.assertTrue(result["research_complete"])
        self.assertEqual(result["next_step"], "synthesize_information")

    def test_evaluate_progress_insufficient(self):
        """Test the evaluate_progress method when information is insufficient."""
        # Set up initial state
        state = {
            "query": "test query",
            "analysis": {"query_type": "factual"},
            "strategy": {"min_sources": 3},
            "search_queries": ["query 1", "query 2"],
            "current_query_index": 0,
            "extracted_content": [
                {"url": "https://example.com/1", "title": "Source 1", "extracted_text": "Content 1"}
            ],
            "next_step": "evaluate_progress",
            "last_updated": datetime.now().isoformat()
        }

        # Set the evaluator to return that information is insufficient
        self.mock_evaluator.check_information_sufficiency.return_value = False

        result = self.workflow.evaluate_progress(state)

        # Verify evaluation was performed
        self.mock_evaluator.check_information_sufficiency.assert_called_once()

        # Verify the result structure for insufficient information
        self.assertFalse(result.get("research_complete", False))
        self.assertEqual(result["next_step"], "perform_search")
        self.assertEqual(result["current_query_index"], 1)  # Should move to next query

    def test_synthesize_information(self):
        """Test the synthesize_information method."""
        # Set up initial state
        state = {
            "query": "test query",
            "analysis": {"query_type": "factual"},
            "extracted_content": [
                {"url": "https://example.com/1", "title": "Source 1", "extracted_text": "Content 1"},
                {"url": "https://example.com/2", "title": "Source 2", "extracted_text": "Content 2"}
            ],
            "next_step": "synthesize_information",
            "last_updated": datetime.now().isoformat(),
            "research_depth": "medium"  # Add research_depth to the state
        }

        result = self.workflow.synthesize_information(state)

        # Verify synthesis was performed with the correct content and research_depth
        self.mock_synthesizer.synthesize.assert_called_once_with(
            state["extracted_content"],
            "test query",
            {"query_type": "factual"},
            research_depth="medium"
        )

        # Verify the result structure
        self.assertEqual(result["synthesized_information"], self.mock_synthesizer.synthesize.return_value)
        self.assertEqual(result["next_step"], "generate_report")

    def test_generate_report(self):
        """Test the generate_report method."""
        # Set up initial state
        state = {
            "query": "test query",
            "synthesized_information": {
                "raw_synthesis": "Synthesized information",
                "sections": {"summary": "Test summary"}
            },
            "extracted_content": [
                {"url": "https://example.com/1", "title": "Source 1", "extracted_text": "Content 1"}
            ],
            "next_step": "generate_report",
            "last_updated": datetime.now().isoformat(),
            "research_depth": "medium"  # Add research_depth to the state
        }

        result = self.workflow.generate_report(state)

        # Verify report generation was performed with the correct information and research_depth
        self.mock_report_generator.generate.assert_called_once_with(
            state["synthesized_information"],
            state["extracted_content"],
            "test query",
            research_depth="medium"
        )

        # Verify the result structure
        self.assertEqual(result["final_report"], self.mock_report_generator.generate.return_value)
        self.assertEqual(result["next_step"], "end")

    def test_run_workflow(self):
        """Test the complete research workflow."""
        query = "test workflow query"
        research_depth = "light"  # Specify a research depth

        result = self.workflow.run_workflow(query, research_depth=research_depth)

        # Verify the workflow ran to completion
        self.assertEqual(result["query"], query)
        self.assertEqual(result["research_depth"], research_depth)  # Verify research_depth is in the result
        self.assertIsNotNone(result["report"])
        self.assertIsInstance(result["sources"], list)
        self.assertIsInstance(result["research_time"], float)

        # Verify that all major workflow steps were executed
        self.mock_query_analyzer.analyze.assert_called_once()
        self.mock_search_query_formulator.formulate_queries.assert_called_once()
        self.mock_strategy_planner.create_strategy.assert_called_once()
        self.mock_search_tool.search.assert_called()  # May be called multiple times
        self.mock_synthesizer.synthesize.assert_called_once()
        self.mock_report_generator.generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()