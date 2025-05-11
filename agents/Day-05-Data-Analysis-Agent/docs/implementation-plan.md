# Day 5: Data Analysis Agent - Detailed Implementation Plan

## 1. Objective for Day 5
*   Implement core CSV file analysis capabilities.
*   Implement integration with at least one SQL Database type (e.g., SQLite or PostgreSQL).
*   Utilize LangChain with OpenRouter for LLM access.
*   Develop a React frontend with Ant Design components.
*   Create a FastAPI backend to handle data processing and LLM interactions.

## 2. Core Technologies (Recap from Architecture Plan)
*   **Backend:** FastAPI
*   **Frontend:** React with Ant Design
*   **LLM Orchestration:** LangChain
*   **LLM Access:** OpenRouter (Primary), Local LLM via Ollama (Secondary/Stretch)
*   **Data Processing (CSV):** Pandas
*   **Data Processing (SQL):** SQLAlchemy (via LangChain SQL tools)
*   **Visualization:** Plotly (backend generates configurations, frontend renders)
*   **Core Languages:** Python (Backend), JavaScript/TypeScript (Frontend)

## 3. Environment Setup

### 3.1 Backend Environment
*   **Project Directory:** `agents/Day-05-Data-Analysis-Agent/backend/`
*   **Virtual Environment:** Create and activate a Python virtual environment.
*   **Dependencies (requirements.txt):**
    ```
    fastapi==0.104.1
    uvicorn==0.23.2
    python-multipart==0.0.6  # For file uploads
    langchain==0.0.325
    langchain-community==0.0.10
    pandas==2.1.1
    matplotlib==3.8.0  # If needed for fallback
    plotly==5.17.0
    python-dotenv==1.0.0
    sqlalchemy==2.0.22
    psycopg2-binary==2.9.9  # For PostgreSQL
    pydantic==2.4.2
    numpy==1.26.0
    cors==1.0.1  # For CORS handling
    openpyxl==3.1.2  # For Excel support (stretch goal)
    ```
*   **`.env` File:** Create a `.env` file for API keys:
    ```
    OPENROUTER_API_KEY="your_openrouter_key"
    DATABASE_URL="your_db_connection_string"  # Optional for non-SQLite configurations
    ```

### 3.2 Frontend Environment
*   **Project Directory:** `agents/Day-05-Data-Analysis-Agent/frontend/`
*   **React Setup:** Create React app structure.
*   **Dependencies (package.json):**
    ```json
    {
      "dependencies": {
        "antd": "^5.9.0",
        "axios": "^1.5.0",
        "plotly.js": "^2.26.0",
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "react-plotly.js": "^2.6.0"
      },
      "devDependencies": {
        "@types/react": "^18.2.21",
        "@types/react-dom": "^18.2.7",
        "typescript": "^5.2.2",
        "vite": "^4.4.9"
      }
    }
    ```

## 4. Implementation Steps (Phased Approach)

### Phase 1: Core Backend Setup (FastAPI) (Total Est: ~4 hours)

*   **Task 1.1: Project Initialization (Est: 0.5 hr)**
    *   1.1.1. Create backend directory: `agents/Day-05-Data-Analysis-Agent/backend/`.
    *   1.1.2. Set up virtual environment (`python -m venv venv`).
    *   1.1.3. Create `requirements.txt` with dependencies.
    *   1.1.4. Create `.env.example` and `.env` files.
    *   1.1.5. Create basic application structure:
        ```
        backend/
        ├── app/
        │   ├── __init__.py
        │   ├── main.py
        │   ├── models/
        │   │   └── __init__.py
        │   ├── routers/
        │   │   ├── __init__.py
        │   │   ├── csv_analysis.py
        │   │   └── sql_analysis.py
        │   └── services/
        │       ├── __init__.py
        │       ├── llm_service.py
        │       ├── csv_service.py
        │       └── db_service.py
        ├── .env
        ├── .env.example
        └── requirements.txt
        ```

*   **Task 1.2: FastAPI App Setup & Base Endpoints (Est: 0.5 hr)**
    *   1.2.1. Set up the FastAPI application in `main.py`:
        *   Create FastAPI app instance.
        *   Configure CORS middleware to allow frontend connections.
        *   Include routers.
        *   Implement a health check endpoint.
    *   1.2.2. Create Pydantic models in `models/__init__.py` for:
        *   Query requests.
        *   CSV upload responses.
        *   DB connection requests.
        *   Analysis results (including text, data, visualizations).

*   **Task 1.3: LLM Service Implementation (Est: 1 hr)**
    *   1.3.1. In `services/llm_service.py`, implement:
        *   OpenRouter API key loading from environment variables.
        *   LLM initialization function using `OpenRouterChat`.
        *   Basic prompt handling.
        *   Error handling for API failures.
    *   1.3.2. Create test function to verify LLM connectivity.

