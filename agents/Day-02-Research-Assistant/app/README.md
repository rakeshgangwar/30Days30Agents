# Research Assistant

A comprehensive research assistant that conducts web research on user-specified topics, synthesizes information from multiple sources, and provides summarized findings with citations.

## Features

- Iterative research process to ensure thorough coverage
- Web search and content extraction
- Information synthesis and source evaluation
- Research report generation with citations
- Interactive Streamlit interface

## Architecture

This project implements a hybrid approach with three frameworks:
- **LangGraph**: For orchestrating the research workflow and managing state transitions
- **LlamaIndex**: For document loading, parsing, indexing, and retrieval
- **LangChain**: For specialized tools and utilities that enhance research capabilities

## Installation

### Prerequisites

- Python 3.12 or higher
- API keys for OpenAI and Exa Search (or SerpAPI as an alternative)

### Setup

1. Clone the repository and navigate to the app directory

2. Create a `.env` file with your API keys:
```bash
# Add your API keys to .env file
OPENAI_API_KEY=your_openai_api_key_here
EXA_API_KEY=your_exa_api_key_here
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here  # Optional
```

3. Install the dependencies:
```bash
# Using uv (recommended)
uv pip install -e .

# Using pip
pip install -e .
```

## Model Configuration

The Research Assistant now supports using different models for different phases of the research process:

### Analysis Phase Models

These models are used for:
- Query analysis
- Search query formulation
- Research strategy planning
- Content extraction
- Source evaluation

Default models:
- OpenAI: `gpt-4o-mini`
- Google Gemini: `gemini-2.0-flash`

### Synthesis Phase Models

These models are used for:
- Information synthesis
- Report generation
- Key findings extraction

Default models:
- OpenAI: `gpt-4o`
- Google Gemini: `gemini-2.5-pro`

## Usage

The Research Assistant can be used in three ways:

### 1. Interactive Web Interface (Recommended)

Launch the Streamlit web interface:

```bash
# Using the main entry point
python main.py ui

# Or directly with streamlit
streamlit run interface/streamlit_app.py
```

### 2. Command Line Interface

Use the CLI to conduct research from the command line:

```bash
# Basic usage
python main.py research "What is quantum computing?"

# Save results to a file
python main.py research "History of artificial intelligence" --output research_results.md

# Get JSON output
python main.py research "Climate change impacts" --format json

# Use specific models for different phases
python main.py research "Quantum computing advances" --analysis-model gpt-4o-mini --synthesis-model gpt-4o
```

### 3. Programmatic API

Use the Research Assistant in your own Python code:

```python
from core.agent import ResearchAssistant

# Initialize the assistant with default models
assistant = ResearchAssistant()

# Or specify a model for all phases
assistant = ResearchAssistant(model_name="gpt-4o")

# Or use different models for different phases
# First initialize with the analysis model
assistant = ResearchAssistant(model_name="gpt-4o-mini")

# Then override the synthesis LLM
from langchain_openai import ChatOpenAI
assistant.synthesis_llm = ChatOpenAI(
    api_key="your_openai_api_key",
    model_name="gpt-4o",
    temperature=0.1
)

# Reinitialize components that use the synthesis LLM
from components.knowledge_processing import InformationSynthesizer
from components.output_formatting import ResearchSummaryGenerator, KeyFindingsExtractor

assistant.synthesizer = InformationSynthesizer(assistant.synthesis_llm)
assistant.summary_generator = ResearchSummaryGenerator(assistant.synthesis_llm)
assistant.findings_extractor = KeyFindingsExtractor(assistant.synthesis_llm)

# Conduct research
results = assistant.research("Your research query here")

# Access the report
print(results["report"]["report_text"])
```

## Project Structure

- `core/`: Core agent implementation and LangGraph workflow
- `components/`: Modular components for different aspects of the research process
- `tools/`: Implementations of various research tools
- `interface/`: User interface implementations

## Troubleshooting

If you encounter any issues:

1. Ensure all required API keys are correctly set in the `.env` file
2. Check that you have installed all dependencies
3. Look for error messages in the terminal output or log file
4. For issues with web browsing, make sure Playwright is correctly installed:

```bash
# Install Playwright and its dependencies
playwright install
```

## License

This project is made available as part of the 30 Days 30 Agents challenge.