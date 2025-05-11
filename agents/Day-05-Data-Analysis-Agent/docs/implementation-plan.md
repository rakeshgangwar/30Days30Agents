# Day 5: Data Analysis Agent - Detailed Implementation Plan

## 1. Objective for Day 5
*   Implement core CSV file analysis capabilities.
*   Implement integration with at least one SQL Database type (e.g., SQLite or PostgreSQL).
*   Utilize LangChain with OpenRouter for LLM access.
*   Develop a basic Streamlit UI for interaction.

## 2. Core Technologies (Recap from Architecture Plan)
*   **Frontend:** Streamlit
*   **LLM Orchestration:** LangChain
*   **LLM Access:** OpenRouter (Primary), Local LLM via Ollama (Secondary/Stretch)
*   **Data Processing (CSV):** Pandas
*   **Data Processing (SQL):** SQLAlchemy (via LangChain SQL tools)
*   **Visualization:** Matplotlib/Seaborn (Primary), Plotly (Stretch)
*   **Core Language:** Python

## 3. Environment Setup
*   **Project Directory:** `agents/Day-05-Data-Analysis-Agent/app/`
*   **Virtual Environment:** Create and activate a Python virtual environment.
*   **`pyproject.toml` Dependencies:**
    *   `streamlit`
    *   `langchain`
    *   `langchain_community` (for OpenRouterChat, SQLDatabase, OllamaChat, CSVLoader, etc.)
    *   `pandas`
    *   `matplotlib`
    *   `seaborn`
    *   `python-dotenv`
    *   `sqlalchemy`
    *   `psycopg2-binary` (if targeting PostgreSQL, otherwise not strictly needed for SQLite)
    *   `openpyxl` (for potential Excel stretch goal)
    *   `plotly` (for stretch goal)
    *   `ollama` (if directly using the ollama python client, or ensure Ollama service is running for LangChain integration)
*   **`.env` File:** Create a `.env` file for API keys:
    *   `OPENROUTER_API_KEY="your_openrouter_key"`
    *   (Potentially `DATABASE_URL="your_db_connection_string"` if not using SQLite file path and not constructing it in code)

## 4. Implementation Steps (Phased Approach)

### Phase 1: Basic Setup & CSV Analysis (Total Est: ~5 hours)

*   **Task 1.1: Project Initialization (Est: 0.5 hr)**
    *   1.1.1. Create agent directory: `agents/Day-05-Data-Analysis-Agent/app/`.
    *   1.1.2. Initialize `pyproject.toml` (e.g., using `poetry init` or manually).
    *   1.1.3. Create `main.py`, `utils.py` (if anticipated), `.env.example`.
    *   1.1.4. Add initial dependencies to `pyproject.toml` and install (e.g., `streamlit`, `python-dotenv`).
*   **Task 1.2: Streamlit UI - Core Layout (Est: 1 hr)**
    *   1.2.1. `main.py`: Set up `st.set_page_config`, page title, header.
    *   1.2.2. Create main sections/columns for UI (e.g., sidebar for controls, main area for output).
    *   1.2.3. Add `st.file_uploader` for CSV files, restrict to `.csv` type.
    *   1.2.4. Add `st.text_area` for natural language queries.
    *   1.2.5. Add a "Submit" button for the query.
    *   1.2.6. Create placeholders in the UI for displaying:
        *   Uploaded data preview.
        *   LLM text responses.
        *   DataFrames (tables).
        *   Plots.
*   **Task 1.3: CSV Data Handling (Est: 0.5 hr)**
    *   1.3.1. Implement a function to load the uploaded CSV file into a Pandas DataFrame upon file upload.
    *   1.3.2. Display the head of the DataFrame (`st.dataframe(df.head())`) and basic info (`st.text(df.info())`) immediately after upload.
    *   1.3.3. Store the DataFrame in Streamlit's session state (`st.session_state`) for persistence across interactions.
*   **Task 1.4: LangChain & OpenRouter LLM Integration (Est: 0.5 hr)**
    *   1.4.1. Add `langchain`, `langchain_community` to `pyproject.toml` and install.
    *   1.4.2. Load `OPENROUTER_API_KEY` from `.env` using `dotenv`.
    *   1.4.3. Initialize `OpenRouterChat` model from `langchain_community.chat_models` with a chosen model (e.g., a free tier or small model like "mistralai/mistral-7b-instruct").
    *   1.4.4. Create a simple test function to send a prompt to the LLM and print/display the response in Streamlit to verify connectivity.
