"""Tests for the knowledge processing components."""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from components.knowledge_processing import ResearchRepository, InformationSynthesizer, SourceEvaluator, CitationFormatter


class TestResearchRepository(unittest.TestCase):
    """Tests for the ResearchRepository class."""

    def setUp(self):
        """Set up test cases."""
        # Create a temporary directory for the repository
        self.temp_dir = tempfile.mkdtemp()

        # Mock the embedding model
        self.mock_embedding_model = MagicMock()

        # Create the repository instance
        self.repository = ResearchRepository(
            embedding_model=self.mock_embedding_model,
            persist_directory=self.temp_dir
        )

        # Sample document and source data
        self.test_document = "This is a test document about artificial intelligence."
        self.test_source = {
            "url": "https://example.com/ai",
            "title": "Introduction to AI",
            "accessed_at": datetime.now().isoformat()
        }

    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir)

    def test_add_document(self):
        """Test adding a document to the repository."""
        # Set up vector store mock
        mock_vector_store = MagicMock()
        self.repository.vector_store = mock_vector_store

        # Add a document
        doc_id = self.repository.add_document(self.test_document, self.test_source)

        # Verify the document was added to the documents list
        self.assertEqual(len(self.repository.documents), 1)
        self.assertEqual(self.repository.documents[0]["content"], self.test_document)

        # Verify the source was added to the sources list
        self.assertEqual(len(self.repository.sources), 1)
        self.assertEqual(self.repository.sources[0]["url"], self.test_source["url"])
        self.assertEqual(self.repository.sources[0]["title"], self.test_source["title"])

        # Verify the vector store was updated
        mock_vector_store.add_texts.assert_called_once()
        args, kwargs = mock_vector_store.add_texts.call_args
        self.assertEqual(args[0], [self.test_document])
        self.assertEqual(kwargs["metadatas"][0]["url"], self.test_source["url"])
        self.assertEqual(kwargs["metadatas"][0]["title"], self.test_source["title"])

        # Verify the returned document ID
        self.assertEqual(doc_id, 0)

    def test_query_with_vector_store(self):
        """Test querying the repository with a vector store."""
        # Set up vector store mock
        mock_vector_store = MagicMock()
        self.repository.vector_store = mock_vector_store

        # Add a test document and source
        self.repository.add_document(self.test_document, self.test_source)

        # Configure the mock vector store to return a sample result
        mock_doc = MagicMock()
        mock_doc.page_content = "Relevant AI content"
        mock_doc.metadata = {
            "source_id": 0,
            "url": self.test_source["url"],
            "title": self.test_source["title"]
        }
        mock_vector_store.similarity_search.return_value = [mock_doc]

        # Query the repository
        results = self.repository.query("What is AI?", top_k=1)

        # Verify the vector store was queried
        mock_vector_store.similarity_search.assert_called_once_with("What is AI?", k=1)

        # Verify the query results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "Relevant AI content")
        self.assertEqual(results[0]["url"], self.test_source["url"])
        self.assertEqual(results[0]["title"], self.test_source["title"])

    def test_query_without_vector_store(self):
        """Test querying the repository without a vector store."""
        # Ensure no vector store is available
        self.repository.vector_store = None

        # Add test documents
        self.repository.add_document("Document 1 about AI", {
            "url": "https://example.com/ai1",
            "title": "AI Introduction",
        })
        self.repository.add_document("Document 2 about Machine Learning", {
            "url": "https://example.com/ml",
            "title": "ML Introduction",
        })

        # Query the repository
        results = self.repository.query("Any query", top_k=2)

        # Verify fallback logic returns the most recent documents
        self.assertEqual(len(results), 2)
        self.assertIn("Machine Learning", results[1]["content"])
        self.assertIn("AI Introduction", results[0]["source"]["title"])

    def test_get_document_by_id(self):
        """Test getting a document by ID."""
        # Add two documents
        self.repository.add_document("Document 1", {"url": "url1", "title": "Title 1"})
        self.repository.add_document("Document 2", {"url": "url2", "title": "Title 2"})

        # Get document by ID
        doc = self.repository.get_document_by_id(1)

        # Verify the retrieved document
        self.assertEqual(doc["content"], "Document 2")
        self.assertEqual(doc["source_id"], 1)

    def test_get_all_sources(self):
        """Test getting all sources in the repository."""
        # Add two documents with different sources
        self.repository.add_document("Document 1", {"url": "url1", "title": "Title 1"})
        self.repository.add_document("Document 2", {"url": "url2", "title": "Title 2"})

        # Get all sources
        sources = self.repository.get_all_sources()

        # Verify the sources
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0]["url"], "url1")
        self.assertEqual(sources[1]["title"], "Title 2")


