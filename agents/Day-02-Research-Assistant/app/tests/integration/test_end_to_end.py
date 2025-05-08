"""End-to-end integration tests for the Research Assistant."""

import os
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Import mock components
from tests.integration.test_search_to_synthesis import MockLLM, MockSearchTool, MockBrowsingTool


class TestEndToEndResearch(unittest.TestCase):
    """End-to-end tests for the Research Assistant."""
    
    def setUp(self):
        """Set up the end-to-end test environment."""
        # Define mock responses for the LLM
        self.mock_llm = MockLLM({
            "Analyze the following research query": """
            Main topics: Artificial Intelligence, Machine Learning
            Key entities: Neural Networks, Deep Learning, AI Applications
            Query type: Exploratory
            Domain: Computer Science, Technology
            Time constraints: Recent developments (last 5 years)
            """,
            
            "Formulate 3-5 effective search queries": """
            1. Latest advancements in artificial intelligence and machine learning
            2. Recent breakthroughs in neural networks and deep learning
            3. Practical applications of AI in industry 2020-2025
            4. State-of-the-art AI research and future directions
            """,
            
            "Develop a research strategy": """
            1. Number of sources to consult: At least 5 sources
            2. Types of sources to prioritize: Academic papers, research reports, tech blogs, industry publications
            3. Criteria for determining enough information: Coverage of all key topics, representation of different perspectives
            4. Approach for conflicting information: Present multiple viewpoints with credibility assessment
            5. Sequence of search operations: General overview, technical details, practical applications, future directions
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
            """,
            
            "Generate a comprehensive research summary": """
            # Research Summary: Recent Advancements in AI
            
            ## Key Findings
            * Deep learning architectures have evolved significantly [1, 3]
            * Large language models can now perform complex reasoning tasks [2]
            * AI applications in healthcare show promising diagnostic capabilities [4]
            
            ## Detailed Analysis
            Artificial intelligence has undergone remarkable development in the past five years,
            with particular advances in neural network architectures and training methods.
            
            The emergence of transformer-based models has revolutionized natural language processing,
            while computer vision continues to benefit from convolutional neural networks.
            
            ## Sources
            [1] "Recent Advances in Deep Learning" - example.com/advances
            [2] "Large Language Models: Capabilities and Limitations" - example.com/llm
            [3] "Neural Network Architectures" - example.com/nn
            [4] "AI in Healthcare" - example.com/health
            """
        })
    
    @patch('components.input_processing.QueryAnalyzer')
    @patch('components.input_processing.SearchQueryFormulator')
    @patch('components.research_workflow.ResearchStrategyPlanner')
    @patch('tools.search_tools.WebSearchTool')
    @patch('tools.browsing_tools.WebBrowsingTool')
    @patch('tools.browsing_tools.ContentExtractionTool')
    @patch('components.knowledge_processing.InformationSynthesizer')
    @patch('components.output_formatting.ResearchReportGenerator')
    def test_full_research_workflow(self, 
                                   mock_report_generator_class,
                                   mock_synthesizer_class,
                                   mock_extraction_tool_class,
                                   mock_browsing_tool_class,
                                   mock_search_tool_class,
                                   mock_strategy_planner_class,
                                   mock_formulator_class,
                                   mock_analyzer_class):
        """Test the full research workflow from query to report."""
        # Set up mock instances with our mock LLM
        mock_analyzer = mock_analyzer_class.return_value
        mock_formulator = mock_formulator_class.return_value
        mock_strategy_planner = mock_strategy_planner_class.return_value
        mock_search_tool = mock_search_tool_class.return_value
        mock_browsing_tool = mock_browsing_tool_class.return_value
        mock_extraction_tool = mock_extraction_tool_class.return_value
        mock_synthesizer = mock_synthesizer_class.return_value
        mock_report_generator = mock_report_generator_class.return_value
        
        # Configure mock behaviors
        mock_analyzer.analyze.return_value = {
            "topics": ["Artificial Intelligence", "Machine Learning"],
            "entities": ["Neural Networks", "Deep Learning"],
            "query_type": "exploratory",
            "domain": "technology"
        }
        
        mock_formulator.formulate_queries.return_value = [
            "latest advancements in AI",
            "recent breakthroughs in machine learning"
        ]
        
        mock_strategy_planner.create_strategy.return_value = {
            "min_sources": 3,
            "source_priorities": ["academic", "tech_blogs"],
            "completion_criteria": {"min_sources_gathered": 3},
            "conflict_resolution": "present_all_perspectives",
            "search_sequence": ["general", "specific"]
        }
        
        mock_search_tool.search.return_value = [
            {"title": "AI Article 1", "url": "https://example.com/1", "snippet": "About AI"},
            {"title": "AI Article 2", "url": "https://example.com/2", "snippet": "About ML"}
        ]
        
        mock_browsing_tool.fetch_content.return_value = {
            "title": "AI Page",
            "content": "<html><body>Content about AI</body></html>",
            "url": "https://example.com/1"
        }
        
        mock_extraction_tool.extract_relevant_content.return_value = "Relevant AI content extracted"
        
        mock_synthesizer.synthesize.return_value = {
            "raw_synthesis": "AI synthesis",
            "sections": {"summary": "AI summary"},
            "source_count": 3,
            "query": "test query"
        }
        
        mock_report_generator.generate.return_value = {
            "report_text": "Final research report on AI",
            "key_findings": ["Finding 1", "Finding 2"],
            "sources": [{"title": "Source 1", "url": "https://example.com/1"}]
        }
        
        # Now import and create the full workflow - do this here to use the mocked dependencies
        from components.research_workflow import ResearchWorkflow
        
        # Create a mock evaluator
        mock_evaluator = MagicMock()
        mock_evaluator.check_information_sufficiency.return_value = True
        
        # Create the research workflow
        workflow = ResearchWorkflow(
            query_analyzer=mock_analyzer,
            search_query_formulator=mock_formulator,
            strategy_planner=mock_strategy_planner,
            search_tool=mock_search_tool,
            browsing_tool=mock_browsing_tool,
            extraction_tool=mock_extraction_tool,
            synthesizer=mock_synthesizer,
            report_generator=mock_report_generator,
            evaluator=mock_evaluator
        )
        
        # Run the full workflow
        test_query = "What are the recent advancements in artificial intelligence?"
        result = workflow.run_workflow(test_query)
        
        # Verify the key components were called
        mock_analyzer.analyze.assert_called_once()
        mock_formulator.formulate_queries.assert_called_once()
        mock_strategy_planner.create_strategy.assert_called_once()
        mock_search_tool.search.assert_called()
        mock_browsing_tool.fetch_content.assert_called()
        mock_extraction_tool.extract_relevant_content.assert_called()
        mock_synthesizer.synthesize.assert_called_once()
        mock_report_generator.generate.assert_called_once()
        
        # Verify the result contains the expected data
        self.assertEqual(result["query"], test_query)
        self.assertIn("report", result)
        self.assertIn("sources", result)
        self.assertIn("research_time", result)
    
    @unittest.skip("This test requires actual API keys and makes real API calls")
    def test_with_real_apis(self):
        """
        Test the Research Assistant with real API calls.
        
        This test is skipped by default as it requires real API keys
        and will make actual API calls. Enable it for manual testing.
        """
        # Check if environment variables for API keys are set
        if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("SERPER_API_KEY"):
            self.skipTest("API keys not set in environment variables")
        
        # Import the actual ResearchAssistant
        from core.agent import ResearchAssistant
        
        # Create the assistant with real APIs
        assistant = ResearchAssistant()
        
        # Run a simple research query with minimal sources to keep test duration reasonable
        result = assistant.research(
            query="What are the benefits of meditation?",
            max_sources=2,
            max_iterations=1
        )
        
        # Verify we got a meaningful result
        self.assertEqual(result["query"], "What are the benefits of meditation?")
        self.assertIn("report", result)
        self.assertIn("sources", result)
        self.assertGreater(len(result["sources"]), 0)


