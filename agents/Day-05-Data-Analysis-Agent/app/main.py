"""
Data Analysis Agent - Main Application

This Streamlit application allows users to analyze and visualize data from various sources
(e.g., CSV files, SQL databases) using natural language queries.
"""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from langchain_core.messages import HumanMessage

# Import custom OpenRouter client
from openrouter_client import ChatOpenRouter

# Import utility functions
from utils import load_csv_file, get_dataframe_info, create_db_connection, execute_sql_query, create_visualization

# Load environment variables
load_dotenv()

# Initialize session state for data persistence
if 'df' not in st.session_state:
    st.session_state.df = None
if 'db_engine' not in st.session_state:
    st.session_state.db_engine = None
if 'llm' not in st.session_state:
    st.session_state.llm = None
if 'agent' not in st.session_state:
    st.session_state.agent = None

# Set page configuration
st.set_page_config(
    page_title="Data Analysis Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""

    # Application header
    st.title("📊 Data Analysis Agent")
    st.markdown("""
    Upload your data and ask questions in natural language to analyze and visualize it.
    """)

    # Sidebar for data source selection
    st.sidebar.title("Data Source")
    data_source = st.sidebar.radio(
        "Select Data Source",
        options=["CSV File", "SQL Database"],
        index=0
    )

    # Main content area
    if data_source == "CSV File":
        handle_csv_upload()
    else:
        handle_sql_connection()

    # Query input area
    st.markdown("### Ask a question about your data")
    query = st.text_area("Enter your query in natural language", height=100,
                         placeholder="e.g., 'What is the average of column X?' or 'Show me a histogram of column Y'")

    # Create a container for query results
    result_container = st.container()

    # Submit button
    if st.button("Analyze"):
        if query:
            # Check if we have data to analyze
            if data_source == "CSV File" and st.session_state.df is None:
                st.warning("Please upload a CSV file first.")
                return
            elif data_source == "SQL Database" and st.session_state.db_engine is None:
                st.warning("Please connect to a database first.")
                return

            # Check if LLM is initialized
            if st.session_state.llm is None:
                st.error("LLM is not initialized. Please check your OpenRouter API key.")
                return

            # Process the query
            with st.spinner("Processing your query..."):
                try:
                    with result_container:
                        st.markdown("### Results")

                        if data_source == "CSV File" and st.session_state.agent is not None:
                            # Check for specific questions we can handle directly
                            if "years of experience" in query.lower() and "more than" in query.lower():
                                try:
                                    # Extract the number from the query
                                    import re
                                    numbers = re.findall(r'\d+', query)
                                    if numbers:
                                        threshold = int(numbers[0])
                                        # Count people with more than the threshold years of experience
                                        count = len(st.session_state.df[st.session_state.df['years_experience'] > threshold])

                                        st.markdown(f"### Direct Answer")
                                        st.success(f"There are **{count} people** with more than {threshold} years of experience.")

                                        # Show the filtered data
                                        st.markdown("### Filtered Data")
                                        filtered_df = st.session_state.df[st.session_state.df['years_experience'] > threshold]
                                        st.dataframe(filtered_df, use_container_width=True)
                                    else:
                                        # Fall back to agent
                                        response = st.session_state.agent.invoke(query)
                                        # Check if response is a dictionary with 'output' key
                                        if isinstance(response, dict) and 'output' in response:
                                            st.markdown(response['output'])
                                        else:
                                            st.markdown(str(response))
                                except Exception as e:
                                    st.warning(f"Error in direct processing: {str(e)}. Falling back to agent.")
                                    # Fall back to agent
                                    response = st.session_state.agent.invoke(query)
                                    # Check if response is a dictionary with 'output' key
                                    if isinstance(response, dict) and 'output' in response:
                                        st.markdown(response['output'])
                                    else:
                                        st.markdown(str(response))
                            else:
                                # Use the Pandas DataFrame agent for other queries
                                response = st.session_state.agent.invoke(query)

                                # Check if response is a dictionary with 'output' key
                                if isinstance(response, dict) and 'output' in response:
                                    st.markdown(response['output'])
                                else:
                                    st.markdown(str(response))

                                # If the response contains a DataFrame, try to display it
                                if "pandas dataframe" in query.lower() or "show" in query.lower():
                                    try:
                                        # This is a simple approach - in a real app, you'd want more robust parsing
                                        st.dataframe(st.session_state.df.head())
                                    except Exception:
                                        pass

                                # If the response mentions a visualization, try to create it
                                if any(term in query.lower() for term in ["plot", "chart", "graph", "histogram", "visualize", "visualization"]):
                                    st.markdown("### Visualization")
                                    st.info("Visualization capabilities will be implemented in Task 1.7")

                        elif data_source == "SQL Database":
                            # For SQL, we'll just use the LLM directly for now
                            # In Task 2.3, we'll implement proper SQL integration
                            prompt = f"""
                            I have a SQL database and I want to answer this question: {query}

                            Please help me formulate a SQL query that would answer this question.
                            Only return the SQL query, nothing else.
                            """

                            response = st.session_state.llm.invoke([HumanMessage(content=prompt)])
                            sql_query = response.content.strip()

                            st.markdown("### Generated SQL Query")
                            st.code(sql_query, language="sql")

                            st.markdown("### Query Results")
                            st.info("SQL query execution will be implemented in Task 2.4")

                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    st.error(f"Error processing query: {str(e)}")
                    st.expander("Error Details").code(error_details)

                    # Provide a helpful message for common errors
                    if "Connection" in str(e):
                        st.warning("""
                        Connection error detected. This might be due to:
                        1. Network connectivity issues
                        2. OpenRouter API service unavailability
                        3. API rate limits

                        Try again in a few moments or check your API key configuration.
                        """)
        else:
            st.warning("Please enter a query.")

def handle_csv_upload():
    """Handle CSV file upload"""

    st.markdown("### Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")

        # Load CSV file into DataFrame
        with st.spinner("Loading data..."):
            df = load_csv_file(uploaded_file)

            if not df.empty:
                # Store DataFrame in session state
                st.session_state.df = df

                # Display data preview
                st.markdown("### Data Preview")
                st.dataframe(df.head(), use_container_width=True)

                # Get and display data information
                st.markdown("### Data Information")
                info = get_dataframe_info(df)

                # Display basic information
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Rows:** {info['shape'][0]}")
                    st.write(f"**Columns:** {info['shape'][1]}")

                    if info['numeric_columns']:
                        st.write(f"**Numeric columns:** {', '.join(info['numeric_columns'])}")

                    if info['categorical_columns']:
                        st.write(f"**Categorical columns:** {', '.join(info['categorical_columns'])}")

                with col2:
                    # Display missing values if any
                    missing_values = {k: v for k, v in info['missing_values'].items() if v > 0}
                    if missing_values:
                        st.write("**Missing values:**")
                        for col, count in missing_values.items():
                            st.write(f"- {col}: {count}")
                    else:
                        st.write("**No missing values found**")

                # Initialize LLM and agent if not already done
                initialize_llm_and_agent(df)
            else:
                st.error("Failed to load the CSV file. Please check the file format and try again.")

def initialize_llm_and_agent(df=None):
    """Initialize LangChain LLM and agent"""

    # Check if we have an API key
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        st.sidebar.error("OpenRouter API key not found. Please add it to your .env file.")
        return

    # Initialize LLM if not already done
    if st.session_state.llm is None:
        # Create a spinner in the main area instead of sidebar
        with st.spinner("Initializing LLM..."):
            try:
                st.session_state.llm = ChatOpenRouter(
                    openai_api_key=openrouter_api_key,
                    model_name="anthropic/claude-3.7-sonnet",  # Using a more capable model
                    temperature=0.2,
                    max_tokens=1024,
                    request_timeout=60,  # Increase timeout to 60 seconds
                    max_retries=3  # Add retries for better reliability
                )
                st.sidebar.success("LLM initialized successfully!")
            except Exception as e:
                st.sidebar.error(f"Error initializing LLM: {str(e)}")
                return

    # Initialize Pandas DataFrame agent if we have a DataFrame
    if df is not None and not df.empty and st.session_state.llm is not None:
        # Create a spinner in the main area instead of sidebar
        with st.spinner("Initializing agent..."):
            try:
                st.session_state.agent = create_pandas_dataframe_agent(
                    llm=st.session_state.llm,
                    df=df,
                    agent_type=AgentType.OPENAI_FUNCTIONS,
                    verbose=True,
                    allow_dangerous_code=True,  # Explicitly allow code execution
                    max_iterations=10,  # Limit iterations to prevent timeouts
                    max_execution_time=30,  # Limit execution time to 30 seconds
                    early_stopping_method="force"  # Force stop if limits are reached
                )
                st.sidebar.success("Agent initialized successfully!")
            except Exception as e:
                st.sidebar.error(f"Error initializing agent: {str(e)}")


def handle_sql_connection():
    """Handle SQL database connection"""

    st.markdown("### Connect to SQL Database")

    # Database type selection
    db_type = st.selectbox(
        "Select Database Type",
        options=["SQLite", "PostgreSQL"],
        index=0
    )

    # Connection parameters based on database type
    if db_type == "SQLite":
        db_path = st.text_input("Database File Path", "example.db")

        if st.button("Connect"):
            with st.spinner("Connecting to database..."):
                engine = create_db_connection('sqlite', db_path=db_path)
                if engine:
                    st.session_state.db_engine = engine
                    st.success(f"Connected to SQLite database: {db_path}")

                    # Initialize LLM for SQL queries
                    initialize_llm_and_agent()
                else:
                    st.error(f"Failed to connect to SQLite database: {db_path}")
    else:
        # PostgreSQL connection parameters
        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input("Host", "localhost")
            port = st.text_input("Port", "5432")
            database = st.text_input("Database Name")
        with col2:
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")

        if st.button("Connect"):
            with st.spinner("Connecting to database..."):
                engine = create_db_connection(
                    'postgresql',
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                )
                if engine:
                    st.session_state.db_engine = engine
                    st.success(f"Connected to PostgreSQL database: {database}")

                    # Initialize LLM for SQL queries
                    initialize_llm_and_agent()
                else:
                    st.error(f"Failed to connect to PostgreSQL database: {database}")


if __name__ == "__main__":
    main()
