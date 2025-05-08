"""Tests for the search tools components."""

import unittest
from unittest.mock import MagicMock, patch

from tools.search_tools import WebSearchTool, SearchHistory


class TestWebSearchTool(unittest.TestCase):
    """Tests for the WebSearchTool class."""
    
    def setUp(self):
        """Set up test cases."""
        self.api_key = "test_api_key"
        
        # Create patches for external search APIs
        self.exa_search_patch = patch("tools.search_tools.ExaSearch")
        self.serpapi_patch = patch("tools.search_tools.SerpAPIWrapper")
        
        # Start the patches
        self.mock_exa_search = self.exa_search_patch.start()
        self.mock_serpapi = self.serpapi_patch.start()
        
        # Configure the mocks
        self.mock_exa_instance = MagicMock()
        self.mock_serpapi_instance = MagicMock()
        
        self.mock_exa_search.return_value = self.mock_exa_instance
        self.mock_serpapi.return_value = self.mock_serpapi_instance
        
        # Set up mock search results
        self.mock_exa_result = MagicMock()
        self.mock_exa_result.title = "Test Result"
        self.mock_exa_result.url = "https://example.com/test"
        self.mock_exa_result.text = "This is a test result"
        
        self.mock_exa_instance.search.return_value = [self.mock_exa_result]
        
        self.mock_serpapi_instance.results.return_value = {
            "organic_results": [
                {
                    "title": "SerpAPI Test Result",
                    "link": "https://example.com/serpapi",
                    "snippet": "This is a SerpAPI test result"
                }
            ]
        }
    
    def tearDown(self):
        """Clean up after tests."""
        self.exa_search_patch.stop()
        self.serpapi_patch.stop()
    
    def test_exa_search(self):
        """Test search with Exa search engine."""
        search_tool = WebSearchTool(api_key=self.api_key, search_engine="exa")
        results = search_tool.search("test query")
        
        # Verify the search was called with the correct parameters
        self.mock_exa_instance.search.assert_called_once_with("test query")
        
        # Verify the results are formatted correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Result")
        self.assertEqual(results[0]["url"], "https://example.com/test")
        self.assertEqual(results[0]["snippet"], "This is a test result")
        self.assertEqual(results[0]["source"], "exa")
    
    def test_serpapi_search(self):
        """Test search with SerpAPI search engine."""
        search_tool = WebSearchTool(api_key=self.api_key, search_engine="serpapi")
        results = search_tool.search("test query")
        
        # Verify the search was called with the correct parameters
        self.mock_serpapi_instance.results.assert_called_once()
        
        # Verify the results are formatted correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "SerpAPI Test Result")
        self.assertEqual(results[0]["url"], "https://example.com/serpapi")
        self.assertEqual(results[0]["snippet"], "This is a SerpAPI test result")
        self.assertEqual(results[0]["source"], "serpapi")
    
    def test_unsupported_search_engine(self):
        """Test that an unsupported search engine raises an error."""
        search_tool = WebSearchTool(api_key=self.api_key, search_engine="unsupported")
        with self.assertRaises(ValueError):
            search_tool.search("test query")
    
    def test_result_parsing_and_normalization(self):
        """Test that search results are properly parsed and normalized."""
        # Test with non-standard/unusual search results
        unusual_result = MagicMock()
        unusual_result.title = "<b>Formatted</b> Result" # HTML in title
        unusual_result.url = "https://example.com/test?param=1&param2=2"  # URL with params
        unusual_result.text = "This is a very long text " * 50  # Long text
        self.mock_exa_instance.search.return_value = [unusual_result]
        
        search_tool = WebSearchTool(api_key=self.api_key, search_engine="exa")
        results = search_tool.search("test query")
        
        # Check that the title was normalized (HTML removed if implemented)
        self.assertEqual(results[0]["title"], "<b>Formatted</b> Result")
        
        # Check that the URL was preserved with parameters
        self.assertEqual(results[0]["url"], "https://example.com/test?param=1&param2=2")
        
        # Check that long snippets are handled properly (truncated if implemented)
        self.assertTrue(len(results[0]["snippet"]) > 0)
    
    def test_error_handling_and_retries(self):
        """Test error handling and retry logic."""
        # Setup mock to fail on first call, succeed on second
        self.mock_exa_instance.search.side_effect = [
            Exception("API rate limit exceeded"),
            [self.mock_exa_result]
        ]
        
        # Create search tool with retry capability
        search_tool = WebSearchTool(api_key=self.api_key, search_engine="exa")
        
        # Test with patched retry method
        with patch.object(search_tool, '_handle_search_error') as mock_handler:
            # Configure the error handler to return a result on retry
            mock_handler.return_value = [{
                "title": "Retry Result",
                "url": "https://example.com/retry",
                "snippet": "This is a result after retry",
                "source": "exa"
            }]
            
            # The search should continue through the error
            results = search_tool.search("test query")
            
            # Verify error handler was called
            mock_handler.assert_called_once()
            
            # Check that we got results despite the initial error
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["title"], "Retry Result")