class TestInformationSynthesizer(unittest.TestCase):
    """Tests for the InformationSynthesizer class."""

    def setUp(self):
        """Set up test cases."""
        self.mock_llm = MagicMock()
        self.mock_llm.invoke.return_value = """
        ## Summary
        This is a summary of the synthesized information.

        ## Key Points
        * Key point 1
        * Key point 2
        * Key point 3

        ## Areas of Consensus
        There is consensus on these topics.

        ## Conflicting Information
        Some sources disagree on these points.

        ## Information Gaps
        More research is needed in these areas.
        """

        self.synthesizer = InformationSynthesizer(llm=self.mock_llm)

        # Sample extracted contents
        self.extracted_contents = [
            {
                "url": "https://example.com/1",
                "title": "Source 1",
                "extracted_text": "Content from source 1 about the topic."
            },
            {
                "url": "https://example.com/2",
                "title": "Source 2",
                "extracted_text": "Content from source 2 providing different perspective."
            }
        ]

        # Sample query and analysis
        self.query = "What are the latest advancements in AI?"
        self.query_analysis = {
            "topics": ["AI", "Technology"],
            "entities": ["Machine Learning", "Deep Learning"],
            "query_type": "exploratory"
        }

    def test_synthesize(self):
        """Test synthesizing information from multiple sources."""
        result = self.synthesizer.synthesize(
            self.extracted_contents,
            self.query,
            self.query_analysis
        )

        # Verify the LLM was called with the correct prompt
        self.mock_llm.invoke.assert_called_once()
        args, _ = self.mock_llm.invoke.call_args
        prompt = args[0]

        # Verify the prompt contains all necessary elements
        self.assertIn(self.query, prompt)
        self.assertIn("Source 1", prompt)
        self.assertIn("Source 2", prompt)
        self.assertIn("Content from source 1", prompt)
        self.assertIn("Content from source 2", prompt)

        # Verify the result structure
        self.assertEqual(result["raw_synthesis"], self.mock_llm.invoke.return_value)
        self.assertEqual(result["query"], self.query)
        self.assertEqual(result["source_count"], 2)
        self.assertIn("sections", result)

    def test_parse_markdown_sections(self):
        """Test parsing Markdown sections from synthesis text."""
        markdown_text = """
        ## Summary
        This is a summary.

        ## Key Points
        * Point 1
        * Point 2

        ## Conclusion
        This is the conclusion.
        """

        sections = self.synthesizer._parse_markdown_sections(markdown_text)

        # Verify the parsed sections
        self.assertEqual(len(sections), 3)
        self.assertIn("Summary", sections)
        self.assertIn("Key Points", sections)
        self.assertIn("Conclusion", sections)
        self.assertEqual(sections["Summary"], "This is a summary.")
        self.assertIn("Point 1", sections["Key Points"])
        self.assertEqual(sections["Conclusion"], "This is the conclusion.")

    def test_synthesize_with_empty_content(self):
        """Test synthesizing with empty extracted content."""
        result = self.synthesizer.synthesize([], self.query, self.query_analysis)

        # The LLM should still be called, but with empty content
        self.mock_llm.invoke.assert_called_once()

        # The result should still have the expected structure
        self.assertIn("raw_synthesis", result)
        self.assertEqual(result["source_count"], 0)
        self.assertEqual(result["query"], self.query)


