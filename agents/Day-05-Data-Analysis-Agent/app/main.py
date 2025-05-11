"""
Data Analysis Agent - Main Application

This Streamlit application allows users to analyze and visualize data from various sources
(e.g., CSV files, SQL databases) using natural language queries.
"""

import streamlit as st
import pandas as pd
import traceback
import sys
import os
import re
from langchain_core.messages import HumanMessage

# Add the parent directory to the Python path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
from config import settings

# Import core modules
from core.llm import initialize_llm
from core.agent import initialize_agent, process_query

# Import data handling modules
from data.csv_handler import load_csv_file, display_dataframe_info
from data.sql_handler import (
    create_db_connection,
    execute_sql_query,
    create_langchain_sql_database,
    initialize_sql_agent,
    initialize_sql_chain,
    get_database_info,
    process_sql_query,
    generate_sql_query,
    get_table_names
)
from data.visualization import (
    create_visualization,
    display_visualization,
    extract_code_from_response,
    execute_visualization_code,
    generate_visualization_prompt,
    create_fallback_visualization
)

# Import utility functions
from utils.helpers import (
    extract_number_from_query,
    detect_visualization_request,
    detect_query_type,
    format_error_message
)

# Import UI components
from ui.components import (
    setup_page_config,
    render_header,
    render_sidebar,
    render_csv_upload_section,
    render_sql_connection_section,
    render_query_input_section,
    render_results_section,
    render_error,
    render_success,
    render_info,
    render_warning
)

# Initialize session state for data persistence
if 'df' not in st.session_state:
    st.session_state.df = None
if 'db_engine' not in st.session_state:
    st.session_state.db_engine = None
if 'llm' not in st.session_state:
    st.session_state.llm = None
if 'agent' not in st.session_state:
    st.session_state.agent = None
# SQL-specific session state variables
if 'sql_database' not in st.session_state:
    st.session_state.sql_database = None
if 'sql_agent' not in st.session_state:
    st.session_state.sql_agent = None
if 'sql_chain' not in st.session_state:
    st.session_state.sql_chain = None
if 'table_names' not in st.session_state:
    st.session_state.table_names = []

