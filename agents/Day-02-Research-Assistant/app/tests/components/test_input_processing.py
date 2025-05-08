"""Tests for the input processing components."""

import unittest
from unittest.mock import MagicMock, patch

from components.input_processing import QueryAnalyzer, SearchQueryFormulator


class TestQueryAnalyzer(unittest.TestCase):
    """Tests for the QueryAnalyzer class."""
    
    def setUp(self):
        """Set up test cases."""
        self.mock_llm = MagicMock()
        self.mock_llm.invoke.return_value = """
        Main topics: Artificial Intelligence, Machine Learning
        Key entities: Neural Networks, Deep Learning, AI Applications
        Query type: Exploratory
        Domain: Computer Science, Technology
        Time constraints: Recent developments (last 5 years)
        """
        self.analyzer = QueryAnalyzer(self.mock_llm)
    
    def test_analyze(self):
        """Test the analyze method."""
        query = "What are the latest developments in AI and machine learning?"
        result = self.analyzer.analyze(query)
        
        # Verify LLM was called with the correct prompt
        self.mock_llm.invoke.assert_called_once()
        args, _ = self.mock_llm.invoke.call_args
        self.assertIn(query, args[0])
        
        # Verify the results are as expected
        self.assertEqual(result["original_query"], query)
        self.assertIn("topics", result)
        self.assertIn("entities", result)
        self.assertIn("query_type", result)
        self.assertIn("domain", result)
        
        # Check that we extracted some entities and topics
        self.assertTrue(len(result["topics"]) > 0)
        self.assertTrue(len(result["entities"]) > 0)
    
    def test_parse_query_topics(self):
        """Test parsing of query topics from LLM response."""
        llm_response = """
        Main topics: Renewable Energy, Solar Power, Wind Energy
        Key entities: Photovoltaic Cells, Wind Turbines, Energy Storage
        Query type: Comparative
        Domain: Environmental Science, Engineering
        """
        
        # Set up a new response for this test
        self.mock_llm.invoke.return_value = llm_response
        
        # Call analyze to trigger the parsing
        query = "Compare solar and wind energy technologies"
        result = self.analyzer.analyze(query)
        
        # Check the parsed topics
        self.assertIn("Renewable Energy", result["topics"])
        self.assertIn("Solar Power", result["topics"])
        self.assertIn("Wind Energy", result["topics"])
    
    def test_handle_edge_cases(self):
        """Test handling of edge cases like very short queries."""
        # Test with a very short query
        short_query = "AI?"
        
        # Mock a different response for short query
        self.mock_llm.invoke.return_value = """
        Main topics: Artificial Intelligence
        Key entities: AI
        Query type: General
        Domain: Technology
        """
        
        result = self.analyzer.analyze(short_query)
        
        # Verify the analyzer handled the short query
        self.assertEqual(result["original_query"], short_query)
        self.assertIn("topics", result)
        self.assertEqual(result["topics"], ["Artificial Intelligence"])


class TestSearchQueryFormulator(unittest.TestCase):
    """Tests for the SearchQueryFormulator class."""
    
    def setUp(self):
        """Set up test cases."""
        self.mock_llm = MagicMock()
        self.mock_llm.invoke.return_value = """
        1. Latest advancements in artificial intelligence research
        2. Recent breakthroughs in machine learning and neural networks
        3. AI applications in industry from 2020-2025
        4. State-of-the-art deep learning techniques
        """
        self.formulator = SearchQueryFormulator(self.mock_llm)
    
    def test_formulate_queries(self):
        """Test the formulate_queries method."""
        analysis = {
            "original_query": "What are the latest developments in AI?",
            "topics": ["Artificial Intelligence", "Machine Learning"],
            "entities": ["Neural Networks", "Deep Learning"],
            "query_type": "exploratory",
            "domain": "technology",
            "time_constraints": "Recent (last 5 years)"
        }
        
        result = self.formulator.formulate_queries(analysis)
        
        # Verify LLM was called with the correct prompt
        self.mock_llm.invoke.assert_called_once()
        
        # Verify we got the expected number of queries
        self.assertEqual(len(result), 4)
        
        # Check that the queries are not empty
        for query in result:
            self.assertTrue(len(query) > 0)
    
    def test_domain_specific_terminology(self):
        """Test handling of domain-specific terminology in query formulation."""
        # Medical domain analysis
        medical_analysis = {
            "original_query": "What are recent treatments for Alzheimer's disease?",
            "topics": ["Alzheimer's Disease", "Medical Treatments"],
            "entities": ["Dementia", "Neurodegenerative Disease"],
            "query_type": "exploratory",
            "domain": "medicine",
            "time_constraints": "Recent (last 3 years)"
        }
        
        # Mock a domain-specific response
        self.mock_llm.invoke.return_value = """
        1. Latest clinical trials for Alzheimer's disease treatments
        2. FDA-approved medications for Alzheimer's disease 2020-2023
        3. Experimental therapies for neurodegenerative disorders
        4. Alzheimer's disease treatment breakthroughs in medical journals
        """
        
        result = self.formulator.formulate_queries(medical_analysis)
        
        # Verify the queries contain domain-specific terminology
        has_medical_terms = False
        for query in result:
            if "clinical trials" in query or "FDA-approved" in query:
                has_medical_terms = True
                break
                
        self.assertTrue(has_medical_terms)
    
    def test_consistency_across_similar_inputs(self):
        """Test consistency of generated queries for similar inputs."""
        # Two similar analyses
        analysis1 = {
            "original_query": "What are recent AI advancements?",
            "topics": ["Artificial Intelligence", "Technology"],
            "entities": ["Machine Learning"],
            "query_type": "exploratory",
            "domain": "technology"
        }
        
        analysis2 = {
            "original_query": "What are the latest AI developments?",
            "topics": ["Artificial Intelligence", "Technology"],
            "entities": ["Machine Learning"],
            "query_type": "exploratory",
            "domain": "technology"
        }
        
        # Generate queries for both analyses
        queries1 = self.formulator.formulate_queries(analysis1)
        queries2 = self.formulator.formulate_queries(analysis2)
        
        # Check that there's significant overlap in the queries
        overlap_count = 0
        for q1 in queries1:
            for q2 in queries2:
                if self._calculate_similarity(q1, q2) > 0.7:  # Simple similarity threshold
                    overlap_count += 1
                    break
        
        # At least some queries should be similar
        self.assertGreater(overlap_count, 0)
    
    def _calculate_similarity(self, query1, query2):
        """Calculate a simple similarity score between two queries."""
        # Convert to lowercase and split into words
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


if __name__ == "__main__":
    unittest.main()