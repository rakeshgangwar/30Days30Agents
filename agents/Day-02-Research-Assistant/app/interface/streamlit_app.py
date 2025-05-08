"""Streamlit interface for the Research Assistant."""

import os
import time
import streamlit as st
from typing import Dict, Any

import sys
import logging
from pathlib import Path

# Add the app directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from core.agent import ResearchAssistant
from core.config import validate_config, OPENAI_API_KEY, EXA_API_KEY, GOOGLE_GEMINI_API_KEY


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def init_session_state():
    """Initialize session state variables."""
    if "research_assistant" not in st.session_state:
        try:
            validate_config()
            st.session_state.research_assistant = ResearchAssistant()
            st.session_state.api_configured = True
        except ValueError as e:
            st.session_state.api_error = str(e)
            st.session_state.api_configured = False

    if "research_history" not in st.session_state:
        st.session_state.research_history = []

    if "current_research" not in st.session_state:
        st.session_state.current_research = None

    if "research_in_progress" not in st.session_state:
        st.session_state.research_in_progress = False


def display_api_config():
    """Display API configuration form."""
    st.header("API Configuration")

    with st.form("api_config_form"):
        openai_key = st.text_input(
            "OpenAI API Key",
            value=os.environ.get("OPENAI_API_KEY", ""),
            type="password"
        )

        exa_key = st.text_input(
            "Exa Search API Key",
            value=os.environ.get("EXA_API_KEY", ""),
            type="password"
        )

        gemini_key = st.text_input(
            "Google Gemini API Key (Optional)",
            value=os.environ.get("GOOGLE_GEMINI_API_KEY", ""),
            type="password"
        )

        submitted = st.form_submit_button("Save Configuration")

        if submitted:
            # Set environment variables
            os.environ["OPENAI_API_KEY"] = openai_key
            os.environ["EXA_API_KEY"] = exa_key

            if gemini_key:
                os.environ["GOOGLE_GEMINI_API_KEY"] = gemini_key

            try:
                validate_config()
                st.session_state.research_assistant = ResearchAssistant()
                st.session_state.api_configured = True
                st.session_state.api_error = None
                st.success("API configuration saved successfully!")
            except ValueError as e:
                st.session_state.api_error = str(e)
                st.session_state.api_configured = False
                st.error(f"API configuration error: {e}")


def display_research_form():
    """Display the research query input form."""
    st.header("Research Assistant")

    with st.form("research_form"):
        query = st.text_area("Enter your research query:", height=100)

        research_depth = st.selectbox(
            "Research Depth:",
            options=["Light", "Medium", "Deep"],
            index=1
        )

        submitted = st.form_submit_button("Start Research")

        if submitted and query:
            st.session_state.research_in_progress = True
            st.session_state.current_research = {
                "query": query,
                "depth": research_depth,
                "start_time": time.time()
            }


def conduct_research():
    """Conduct research based on the current query."""
    if not st.session_state.current_research:
        return

    query = st.session_state.current_research["query"]
    research_depth = st.session_state.current_research["depth"]

    try:
        with st.spinner(f"Researching: {query} (Depth: {research_depth})"):
            # Conduct the research with the specified depth
            research_result = st.session_state.research_assistant.research(
                query=query,
                max_iterations=20,
                return_intermediate_steps=True,
                research_depth=research_depth
            )

            # Calculate duration
            duration = time.time() - st.session_state.current_research["start_time"]
            research_result["metadata"]["duration_seconds"] = duration

            # Add to history
            st.session_state.research_history.append(research_result)

            # Clear current research
            st.session_state.current_research = None
            st.session_state.research_in_progress = False

            # Rerun to update UI
            st.rerun()

    except Exception as e:
        st.error(f"Research error: {str(e)}")
        logger.error(f"Research error: {str(e)}", exc_info=True)
        st.session_state.research_in_progress = False
        st.session_state.current_research = None


