"""Input processing components for the Research Assistant."""

from typing import Dict, List, Any


class QueryAnalyzer:
    """
    Analyzes research queries to identify key topics, entities, and characteristics.
    
    This component is responsible for breaking down a user's research query into
    structured elements that help guide the research process.
    """

    def __init__(self, llm):
        """
        Initialize the QueryAnalyzer.
        
        Args:
            llm: Language model for analysis
        """
        self.llm = llm
        self.prompt_template = """
        Analyze the following research query:
        {query}

        Identify:
        1. Main topic(s)
        2. Key entities
        3. Query type (factual, comparative, exploratory, etc.)
        4. Domain-specific requirements
        5. Time constraints or recency requirements
        """

    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Analyze a research query.
        
        Args:
            query: The user's research query
            
        Returns:
            Dictionary containing analysis results
        """
        response = self.llm.invoke(self.prompt_template.format(query=query))
        
        # In a real implementation, we would parse the LLM response into a structured format
        # For the boilerplate, we'll simulate the extraction with a simple parsing function
        return self._parse_analysis_response(response, query)
    
    def _parse_analysis_response(self, response: str, original_query: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured format.
        
        Args:
            response: Raw LLM response
            original_query: The original query for fallback
            
        Returns:
            Dictionary with structured analysis
        """
        # This is a simplified parsing function
        # In production, you would implement a more robust parser
        
        lines = response.strip().split('\n')
        analysis = {
            "original_query": original_query,
            "topics": [],
            "entities": [],
            "query_type": "exploratory",  # Default
            "domain": "general",  # Default
            "time_constraints": None
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "topic" in line.lower() and ":" in line:
                current_section = "topics"
                topics = line.split(":", 1)[1].strip()
                analysis["topics"] = [t.strip() for t in topics.split(",")]
            elif "entit" in line.lower() and ":" in line:
                current_section = "entities"
                entities = line.split(":", 1)[1].strip()
                analysis["entities"] = [e.strip() for e in entities.split(",")]
            elif "type" in line.lower() and ":" in line:
                query_type = line.split(":", 1)[1].strip().lower()
                if any(t in query_type for t in ["fact", "compar", "explor", "opinion"]):
                    analysis["query_type"] = query_type
            elif "domain" in line.lower() and ":" in line:
                domain = line.split(":", 1)[1].strip().lower()
                analysis["domain"] = domain
            elif "time" in line.lower() and ":" in line:
                analysis["time_constraints"] = line.split(":", 1)[1].strip()
        
        return analysis


class SearchQueryFormulator:
    """
    Transforms a research query and its analysis into effective search queries.
    
    This component creates multiple search variations to ensure comprehensive coverage
    of the research topic.
    """

    def __init__(self, llm):
        """
        Initialize the SearchQueryFormulator.
        
        Args:
            llm: Language model for query formulation
        """
        self.llm = llm
        self.prompt_template = """
        Based on the research query analysis:
        {analysis}

        Formulate 3-5 effective search queries that will:
        1. Cover different aspects of the topic
        2. Target high-quality sources
        3. Use domain-specific terminology where appropriate
        4. Address different time periods if temporal information is needed
        
        Format your response as a numbered list of search queries, one per line.
        """

    def formulate_queries(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Formulate multiple search queries based on query analysis.
        
        Args:
            analysis: The analysis of the research query
            
        Returns:
            List of search queries
        """
        # Convert analysis dict to a readable string format
        analysis_str = "\n".join([f"{k}: {v}" for k, v in analysis.items()])
        
        response = self.llm.invoke(self.prompt_template.format(analysis=analysis_str))
        
        # Parse the response to extract search queries
        return self._extract_queries(response)
    
    def _extract_queries(self, response: str) -> List[str]:
        """
        Extract search queries from the LLM response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            List of search queries
        """
        queries = []
        lines = response.strip().split('\n')
        
        for line in lines:
            # Looking for lines with patterns like "1. query" or "1) query"
            if line.strip() and (line[0].isdigit() or line[1].isdigit()):
                # Strip the numbering and any leading symbols
                query_text = line.split(".", 1)[-1].split(")", 1)[-1].strip()
                if query_text:
                    queries.append(query_text)
        
        # Ensure we have at least one query
        if not queries:
            # Fallback: Extract anything that looks like a query
            for line in lines:
                if "?" in line or any(keyword in line.lower() for keyword in ["how", "what", "why", "when", "where", "who"]):
                    queries.append(line.strip())
        
        return queries