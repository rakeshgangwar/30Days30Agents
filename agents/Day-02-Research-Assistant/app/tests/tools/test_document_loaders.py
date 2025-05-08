"""Tests for the document loaders."""

import os
import pytest
from unittest.mock import patch, MagicMock

from tools.document_loaders import DocumentLoaderManager
from langchain_core.documents import Document


@pytest.fixture
def document_loader():
    """Create a document loader for testing."""
    return DocumentLoaderManager(cache_dir="./test_cache")


def test_document_loader_initialization(document_loader):
    """Test that the document loader initializes correctly."""
    assert document_loader.cache_dir == "./test_cache"
    assert document_loader.text_splitter is not None


@patch("tools.document_loaders.WebBaseLoader")
def test_load_from_web(mock_web_loader, document_loader):
    """Test loading content from a web URL."""
    # Setup mock
    mock_instance = MagicMock()
    mock_web_loader.return_value = mock_instance
    
    # Mock the load method to return a document
    mock_instance.load.return_value = [
        Document(
            page_content="Test web content",
            metadata={"source": "https://example.com", "title": "Test Page"}
        )
    ]
    
    # Call the method
    result = document_loader.load_from_web("https://example.com")
    
    # Verify the result
    assert len(result) == 1
    assert result[0]["content"] == "Test web content"
    assert result[0]["url"] == "https://example.com"
    assert result[0]["source_type"] == "web"


@patch("tools.document_loaders.ArxivLoader")
def test_load_from_arxiv(mock_arxiv_loader, document_loader):
    """Test loading content from Arxiv."""
    # Setup mock
    mock_instance = MagicMock()
    mock_arxiv_loader.return_value = mock_instance
    
    # Mock the load method to return a document
    mock_instance.load.return_value = [
        Document(
            page_content="Test arxiv content",
            metadata={
                "entry_id": "https://arxiv.org/abs/1234.5678",
                "title": "Test Arxiv Paper"
            }
        )
    ]
    
    # Call the method
    result = document_loader.load_from_arxiv("quantum computing")
    
    # Verify the result
    assert len(result) == 1
    assert result[0]["content"] == "Test arxiv content"
    assert result[0]["url"] == "https://arxiv.org/abs/1234.5678"
    assert result[0]["source_type"] == "arxiv"


@patch("tools.document_loaders.WikipediaLoader")
def test_load_from_wikipedia(mock_wiki_loader, document_loader):
    """Test loading content from Wikipedia."""
    # Setup mock
    mock_instance = MagicMock()
    mock_wiki_loader.return_value = mock_instance
    
    # Mock the load method to return a document
    mock_instance.load.return_value = [
        Document(
            page_content="Test wikipedia content",
            metadata={"source": "Wikipedia", "title": "Test Wiki Page"}
        )
    ]
    
    # Call the method
    result = document_loader.load_from_wikipedia("artificial intelligence")
    
    # Verify the result
    assert len(result) == 1
    assert result[0]["content"] == "Test wikipedia content"
    assert result[0]["source_type"] == "wikipedia"


def test_chunk_documents(document_loader):
    """Test chunking documents."""
    # Create test documents
    docs = [
        {
            "content": "This is a test document with enough content to be split into multiple chunks. " * 20,
            "metadata": {"source": "test"},
            "source_type": "test",
            "url": "https://example.com"
        }
    ]
    
    # Chunk the documents
    chunked_docs = document_loader.chunk_documents(docs)
    
    # Verify that chunking occurred
    assert len(chunked_docs) > 1
    assert all(len(doc["content"]) <= 1000 for doc in chunked_docs)
