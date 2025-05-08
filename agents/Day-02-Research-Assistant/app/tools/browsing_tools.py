"""Web browsing and content extraction tools for the Research Assistant."""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import hashlib
import json


class WebBrowsingTool:
    """
    Tool for fetching and processing content from web pages.
    
    This component handles the retrieval of web page content, with
    support for JavaScript-heavy sites and different content types.
    """
    
    def __init__(self, use_playwright: bool = True, cache_dir: str = "./cache"):
        """
        Initialize the WebBrowsingTool.
        
        Args:
            use_playwright: Whether to use Playwright for JavaScript rendering
            cache_dir: Directory to cache fetched pages
        """
        self.use_playwright = use_playwright
        self.cache_dir = cache_dir
        self.document_cache = DocumentCache(cache_dir)
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def fetch_content(self, url: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch content from a web page, with caching.
        
        Args:
            url: URL to fetch content from
            force_refresh: Whether to bypass the cache
            
        Returns:
            Dictionary with page title, content, and metadata
        """
        # Check if the page is in the cache and we're not forcing a refresh
        if not force_refresh:
            cached_content = self.document_cache.get_cached_document(url)
            if cached_content:
                return cached_content
        
        # Fetch the content based on the configured method
        if self.use_playwright:
            content = self._fetch_with_playwright(url)
        else:
            content = self._fetch_with_requests(url)
        
        # Cache the content for future use
        if content:
            self.document_cache.cache_document(url, content)
        
        return content
    
    def _fetch_with_playwright(self, url: str) -> Dict[str, Any]:
        """
        Fetch content using Playwright (for JavaScript rendering).
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with page title, content, and metadata
        """
        # Note: In a real implementation, we would use Playwright here.
        # For the boilerplate, we'll simulate the behavior with a stub.
        try:
            # This is a stub method. In a real implementation, this would use Playwright.
            print(f"Fetching {url} with Playwright (stub)")
            
            # Simulate network delay
            time.sleep(0.1)
            
            # Return a dummy response
            return {
                "title": f"Page title for {url}",
                "content": f"<html><head><title>Page title for {url}</title></head>"
                          f"<body><h1>Content for {url}</h1><p>This is a stub response.</p></body></html>",
                "url": url,
                "fetched_at": datetime.now().isoformat(),
                "method": "playwright"
            }
            
        except Exception as e:
            print(f"Error fetching {url} with Playwright: {e}")
            return {}
    
    def _fetch_with_requests(self, url: str) -> Dict[str, Any]:
        """
        Fetch content using the requests library (for simple pages).
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with page title, content, and metadata
        """
        # Note: In a real implementation, we would use requests here.
        # For the boilerplate, we'll simulate the behavior with a stub.
        try:
            # This is a stub method. In a real implementation, this would use requests.
            print(f"Fetching {url} with requests (stub)")
            
            # Simulate network delay
            time.sleep(0.1)
            
            # Return a dummy response
            return {
                "title": f"Page title for {url}",
                "content": f"<html><head><title>Page title for {url}</title></head>"
                          f"<body><h1>Content for {url}</h1><p>This is a stub response.</p></body></html>",
                "url": url,
                "fetched_at": datetime.now().isoformat(),
                "method": "requests"
            }
            
        except Exception as e:
            print(f"Error fetching {url} with requests: {e}")
            return {}


class DocumentCache:
    """
    Caches fetched web pages to avoid redundant network requests.
    
    This component stores web page content locally, reducing the need
    for repeated fetches and speeding up the research process.
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialize the DocumentCache.
        
        Args:
            cache_dir: Directory to store cached documents
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cached_document(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document from cache if it exists.
        
        Args:
            url: URL of the document
            
        Returns:
            Cached document if it exists, otherwise None
        """
        # Create a filename from the URL
        filename = self._get_cache_filename(url)
        filepath = os.path.join(self.cache_dir, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading from cache: {e}")
                return None
        
        return None
    
    def cache_document(self, url: str, document: Dict[str, Any]) -> bool:
        """
        Cache a document for future use.
        
        Args:
            url: URL of the document
            document: Document content and metadata
            
        Returns:
            True if caching was successful, otherwise False
        """
        # Create a filename from the URL
        filename = self._get_cache_filename(url)
        filepath = os.path.join(self.cache_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                # Store document with metadata
                cache_entry = {
                    "url": url,
                    "title": document.get("title", ""),
                    "content": document.get("content", ""),
                    "cached_at": datetime.now().isoformat()
                }
                json.dump(cache_entry, f)
                return True
        except Exception as e:
            print(f"Error writing to cache: {e}")
            return False
    
    def _get_cache_filename(self, url: str) -> str:
        """
        Generate a cache filename from a URL.
        
        Args:
            url: URL to generate filename for
            
        Returns:
            Cache filename
        """
        # Create a hash of the URL to use as the filename
        return hashlib.md5(url.encode()).hexdigest() + ".json"
    
    def clear_cache(self) -> bool:
        """
        Clear all cached documents.
        
        Returns:
            True if clearing was successful, otherwise False
        """
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.cache_dir, filename)
                    os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            files = [f for f in os.listdir(self.cache_dir) if f.endswith(".json")]
            total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in files)
            
            return {
                "cache_dir": self.cache_dir,
                "document_count": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024)
            }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {
                "cache_dir": self.cache_dir,
                "error": str(e)
            }


class ContentExtractionTool:
    """
    Extracts relevant information from web page content.
    
    This component processes raw HTML content to extract the most relevant
    information based on the user's query.
    """
    
    def __init__(self, llm, use_html_parser: bool = True):
        """
        Initialize the ContentExtractionTool.
        
        Args:
            llm: Language model for content extraction
            use_html_parser: Whether to use HTML parsing
        """
        self.llm = llm
        self.use_html_parser = use_html_parser
        
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def extract_relevant_content(
        self, content: str, query: str, max_length: int = 10000
    ) -> str:
        """
        Extract relevant content from a web page based on a query.
        
        Args:
            content: Web page content (HTML)
            query: Research query
            max_length: Maximum length of content to process
            
        Returns:
            Extracted relevant content
        """
        if self.use_html_parser:
            cleaned_text = self._clean_html(content)
        else:
            cleaned_text = content
        
        # Limit the length to avoid token issues
        if len(cleaned_text) > max_length:
            cleaned_text = cleaned_text[:max_length]
        
        # Use the LLM to extract the most relevant parts
        prompt = f"""
        Based on the research query: "{query}"

        Extract the most relevant information from the following web page content:
        {cleaned_text}

        Extract only information that is directly relevant to the query.
        Format the output as plain text with clear paragraphs.
        Include any important facts, figures, dates, or statistics.
        """
        
        extracted_content = self.llm.invoke(prompt)
        return extracted_content
    
    def _clean_html(self, html_content: str) -> str:
        """
        Clean HTML content by removing scripts, styles, and other irrelevant elements.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Cleaned text
        """
        # Note: In a real implementation, we would use BeautifulSoup here.
        # For the boilerplate, we'll simulate the behavior with a stub.
        
        # Simulate HTML cleaning
        text = html_content.replace('<script>', '').replace('</script>', '')
        text = text.replace('<style>', '').replace('</style>', '')
        text = text.replace('<header>', '').replace('</header>', '')
        text = text.replace('<footer>', '').replace('</footer>', '')
        
        # Very basic removal of HTML tags
        # This is a simplified approach; a real implementation would use BeautifulSoup
        import re
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_structured_data(
        self, content: str, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured data from web content based on a schema.
        
        Args:
            content: Web page content
            schema: Schema defining the structure to extract
            
        Returns:
            Structured data according to the schema
        """
        # Clean the HTML
        cleaned_text = self._clean_html(content)
        
        # Create a prompt based on the schema
        schema_str = json.dumps(schema, indent=2)
        prompt = f"""
        Extract structured information from the following web content according to this schema:
        {schema_str}

        Web content:
        {cleaned_text[:10000]}  # Limit to avoid token issues

        Return ONLY a valid JSON object matching the schema.
        """
        
        # Use the LLM to extract structured data
        response = self.llm.invoke(prompt)
        
        # Parse the response as JSON
        try:
            # Extract JSON from the response (in case there's additional text)
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
                
            # Parse the JSON
            result = json.loads(json_str)
            return result
        except Exception as e:
            print(f"Error parsing structured data: {e}")
            return {"error": str(e), "raw_response": response}