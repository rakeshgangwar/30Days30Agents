# Data Analysis Agent

This Streamlit application allows users to analyze and visualize data from various sources (e.g., CSV files, SQL databases) using natural language queries.

## Project Structure

The application is organized into the following modules:

```
app/
├── __init__.py
├── main.py (entry point)
├── config/
│   ├── __init__.py
│   └── settings.py (environment variables and configuration)
├── core/
│   ├── __init__.py
│   ├── llm.py (LLM initialization and configuration)
│   └── agent.py (Agent creation and management)
├── data/
│   ├── __init__.py
│   ├── csv_handler.py (CSV file handling)
│   ├── sql_handler.py (SQL database handling)
│   └── visualization.py (Data visualization functions)
├── utils/
│   ├── __init__.py
│   └── helpers.py (General utility functions)
├── scripts/
│   ├── __init__.py
│   └── create_test_db.py (Database creation script)
└── ui/
    ├── __init__.py
    └── components.py (UI components for Streamlit)
```

## Setup

1. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Running the Application

Start the Streamlit application from the app directory:
```
cd agents/Day-05-Data-Analysis-Agent/app
streamlit run main.py
```

Or specify the full path:
```
streamlit run agents/Day-05-Data-Analysis-Agent/app/main.py
```

## Features

- Upload and analyze CSV files
- Connect to SQL databases
- Ask natural language questions about your data
- Visualize data with charts and graphs
- Get detailed information about your dataset

## Creating a Test Database

To create a test SQLite database with sample data:
```
cd agents/Day-05-Data-Analysis-Agent/app
python scripts/create_test_db.py
```

This will create a test_data.db file in the app directory with sample tables and data.