*   **Task 1.5: CSV Analysis Agent/Chain (Est: 1.5 hrs)**
    *   1.5.1. Decide on approach: `create_pandas_dataframe_agent` or a custom chain using LLM to generate Pandas code. Start with the agent for speed.
    *   1.5.2. If using agent: Instantiate `create_pandas_dataframe_agent` with the loaded DataFrame and the initialized LLM.
    *   1.5.3. Implement logic to take the user's NL query from `st.text_area` and pass it to the agent/chain upon "Submit" button click.
    *   1.5.4. Test basic descriptive queries: "Summarize this data", "What are the columns?", "Show the first 3 rows".
    *   1.5.5. Test basic aggregation queries: "What is the average of column X?", "What is the total sum of column Y?".
    *   1.5.6. Test basic filtering: "Show rows where column X is greater than 10".
*   **Task 1.6: Displaying Agent's Output (Est: 0.5 hr)**
    *   1.6.1. Capture the agent's textual response and display it using `st.markdown()` or `st.write()`.
    *   1.6.2. If the agent's response implies a DataFrame (e.g., from filtering), attempt to parse/extract it or ensure the agent returns it in a usable format to display with `st.dataframe()`. (This might be tricky with the default agent output, may need prompt engineering or output parsing).
*   **Task 1.7: CSV Data Visualization (Matplotlib/Seaborn via LLM) (Est: 0.5 hr)**
    *   1.7.1. Enhance prompting for the agent/chain (or create a separate tool/chain) to understand visualization requests (e.g., "Plot a histogram of column X", "Create a bar chart for column Y").
    *   1.7.2. The LLM should generate Python code using Matplotlib/Seaborn to create the plot.
    *   1.7.3. Implement a secure way to execute this generated plotting code (e.g., `exec()`, carefully considering security implications, or using a safer sandbox if possible. For a quick prototype, `exec` might be used with caution).
    *   1.7.4. Capture the Matplotlib figure and display it in Streamlit using `st.pyplot(fig)`.

### Phase 2: SQL Database Integration (Total Est: ~4.5 hours)

*   **Task 2.1: Streamlit UI for Database Connection (Est: 0.75 hr)**
    *   2.1.1. Add `st.selectbox` for choosing DB type (e.g., "SQLite", "PostgreSQL").
    *   2.1.2. Conditionally display input fields based on DB type:
        *   SQLite: `st.text_input` for database file path (e.g., `my_data.db`).
        *   PostgreSQL: `st.text_input` for Host, Port, User, Password, Database Name.
    *   2.1.3. Add a "Connect to Database" button.
*   **Task 2.2: Database Connection Logic (SQLAlchemy) (Est: 0.75 hr)**
    *   2.2.1. Add `sqlalchemy` and relevant DB driver (e.g., `psycopg2-binary`) to `pyproject.toml` and install.
    *   2.2.2. Implement a function that takes connection parameters and creates a SQLAlchemy engine string.
    *   2.2.3. On "Connect to Database" click, attempt to create the engine using `create_engine`.
    *   2.2.4. Store the engine or `SQLDatabase` utility in `st.session_state`.
    *   2.2.5. Provide feedback to the user (success/failure of connection).
*   **Task 2.3: LangChain SQL Integration (Est: 1 hr)**
    *   2.3.1. Initialize `SQLDatabase` from `langchain_community.utilities` using the created SQLAlchemy engine.
    *   2.3.2. Instantiate `create_sql_agent` (from `langchain_community.agent_toolkits`) or `SQLDatabaseChain` (from `langchain.chains`) using the `SQLDatabase` utility and the initialized LLM.
*   **Task 2.4: Handling NL Queries for SQL (Est: 1 hr)**
    *   2.4.1. If a DB connection is active, route the user's NL query from `st.text_area` to the SQL agent/chain.
    *   2.4.2. Test basic SQL queries via NL: "List all tables.", "Describe the 'users' table.", "Show me all data from the 'products' table where price > 100."
    *   2.4.3. Display the generated SQL (optional, for transparency) and the textual result from the agent/chain using `st.markdown()` or `st.write()`.
*   **Task 2.5: SQL Data Visualization (Matplotlib/Seaborn via LLM) (Est: 1 hr)**
    *   2.5.1. Similar to Task 1.7, adapt the LLM prompting or create a specific tool/chain to generate Matplotlib/Seaborn plotting code based on the results of SQL queries.
    *   2.5.2. The process might involve: NL query -> SQL query -> SQL result -> (optional) Convert to Pandas DataFrame -> Generate Plotting Code -> Execute Plotting Code -> Display Plot.
    *   2.5.3. Display the plot in Streamlit using `st.pyplot(fig)`.

