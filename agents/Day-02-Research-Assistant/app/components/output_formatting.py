"""Output formatting components for the Research Assistant."""

from typing import Dict, List, Any


class ResearchSummaryGenerator:
    """
    Creates structured research reports from synthesized information.

    This component takes the synthesized research and formats it into
    a clear, well-organized report for the user.
    """

    def __init__(self, llm):
        """
        Initialize the ResearchSummaryGenerator.

        Args:
            llm: Language model for summary generation
        """
        self.llm = llm

    def generate_summary(
        self, synthesized_info: Dict[str, Any], query: str, sources: List[Dict[str, Any]],
        research_depth: str = "medium"
    ) -> str:
        """
        Generate a research summary report.

        Args:
            synthesized_info: Synthesized research information
            query: Original research query
            sources: List of research sources
            research_depth: Depth of research (light, medium, deep)

        Returns:
            Formatted research summary
        """
        # Format sources for citation
        formatted_sources = []
        for idx, source in enumerate(sources, 1):
            formatted_sources.append(f"[{idx}] {source['title']}. {source['url']}")

        sources_text = "\n".join(formatted_sources)

        # Extract the synthesized content
        synthesis_text = synthesized_info.get("raw_synthesis", "")
        if not synthesis_text and synthesized_info.get("sections"):
            # Reconstruct from sections
            sections = synthesized_info["sections"]
            synthesis_parts = []
            for title, content in sections.items():
                synthesis_parts.append(f"## {title}\n{content}")
            synthesis_text = "\n\n".join(synthesis_parts)

        # Adjust report detail based on research depth
        detail_level = "moderate"
        word_count_guidance = "800-1200"

        if research_depth == "light":
            detail_level = "concise"
            word_count_guidance = "400-600"
        elif research_depth == "deep":
            detail_level = "comprehensive"
            word_count_guidance = "1500-2500"

        prompt = f"""
        RESEARCH QUERY: {query}

        SYNTHESIZED INFORMATION:
        {synthesis_text}

        SOURCES USED:
        {sources_text}

        Based on the above research, generate a {detail_level} research summary that:
        1. Directly addresses the original query
        2. Is well-organized with sections and bullet points for clarity
        3. Cites sources using the [n] notation throughout the text
        4. Highlights the most important findings
        5. Provides a balanced view if conflicting information exists

        The report should be approximately {word_count_guidance} words in length, appropriate for a {research_depth} research depth.

        FORMAT:

        # Research Summary: [Query]

        ## Key Findings
        * Finding 1 [n]
        * Finding 2 [n, m]
        ...

        ## Detailed Analysis
        [Analysis with appropriate sections and detail level for {research_depth} research]

        ## Additional Information
        [Any relevant context or caveats]

        ## Sources
        [Sources formatted as already provided]
        """

        # Log which model is being used for report generation
        import logging
        logger = logging.getLogger(__name__)
        model_info = getattr(self.llm, 'model_name', getattr(self.llm, 'model', 'unknown'))
        logger.info(f"Using model {model_info} for research report generation")

        summary_response = self.llm.invoke(prompt)

        # Convert AIMessage to string if needed
        if hasattr(summary_response, 'content'):
            return summary_response.content
        else:
            return str(summary_response)

    def format_for_display(
        self, report: str, query: str, research_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format the research report for display in a user interface.

        Args:
            report: Research report text
            query: Original research query
            research_metadata: Metadata about the research process

        Returns:
            Dictionary with formatted display content
        """
        # Split the report into sections
        sections = self._parse_markdown_sections(report)

        # Add metadata
        formatted_display = {
            "title": f"Research: {query}",
            "query": query,
            "sections": sections,
            "metadata": {
                "sources_used": research_metadata.get("source_count", 0),
                "research_time_seconds": research_metadata.get("research_time", 0)
            }
        }

        return formatted_display

    def _parse_markdown_sections(self, markdown_text: str) -> Dict[str, str]:
        """
        Parse a Markdown string into sections.

        Args:
            markdown_text: Markdown text to parse

        Returns:
            Dictionary with section names as keys and content as values
        """
        sections = {}
        current_section = "title"
        current_content = []

        for line in markdown_text.split('\n'):
            if line.startswith('# '):
                # Save the previous section if it exists
                if current_content and current_section != "title":
                    sections[current_section] = '\n'.join(current_content).strip()
                    current_content = []

                # Start with the title
                current_section = "title"
                current_content = [line.replace('# ', '')]
            elif line.startswith('## '):
                # Save the previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                    current_content = []

                # Start a new section
                current_section = line.replace('## ', '').strip()
            else:
                current_content.append(line)

        # Save the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections


class KeyFindingsExtractor:
    """
    Extracts the most important findings from research.

    This component distills research into key points for quick comprehension.
    """

    def __init__(self, llm):
        """
        Initialize the KeyFindingsExtractor.

        Args:
            llm: Language model for findings extraction
        """
        self.llm = llm

    def extract_key_findings(
        self, synthesized_info: Dict[str, Any], query: str, max_findings: int = 5
    ) -> List[str]:
        """
        Extract key findings from synthesized research.

        Args:
            synthesized_info: Synthesized research information
            query: Original research query
            max_findings: Maximum number of findings to extract

        Returns:
            List of key findings
        """
        # Extract synthesis text
        synthesis_text = synthesized_info.get("raw_synthesis", "")
        if not synthesis_text and synthesized_info.get("sections"):
            # Reconstruct from sections
            sections = synthesized_info["sections"]
            synthesis_parts = []
            for title, content in sections.items():
                synthesis_parts.append(f"## {title}\n{content}")
            synthesis_text = "\n\n".join(synthesis_parts)

        prompt = f"""
        Based on the following synthesized research for the query: "{query}"

        {synthesis_text}

        Extract the {max_findings} most important findings or key points.
        Format each finding as a single, concise bullet point (1-2 sentences).
        Focus on the most significant or surprising information that directly addresses the query.
        """

        response = self.llm.invoke(prompt)

        # Convert AIMessage to string if needed
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)

        # Parse the bullet points
        findings = []
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('*') or line.startswith('-') or (line.startswith(str(len(findings) + 1)) and '.' in line):
                # Remove bullet point markers and numbers
                clean_line = line.lstrip('*-0123456789. ')
                if clean_line:
                    findings.append(clean_line)
                    if len(findings) >= max_findings:
                        break

        return findings

    def generate_summary_bullets(self, findings: List[str]) -> str:
        """
        Format key findings as a bullet list.

        Args:
            findings: List of key findings

        Returns:
            Formatted bullet list
        """
        return "\n".join([f"• {finding}" for finding in findings])


class ResearchReportGenerator:
    """
    Generates the final research report combining all components.

    This component coordinates the various output components to
    create a cohesive final report.
    """

    def __init__(
        self, summary_generator, findings_extractor, citation_formatter
    ):
        """
        Initialize the ResearchReportGenerator.

        Args:
            summary_generator: Component for generating summaries
            findings_extractor: Component for extracting key findings
            citation_formatter: Component for formatting citations
        """
        self.summary_generator = summary_generator
        self.findings_extractor = findings_extractor
        self.citation_formatter = citation_formatter

    def generate(
        self,
        synthesized_info: Dict[str, Any],
        extracted_content: List[Dict[str, Any]],
        query: str,
        research_depth: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate a complete research report.

        Args:
            synthesized_info: Synthesized research information
            extracted_content: Extracted content from sources
            query: Original research query
            research_depth: Depth of research (light, medium, deep)

        Returns:
            Dictionary with the complete report and metadata
        """
        # Format citations
        formatted_citations = self.citation_formatter.format_citations(extracted_content)

        # Generate the report narrative with appropriate detail level based on research depth
        report_narrative = self.summary_generator.generate_summary(
            synthesized_info, query, extracted_content, research_depth=research_depth
        )

        # Extract key findings - adjust number based on research depth
        max_findings = 3  # Default for light research
        if research_depth == "medium":
            max_findings = 5
        elif research_depth == "deep":
            max_findings = 8

        key_findings = self.findings_extractor.extract_key_findings(
            synthesized_info, query, max_findings=max_findings
        )

        # Calculate some metrics
        word_count = len(report_narrative.split())
        source_count = len(extracted_content)

        # Create the complete report
        report = {
            "query": query,
            "report_text": report_narrative,
            "key_findings": key_findings,
            "sources": [
                {
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "citation": next(
                        (c["formatted_citation"] for c in formatted_citations if c["url"] == source.get("url", "")),
                        f"{source.get('title', '')}. {source.get('url', '')}"
                    )
                }
                for source in extracted_content
            ],
            "metadata": {
                "word_count": word_count,
                "source_count": source_count,
                "research_depth": research_depth,
                "generated_at": self._get_timestamp()
            }
        }

        return report

    def _get_timestamp(self) -> str:
        """
        Get the current timestamp in ISO format.

        Returns:
            ISO formatted timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()