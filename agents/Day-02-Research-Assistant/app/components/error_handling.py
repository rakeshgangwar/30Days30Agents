"""Error handling components for the Research Assistant."""

import time
from typing import Dict, List, Any, Optional, Callable
import requests


class SearchFailureHandler:
    """
    Manages API errors and rate limits for search operations.
    
    This component implements retry logic and fallback strategies
    when search operations fail.
    """
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2):
        """
        Initialize the SearchFailureHandler.
        
        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Factor for exponential backoff between retries
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def handle_search_failure(
        self, search_tool, query: str, error: Exception
    ) -> List[Dict[str, Any]]:
        """
        Handle failures in the search process with retries and fallbacks.
        
        Args:
            search_tool: The search tool to use
            query: Search query
            error: The original error
            
        Returns:
            Search results (original or fallback)
        """
        search_successful = False
        results = []
        
        # Try with retries and exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Wait with exponential backoff
                if attempt > 0:
                    wait_time = self.backoff_factor ** attempt
                    print(f"Retry attempt {attempt+1} after {wait_time:.1f}s wait")
                    time.sleep(wait_time)
                
                # Try searching
                results = search_tool.search(query)
                if results:  # Consider empty results as a failure
                    search_successful = True
                    break
                else:
                    print(f"Search attempt {attempt+1} returned no results")
            except Exception as e:
                print(f"Search attempt {attempt+1} failed: {e}")
        
        # If all retries failed, try fallback strategies
        if not search_successful:
            results = self._fallback_search_strategies(query, error)
        
        return results
    
    def _fallback_search_strategies(
        self, query: str, original_error: Exception
    ) -> List[Dict[str, Any]]:
        """
        Implement fallback search strategies when primary search fails.
        
        Args:
            query: Search query
            original_error: The original error
            
        Returns:
            Fallback search results
        """
        # Strategies could include:
        # 1. Try alternative search engines
        # 2. Modify the query to be simpler
        # 3. Use cached results if available
        # 4. Return a minimal placeholder result
        
        # Simplify the query (remove complex terms)
        simple_query = self._simplify_query(query)
        if simple_query != query:
            try:
                # Try with simplified query
                results = self._try_alternate_search(simple_query)
                if results:
                    return results
            except Exception as e:
                print(f"Simplified query search failed: {e}")
        
        # Try with Wikipedia fallback
        try:
            wikipedia_results = self._try_wikipedia_search(query)
            if wikipedia_results:
                return wikipedia_results
        except Exception as e:
            print(f"Wikipedia fallback failed: {e}")
        
        # Return a minimal placeholder as last resort
        return [{
            "title": "Search Error",
            "url": "",
            "snippet": f"Could not perform search due to: {str(original_error)}",
            "source": "error_handler",
            "is_fallback": True
        }]
    
    def _simplify_query(self, query: str) -> str:
        """
        Simplify a complex query by removing specialized terms.
        
        Args:
            query: Original query
            
        Returns:
            Simplified query
        """
        # Remove quotes, special operators, and other search syntax
        simplified = query.replace('"', '').replace(':', ' ').replace('site:', '')
        
        # Take only the first N words if the query is very long
        words = simplified.split()
        if len(words) > 8:
            simplified = ' '.join(words[:8])
        
        return simplified
    
    def _try_alternate_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Try an alternate method for searching.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        # This is a stub implementation
        # In a real application, this would try alternate search APIs
        
        return [{
            "title": f"Fallback Result for {query}",
            "url": "https://example.com/fallback",
            "snippet": f"This is a fallback result for the query: {query}",
            "source": "fallback_search",
            "is_fallback": True
        }]
    
    def _try_wikipedia_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Try to search Wikipedia as a fallback.
        
        Args:
            query: Search query
            
        Returns:
            Search results from Wikipedia
        """
        # This is a stub implementation
        # In a real application, this would use the Wikipedia API
        
        return [{
            "title": f"Wikipedia: {query}",
            "url": f"https://en.wikipedia.org/wiki/Special:Search?search={query.replace(' ', '+')}",
            "snippet": f"Wikipedia search results for: {query}",
            "source": "wikipedia_fallback",
            "is_fallback": True
        }]


