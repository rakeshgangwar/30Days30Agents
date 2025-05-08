"""Integration tests for the search-to-synthesis pipeline."""

import tempfile
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from components.input_processing import QueryAnalyzer
from components.research_workflow import ResearchWorkflow
from tools.search_tools import WebSearchTool
from tools.browsing_tools import WebBrowsingTool, ContentExtractionTool
from components.knowledge_processing import InformationSynthesizer


class MockLLM:
    """Mock LLM for testing."""
    
    def __init__(self, responses=None):
        """
        Initialize the MockLLM.
        
        Args:
            responses: Dictionary mapping prompt substrings to responses
        """
        self.responses = responses or {}
        self.default_response = "Default mock response"
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
        
        # Check if we have a matching response
        for key, response in self.responses.items():
            if key in prompt:
                return response
        
        # Fall back to default response
        return self.default_response


class TestSearchToSynthesisPipeline(unittest.TestCase):
    """Integration tests for the search-to-synthesis pipeline."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Set up mock LLM with predefined responses
        self.mock_llm = MockLLM({
            "Analyze the following research query": """
            Main topics: Artificial Intelligence, Machine Learning
            Key entities: Neural Networks, Deep Learning, AI Applications
            Query type: Exploratory
            Domain: Computer Science, Technology
            Time constraints: Recent developments (last 5 years)
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
            """
        })
        
        # Create mock components
        self.query_analyzer = QueryAnalyzer(self.mock_llm)
        self.extraction_tool = ContentExtractionTool(self.mock_llm)
        self.synthesizer = InformationSynthesizer(self.mock_llm)
        
        # Create mock search and browsing tools
        self.search_tool = MockSearchTool()
        self.browsing_tool = MockBrowsingTool()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_search_to_extraction_pipeline(self):
        """Test the search-to-extraction pipeline."""
        # Start with a query
        query = "What are the recent advancements in artificial intelligence?"
        
        # Analyze the query
        analysis = self.query_analyzer.analyze(query)
        
        # Verify analysis structure and content
        self.assertIn("topics", analysis)
        self.assertIn("entities", analysis)
        self.assertIn("query_type", analysis)
        
        # Perform search
        search_results = self.search_tool.search(query)
        
        # Verify search results
        self.assertGreater(len(search_results), 0)
        
        # Browse content from search results
        browsed_content = self.browsing_tool.fetch_content(search_results[0]["url"])
        
        # Verify browsed content
        self.assertIn("content", browsed_content)
        self.assertIn("title", browsed_content)
        
        # Extract relevant information
        extracted_content = self.extraction_tool.extract_relevant_content(
            browsed_content["content"],
            query
        )
        
        # Verify extraction
        self.assertIsNotNone(extracted_content)
        self.assertGreater(len(extracted_content), 0)
        
        # Create a structured extracted content item
        extracted_item = {
            "url": browsed_content["url"],
            "title": browsed_content["title"],
            "extracted_text": extracted_content
        }
        
        # Synthesize information
        synthesis = self.synthesizer.synthesize(
            [extracted_item],
            query,
            analysis
        )
        
        # Verify synthesis
        self.assertIn("raw_synthesis", synthesis)
        self.assertIn("sections", synthesis)
        self.assertIn("Summary", synthesis["sections"])
        self.assertIn("Key Points", synthesis["sections"])
        
        # Check that the synthesis content is relevant to AI
        self.assertIn("AI", synthesis["raw_synthesis"])
        self.assertIn("learning", synthesis["raw_synthesis"].lower())
    
    def test_input_to_search_integration(self):
        """Test the integration from input processing to search."""
        # Create mock search query formulator
        mock_formulator = MagicMock()
        mock_formulator.formulate_queries.return_value = [
            "recent advancements in artificial intelligence",
            "breakthroughs in machine learning 2023-2025"
        ]
        
        # Set up input processing components
        query = "What are the latest developments in AI?"
        analysis = self.query_analyzer.analyze(query)
        
        # Formulate search queries
        search_queries = mock_formulator.formulate_queries(analysis)
        
        # Verify search queries
        self.assertEqual(len(search_queries), 2)
        
        # Perform searches with all queries
        all_results = []
        for search_query in search_queries:
            results = self.search_tool.search(search_query)
            all_results.extend(results)
        
        # Verify combined search results
        self.assertGreater(len(all_results), 0)
        # Each search should yield unique results
        self.assertGreater(len(all_results), len(self.search_tool.search(search_queries[0])))
    
    def test_extraction_to_synthesis_integration(self):
        """Test the integration from content extraction to synthesis."""
        query = "What are the recent advancements in artificial intelligence?"
        analysis = self.query_analyzer.analyze(query)
        
        # Create multiple extracted content items
        extracted_contents = [
            {
                "url": "https://example.com/1",
                "title": "AI Research Breakthroughs",
                "extracted_text": "Content about recent AI breakthroughs."
            },
            {
                "url": "https://example.com/2",
                "title": "Machine Learning Applications",
                "extracted_text": "Content about ML applications in industry."
            }
        ]
        
        # Synthesize the information
        synthesis = self.synthesizer.synthesize(
            extracted_contents,
            query,
            analysis
        )
        
        # Verify synthesis results
        self.assertEqual(synthesis["source_count"], 2)
        self.assertEqual(synthesis["query"], query)
        self.assertIn("raw_synthesis", synthesis)
        self.assertIn("sections", synthesis)
        
        # Verify synthesis includes content from both sources
        prompt = self.mock_llm.invocations[-1] if self.mock_llm.invocations else ""
        self.assertIn("AI Research Breakthroughs", prompt)
        self.assertIn("Machine Learning Applications", prompt)


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
        return {
            "title": f"Page title for {url}",
            "content": f"<html><body><h1>Content for {url}</h1><p>This is a detailed article about artificial intelligence, machine learning, and neural networks. The field has seen significant advancements in recent years.</p></body></html>",
            "url": url,
            "fetched_at": datetime.now().isoformat()
        }


if __name__ == "__main__":
    unittest.main()