class TestIntegrationWithTestQuestions(unittest.TestCase):
    """Integration tests using the test questions from the documentation."""
    
    def setUp(self):
        """Set up test environment with mocked components."""
        # Create a mock Research Assistant
        self.mock_assistant = MagicMock()
        self.mock_assistant.research.return_value = {
            "query": "Test query",
            "report": {
                "report_text": "Test report content",
                "key_findings": ["Finding 1", "Finding 2"]
            },
            "sources": [
                {"title": "Source 1", "url": "https://example.com/1"},
                {"title": "Source 2", "url": "https://example.com/2"}
            ],
            "metadata": {
                "source_count": 2,
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "error_count": 0
            }
        }
    
    def test_general_knowledge_question(self):
        """Test using a general knowledge question from the test questions document."""
        # From test_questions.md, general knowledge section
        question = "What are the main differences between renewable and non-renewable energy sources?"
        
        # Run research with the mock assistant
        result = self.mock_assistant.research(query=question)
        
        # Verify the research call was made with the right question
        self.mock_assistant.research.assert_called_once_with(query=question)
        
        # Verify result structure
        self.assertIn("report", result)
        self.assertIn("sources", result)
    
    def test_complex_multipart_question(self):
        """Test using a complex multi-part question from the test questions document."""
        # From test_questions.md, complex multi-part questions section
        question = "Research the development of mRNA vaccines, their effectiveness against COVID-19, and potential future applications."
        
        # Run research with the mock assistant
        result = self.mock_assistant.research(query=question)
        
        # Verify the research call was made with the right question
        self.mock_assistant.research.assert_called_once_with(query=question)
        
        # Verify result structure
        self.assertIn("report", result)
        self.assertIn("sources", result)
    
    def test_comparative_analysis_question(self):
        """Test using a comparative analysis question from the test questions document."""
        # From test_questions.md, comparative analysis section
        question = "Compare the healthcare systems of the United States, United Kingdom, and Canada."
        
        # Run research with the mock assistant
        result = self.mock_assistant.research(query=question)
        
        # Verify the research call was made with the right question
        self.mock_assistant.research.assert_called_once_with(query=question)
        
        # Verify result structure
        self.assertIn("report", result)
        self.assertIn("sources", result)


if __name__ == "__main__":
    unittest.main()