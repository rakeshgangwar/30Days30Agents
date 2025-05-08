"""Document loader tools for the Research Assistant."""

from typing import Dict, List, Any, Optional, Union
import os
import logging
from pathlib import Path
from datetime import datetime

from langchain_community.document_loaders import (
    WebBaseLoader,
    PlaywrightURLLoader,
    ArxivLoader,
    PubMedLoader,
    PyMuPDFLoader,
    WikipediaLoader,
    RecursiveUrlLoader,
    UnstructuredFileLoader,
    CSVLoader,
    JSONLoader,
    BSHTMLLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("research_assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("document_loaders")

class DocumentLoaderManager:
    """
    Manages different document loaders for various content types.

    This component provides a unified interface for loading documents
    from different sources and formats.
    """

    def __init__(self, cache_dir: str = "./document_cache"):
        """
        Initialize the DocumentLoaderManager.

        Args:
            cache_dir: Directory to cache loaded documents
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def load_from_web(self, url: str, use_playwright: bool = False) -> List[Dict[str, Any]]:
        """
        Load content from a web URL.

        Args:
            url: The URL to load
            use_playwright: Whether to use Playwright for JavaScript rendering

        Returns:
            List of document dictionaries
        """
        loader_type = "PlaywrightURLLoader" if use_playwright else "WebBaseLoader"
        logger.info(f"Loading content from web URL {url} using {loader_type}")

        try:
            if use_playwright:
                loader = PlaywrightURLLoader(urls=[url])
            else:
                loader = WebBaseLoader(url)

            documents = loader.load()

            # Log success
            logger.info(f"Successfully loaded {len(documents)} documents from {url}")

            # Convert to dictionary format
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_type": "web",
                    "url": url
                }
                for doc in documents
            ]
        except Exception as e:
            logger.error(f"Error loading from web URL {url}: {e}")
            return []

    def load_from_arxiv(self, query: str, max_docs: int = 5) -> List[Dict[str, Any]]:
        """
        Load papers from Arxiv based on a query.

        Args:
            query: Search query for Arxiv
            max_docs: Maximum number of documents to load

        Returns:
            List of document dictionaries
        """
        logger.info(f"Loading papers from Arxiv with query: '{query}', max_docs: {max_docs}")

        try:
            loader = ArxivLoader(query=query, load_max_docs=max_docs)
            documents = loader.load()

            logger.info(f"Successfully loaded {len(documents)} papers from Arxiv")

            result = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_type": "arxiv",
                    "url": doc.metadata.get("entry_id", "")
                }
                for doc in documents
            ]

            # Log paper titles
            for i, doc in enumerate(result):
                title = doc.get("metadata", {}).get("title", "Unknown title")
                logger.info(f"Arxiv paper {i+1}: {title}")

            return result
        except Exception as e:
            logger.error(f"Error loading from Arxiv with query {query}: {e}")
            return []

    def load_from_pubmed(self, query: str, max_docs: int = 5) -> List[Dict[str, Any]]:
        """
        Load papers from PubMed based on a query.

        Args:
            query: Search query for PubMed
            max_docs: Maximum number of documents to load

        Returns:
            List of document dictionaries
        """
        logger.info(f"Loading papers from PubMed with query: '{query}', max_docs: {max_docs}")

        try:
            loader = PubMedLoader(query=query, load_max_docs=max_docs)
            documents = loader.load()

            logger.info(f"Successfully loaded {len(documents)} papers from PubMed")

            result = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_type": "pubmed",
                    "url": doc.metadata.get("entry_id", "")
                }
                for doc in documents
            ]

            # Log paper titles
            for i, doc in enumerate(result):
                title = doc.get("metadata", {}).get("title", "Unknown title")
                logger.info(f"PubMed paper {i+1}: {title}")

            return result
        except Exception as e:
            logger.error(f"Error loading from PubMed with query {query}: {e}")
            return []

    def load_from_wikipedia(self, query: str, max_docs: int = 3) -> List[Dict[str, Any]]:
        """
        Load content from Wikipedia based on a query.

        Args:
            query: Search query for Wikipedia
            max_docs: Maximum number of documents to load

        Returns:
            List of document dictionaries
        """
        logger.info(f"Loading content from Wikipedia with query: '{query}', max_docs: {max_docs}")

        try:
            loader = WikipediaLoader(query=query, load_max_docs=max_docs)
            documents = loader.load()

            logger.info(f"Successfully loaded {len(documents)} articles from Wikipedia")

            result = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_type": "wikipedia",
                    "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
                }
                for doc in documents
            ]

            # Log article titles
            for i, doc in enumerate(result):
                title = doc.get("metadata", {}).get("title", query)
                logger.info(f"Wikipedia article {i+1}: {title}")

            return result
        except Exception as e:
            logger.error(f"Error loading from Wikipedia with query {query}: {e}")
            return []

    def load_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load content from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of document dictionaries
        """
        logger.info(f"Loading content from PDF file: {file_path}")

        try:
            loader = PyMuPDFLoader(file_path)
            documents = loader.load()

            logger.info(f"Successfully loaded {len(documents)} pages from PDF file")

            result = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_type": "pdf",
                    "file_path": file_path
                }
                for doc in documents
            ]

            # Log page numbers
            for i, doc in enumerate(result):
                page_num = doc.get("metadata", {}).get("page", i)
                logger.info(f"PDF page {page_num} loaded from {file_path}")

            return result
        except Exception as e:
            logger.error(f"Error loading from PDF file {file_path}: {e}")
            return []

    def load_from_recursive_url(self, url: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """
        Load content from a URL and its linked pages recursively.

        Args:
            url: The base URL to start from
            max_depth: Maximum recursion depth

        Returns:
            List of document dictionaries
        """
        logger.info(f"Loading content recursively from URL {url} with max_depth {max_depth}")

        try:
            # Simple link extraction function
            def extract_links(html):
                import re
                return re.findall(r'href=["\'](https?://[^"\']+)["\']', html)

            loader = RecursiveUrlLoader(
                url=url,
                max_depth=max_depth,
                extractor=extract_links
            )
            documents = loader.load()

            logger.info(f"Successfully loaded {len(documents)} documents recursively from {url}")

            result = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_type": "web_recursive",
                    "url": doc.metadata.get("source", "")
                }
                for doc in documents
            ]

            # Log URLs
            for i, doc in enumerate(result):
                source_url = doc.get("url", "unknown")
                logger.info(f"Recursive URL {i+1}: {source_url}")

            return result
        except Exception as e:
            logger.error(f"Error loading recursively from URL {url}: {e}")
            return []

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Split documents into smaller chunks for processing.

        Args:
            documents: List of document dictionaries

        Returns:
            List of chunked document dictionaries
        """
        if not documents:
            logger.info("No documents to chunk")
            return []

        logger.info(f"Chunking {len(documents)} documents")

        chunked_docs = []

        for doc in documents:
            # Convert to LangChain Document format for splitting
            lc_doc = Document(
                page_content=doc["content"],
                metadata=doc["metadata"]
            )

            # Split the document
            chunks = self.text_splitter.split_documents([lc_doc])

            # Convert back to our dictionary format
            for chunk in chunks:
                chunked_docs.append({
                    "content": chunk.page_content,
                    "metadata": chunk.metadata,
                    "source_type": doc["source_type"],
                    "url": doc.get("url", ""),
                    "file_path": doc.get("file_path", "")
                })

        logger.info(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
        return chunked_docs
