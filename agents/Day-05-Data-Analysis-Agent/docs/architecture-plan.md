# Day 5: Data Analysis Agent - Architecture Plan

## 1. Project Goal
Develop a Data Analysis Agent capable of loading, analyzing, and visualizing data from various sources including CSV files, other structured file formats, and databases (e.g., PostgreSQL, MySQL, MongoDB), based on natural language queries, with potential for robust and unique features.

## 2. Core Components & Workflow

```mermaid
graph TD
    UserInput[User Enters NL Query & Chooses Data Source] --> REACT[React Frontend];
    REACT -- API Request --> API[FastAPI Backend];
    
    subgraph "Backend Processing"
        API -- CSV File --> FU[File Processor];
        API -- DB Connection Details & Query --> DBC[Database Connector];
        
        FU -- Processed Data --> CAL{"Core Agent Logic (LangChain + LLM)"};
        DBC -- Fetched Data --> CAL;
        
        CAL -- Data Operations / SQL Generation --> DH["Data Handling (Pandas/Polars/SQLAlchemy/PyMongo)"];
        DH -- Data for Analysis/Viz --> CAL;
        CAL -- Visualization Commands --> VE["Visualization Engine (Plotly/Matplotlib)"];
        VE -- Plot Data/Config --> CAL;
        CAL -- Results/Plot Data --> API;
    end
    
    API -- JSON Response --> REACT;
    REACT -- Display Results --> UI[User Interface Components];
    
    subgraph "Frontend (React)"
        REACT
        UI
        UserInput
    end
```

## 3. Detailed Initial Plan (Baseline from Spec, expanded for DB & File Loaders)

1.  **Environment Setup & Basic Structure:**
    *   **Backend Structure:** Directory structure for `agents/Day-05-Data-Analysis-Agent/backend`.
    *   **Frontend Structure:** Directory structure for `agents/Day-05-Data-Analysis-Agent/frontend`.
    *   `requirements.txt` and `pyproject.toml` for backend dependencies.
    *   `package.json` with React dependencies for frontend.
    *   Basic `.gitignore`, `.env.example`, `README.md`.