def main():
    """Main application function"""

    # Set up page configuration
    setup_page_config()

    # Application header
    render_header()

    # Sidebar for data source selection
    data_source = render_sidebar()

    # Main content area
    if data_source == "CSV File":
        handle_csv_upload()
    else:
        handle_sql_connection()

    # Query input area
    query, analyze_clicked = render_query_input_section()

    # Create a container for query results
    result_container = render_results_section()

    # Submit button
    if analyze_clicked:
        if query:
            # Check if we have data to analyze
            if data_source == "CSV File" and st.session_state.df is None:
                render_warning("Please upload a CSV file first.")
                return
            elif data_source == "SQL Database" and st.session_state.db_engine is None:
                render_warning("Please connect to a database first.")
                return

            # Check if LLM is initialized
            if st.session_state.llm is None:
                render_error("LLM is not initialized. Please check your OpenRouter API key.")
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
                                    threshold = extract_number_from_query(query)
                                    if threshold:
                                        # Count people with more than the threshold years of experience
                                        count = len(st.session_state.df[st.session_state.df['years_experience'] > threshold])

                                        st.markdown(f"### Direct Answer")
                                        render_success(f"There are **{count} people** with more than {threshold} years of experience.")

                                        # Show the filtered data
                                        st.markdown("### Filtered Data")
                                        filtered_df = st.session_state.df[st.session_state.df['years_experience'] > threshold]
                                        st.dataframe(filtered_df, use_container_width=True)
                                    else:
                                        # Fall back to agent
                                        response = process_query(st.session_state.agent, query)
                                        # Check if response is a dictionary with 'output' key
                                        if isinstance(response, dict) and 'output' in response:
                                            st.markdown(response['output'])
                                        else:
                                            st.markdown(str(response))
                                except Exception as e:
                                    render_warning(f"Error in direct processing: {str(e)}. Falling back to agent.")
                                    # Fall back to agent
                                    response = process_query(st.session_state.agent, query)
                                    # Check if response is a dictionary with 'output' key
                                    if isinstance(response, dict) and 'output' in response:
                                        st.markdown(response['output'])
                                    else:
                                        st.markdown(str(response))
                            else:
                                # Use the Pandas DataFrame agent for other queries
                                response = process_query(st.session_state.agent, query)

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

                                # If the response mentions a visualization, generate and execute visualization code
                                if detect_visualization_request(query):
                                    st.markdown("### Visualization")

                                    with st.spinner("Generating visualization..."):
                                        # Generate a specialized prompt for visualization
                                        viz_prompt = generate_visualization_prompt(query, st.session_state.df)

                                        # Get visualization code from LLM
                                        viz_response = st.session_state.llm.invoke([HumanMessage(content=viz_prompt)])
                                        viz_code = extract_code_from_response(viz_response.content)

                                        if viz_code:
                                            # Display the generated code in an expander
                                            with st.expander("View Generated Visualization Code"):
                                                st.code(viz_code, language="python")

                                            # Execute the code and get the figure
                                            fig, message = execute_visualization_code(viz_code, st.session_state.df)

                                            if fig:
                                                # Display the visualization
                                                display_visualization(fig)
                                            else:
                                                render_warning(f"Failed to create visualization: {message}")
                                        else:
                                            render_warning("Could not generate visualization code from the LLM response.")

                        elif data_source == "SQL Database":
                            # Check if we have the SQL database and agent initialized
                            if not st.session_state.sql_database:
                                render_error("SQL Database not properly initialized. Please reconnect to the database.")
                                return

                            # Display database schema information in an expander
                            with st.expander("Database Schema Information"):
                                st.markdown("#### Tables")
                                for table in st.session_state.table_names:
                                    st.markdown(f"- {table}")

                                # Add a button to show detailed schema
                                if st.button("Show Detailed Schema"):
                                    schema_info = get_database_info(st.session_state.sql_database)
                                    st.markdown(schema_info)

                            # Process the query using the SQL agent if available
                            if st.session_state.sql_agent:
                                st.markdown("### Using SQL Agent")

                                with st.spinner("Processing your query with SQL Agent..."):
                                    # Process the query using the SQL agent
                                    agent_result = process_sql_query(st.session_state.sql_agent, query)

                                    # Store the agent's response for later display
                                    agent_output = ""
                                    if isinstance(agent_result, dict) and 'output' in agent_result:
                                        agent_output = agent_result['output']
                                    else:
                                        agent_output = str(agent_result)

                                    # Try to extract SQL query from the agent's response
                                    sql_query = None
                                    if isinstance(agent_result, dict) and 'output' in agent_result:
                                        # Look for SQL code blocks in the output
                                        sql_blocks = re.findall(r"```sql\s*(.*?)\s*```", agent_result['output'], re.DOTALL)
                                        if sql_blocks:
                                            sql_query = sql_blocks[0].strip()

                                    # If we found a SQL query, execute it and get the results
                                    result_df = None
                                    if sql_query:
                                        st.markdown("### Generated SQL Query")
                                        st.code(sql_query, language="sql")

                                        st.markdown("### Query Results")
                                        try:
                                            success, result = execute_sql_query(st.session_state.db_engine, sql_query)
                                            if success and isinstance(result, pd.DataFrame):
                                                result_df = result
                                                st.dataframe(result, use_container_width=True)
                                            else:
                                                render_error(f"Error executing SQL query: {result}")
                                        except Exception as e:
                                            render_error(f"Error executing SQL query: {str(e)}")

                                    # Check for visualization requests in both the original query and the agent's response
                                    # This ensures we catch visualization requests that might be in either place
                                    is_viz_request = detect_visualization_request(query)

                                    # Also check the agent's response for visualization terms
                                    if not is_viz_request and isinstance(agent_output, str):
                                        is_viz_request = detect_visualization_request(agent_output)

                                    # Add debugging information
                                    st.markdown("### Debug Information")
                                    st.write(f"Query: '{query}'")
                                    st.write(f"Visualization detected in query: {detect_visualization_request(query)}")
                                    if isinstance(agent_output, str):
                                        st.write(f"Agent output contains visualization terms: {detect_visualization_request(agent_output)}")
                                    st.write(f"Final visualization decision: {is_viz_request}")

                                    if is_viz_request and result_df is not None and not result_df.empty:
                                        st.markdown("### Visualization")

                                        with st.spinner("Generating visualization..."):
                                            # Generate a specialized prompt for the visualization
                                            viz_prompt = generate_visualization_prompt(query, result_df)

                                            # Get visualization code from LLM
                                            viz_response = st.session_state.llm.invoke([HumanMessage(content=viz_prompt)])
                                            viz_code = extract_code_from_response(viz_response.content)

                                            if viz_code:
                                                # Display the generated code
                                                with st.expander("View Generated Visualization Code"):
                                                    st.code(viz_code, language="python")

                                                # Execute the code and display the figure
                                                fig, message = execute_visualization_code(viz_code, result_df)
                                                if fig:
                                                    display_visualization(fig)
                                                else:
                                                    render_warning(f"Failed to create visualization: {message}")

                                                    # Try a more robust fallback visualization
                                                    st.markdown("### Fallback Visualization")
                                                    fallback_fig, fallback_msg = create_fallback_visualization(result_df, query)
                                                    if fallback_fig:
                                                        st.pyplot(fallback_fig)
                                                    else:
                                                        render_warning(f"Fallback visualization failed: {fallback_msg}")
                                            else:
                                                render_warning("Could not generate visualization code from the LLM response.")


                                    # Display the agent's response after handling visualizations
                                    st.markdown("### Agent Response")
                                    st.markdown(agent_output)

                            # If SQL agent is not available, fall back to SQL chain
                            elif st.session_state.sql_chain:
                                st.markdown("### Using SQL Chain")

                                with st.spinner("Generating SQL query..."):
                                    # Generate SQL query using the chain
                                    sql_query = generate_sql_query(st.session_state.sql_chain, query)

                                    # Display the generated SQL query
                                    st.markdown("### Generated SQL Query")
                                    st.code(sql_query, language="sql")

                                    # Execute the SQL query
                                    st.markdown("### Query Results")
                                    result_df = None
                                    try:
                                        success, result = execute_sql_query(st.session_state.db_engine, sql_query)
                                        if success and isinstance(result, pd.DataFrame):
                                            result_df = result
                                            st.dataframe(result, use_container_width=True)
                                        else:
                                            render_error(f"Error executing SQL query: {result}")
                                    except Exception as e:
                                        render_error(f"Error executing SQL query: {str(e)}")

                                    # Handle visualization if requested
                                    # Check both the original query and the SQL query for visualization terms
                                    is_viz_request = detect_visualization_request(query)

                                    # Also check the SQL query for visualization terms
                                    if not is_viz_request and isinstance(sql_query, str):
                                        is_viz_request = detect_visualization_request(sql_query)

                                    if is_viz_request and result_df is not None and not result_df.empty:
                                        st.markdown("### Visualization")

                                        with st.spinner("Generating visualization..."):
                                            # Generate a specialized prompt for the visualization
                                            viz_prompt = generate_visualization_prompt(query, result_df)

                                            # Get visualization code from LLM
                                            viz_response = st.session_state.llm.invoke([HumanMessage(content=viz_prompt)])
                                            viz_code = extract_code_from_response(viz_response.content)

                                            if viz_code:
                                                # Display the generated code
                                                with st.expander("View Generated Visualization Code"):
                                                    st.code(viz_code, language="python")

                                                # Execute the code and display the figure
                                                fig, message = execute_visualization_code(viz_code, result_df)
                                                if fig:
                                                    display_visualization(fig)
                                                else:
                                                    render_warning(f"Failed to create visualization: {message}")

                                                    # Try a more robust fallback visualization
                                                    st.markdown("### Fallback Visualization")
                                                    fallback_fig, fallback_msg = create_fallback_visualization(result_df, query)
                                                    if fallback_fig:
                                                        st.pyplot(fallback_fig)
                                                    else:
                                                        render_warning(f"Fallback visualization failed: {fallback_msg}")
                                            else:
                                                render_warning("Could not generate visualization code from the LLM response.")

                            # If neither SQL agent nor SQL chain is available, fall back to basic LLM
                            else:
                                st.markdown("### Using Basic LLM for SQL Generation")
                                render_warning("SQL Agent and Chain not available. Using basic LLM for SQL generation.")

                                prompt = f"""
                                I have a SQL database with the following tables: {', '.join(st.session_state.table_names)}
                                I want to answer this question: {query}

                                Please help me formulate a SQL query that would answer this question.
                                Only return the SQL query, nothing else.
                                """

                                response = st.session_state.llm.invoke([HumanMessage(content=prompt)])
                                sql_query = response.content.strip()

                                st.markdown("### Generated SQL Query")
                                st.code(sql_query, language="sql")

                                st.markdown("### Query Results")
                                # Execute the SQL query if we have a database connection
                                result_df = None
                                if st.session_state.db_engine:
                                    try:
                                        success, result = execute_sql_query(st.session_state.db_engine, sql_query)
                                        if success and isinstance(result, pd.DataFrame):
                                            result_df = result
                                            st.dataframe(result, use_container_width=True)
                                        else:
                                            render_error(f"Error executing SQL query: {result}")
                                    except Exception as e:
                                        render_error(f"Error executing SQL query: {str(e)}")
                                else:
                                    render_error("Database connection not available.")

                                # If the query is a visualization request, generate a visualization
                                # Check both the original query and the SQL query for visualization terms
                                is_viz_request = detect_visualization_request(query)

                                # Also check the SQL query for visualization terms
                                if not is_viz_request and isinstance(sql_query, str):
                                    is_viz_request = detect_visualization_request(sql_query)

                                if is_viz_request and result_df is not None and not result_df.empty:
                                    st.markdown("### Visualization")

                                    with st.spinner("Generating visualization..."):
                                        # Generate a specialized prompt for the visualization
                                        viz_prompt = generate_visualization_prompt(query, result_df)

                                        # Get visualization code from LLM
                                        viz_response = st.session_state.llm.invoke([HumanMessage(content=viz_prompt)])
                                        viz_code = extract_code_from_response(viz_response.content)

                                        if viz_code:
                                            # Display the generated code in an expander
                                            with st.expander("View Generated Visualization Code"):
                                                st.code(viz_code, language="python")

                                            # Execute the code and get the figure
                                            fig, message = execute_visualization_code(viz_code, result_df)

                                            if fig:
                                                # Display the visualization
                                                display_visualization(fig)
                                            else:
                                                render_warning(f"Failed to create visualization: {message}")

                                                # Try a more robust fallback visualization
                                                st.markdown("### Fallback Visualization")
                                                fallback_fig, fallback_msg = create_fallback_visualization(result_df, query)
                                                if fallback_fig:
                                                    st.pyplot(fallback_fig)
                                                else:
                                                    render_warning(f"Fallback visualization failed: {fallback_msg}")
                                        else:
                                            render_warning("Could not generate visualization code from the LLM response.")

                except Exception as e:
                    error_details = traceback.format_exc()
                    render_error(f"Error processing query: {str(e)}", True, error_details)

                    # Provide a helpful message for common errors
                    if "Connection" in str(e):
                        render_warning(format_error_message(e))
        else:
            render_warning("Please enter a query.")