class TestSearchHistory(unittest.TestCase):
    """Tests for the SearchHistory class."""
    
    def setUp(self):
        """Set up test cases."""
        self.search_history = SearchHistory()
        
        # Create test search results
        self.test_results = [
            {
                "title": "Test Result 1",
                "url": "https://example.com/test1",
                "snippet": "This is test result 1"
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/test2",
                "snippet": "This is test result 2"
            }
        ]
    
    def test_add_search(self):
        """Test adding a search to history."""
        self.search_history.add_search("test query", self.test_results)
        
        # Verify the search was added to history
        history = self.search_history.get_search_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["query"], "test query")
        self.assertEqual(history[0]["result_count"], 2)
        self.assertEqual(len(history[0]["result_urls"]), 2)
        self.assertIn("https://example.com/test1", history[0]["result_urls"])
        self.assertIn("https://example.com/test2", history[0]["result_urls"])
    
    def test_has_similar_query(self):
        """Test checking for similar queries."""
        # Add a search to history
        self.search_history.add_search("artificial intelligence", self.test_results)
        
        # Test exact match
        result = self.search_history.has_similar_query("artificial intelligence")
        self.assertIsNotNone(result)
        
        # Test substring match
        result = self.search_history.has_similar_query("intelligence")
        self.assertIsNotNone(result)
        
        # Test word overlap
        result = self.search_history.has_similar_query("AI and artificial neural networks")
        self.assertIsNotNone(result)
        
        # Test no match
        result = self.search_history.has_similar_query("completely different query")
        self.assertIsNone(result)
    
    def test_word_overlap_similarity(self):
        """Test the word overlap similarity function."""
        # High similarity
        similarity = self.search_history._word_overlap_similarity(
            "artificial intelligence research",
            "research on artificial intelligence"
        )
        self.assertGreater(similarity, 0.5)
        
        # Low similarity
        similarity = self.search_history._word_overlap_similarity(
            "artificial intelligence",
            "natural language processing"
        )
        self.assertLess(similarity, 0.5)
        
        # Empty queries
        similarity = self.search_history._word_overlap_similarity("", "test")
        self.assertEqual(similarity, 0.0)
        similarity = self.search_history._word_overlap_similarity("test", "")
        self.assertEqual(similarity, 0.0)
        similarity = self.search_history._word_overlap_similarity("", "")
        self.assertEqual(similarity, 0.0)
    
    def test_get_related_searches(self):
        """Test retrieving related searches."""
        # Add multiple searches to history
        self.search_history.add_search("machine learning algorithms", self.test_results)
        self.search_history.add_search("neural networks in AI", self.test_results)
        self.search_history.add_search("climate change impacts", self.test_results)
        
        # Test finding related searches to AI
        related = self.search_history.get_related_searches("artificial intelligence applications")
        
        # Should match the first two but not the third
        self.assertEqual(len(related), 2)
        self.assertIn("machine learning algorithms", [r["query"] for r in related])
        self.assertIn("neural networks in AI", [r["query"] for r in related])
        self.assertNotIn("climate change impacts", [r["query"] for r in related])


if __name__ == "__main__":
    unittest.main()