class TestSourceEvaluator(unittest.TestCase):
    """Tests for the SourceEvaluator class."""

    def setUp(self):
        """Set up test cases."""
        self.mock_llm = MagicMock()
        self.mock_llm.invoke.return_value = """
        Factor 1: 4/5 - This is from a reputable website.
        Factor 2: 3/5 - It appears to be edited but not peer-reviewed.
        Factor 3: 4/5 - Content seems objective with minimal bias.
        Factor 4: 2/5 - This is secondary research.
        Factor 5: 5/5 - Information appears to be very recent.

        Overall credibility score: 4
        """

        self.evaluator = SourceEvaluator(llm=self.mock_llm)

        # Sample sources
        self.test_sources = [
            {
                "url": "https://example.com/article",
                "title": "Test Article",
                "extracted_text": "This is a test article about artificial intelligence and its applications."
            },
            {
                "url": "https://blog.example.com/opinion",
                "title": "Opinion Piece",
                "extracted_text": "I believe artificial intelligence will dramatically change society in the next decade."
            }
        ]

    def test_evaluate_sources(self):
        """Test evaluating multiple sources."""
        results = self.evaluator.evaluate_sources(self.test_sources)

        # Verify the LLM was called for each source
        self.assertEqual(self.mock_llm.invoke.call_count, 2)

        # Verify the evaluation results structure
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["source"], self.test_sources[0])
        self.assertEqual(results[0]["evaluation"], self.mock_llm.invoke.return_value)
        self.assertEqual(results[0]["credibility_score"], 4)

    def test_extract_score(self):
        """Test extracting credibility score from evaluation text."""
        # Test with standard format
        text1 = "Overall credibility score: 4"
        score1 = self.evaluator._extract_score(text1)
        self.assertEqual(score1, 4)

        # Test with different format
        text2 = "The overall score for credibility is 3."
        score2 = self.evaluator._extract_score(text2)
        self.assertEqual(score2, 3)

        # Test with missing score
        text3 = "This source has various quality attributes."
        score3 = self.evaluator._extract_score(text3)
        self.assertEqual(score3, 3)  # Should return default score


class TestCitationFormatter(unittest.TestCase):
    """Tests for the CitationFormatter class."""

    def setUp(self):
        """Set up test cases."""
        # Create formatter instances for different styles
        self.apa_formatter = CitationFormatter(citation_style="apa")
        self.mla_formatter = CitationFormatter(citation_style="mla")
        self.simple_formatter = CitationFormatter(citation_style="simple")

        # Sample sources
        self.test_date = datetime(2023, 5, 15, 10, 30, 0)
        self.test_sources = [
            {
                "id": 0,
                "url": "https://example.com/article1",
                "title": "Example Article 1",
                "accessed_at": self.test_date.isoformat()
            },
            {
                "id": 1,
                "url": "https://example.com/article2",
                "title": "Example Article 2",
                "accessed_at": self.test_date.isoformat()
            }
        ]

    def test_format_citations_apa(self):
        """Test formatting citations in APA style."""
        citations = self.apa_formatter.format_citations(self.test_sources)

        # Verify the formatted citations
        self.assertEqual(len(citations), 2)
        self.assertEqual(citations[0]["source_id"], 0)
        self.assertEqual(citations[0]["url"], "https://example.com/article1")

        # Check APA formatting
        self.assertIn("Retrieved 2023, May 15", citations[0]["formatted_citation"])
        self.assertIn("Example Article 1", citations[0]["formatted_citation"])

    def test_format_citations_mla(self):
        """Test formatting citations in MLA style."""
        citations = self.mla_formatter.format_citations(self.test_sources)

        # Verify the formatted citations
        self.assertEqual(len(citations), 2)

        # Check MLA formatting
        self.assertIn("Accessed 15 May. 2023", citations[0]["formatted_citation"])
        self.assertIn('"Example Article 1."', citations[0]["formatted_citation"])

    def test_format_citations_simple(self):
        """Test formatting citations in simple style."""
        citations = self.simple_formatter.format_citations(self.test_sources)

        # Verify the formatted citations
        self.assertEqual(len(citations), 2)

        # Check simple formatting
        self.assertIn("(Accessed: 2023-05-15)", citations[0]["formatted_citation"])
        self.assertIn("Example Article 1", citations[0]["formatted_citation"])

    def test_iso_date_parsing(self):
        """Test handling of ISO format date strings."""
        # Create a source with ISO format date string
        source_with_iso_date = {
            "id": 0,
            "url": "https://example.com/article",
            "title": "Example Article",
            "accessed_at": "2023-05-15T10:30:00"
        }

        # Format the citation
        citation = self.apa_formatter.format_citations([source_with_iso_date])[0]

        # Verify the date was parsed correctly
        self.assertIn("Retrieved 2023, May 15", citation["formatted_citation"])


if __name__ == "__main__":
    unittest.main()