def handle_csv_upload():
    """Handle CSV file upload"""

    uploaded_file = render_csv_upload_section()

    if uploaded_file is not None:
        # Load CSV file into DataFrame
        with st.spinner("Loading data..."):
            df = load_csv_file(uploaded_file)

            if not df.empty:
                # Store DataFrame in session state
                st.session_state.df = df

                # Display data information
                display_dataframe_info(df)

                # Initialize LLM and agent if not already done
                initialize_llm_and_agent(df)
            else:
                render_error("Failed to load the CSV file. Please check the file format and try again.")

def initialize_llm_and_agent(df=None):
    """Initialize LangChain LLM and agent"""

    # Initialize LLM if not already done
    if st.session_state.llm is None:
        st.session_state.llm = initialize_llm()

    # Initialize Pandas DataFrame agent if we have a DataFrame
    if df is not None and not df.empty and st.session_state.llm is not None:
        st.session_state.agent = initialize_agent(st.session_state.llm, df)


def handle_sql_connection():
    """Handle SQL database connection"""

    db_type, connection_params = render_sql_connection_section()

    # Display database schema information if already connected
    if st.session_state.db_engine and st.session_state.sql_database:
        st.markdown("### Database Information")

        # Display table names
        if st.session_state.table_names:
            st.markdown("#### Tables")
            for table in st.session_state.table_names:
                st.markdown(f"- {table}")

        # Add a button to show detailed schema information
        if st.button("Show Database Schema"):
            with st.spinner("Loading database schema..."):
                schema_info = get_database_info(st.session_state.sql_database)
                with st.expander("Database Schema", expanded=True):
                    st.markdown(schema_info)

    # Connect button
    if st.button("Connect to Database"):
        with st.spinner("Connecting to database..."):
            # Create SQLAlchemy engine
            engine = create_db_connection(db_type, **connection_params)
            if engine:
                st.session_state.db_engine = engine

                # Get table names
                st.session_state.table_names = get_table_names(engine)

                # Create LangChain SQLDatabase
                sql_db = create_langchain_sql_database(
                    engine=engine,
                    sample_rows_in_table_info=3
                )

                if sql_db:
                    st.session_state.sql_database = sql_db

                    # Initialize LLM if not already done
                    if st.session_state.llm is None:
                        st.session_state.llm = initialize_llm()

                    # Initialize SQL agent and chain
                    if st.session_state.llm:
                        # Initialize SQL agent
                        sql_agent = initialize_sql_agent(
                            llm=st.session_state.llm,
                            db=sql_db,
                            verbose=True
                        )

                        if sql_agent:
                            st.session_state.sql_agent = sql_agent

                        # Initialize SQL chain
                        sql_chain = initialize_sql_chain(
                            llm=st.session_state.llm,
                            db=sql_db
                        )

                        if sql_chain:
                            st.session_state.sql_chain = sql_chain

                    render_success(f"Connected to {db_type.capitalize()} database with {len(st.session_state.table_names)} tables")
                else:
                    render_error(f"Failed to create LangChain SQLDatabase from {db_type.capitalize()} connection")
            else:
                render_error(f"Failed to connect to {db_type.capitalize()} database")


if __name__ == "__main__":
    main()
