# Data Analysis Agent

A powerful agent that helps users analyze and visualize data from various sources (e.g., CSV files, SQL databases) using natural language queries.

## Features

- Data loading from CSV files
- SQL database connections (SQLite, PostgreSQL)
- Natural language querying of data
- Data visualization (bar charts, line plots, scatter plots, histograms)
- Descriptive statistics calculation
- Basic data cleaning and preprocessing

## Setup Instructions

### Prerequisites

- Python 3.8+
- uv (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/30Days30Agents.git
   cd 30Days30Agents/agents/Day-05-Data-Analysis-Agent
   ```

2. Create and activate a virtual environment:
   ```bash
   cd app
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv add streamlit langchain langchain_community pandas matplotlib seaborn python-dotenv sqlalchemy psycopg2-binary
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your OpenRouter API key.

### Running the Application

Start the Streamlit app:
```bash
streamlit run main.py
```

The application will be available at http://localhost:8501

## Usage Examples

### CSV Data Analysis

1. Upload a CSV file using the file uploader
2. Ask questions about your data:
   - "Show me the first 5 rows of the data"
   - "What are the mean and median values for the 'Sales' column?"
   - "Show me a histogram of the 'Age' column"
   - "Is there a correlation between 'Marketing Spend' and 'Revenue'?"
   - "Generate a bar chart showing sales per region"
   - "Filter the data for customers in 'California'"

### SQL Database Analysis

1. Connect to a SQL database (SQLite or PostgreSQL)
2. Ask questions about your data:
   - "List all tables in the database"
   - "Show me the schema of the 'customers' table"
   - "How many orders were placed in the last month?"
   - "What is the average order value by product category?"
   - "Show me the top 10 customers by revenue"

## Project Structure

- `main.py`: Main Streamlit application
- `utils.py`: Utility functions for data loading, processing, and visualization
- `.env.example`: Example environment variables file

## License

MIT