class ContentAccessRetrier:
    """
    Handles website access failures with retries and alternate methods.
    
    This component implements various strategies for accessing web content
    when initial attempts fail.
    """
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2):
        """
        Initialize the ContentAccessRetrier.
        
        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Factor for exponential backoff between retries
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def fetch_with_retry(self, browsing_tool, url: str) -> Dict[str, Any]:
        """
        Fetch content with retries and fallback strategies.
        
        Args:
            browsing_tool: The browsing tool to use
            url: URL to fetch
            
        Returns:
            Fetched content (original or fallback)
        """
        # Try with the main browsing tool
        for attempt in range(self.max_retries):
            try:
                # Wait with exponential backoff if not first attempt
                if attempt > 0:
                    wait_time = self.backoff_factor ** attempt
                    print(f"Retry attempt {attempt+1} after {wait_time:.1f}s wait")
                    time.sleep(wait_time)
                
                # Try fetching content
                result = browsing_tool.fetch_content(url)
                if result:  # Check if we got a valid result
                    return result
                else:
                    print(f"Fetch attempt {attempt+1} returned empty result")
            except Exception as e:
                print(f"Fetch attempt {attempt+1} for {url} failed: {e}")
        
        # If all retries fail, try alternative approaches
        return self._try_alternative_access_methods(url)
    
    def _try_alternative_access_methods(self, url: str) -> Dict[str, Any]:
        """
        Try alternative methods to access content.
        
        Args:
            url: URL to access
            
        Returns:
            Fetched content using alternative methods
        """
        # Methods to try:
        # 1. Try with a different User-Agent
        # 2. Try with a simple requests approach if Playwright failed
        # 3. Check for cached versions via archive.org
        # 4. Extract from Google's cached version
        
        # Try with simple requests with a different User-Agent
        try:
            result = self._try_simple_request(url)
            if result:
                return result
        except Exception as e:
            print(f"Simple requests fallback failed: {e}")
        
        # Try archive.org
        try:
            result = self._try_archive_org(url)
            if result:
                return result
        except Exception as e:
            print(f"Archive.org fallback failed: {e}")
        
        # Try Google Cache (stub)
        try:
            result = self._try_google_cache(url)
            if result:
                return result
        except Exception as e:
            print(f"Google cache fallback failed: {e}")
        
        # Return minimal placeholder if all fallbacks fail
        return {
            "title": "Access Failed",
            "content": "Could not access the content of this page.",
            "url": url,
            "access_method": "failed",
            "is_fallback": True
        }
    
    def _try_simple_request(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Try to access content with a simple HTTP request.
        
        Args:
            url: URL to access
            
        Returns:
            Fetched content if successful, otherwise None
        """
        # This is a stub implementation
        # In a real application, this would use the requests library
        
        # Simulate successful fetch
        return {
            "title": f"Simple Request: {url}",
            "content": f"<html><body>Content fetched via simple request from {url}</body></html>",
            "url": url,
            "access_method": "simple_request",
            "is_fallback": True
        }
    
    def _try_archive_org(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Try to access content via archive.org.
        
        Args:
            url: URL to access
            
        Returns:
            Fetched content if successful, otherwise None
        """
        # This is a stub implementation
        # In a real application, this would use archive.org API
        
        archive_url = f"https://web.archive.org/web/{url}"
        
        # Simulate successful fetch
        return {
            "title": f"Archive.org: {url}",
            "content": f"<html><body>Content fetched via archive.org for {url}</body></html>",
            "url": url,
            "archive_url": archive_url,
            "access_method": "archive_org",
            "is_fallback": True
        }
    
    def _try_google_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Try to access content via Google's cache.
        
        Args:
            url: URL to access
            
        Returns:
            Fetched content if successful, otherwise None
        """
        # This is a stub implementation
        # In a real application, this would use Google's cache
        
        cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
        
        # Simulate successful fetch
        return {
            "title": f"Google Cache: {url}",
            "content": f"<html><body>Content fetched via Google cache for {url}</body></html>",
            "url": url,
            "cache_url": cache_url,
            "access_method": "google_cache",
            "is_fallback": True
        }


class FallbackInformationSources:
    """
    Provides alternative information sources when primary sources fail.
    
    This component maintains a set of reliable fallback sources that can
    be used when primary research sources are unavailable.
    """
    
    def __init__(self):
        """Initialize the FallbackInformationSources."""
        # List of reliable fallback sources by category
        self.fallback_sources = {
            "general": [
                {"name": "Wikipedia", "url_template": "https://en.wikipedia.org/wiki/{query}"},
                {"name": "Encyclopedia Britannica", "url_template": "https://www.britannica.com/search?query={query}"}
            ],
            "science": [
                {"name": "Science.gov", "url_template": "https://www.science.gov/sciencegov/desktop/en/search.html?q={query}"},
                {"name": "NASA", "url_template": "https://www.nasa.gov/search/{query}"}
            ],
            "news": [
                {"name": "Reuters", "url_template": "https://www.reuters.com/search/news?blob={query}"},
                {"name": "AP News", "url_template": "https://apnews.com/search?q={query}"}
            ],
            "academic": [
                {"name": "Google Scholar", "url_template": "https://scholar.google.com/scholar?q={query}"},
                {"name": "arXiv", "url_template": "https://arxiv.org/search/?query={query}&searchtype=all"}
            ]
        }
    
    def get_fallback_sources(self, category: str, query: str) -> List[Dict[str, str]]:
        """
        Get fallback sources for a specific category and query.
        
        Args:
            category: Source category (general, science, news, academic)
            query: Search query
            
        Returns:
            List of fallback sources with formatted URLs
        """
        sources = self.fallback_sources.get(category, self.fallback_sources["general"])
        
        # Format the URL templates with the query
        formatted_sources = []
        url_safe_query = query.replace(' ', '+')
        
        for source in sources:
            formatted_sources.append({
                "name": source["name"],
                "url": source["url_template"].format(query=url_safe_query)
            })
        
        return formatted_sources
    
    def generate_fallback_content(
        self, query: str, category: str, llm
    ) -> Dict[str, Any]:
        """
        Generate fallback content when no sources are available.
        
        Args:
            query: The research query
            category: Query category
            llm: Language model for content generation
            
        Returns:
            Dictionary with fallback content and sources
        """
        # Get relevant fallback sources
        sources = self.get_fallback_sources(category, query)
        
        # Create a prompt for the LLM to generate baseline information
        source_texts = "\n".join([f"- {s['name']}: {s['url']}" for s in sources])
        prompt = f"""
        I need to provide basic information about the following query:
        "{query}"
        
        I don't have direct access to search results, but I should provide:
        1. A basic overview of what is known about this topic
        2. Key concepts or definitions related to the query
        3. Important considerations or limitations in researching this topic
        
        Additionally, I should recommend these sources for further research:
        {source_texts}
        
        Provide a concise but informative response that acknowledges the limitations
        but still gives useful baseline information. Format as Markdown.
        """
        
        # Generate fallback content
        fallback_content = llm.invoke(prompt)
        
        return {
            "content": fallback_content,
            "fallback_sources": sources,
            "is_fallback": True,
            "query": query
        }


class ErrorLogger:
    """
    Logs errors and exceptions during the research process.
    
    This component maintains a record of errors for debugging
    and improvement of the research process.
    """
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the ErrorLogger.
        
        Args:
            log_file: Path to log file (optional)
        """
        self.log_file = log_file
        self.errors = []
        
        # Create log file if specified
        if log_file:
            with open(log_file, 'a') as f:
                f.write(f"=== Research Assistant Error Log ===\n")
                f.write(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def log_error(
        self, error: Exception, context: str, severity: str = "ERROR"
    ) -> None:
        """
        Log an error with context.
        
        Args:
            error: The exception or error
            context: Additional context about when/where the error occurred
            severity: Error severity (INFO, WARNING, ERROR, CRITICAL)
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        error_message = str(error)
        error_type = type(error).__name__
        
        log_entry = {
            "timestamp": timestamp,
            "severity": severity,
            "error_type": error_type,
            "error_message": error_message,
            "context": context
        }
        
        self.errors.append(log_entry)
        
        log_text = f"[{timestamp}] {severity}: {error_type} - {error_message} ({context})"
        print(log_text)
        
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(log_text + "\n")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of logged errors.
        
        Returns:
            Dictionary with error summary
        """
        error_types = {}
        for error in self.errors:
            error_type = error["error_type"]
            if error_type in error_types:
                error_types[error_type] += 1
            else:
                error_types[error_type] = 1
        
        return {
            "total_errors": len(self.errors),
            "error_types": error_types,
            "error_log": self.errors
        }