*   **Task 1.4: CSV Analysis Service & Router (Est: 1 hr)**
    *   1.4.1. In `services/csv_service.py`, implement:
        *   Function to handle uploaded CSV files and load into Pandas DataFrame.
        *   Function to create DataFrame agent using LangChain.
        *   Function to execute queries against DataFrame agent.
        *   Function to generate Plotly visualizations as JSON.
    *   1.4.2. In `routers/csv_analysis.py`, create endpoints:
        *   `POST /csv/upload` - For uploading CSV files.
        *   `POST /csv/query` - For running natural language queries.

*   **Task 1.5: SQL Database Service & Router (Est: 1 hr)**
    *   1.5.1. In `services/db_service.py`, implement:
        *   Function to create DB connection.
        *   Function to create SQL Database agent.
        *   Function to execute natural language queries.
        *   Function to generate Plotly visualizations from SQL results.
    *   1.5.2. In `routers/sql_analysis.py`, create endpoints:
        *   `POST /db/connect` - For establishing database connections.
        *   `POST /db/query` - For running natural language queries.

### Phase 2: Frontend Development with React (Total Est: ~5 hours)

*   **Task 2.1: Project Setup & Basic Structure (Est: 0.5 hr)**
    *   2.1.1. Create frontend directory: `agents/Day-05-Data-Analysis-Agent/frontend/`.
    *   2.1.2. Initialize a new React project with TypeScript using Vite:
        ```bash
        npm create vite@latest . -- --template react-ts
        ```
    *   2.1.3. Install dependencies:
        ```bash
        npm install antd axios plotly.js react-plotly.js
        ```
    *   2.1.4. Create basic application structure:
        ```
        frontend/
        ├── public/
        ├── src/
        │   ├── components/
        │   │   ├── DataSourceSelection.tsx
        │   │   ├── QueryInput.tsx
        │   │   ├── ResultsDisplay.tsx
        │   │   ├── CSVUpload.tsx
        │   │   ├── DBConnection.tsx
        │   │   └── Visualization.tsx
        │   ├── services/
        │   │   └── api.ts
        │   ├── contexts/
        │   │   └── AppContext.tsx
        │   ├── types/
        │   │   └── index.ts
        │   ├── App.tsx
        │   ├── main.tsx
        │   └── styles.css
        ├── index.html
        ├── package.json
        └── tsconfig.json
        ```

*   **Task 2.2: Context Setup & API Service (Est: 0.5 hr)**
    *   2.2.1. Create API service in `services/api.ts`:
        *   Setup Axios instance.
        *   Implement functions for CSV upload, DB connection, and query execution.
    *   2.2.2. Create application context in `contexts/AppContext.tsx`:
        *   Create state for data source type (CSV or DB).
        *   Create state for current data (either CSV data or DB connection).
        *   Create state for query results and visualization data.
        *   Implement context provider with state management.

*   **Task 2.3: Main Layout & Data Source Selection (Est: 1 hr)**
    *   2.3.1. In `App.tsx`, implement:
        *   Main layout using Ant Design's Layout component.
        *   Context provider wrapper.
        *   Header with title and information.
        *   Content area with main component.
    *   2.3.2. In `components/DataSourceSelection.tsx`, implement:
        *   Radio or tab selection for CSV vs. DB.
        *   Conditional rendering of the appropriate input component.

*   **Task 2.4: CSV & Database Components (Est: 1 hr)**
    *   2.4.1. In `components/CSVUpload.tsx`, implement:
        *   Ant Design's Upload component for CSV file selection.
        *   Progress indicator during upload.
        *   Preview of uploaded data (first few rows).
    *   2.4.2. In `components/DBConnection.tsx`, implement:
        *   Database type selection (SQLite, PostgreSQL).
        *   Form inputs for connection parameters.
        *   Test connection button.
        *   Success/failure feedback.

*   **Task 2.5: Query & Results Components (Est: 1 hr)**
    *   2.5.1. In `components/QueryInput.tsx`, implement:
        *   Text area for natural language query input.
        *   Submit button.
        *   Loading indicator during query processing.
    *   2.5.2. In `components/ResultsDisplay.tsx`, implement:
        *   Section for textual response.
        *   Section for data table (using Ant Design Table).
        *   Section for visualization.
        *   Export options (if time permits).

*   **Task 2.6: Visualization Component (Est: 1 hr)**
    *   2.6.1. In `components/Visualization.tsx`, implement:
        *   Wrapper for Plotly.js React component.
        *   Logic to handle visualization data from backend.
        *   Default placeholder when no visualization is available.
        *   Basic interactive features (zoom, tooltip hover).

### Phase 3: Integration & End-to-End Testing (Total Est: ~3 hours)

*   **Task 3.1: Backend CORS & Error Handling (Est: 0.5 hr)**
    *   3.1.1. Ensure CORS is properly configured in FastAPI to accept requests from the React frontend.
    *   3.1.2. Implement comprehensive error handling in all endpoints.
    *   3.1.3. Add detailed logging for debugging.

*   **Task 3.2: Frontend-Backend Integration (Est: 1 hr)**
    *   3.2.1. Test CSV upload flow from frontend to backend.
    *   3.2.2. Test database connection flow.
    *   3.2.3. Test query submission and result rendering.
    *   3.2.4. Test visualization rendering in the frontend.