2.  **Input Processing Module (Backend):**
    *   **2.1. API Endpoints:** FastAPI endpoints for file uploads and database connections.
    *   **2.2. File Upload & Database Connector:**
        *   **File Upload:** API endpoint for accepting file uploads.
        *   **Database Connector:** API endpoint for DB connection parameters, establishing connections, and executing queries.
    *   **2.3. Supported Data Formats & Loaders (LangChain Integrations):**
        *   The agent will aim to support a variety of structured data sources through LangChain document loaders. The initial focus will be on the most common formats, with others as stretch goals or future enhancements.
        *   **Core File Formats:**
            *   CSV: [`CSVLoader`](https://python.langchain.com/docs/integrations/document_loaders/csv)
            *   Microsoft Excel (.xls, .xlsx): [`UnstructuredExcelLoader`](https://python.langchain.com/docs/integrations/document_loaders/microsoft_excel) (via `unstructured` library)
            *   JSON: [`JSONLoader`](https://python.langchain.com/docs/integrations/document_loaders/json) (potentially with `jq_schema`)
            *   TSV: [`TSVLoader`](https://python.langchain.com/docs/integrations/document_loaders/tsv) (or generic text/CSV loader configured for tabs)
        *   **DataFrame Loaders:**
            *   Pandas DataFrame: [`PandasDataFrameLoader`](https://python.langchain.com/docs/integrations/document_loaders/pandas_dataframe)
            *   Polars DataFrame: [`PolarsDataFrameLoader`](https://python.langchain.com/docs/integrations/document_loaders/polars_dataframe)
        *   **Cloud/Hybrid Spreadsheet/Database Services:**
            *   Google Drive (for Google Sheets, if feasible for tabular data): [`GoogleDriveLoader`](https://python.langchain.com/docs/integrations/document_loaders/google_drive)
            *   Airtable: [`AirtableLoader`](https://python.langchain.com/docs/integrations/document_loaders/airtable)
        *   **Database Systems (via SQLAlchemy for SQL, specific drivers for NoSQL):**
            *   PostgreSQL, MySQL, SQLite (via SQLAlchemy)
            *   MongoDB (via PyMongo)
            *   *For a comprehensive list of potential database loaders, see Section 5.*
    *   **2.4. Data Loading:** Load data from the file upload or database query result into a Pandas/Polars DataFrame.
    *   **2.5. Natural Language Query API:** Endpoint to process natural language queries.
3.  **Core Agent Logic - LLM Integration (Backend):**
    *   LangChain Agent/Chain setup.
        *   For CSV/DataFrame/File-based data: Pandas DataFrame Agent or custom chain.
        *   For SQL DBs: LangChain SQLDatabaseChain or SQL Agent.
    *   LLM Prompting:
        *   For DataFrames: Generate Pandas/Polars code, visualization code, and interpret results.
        *   For SQL DBs: Generate SQL queries based on NL, then potentially Pandas/visualization code on results.
        *   For NoSQL (MongoDB): Generate PyMongo code to fetch data, then treat as DataFrame.
    *   Secure code/query execution.
    *   Error handling for connections, queries, and code execution.
4.  **Data Handling & Analysis (Backend):**
    *   Driven by LLM-generated code/queries.
    *   Operations on DataFrames (inspection, stats, filtering, correlation).
    *   Direct SQL querying for SQL DBs.
5.  **Visualization Engine (Backend):**
    *   LLM generates code for various chart types.
    *   For backend-generated visualizations: Capture and send plot data/configuration.
    *   For Plotly: Send Plotly figure JSON for client-side rendering.
6.  **API Response Formatting (Backend):**
    *   Format DataFrames as JSON.
    *   Format visualizations as Plotly figure JSON or base64-encoded images.
    *   Structure and send full response with results, visualizations, and supplementary info.
7.  **User Interface (Frontend - React):**
    *   React components for data source selection, file upload, and DB connection input.
    *   Components for displaying query results, tables, and visualizations.
    *   Responsive design with Ant Design components.
8.  **Testing & Refinement:**
    *   Test API endpoints with various file types and database connections.
    *   Test React component integration.
    *   End-to-end testing of full user flows.

## 4. Potential Unique Features (Brainstormed)
*   **Multi-Source Connectivity:** Seamlessly switch between and analyze data from various files (CSV, Excel, JSON, TSV) and databases (PostgreSQL, MySQL, MongoDB, etc.).
*   **Flexible LLM Access:** Utilize OpenRouter for a wide range of hosted models and support local LLMs for privacy/offline use.
*   **Proactive Insights & Anomaly Detection:** Agent suggests analyses or highlights anomalies.
*   **Conversational Refinement of Visualizations:** Users iteratively modify plots via natural language.
*   **Code Transparency & Export:** Display and allow export of generated code/SQL, data, and plots.
*   **Automated Data Cleaning Suggestions:** Agent identifies and suggests fixes for data quality issues.
*   **Interactive Visualizations:** Using libraries like Plotly for dynamic charts.
*   **Simplified Statistical Explanations:** LLM explains statistical results in plain language.

## 5. Proposed Robust Tech Stack (Broad Horizon)

*   **Core Language & Backend Framework:**
    *   **Python**
    *   **FastAPI** (Required for API endpoints)
*   **LLM Orchestration & Agent Logic:**
    *   **LangChain** (including SQLDatabaseChain/Agent and various Document Loaders)
    *   **LLM Access Layer:**
        *   **OpenRouter:** For access to a wide variety of hosted LLMs (e.g., GPT models, Claude models, Llama models, etc.) via a unified API. (LangChain Integration: `OpenRouterChat`)
        *   **Local LLMs:** For privacy, offline use, and cost-effectiveness.
            *   Serving: Ollama, llama.cpp server, Hugging Face TGI, vLLM, etc.
            *   LangChain Integration: `OllamaChat`, `ChatMLflowAIGateway`, or custom wrappers for local endpoints.
    *   **LLM Choice (Examples):**
        *   Via OpenRouter: GPT-4/GPT-4o, Claude 3 Opus/Sonnet/Haiku, Llama 3, Mistral Large/Medium, etc.
        *   Local: Llama 3, Mistral, Phi-3, Gemma, etc. (depending on local hardware capabilities).
*   **Data Connectors, Loaders & Processing Engine:**
    *   **File Loaders (LangChain):**
        *   [`CSVLoader`](https://python.langchain.com/docs/integrations/document_loaders/csv)
        *   [`UnstructuredExcelLoader`](https://python.langchain.com/docs/integrations/document_loaders/microsoft_excel) (requires `unstructured`, `python-magic`, `openpyxl`, `xlrd`)
        *   [`JSONLoader`](https://python.langchain.com/docs/integrations/document_loaders/json) (optional `jq`)
        *   [`TSVLoader`](https://python.langchain.com/docs/integrations/document_loaders/tsv)
        *   [`PandasDataFrameLoader`](https://python.langchain.com/docs/integrations/document_loaders/pandas_dataframe)
        *   [`PolarsDataFrameLoader`](https://python.langchain.com/docs/integrations/document_loaders/polars_dataframe)
        *   [`GoogleDriveLoader`](https://python.langchain.com/docs/integrations/document_loaders/google_drive) (requires `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`) - *Note: LangChain docs state "Google Docs only", feasibility for Sheets to be confirmed.*
        *   [`AirtableLoader`](https://python.langchain.com/docs/integrations/document_loaders/airtable) (requires `pyairtable`)
    *   **Database Connectivity & Loaders (LangChain & direct drivers):**
        *   SQLAlchemy (ORM for SQL DBs): `https://python.langchain.com/docs/integrations/tools/sql_database`
            *   PostgreSQL (driver: `psycopg2-binary`)
            *   MySQL (driver: `mysql-connector-python`)
            *   SQLite (built-in)
            *   Microsoft SQL Server (driver: `pyodbc`)
            *   Oracle (driver: `cx_Oracle`)
            *   *Many others supported by SQLAlchemy*
        *   MongoDB: [`MongoLoader`](https://python.langchain.com/docs/integrations/document_loaders/mongodb) (requires `pymongo`)
        *   DuckDB: [`DuckDBLoader`](https://python.langchain.com/docs/integrations/document_loaders/duckdb) (requires `duckdb_engine` for SQLAlchemy or `duckdb` direct)
        *   Google BigQuery: [`BigQueryLoader`](https://python.langchain.com/docs/integrations/document_loaders/google_bigquery) (requires `google-cloud-bigquery`)
        *   Snowflake: [`SnowflakeLoader`](https://python.langchain.com/docs/integrations/document_loaders/snowflake) (requires `snowflake-connector-python` or `snowflake-sqlalchemy`)
        *   *Selected other relevant database loaders from LangChain documentation (refer to links for specific dependencies):*
            *   Alibaba Cloud MaxCompute: [`MaxComputeLoader`](https://python.langchain.com/docs/integrations/document_loaders/alibaba_cloud_maxcompute)
            *   Amazon Athena: [`AthenaLoader`](https://python.langchain.com/docs/integrations/document_loaders/athena)
            *   AstraDB (Cassandra): [`AstraDBLoader`](https://python.langchain.com/docs/integrations/document_loaders/astradb)
            *   Cassandra (direct): [`CassandraLoader`](https://python.langchain.com/docs/integrations/document_loaders/cassandra)
            *   Couchbase: [`CouchbaseLoader`](https://python.langchain.com/docs/integrations/document_loaders/couchbase)
            *   Fauna: [`FaunaLoader`](https://python.langchain.com/docs/integrations/document_loaders/fauna)
            *   Google Cloud SQL variants (covered by SQLAlchemy drivers)
            *   Google Firestore: [`FirestoreLoader`](https://python.langchain.com/docs/integrations/document_loaders/google_firestore)
            *   Google Spanner: [`SpannerLoader`](https://python.langchain.com/docs/integrations/document_loaders/google_spanner)
            *   Kinetica: [`KineticaLoader`](https://python.langchain.com/docs/integrations/document_loaders/kinetica)
            *   Oracle Autonomous Database: [`OracleAutonomousDatabaseLoader`](https://python.langchain.com/docs/integrations/document_loaders/oracleadb_loader)
            *   Rockset: [`RocksetLoader`](https://python.langchain.com/docs/integrations/document_loaders/rockset)
            *   SingleStore: [`SingleStoreLoader`](https://python.langchain.com/docs/integrations/document_loaders/singlestore)
            *   SurrealDB: [`SurrealDBLoader`](https://python.langchain.com/docs/integrations/document_loaders/surrealdb)
            *   TiDB: [`TiDBLoader`](https://python.langchain.com/docs/integrations/document_loaders/tidb)
    *   **Core Data Processing Libraries:**
        *   **Pandas** (Baseline for DataFrame operations)
        *   **Polars** (For performance with larger datasets)
        *   **NumPy & SciPy** (Advanced statistics)
*   **Visualization Engine:**
    *   **Plotly & Plotly Express** (Primary for interactivity)
    *   **Matplotlib & Seaborn** (For generating images on the backend if needed)
*   **Frontend/User Interface:**
    *   **React** (Frontend framework)
    *   **Ant Design** (UI component library for React)
    *   **Plotly.js** (For client-side rendering of interactive visualizations)
    *   **State Management:** React Context API or Zustand (lightweight state management)
*   **Database (Optional - Persistence/Caching for Agent itself):**
    *   **SQLite** (Simple local storage)

## 6. Focused Tech Stack for Day 5 Implementation

To balance ambition with the 30-day challenge timeline, the core focus for Day 5 will be:

*   **Primary Data Source Goals for Day 5:**
    *   Robust **CSV file** analysis capabilities.
    *   Integration with at least **one SQL Database type** (e.g., SQLite for ease of setup, or PostgreSQL if a local instance is available) using LangChain's SQL tools (e.g., `SQLDatabaseChain` or SQL Agent).
*   **Backend Framework:** FastAPI.
*   **LLM Orchestration:** LangChain.
*   **LLM Access & Choice:**
    *   **Primary:** Utilize **OpenRouter** via LangChain integration (`OpenRouterChat`) to access a suitable hosted model (e.g., Claude 3 Haiku, Llama 3 8B, or a free-tier model for initial development).
    *   **Secondary/Stretch Goal:** Implement support for at least one **Local LLM** via Ollama (`OllamaChat` in LangChain) if time permits, allowing for offline/private use.
*   **Data Processing:**
    *   For CSV: Pandas (leveraging `read_csv`).
    *   For SQL Databases: SQLAlchemy (as used by LangChain's SQL tools).
*   **Visualization:** 
    *   Backend: Generate Plotly JSON configurations from data analysis.
    *   Frontend: Render interactive Plotly visualizations using the configurations.
*   **Frontend:** 
    *   **React** with **Ant Design** components.
    *   State management: React Context API (for simplicity).
    *   Visualization rendering: Plotly.js.
*   **Core Languages:** 
    *   Backend: Python
    *   Frontend: JavaScript/TypeScript
*   **Further Stretch Goals for Day 5 / Subsequent Iterations:**
    *   Support for Microsoft Excel files.
    *   Broader file format support (JSON, TSV).
    *   Support for other SQL database types or NoSQL databases (e.g., MongoDB).
    *   More advanced interactive visualizations.
    *   UI elements to select between OpenRouter models or local LLMs.

This revised focus ensures that core connectivity to both flat files (CSV) and relational databases (SQL) is achieved on Day 5, with an improved user experience through the React frontend and interactive visualizations.