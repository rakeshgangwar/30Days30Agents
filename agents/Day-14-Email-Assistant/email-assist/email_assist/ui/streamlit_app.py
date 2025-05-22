import os
import streamlit as st
from dotenv import load_dotenv

from email_assist.email_agent import EmailAssistant
from email_assist.auth.gmail_auth import GmailAuth
from email_assist.auth.ms_graph_auth import MSGraphAuth
from email_assist.tools.gmail_tools import GmailTools
from email_assist.tools.ms_graph_tools import MSGraphTools

# Load environment variables
load_dotenv()

# App title and configuration
st.set_page_config(page_title="Email Assistant", page_icon="✉️", layout="wide")

def main():
    # App header
    st.title("✉️ Email Assistant")
    st.markdown("*Your AI-powered email management assistant*")
    
    # Sidebar for authentication and settings
    with st.sidebar:
        st.header("Settings")
        
        # Email provider selection
        email_provider = st.selectbox(
            "Select Email Provider",
            options=["Gmail", "Microsoft Outlook"],
            index=0
        )
        
        # Model provider selection
        model_provider = st.selectbox(
            "Select AI Model",
            options=["OpenAI (GPT-4o)", "Anthropic (Claude)"],
            index=0
        )
        
        # Authentication section
        st.subheader("Authentication")
        
        if email_provider == "Gmail":
            # Gmail authentication
            if 'gmail_authenticated' not in st.session_state:
                st.session_state.gmail_authenticated = False
            
            if not st.session_state.gmail_authenticated:
                st.info("Please authenticate with Gmail to continue.")
                
                # File uploader for credentials.json
                credentials_file = st.file_uploader("Upload credentials.json", type="json")
                
                if credentials_file is not None and st.button("Authenticate"):
                    # Save the uploaded credentials file
                    os.makedirs("temp", exist_ok=True)
                    with open("temp/credentials.json", "wb") as f:
                        f.write(credentials_file.getbuffer())
                    
                    try:
                        # Initialize Gmail authentication
                        gmail_auth = GmailAuth(
                            credentials_file="temp/credentials.json",
                            token_file="temp/token.pickle"
                        )
                        
                        # Attempt to authenticate
                        if gmail_auth.authenticate():
                            st.session_state.gmail_auth = gmail_auth
                            st.session_state.gmail_authenticated = True
                            st.success("Authentication successful!")
                            st.rerun()
                        else:
                            st.error("Authentication failed. Please try again.")
                    except Exception as e:
                        st.error(f"Error during authentication: {e}")
            else:
                st.success("Authenticated with Gmail")
                if st.button("Sign Out"):
                    # Clear authentication state
                    st.session_state.gmail_authenticated = False
                    if 'gmail_auth' in st.session_state:
                        del st.session_state.gmail_auth
                    if 'email_assistant' in st.session_state:
                        del st.session_state.email_assistant
                    st.rerun()
        
        elif email_provider == "Microsoft Outlook":
            # Microsoft Graph authentication
            if 'msgraph_authenticated' not in st.session_state:
                st.session_state.msgraph_authenticated = False
            
            if not st.session_state.msgraph_authenticated:
                st.subheader("Microsoft Graph Authentication")
                
                # Authentication steps
                auth_steps = ["Credentials", "Authorization", "Complete"]
                
                # Initialize current step if not present
                if 'ms_auth_step' not in st.session_state:
                    st.session_state.ms_auth_step = 0
                
                # Display progress bar
                current_step = st.session_state.ms_auth_step
                st.progress(current_step / len(auth_steps))
                st.write(f"Step {current_step + 1}/{len(auth_steps)}: {auth_steps[current_step]}")
                
                # Step 1: Credentials
                if current_step == 0:
                    # Try to get credentials from environment variables
                    env_client_id = os.getenv("MS_CLIENT_ID")
                    env_client_secret = os.getenv("MS_CLIENT_SECRET")
                    env_tenant_id = os.getenv("MS_TENANT_ID")
                    
                    if env_client_id and env_client_secret and env_tenant_id:
                        st.success("Microsoft Graph credentials found in environment variables.")
                        
                        if st.button("Use Environment Credentials"):
                            # Store credentials in session state
                            st.session_state.ms_client_id = env_client_id
                            st.session_state.ms_client_secret = env_client_secret
                            st.session_state.ms_tenant_id = env_tenant_id
                            
                            # Move to next step
                            st.session_state.ms_auth_step = 1
                            st.rerun()
                    else:
                        st.info("Please enter Microsoft Graph API credentials.")
                        
                        # Input fields for Microsoft Graph credentials
                        client_id = st.text_input("Client ID", type="password")
                        client_secret = st.text_input("Client Secret", type="password")
                        tenant_id = st.text_input("Tenant ID", type="password")
                        
                        if client_id and client_secret and tenant_id and st.button("Continue"):
                            # Store credentials in session state
                            st.session_state.ms_client_id = client_id
                            st.session_state.ms_client_secret = client_secret
                            st.session_state.ms_tenant_id = tenant_id
                            
                            # Move to next step
                            st.session_state.ms_auth_step = 1
                            st.rerun()
                
                # Step 2: Authorization
                elif current_step == 1:
                    try:
                        # Create temp directory if it doesn't exist
                        os.makedirs("temp", exist_ok=True)
                        
                        # Get credentials from session state
                        client_id = st.session_state.ms_client_id
                        client_secret = st.session_state.ms_client_secret
                        tenant_id = st.session_state.ms_tenant_id
                        
                        # Initialize Microsoft Graph authentication
                        msgraph_auth = MSGraphAuth(
                            client_id=client_id,
                            client_secret=client_secret,
                            tenant_id=tenant_id,
                            token_cache_file="temp/msgraph_token_cache.json"
                        )
                        
                        # Store auth object in session state
                        st.session_state.temp_msgraph_auth = msgraph_auth
                        
                        # Get the authorization URL
                        redirect_uri = "http://localhost:8501/"
                        auth_url = msgraph_auth.get_auth_url(redirect_uri=redirect_uri)
                        
                        # Store redirect URI for later use
                        st.session_state.ms_redirect_uri = redirect_uri
                        
                        # Display instructions
                        st.info("""Please follow these steps to complete authentication:

1. Click the link below to sign in with your Microsoft account
2. Grant the requested permissions
3. After being redirected, copy the 'code' parameter from the URL
4. Paste the code below and click 'Continue'""")
                        
                        st.markdown(f"### [Click here to authorize with Microsoft]({auth_url})")
                        
                        # Input for authorization code
                        auth_code = st.text_input("Enter the authorization code from the redirect URL")
                        
                        if auth_code and st.button("Continue"):
                            try:
                                # Exchange code for token
                                token = msgraph_auth.get_token_from_code(
                                    code=auth_code,
                                    redirect_uri=redirect_uri
                                )
                                
                                if token and 'access_token' in token:
                                    # Store the authenticated auth object in session state
                                    st.session_state.msgraph_auth = msgraph_auth
                                    st.session_state.msgraph_authenticated = True
                                    
                                    # Move to next step
                                    st.session_state.ms_auth_step = 2
                                    st.success("Authentication successful!")
                                    st.rerun()
                                else:
                                    st.error("Authentication failed: Invalid token response")
                                    st.error(f"Token response: {token}")
                            except Exception as e:
                                st.error(f"Error completing authentication: {e}")
                    except Exception as e:
                        st.error(f"Error in authorization step: {e}")
                        
                        # Add button to go back to credentials step
                        if st.button("Back to Credentials"):
                            st.session_state.ms_auth_step = 0
                            st.rerun()
                
                # Step 3: Authentication Complete
                elif current_step == 2:
                    st.success("Microsoft Graph authentication completed successfully!")
                    st.info("You can now use the Email Assistant with your Microsoft Outlook account.")
                    
                    # Add button to restart authentication if needed
                    if st.button("Restart Authentication"):
                        # Reset authentication state
                        st.session_state.ms_auth_step = 0
                        st.session_state.msgraph_authenticated = False
                        if 'msgraph_auth' in st.session_state:
                            del st.session_state.msgraph_auth
                        st.rerun()



            else:
                st.success("Authenticated with Microsoft Outlook")
                if st.button("Sign Out"):
                    # Clear authentication state
                    st.session_state.msgraph_authenticated = False
                    if 'msgraph_auth' in st.session_state:
                        del st.session_state.msgraph_auth
                    if 'email_assistant' in st.session_state:
                        del st.session_state.email_assistant
                    st.rerun()
    
    # Initialize email assistant if authenticated
    if ('gmail_authenticated' in st.session_state and st.session_state.gmail_authenticated) or \
       ('msgraph_authenticated' in st.session_state and st.session_state.msgraph_authenticated):
        
        if 'email_assistant' not in st.session_state:
            # Create the appropriate email service
            if 'gmail_authenticated' in st.session_state and st.session_state.gmail_authenticated:
                gmail_service = st.session_state.gmail_auth.get_service()
                email_service = GmailTools(gmail_service)
            else:  # Microsoft Graph
                # Get the Microsoft Graph client from the auth object
                graph_client = st.session_state.msgraph_auth.get_graph_client()
                if not graph_client:
                    st.error("Failed to get Microsoft Graph client. Please try re-authenticating.")
                    return
                email_service = MSGraphTools(graph_client)
            
            # Determine the model provider
            model_provider_name = "openai" if model_provider == "OpenAI (GPT-4o)" else "anthropic"
            
            # Create the email assistant
            email_assistant = EmailAssistant(
                email_service=email_service,
                model_provider=model_provider_name,
                enable_reasoning=True
            )
            
            st.session_state.email_assistant = email_assistant
        
        # Main content area with tabs for different functionalities
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📥 Inbox", "📝 Summarize", "✏️ Draft Reply", "🔍 Search", "📋 Templates", "❓ Ask Assistant"
        ])
        
        # Tab 1: Inbox (Email List and Prioritization)
        with tab1:
            st.header("📥 Inbox")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.subheader("Actions")
                if st.button("Refresh Inbox"):
                    st.session_state.inbox_refreshed = True
                
                st.divider()
                
                st.subheader("Prioritize")
                if st.button("Prioritize Emails"):
                    with st.spinner("Prioritizing emails..."):
                        prioritized_emails = st.session_state.email_assistant.prioritize_emails(max_results=10)
                        st.session_state.prioritized_emails = prioritized_emails
            
            with col2:
                if 'inbox_refreshed' in st.session_state and st.session_state.inbox_refreshed:
                    try:
                        with st.spinner("Fetching emails..."):
                            # Actually fetch emails from the authenticated account
                            # Use the direct method we added to the EmailAssistant class
                            # Call the method on the email_service directly, not through the agent
                            if isinstance(st.session_state.email_assistant.email_service, GmailTools):
                                emails = st.session_state.email_assistant.email_service.list_messages(query=None, max_results=20)
                            else:  # MSGraphTools
                                emails = st.session_state.email_assistant.email_service.list_messages(folder="inbox", query=None, max_results=20)
                            
                            if emails and len(emails) > 0:
                                st.subheader(f"Found {len(emails)} emails")
                                
                                # Display emails in a nice format
                                for i, email in enumerate(emails):
                                    with st.expander(f"{email.get('subject', 'No Subject')} - {email.get('from', 'Unknown Sender')}"):
                                        st.write(f"**From:** {email.get('from', 'Unknown')}")
                                        st.write(f"**Date:** {email.get('date', 'Unknown')}")
                                        st.write(f"**Subject:** {email.get('subject', 'No Subject')}")
                                        
                                        # Show snippet or preview
                                        if 'snippet' in email:
                                            st.write("**Preview:**")
                                            st.write(email['snippet'])
                                        
                                        # Add buttons for actions
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            if st.button("View Full Message", key=f"view_{i}"):
                                                st.session_state.selected_email_id = email['id']
                                                st.session_state.view_full_email = True
                                        with col2:
                                            if st.button("Summarize", key=f"summarize_{i}"):
                                                st.session_state.selected_email_id = email['id']
                                                st.session_state.summarize_email = True
                                        with col3:
                                            if st.button("Draft Reply", key=f"reply_{i}"):
                                                st.session_state.selected_email_id = email['id']
                                                st.session_state.draft_reply = True
                            else:
                                st.info("No emails found in your inbox.")
                    except Exception as e:
                        st.error(f"Error fetching emails: {e}")
                        st.error("Please check the console for more details.")
                        import traceback
                        st.code(traceback.format_exc())
                    
                    # Display prioritized emails if available
                    if 'prioritized_emails' in st.session_state:
                        st.subheader("Prioritized Emails")
                        st.markdown(st.session_state.prioritized_emails)
                else:
                    st.info("Click 'Refresh Inbox' to view your emails.")
                
                # Process email action buttons
                if 'selected_email_id' in st.session_state:
                    # View full email
                    if 'view_full_email' in st.session_state and st.session_state.view_full_email:
                        try:
                            with st.spinner("Loading full message..."):
                                email_id = st.session_state.selected_email_id
                                full_email = st.session_state.email_assistant.get_email(email_id)
                                
                                if full_email:
                                    st.subheader("Full Email Content")
                                    st.write(f"**From:** {full_email.get('from', 'Unknown')}")
                                    st.write(f"**To:** {full_email.get('to', 'Unknown')}")
                                    st.write(f"**Date:** {full_email.get('date', 'Unknown')}")
                                    st.write(f"**Subject:** {full_email.get('subject', 'No Subject')}")
                                    st.write("**Content:**")
                                    
                                    # Display the body with proper formatting
                                    if 'body' in full_email:
                                        # Check if the content is HTML (contains HTML tags)
                                        if '<html' in full_email['body'].lower() or '<body' in full_email['body'].lower():
                                            # For HTML content, use st.components.html to render it properly
                                            st.components.v1.html(full_email['body'], height=600, scrolling=True)
                                        else:
                                            # For plain text, use markdown
                                            st.markdown(full_email['body'])
                                    else:
                                        st.info("No content available for this email.")
                                    
                                    # Display attachments if any
                                    if 'attachments' in full_email and full_email['attachments']:
                                        st.write("**Attachments:**")
                                        for attachment in full_email['attachments']:
                                            st.write(f"- {attachment.get('name', 'Unnamed attachment')}")
                                else:
                                    st.error("Failed to retrieve the full email content.")
                            
                            # Reset the view flag after displaying
                            st.session_state.view_full_email = False
                        except Exception as e:
                            st.error(f"Error retrieving full email: {e}")
                            st.session_state.view_full_email = False
                    
                    # Summarize email
                    if 'summarize_email' in st.session_state and st.session_state.summarize_email:
                        try:
                            with st.spinner("Summarizing email..."):
                                email_id = st.session_state.selected_email_id
                                summary = st.session_state.email_assistant.summarize_email(email_id)
                                
                                st.subheader("Email Summary")
                                st.markdown(summary)
                            
                            # Reset the summarize flag after displaying
                            st.session_state.summarize_email = False
                        except Exception as e:
                            st.error(f"Error summarizing email: {e}")
                            st.session_state.summarize_email = False
                    
                    # Draft reply
                    if 'draft_reply' in st.session_state and st.session_state.draft_reply:
                        try:
                            # Show input for reply instructions
                            st.subheader("Draft Reply")
                            instructions = st.text_area("Instructions for the reply", 
                                                    placeholder="E.g., 'Politely decline the meeting invitation' or 'Ask for more details about the project'",
                                                    key="inbox_reply_instructions")
                            
                            if instructions and st.button("Generate Reply"):
                                with st.spinner("Drafting reply..."):
                                    email_id = st.session_state.selected_email_id
                                    reply = st.session_state.email_assistant.draft_reply(email_id, instructions)
                                    
                                    st.subheader("Generated Reply")
                                    st.markdown(reply)
                                
                                # Reset the draft reply flag after displaying
                                st.session_state.draft_reply = False
                        except Exception as e:
                            st.error(f"Error drafting reply: {e}")
                            st.session_state.draft_reply = False
        
        # Tab 2: Summarize Emails
        with tab2:
            st.header("📝 Summarize")
            
            summary_type = st.radio("Select what to summarize:", ["Email", "Thread"])
            
            if summary_type == "Email":
                email_id = st.text_input("Enter Email ID")
                if email_id and st.button("Summarize Email"):
                    with st.spinner("Summarizing email..."):
                        summary = st.session_state.email_assistant.summarize_email(email_id)
                        st.subheader("Summary")
                        st.markdown(summary)
            else:  # Thread
                thread_id = st.text_input("Enter Thread ID")
                if thread_id and st.button("Summarize Thread"):
                    with st.spinner("Summarizing thread..."):
                        summary = st.session_state.email_assistant.summarize_thread(thread_id)
                        st.subheader("Summary")
                        st.markdown(summary)
        
        # Tab 3: Draft Reply
        with tab3:
            st.header("✏️ Draft Reply")
            
            email_id = st.text_input("Enter Email ID to reply to")
            instructions = st.text_area("Instructions for the reply", 
                                      placeholder="E.g., 'Politely decline the meeting invitation' or 'Ask for more details about the project'",
                                      key="tab_reply_instructions")
            
            if email_id and instructions and st.button("Draft Reply"):
                with st.spinner("Drafting reply..."):
                    reply = st.session_state.email_assistant.draft_reply(email_id, instructions)
                    st.subheader("Draft Reply")
                    st.markdown(reply)
        
        # Tab 4: Search Emails
        with tab4:
            st.header("🔍 Search")
            
            search_query = st.text_input("Enter search query", 
                                       placeholder="E.g., 'Emails about the budget meeting' or 'Attachments from John last week'")
            
            if search_query and st.button("Search"):
                with st.spinner("Searching emails..."):
                    # Call the search method directly on the email_service
                    search_results = st.session_state.email_assistant.email_service.search_messages(query=search_query, max_results=10)
                    st.subheader("Search Results")
                    
                    if search_results and len(search_results) > 0:
                        for i, email in enumerate(search_results):
                            with st.expander(f"{email.get('subject', 'No Subject')} - {email.get('from', 'Unknown Sender')}"):
                                st.write(f"**From:** {email.get('from', 'Unknown')}")
                                st.write(f"**Date:** {email.get('date', 'Unknown')}")
                                st.write(f"**Subject:** {email.get('subject', 'No Subject')}")
                                
                                # Show body preview
                                if 'body' in email:
                                    st.write("**Content:**")
                                    st.write(email['body'][:500] + '...' if len(email['body']) > 500 else email['body'])
                    else:
                        st.info("No emails found matching your search query.")
        
        # Tab 5: Email Templates
        with tab5:
            st.header("📋 Templates")
            
            template_type = st.selectbox(
                "Select template type",
                options=[
                    "Meeting Request",
                    "Meeting Confirmation",
                    "Application Acknowledgment",
                    "Project Update",
                    "Follow-up",
                    "Thank You",
                    "Introduction",
                    "Apology",
                    "Feedback Request",
                    "Custom"
                ]
            )
            
            if template_type == "Custom":
                template_type = st.text_input("Enter custom template type")
            
            customization = st.text_area("Customization requirements (optional)", 
                                       placeholder="E.g., 'Include a section about project timeline' or 'Use a formal tone'",
                                       key="template_customization")
            
            if template_type and st.button("Generate Template"):
                with st.spinner("Generating template..."):
                    template = st.session_state.email_assistant.generate_template(template_type, customization)
                    st.subheader("Generated Template")
                    st.markdown(template)
        
        # Tab 6: Ask Assistant (General Queries)
        with tab6:
            st.header("❓ Ask Assistant")
            
            if 'messages' not in st.session_state:
                st.session_state.messages = []
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            prompt = st.chat_input("Ask about your emails or for help with email tasks...")
            
            if prompt:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate assistant response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = st.session_state.email_assistant.process_query(prompt)
                        st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    else:
        # Display welcome message when not authenticated
        st.info("Please authenticate with your email provider in the sidebar to get started.")
        
        # App description
        st.markdown("""
        ## Welcome to Email Assistant!
        
        This AI-powered assistant helps you manage your email inbox efficiently by:
        
        - **Summarizing** emails and threads
        - **Drafting** contextually appropriate replies
        - **Prioritizing** messages based on importance
        - **Extracting** key information and action items
        - **Searching** emails with natural language queries
        - **Generating** templates for common email scenarios
        
        To get started, please authenticate with your email provider using the sidebar.
        """)

if __name__ == "__main__":
    main()