*   **Task 3.3: User Experience Enhancements (Est: 1 hr)**
    *   3.3.1. Add loading states for all operations.
    *   3.3.2. Implement error notifications using Ant Design message or notification components.
    *   3.3.3. Add tooltips and helper text for better usability.
    *   3.3.4. Ensure responsive design works on different screen sizes.

*   **Task 3.4: Documentation & Deployment Guide (Est: 0.5 hr)**
    *   3.4.1. Update/create `README.md` with:
        *   Project description and features.
        *   Setup instructions for both backend and frontend.
        *   API documentation.
        *   Usage examples.
    *   3.4.2. Document deployment options.

### Phase 4: Refinements & Stretch Goals (If time permits on Day 5) (Total Est: ~3-5 hours)

*   **Task 4.1: Local LLM Integration (Est: 1-1.5 hrs)**
    *   4.1.1. Add Ollama support in backend.
    *   4.1.2. Add LLM selection option in frontend.
    *   4.1.3. Implement switching logic between OpenRouter and local LLM.

*   **Task 4.2: Enhanced Visualization Options (Est: 1 hr)**
    *   4.2.1. Add support for more Plotly chart types.
    *   4.2.2. Implement visualization customization options in the UI.
    *   4.2.3. Add the ability to save or export visualizations.

*   **Task 4.3: Excel File Support (Est: 1 hr)**
    *   4.3.1. Add Excel file processing in the backend.
    *   4.3.2. Update file upload component to accept .xlsx files.
    *   4.3.3. Test with sample Excel files.

*   **Task 4.4: Code View & Export (Est: 0.5-1 hr)**
    *   4.4.1. Expose generated Python/SQL code in the API response.
    *   4.4.2. Add a code viewer component in the frontend.
    *   4.4.3. Implement code copy/export functionality.

## 5. Key Components & Integration Points

### 5.1 Backend (FastAPI)
*   **LangChain Components:**
    *   `OpenRouterChat` for LLM access
    *   `create_pandas_dataframe_agent` for CSV analysis
    *   `SQLDatabase` and `create_sql_agent` for SQL database analysis
*   **Key API Endpoints:**
    *   `/csv/upload` - Upload and process CSV files
    *   `/csv/query` - Execute natural language queries on CSV data
    *   `/db/connect` - Establish database connections
    *   `/db/query` - Execute natural language queries on connected databases
*   **Response Structure:**
    ```json
    {
      "success": true,
      "result": {
        "text": "Analysis shows...",
        "data": [
          {"column1": "value1", "column2": "value2", ...}
        ],
        "visualization": {
          "type": "plotly",
          "figure": {...} // Plotly figure JSON
        },
        "code": "# Generated Python/SQL code" // Optional
      }
    }
    ```

### 5.2 Frontend (React)
*   **Key Components:**
    *   `DataSourceSelection` - Choose between CSV and DB
    *   `CSVUpload` - Handle file uploads
    *   `DBConnection` - Manage database connections
    *   `QueryInput` - Input natural language queries
    *   `ResultsDisplay` - Show results and visualizations
*   **State Management:**
    *   React Context API for application state
    *   Local component state for UI-specific state

### 5.3 Integration Points
*   File uploads using `FormData` and `multipart/form-data`
*   JSON API requests and responses
*   Plotly figure JSON passed from backend to frontend for rendering

## 6. Testing Strategy

### 6.1 Backend Testing
*   Create a sample CSV file (e.g., `sample_data.csv` with varied data types).
*   Create a sample SQLite database (e.g., `sample_db.sqlite`) with 2-3 tables and sample data.
*   If using PostgreSQL, set up a test database.
*   **API Endpoint Tests:**
    *   CSV upload endpoint - test with valid and invalid files
    *   CSV query endpoint - test with various query types
    *   DB connection endpoint - test with valid and invalid credentials
    *   DB query endpoint - test with various SQL-related queries

### 6.2 Frontend Testing
*   **Component Testing:**
    *   Form submissions and validations
    *   File upload component
    *   Visualization rendering
*   **Integration Testing:**
    *   End-to-end user flows
    *   Error handling and UI feedback

### 6.3 Query Testing
*   **CSV Analysis Queries:**
    *   "Summarize this data"
    *   "What are the columns?"
    *   "What is the average of column X?"
    *   "Show rows where column X is greater than 10"
    *   "Create a histogram of column Y"
    *   "Plot the relationship between column X and Y"
*   **SQL DB Queries:**
    *   "List all tables"
    *   "Describe the 'users' table"
    *   "Show me all data from the 'products' table where price > 100"
    *   "What is the average order value?"
    *   "Create a bar chart of sales by region"

### 6.4 Error Handling Tests
*   Upload incorrect file types
*   Provide invalid DB credentials
*   Enter ambiguous or unanswerable queries
*   Test API timeout scenarios

### 6.5 Browser Compatibility
*   Test on Chrome, Firefox, Safari (if available)
*   Test responsive design on different screen sizes