def display_research_results():
    """Display research results."""
    if not st.session_state.research_history:
        st.info("No research results yet. Enter a query to get started.")
        return

    # Get the most recent research
    research = st.session_state.research_history[-1]

    st.header(f"Research: {research['query']}")

    # Display metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sources", research["metadata"].get("source_count", 0))
    with col2:
        duration = research["metadata"].get("duration_seconds", 0)
        st.metric("Research Time", f"{duration:.1f}s")
    with col3:
        errors = research["metadata"].get("error_count", 0)
        st.metric("Errors", errors)

    # Display report
    if "report" in research and "report_text" in research["report"]:
        st.markdown(research["report"]["report_text"])

        # Check if the report already contains a Sources section
        report_has_sources_section = "## Sources" in research["report"]["report_text"]

        # Only display sources separately if not already in the report
        if not report_has_sources_section:
            st.subheader("Sources")
            for idx, source in enumerate(research.get("sources", []), 1):
                st.markdown(f"{idx}. [{source['title']}]({source['url']})")
    else:
        st.warning("No report was generated.")

        # If no report, still show sources
        st.subheader("Sources")
        for idx, source in enumerate(research.get("sources", []), 1):
            st.markdown(f"{idx}. [{source['title']}]({source['url']})")

    # Display any errors
    if errors > 0 and "intermediate_steps" in research:
        with st.expander("Errors"):
            for error in research["intermediate_steps"].get("errors", []):
                st.error(f"Step: {error.get('step', 'unknown')}, Error: {error.get('error', 'unknown')}")


def display_research_history():
    """Display research history."""
    if not st.session_state.research_history:
        return

    st.header("Research History")

    for idx, research in enumerate(reversed(st.session_state.research_history)):
        with st.expander(f"Research {len(st.session_state.research_history) - idx}: {research['query']}"):
            # Display metadata
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Sources", research["metadata"].get("source_count", 0))
            with col2:
                duration = research["metadata"].get("duration_seconds", 0)
                st.metric("Research Time", f"{duration:.1f}s")

            # Display key findings
            if "report" in research and "key_findings" in research["report"]:
                st.subheader("Key Findings")
                for finding in research["report"]["key_findings"]:
                    st.markdown(f"• {finding}")

            # Check if we need to display sources separately
            display_sources = True
            if "report" in research and "report_text" in research["report"]:
                # Only display sources separately if not already in the report
                if "## Sources" in research["report"]["report_text"]:
                    display_sources = False

            # Display sources if needed
            if display_sources:
                st.subheader("Sources")
                for idx, source in enumerate(research.get("sources", []), 1):
                    st.markdown(f"{idx}. [{source['title']}]({source['url']})")


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Research Assistant",
        page_icon="🔍",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
        }
        .stProgress > div > div {
            background-color: #4CAF50;
        }
        .report-container {
            border-left: 1px solid #ddd;
            padding-left: 20px;
            height: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.title("Research Assistant")
        st.markdown("---")

        # API Configuration
        if not st.session_state.api_configured:
            st.warning("API Keys not configured or invalid.")

            if "api_error" in st.session_state and st.session_state.api_error:
                st.error(st.session_state.api_error)

            display_api_config()
        else:
            st.success("API Keys configured")

            if st.button("Update API Keys"):
                display_api_config()

        st.markdown("---")

        # About
        st.markdown("""
            ### About

            This Research Assistant helps you conduct comprehensive web research on any topic.

            It:
            - Searches the web for relevant information
            - Extracts key content from web pages
            - Synthesizes information from multiple sources
            - Generates a comprehensive research report with citations

            Enter your research query to get started!
        """)

    # Main content
    if not st.session_state.api_configured:
        st.header("Welcome to Research Assistant!")
        st.info("Please configure your API keys in the sidebar to get started.")
        return

    # Check if we have research results to display
    has_results = len(st.session_state.research_history) > 0

    # Layout changes based on whether we have results
    if has_results:
        # Side-by-side layout when results are available
        input_col, report_col = st.columns([1, 1])

        with input_col:
            # Display research form in left column
            if not st.session_state.research_in_progress:
                display_research_form()

        with report_col:
            # Add a container class for styling
            st.markdown('<div class="report-container"></div>', unsafe_allow_html=True)
            # Display results in right column
            display_research_results()
    else:
        # Centered layout when no results yet
        # Display research form centered
        if not st.session_state.research_in_progress:
            display_research_form()

    # Conduct research if in progress
    if st.session_state.research_in_progress and st.session_state.current_research:
        conduct_research()

    # Display history below everything
    if len(st.session_state.research_history) > 1:
        st.markdown("---")
        display_research_history()


if __name__ == "__main__":
    main()