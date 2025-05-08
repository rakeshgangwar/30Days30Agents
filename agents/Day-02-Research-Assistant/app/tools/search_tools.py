"""Web search tools for the Research Assistant."""

from typing import Dict, List, Any, Optional
import os

from langchain_exa import ExaSearch
from langchain_community.utilities import SerpAPIWrapper


class WebSearchTool:
    """
    Tool for performing web searches using different search engines.
    
    This component abstracts away the specifics of different search engines
    and provides a unified interface for web searching.
    """

    def __init__(self, api_key: str, search_engine: str = "exa"):
        """
        Initialize the WebSearchTool.
        
        Args:
            api_key: API key for the search engine
            search_engine: Search engine to use ("exa" or "serpapi")
        """
        self.api_key = api_key
        self.search_engine = search_engine
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search the web using the configured search engine.
        
        Args:
            query: The search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        if self.search_engine == "exa":
            return self._search_exa(query, num_results)
        elif self.search_engine == "serpapi":
            return self._search_serpapi(query, num_results)
        else:
            raise ValueError(f"Unsupported search engine: {self.search_engine}")
    
    def _search_exa(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search using Exa Search API.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            search_tool = ExaSearch(api_key=self.api_key)
            results = search_tool.search(query, num_results=num_results)
            
            return [
                {
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.text,
                    "source": "exa"
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error with Exa search: {e}")
            return []
    
    def _search_serpapi(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search using SerpAPI.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            search = SerpAPIWrapper(serpapi_api_key=self.api_key)
            results = search.results(query, num_results=num_results)
            
            # SerpAPI returns different structure, normalize it
            normalized_results = []
            
            if 'organic_results' in results:
                for result in results['organic_results'][:num_results]:
                    normalized_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": "serpapi"
                    })
            
            return normalized_results
        except Exception as e:
            print(f"Error with SerpAPI search: {e}")
            return []


class SearchHistory:
    """
    Tracks search history to prevent redundant searches.
    
    This component maintains a record of previous searches and their results,
    which can be used to optimize subsequent searches.
    """
    
    def __init__(self):
        """Initialize the search history tracker."""
        self.history: List[Dict[str, Any]] = []
        
    def add_search(self, query: str, results: List[Dict[str, Any]]) -> None:
        """
        Add a search query and its results to history.
        
        Args:
            query: The search query
            results: Search results
        """
        search_record = {
            "query": query,
            "timestamp": os.times(),
            "result_count": len(results),
            "result_urls": [r["url"] for r in results]
        }
        
        self.history.append(search_record)
    
    def has_similar_query(self, query: str, threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """
        Check if a similar query has been searched before.
        
        In a real implementation, this would use embedding similarity.
        For the boilerplate, we use a simple substring check.
        
        Args:
            query: The search query
            threshold: Similarity threshold
            
        Returns:
            The previous search record if found, otherwise None
        """
        # Simple approach for the boilerplate
        query_lower = query.lower()
        
        for record in reversed(self.history):
            record_query = record["query"].lower()
            
            # Check if queries are similar based on substring matching
            # This is a simplified approach; a real implementation would use embeddings
            if (query_lower in record_query or record_query in query_lower or
                self._word_overlap_similarity(query_lower, record_query) > threshold):
                return record
        
        return None
    
    def _word_overlap_similarity(self, query1: str, query2: str) -> float:
        """
        Calculate word overlap similarity between two queries.
        
        Args:
            query1: First query
            query2: Second query
            
        Returns:
            Similarity score between 0 and 1
        """
        words1 = set(query1.split())
        words2 = set(query2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """
        Get all search history.
        
        Returns:
            List of search records
        """
        return self.history