### Phase 3: Refinements & Stretch Goals (If time permits on Day 5) (Total Est: ~3-5 hours)

*   **Task 3.1: Robust Error Handling & User Feedback (Est: 1 hr)**
    *   3.1.1. Wrap file loading logic in `try-except` blocks, show `st.error()` for invalid files.
    *   3.1.2. Wrap DB connection logic in `try-except`, show `st.error()` for connection failures.
    *   3.1.3. Wrap agent/chain execution in `try-except`, show `st.warning()` or `st.error()` if the LLM or code execution fails, and display the error message if helpful.
    *   3.1.4. Add loading spinners (`st.spinner`) for long operations.
*   **Task 3.2: Plotly Integration (One Chart Type) (Est: 1-1.5 hrs)**
    *   3.2.1. Add `plotly` to `pyproject.toml` and install.
    *   3.2.2. Adapt LLM prompting to generate Plotly Express code for one chart type (e.g., a scatter plot).
    *   3.2.3. Execute the generated code.
    *   3.2.4. Display the interactive Plotly chart using `st.plotly_chart()`.
*   **Task 3.3: Local LLM Integration (Ollama - Basic) (Est: 1-1.5 hrs)**
    *   3.3.1. Ensure Ollama is installed and a model (e.g., `llama3:8b-instruct` or `mistral`) is pulled.
    *   3.3.2. Add `ollama` to `pyproject.toml` if using the direct client, or rely on LangChain's `OllamaChat`.
    *   3.3.3. Initialize `OllamaChat` from `langchain_community.chat_models`.
    *   3.3.4. Add a simple UI element (e.g., `st.checkbox` or `st.radio`) to allow the user to switch between OpenRouter and the local Ollama LLM.
    *   3.3.5. Re-initialize the LLM object for agents/chains based on user selection.
    *   3.3.6. Test basic functionality with the local LLM.
*   **Task 3.4: Code Organization & README Update (Est: 0.5 hr)**
    *   3.4.1. Refactor `main.py` into smaller functions or move parts to `utils.py` if it becomes too large.
    *   3.4.2. Add comments to clarify complex sections of code.
    *   3.4.3. Create/update a `README.md` within the `agents/Day-05-Data-Analysis-Agent/` directory with:
        *   Brief description of the agent.
        *   Setup instructions (virtual env, dependencies, `.env` file).
        *   How to run the Streamlit app.
        *   Example queries.

## 5. Key LangChain Components (Anticipated)
*   `CSVLoader` (from `langchain_community.document_loaders`)
*   `create_pandas_dataframe_agent` (from `langchain_community.agent_toolkits`)
*   `SQLDatabase` (from `langchain_community.utilities`)
*   `create_sql_agent` (from `langchain_community.agent_toolkits`) or `SQLDatabaseChain` (from `langchain.chains`)
*   `OpenRouterChat` (from `langchain_community.chat_models.openrouter`)
*   `OllamaChat` (from `langchain_community.chat_models.ollama`)
*   Prompt Templates (as needed for custom chains or agent refinements)

## 6. Testing Strategy
*   Create a sample CSV file (e.g., `sample_data.csv` with varied data types).
*   Create a sample SQLite database (e.g., `sample_db.sqlite`) with 2-3 tables and sample data.
*   If using PostgreSQL, set up a test database.
*   **CSV Tests:**
    *   File upload success/failure.
    *   Correct display of DataFrame head/info.
    *   NL queries for summarization, column listing, head/tail.
    *   NL queries for aggregations (mean, sum, count) on numeric columns.
    *   NL queries for filtering on various conditions (text, numeric, date if applicable).
    *   NL queries for simple Matplotlib/Seaborn plots (histogram, bar chart).
*   **SQL DB Tests:**
    *   Connection success/failure for SQLite (and PostgreSQL if implemented).
    *   NL queries for listing tables, describing table schemas.
    *   NL queries for `SELECT *` from tables.
    *   NL queries for `SELECT` with `WHERE` clauses.
    *   NL queries for basic aggregations (`COUNT`, `SUM`, `AVG`) using SQL.
    *   NL queries for simple Matplotlib/Seaborn plots based on SQL results.
*   **LLM Switching Tests (if local LLM implemented):**
    *   Verify UI switch works.
    *   Test a few CSV and SQL queries with the local LLM to check for comparable (though potentially different quality) results.
*   **Error Handling Tests:**
    *   Upload incorrect file type.
    *   Provide invalid DB credentials.
    *   Enter ambiguous or unanswerable queries.
*   **UI/UX Tests:**
    *   Clarity of instructions and feedback.
    *   Responsiveness of the application.