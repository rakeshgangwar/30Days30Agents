from typing import List, Dict, Any, Optional, Union
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.tools.reasoning import ReasoningTools

from email_assist.tools.email_tools import EmailTools
from email_assist.tools.gmail_tools import GmailTools
from email_assist.tools.ms_graph_tools import MSGraphTools

class EmailAssistant:
    """
    Email Assistant Agent that helps users manage their email inbox by summarizing emails,
    drafting replies, prioritizing messages, and automating email-related tasks.
    """
    
    def __init__(self, 
                 email_service: Union[GmailTools, MSGraphTools],
                 model_provider: str = "openai", 
                 model_id: Optional[str] = None,
                 enable_reasoning: bool = True):
        """
        Initialize the Email Assistant Agent.
        
        Args:
            email_service: An instance of GmailTools or MSGraphTools
            model_provider: The model provider to use ("openai" or "anthropic")
            model_id: The specific model ID to use (if None, uses default)
            enable_reasoning: Whether to enable reasoning tools for the agent
        """
        self.email_service = email_service
        self.model_provider = model_provider
        
        # Set default model IDs based on provider
        if model_id is None:
            if model_provider == "openai":
                model_id = "gpt-4o"
            elif model_provider == "anthropic":
                model_id = "claude-3-7-sonnet-latest"
            else:
                raise ValueError(f"Unsupported model provider: {model_provider}")
        
        self.model_id = model_id
        self.enable_reasoning = enable_reasoning
        
        # Create the Agno agent
        self.agent = self._create_agent()
    
    # Direct methods for UI operations
    def list_emails(self, folder: str = "inbox", query: str = None, max_results: int = 20):
        """
        List emails directly from the email service.
        This method is for direct UI operations, not for agent use.
        
        Args:
            folder: The mail folder to list messages from
            query: Search query for filtering messages
            max_results: Maximum number of messages to return
            
        Returns:
            List of email messages
        """
        try:
            if isinstance(self.email_service, GmailTools):
                return self.email_service.list_messages(query=query, max_results=max_results)
            else:  # MSGraphTools
                return self.email_service.list_messages(folder=folder, query=query, max_results=max_results)
        except Exception as e:
            print(f"Error in list_emails: {e}")
            return []
    
    def get_email(self, msg_id: str):
        """
        Get a specific email by ID directly from the email service.
        This method is for direct UI operations, not for agent use.
        
        Args:
            msg_id: The ID of the email to retrieve
            
        Returns:
            Email message details
        """
        return self.email_service.get_message(msg_id)
    
    def get_email_thread(self, thread_id: str):
        """
        Get an email thread directly from the email service.
        This method is for direct UI operations, not for agent use.
        
        Args:
            thread_id: The ID of the thread to retrieve
            
        Returns:
            Email thread details
        """
        return self.email_service.get_thread(thread_id)
    
    def send_email(self, to: str, subject: str, body: str, cc: str = None, bcc: str = None):
        """
        Send an email directly through the email service.
        This method is for direct UI operations, not for agent use.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Email body content
            cc: Carbon copy recipient(s)
            bcc: Blind carbon copy recipient(s)
            
        Returns:
            Result of the send operation
        """
        return self.email_service.send_message(to=to, subject=subject, body=body, cc=cc, bcc=bcc)
    
    def search_emails(self, query: str, max_results: int = 20):
        """
        Search for emails directly through the email service.
        This method is for direct UI operations, not for agent use.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of matching emails
        """
        try:
            return self.email_service.search_messages(query=query, max_results=max_results)
        except Exception as e:
            print(f"Error in search_emails: {e}")
            return []
    
    def _create_agent(self) -> Agent:
        """
        Create and configure the Agno agent with appropriate tools and instructions.
        
        Returns:
            Configured Agno agent
        """
        # Select the appropriate model based on provider
        if self.model_provider == "openai":
            model = OpenAIChat(id=self.model_id)
        elif self.model_provider == "anthropic":
            model = Claude(id=self.model_id)
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
        
        # Create the email tools for the agent
        self.tools = EmailTools(self.email_service)
        
        # We already stored the email service in __init__
        # No need to reassign it here
        
        # Prepare the tools list
        # Important: We need to pass the EmailTools instance itself, not its methods
        # This ensures the 'self' parameter is correctly passed when the agent calls the methods
        tools = [self.tools]
        
        # Add reasoning tools if enabled
        if self.enable_reasoning:
            tools.append(ReasoningTools(add_instructions=True))
        
        # Create the agent with email-specific instructions
        agent = Agent(
            model=model,
            description="You are an email assistant that helps users manage their inbox efficiently.",
            instructions=[
                "Summarize emails concisely, focusing on key information and action items.",
                "Draft professional and contextually appropriate email replies.",
                "Prioritize emails based on importance, urgency, and required actions.",
                "Extract key information and action items from emails.",
                "Generate templates for common email scenarios.",
                "Always respect user privacy and handle email data securely.",
                "When reasoning through tasks, explain your thought process clearly."
            ],
            tools=tools,
            markdown=True,
            show_tool_calls=True,
        )
        
        return agent
    
    def summarize_email(self, email_id: str) -> str:
        """
        Summarize a specific email by ID.
        
        Args:
            email_id: The ID of the email to summarize
            
        Returns:
            A concise summary of the email
        """
        try:
            # First, explicitly fetch the email using the email service
            email = self.email_service.get_message(email_id)
            
            if not email:
                return "Error: Could not retrieve the email. Please check the email ID and try again."
            
            # Extract relevant parts of the email for summarization
            subject = email.get('subject', '(No Subject)')
            sender = email.get('from', 'Unknown Sender')
            body = email.get('body', '')
            date = email.get('date', '')
            
            # Create a prompt with the actual email content
            prompt = f"""Summarize the following email:
            
            From: {sender}
            Date: {date}
            Subject: {subject}
            
            {body}
            
            Focus on the key points, main message, and any action items or requests.
            Format the summary in a clear and structured way, highlighting the most important parts of the email.
            """
            
            # Use the agent's run method to summarize the email content
            response = self.agent.run(prompt)
            
            # Check if the response is a RunResponse object and extract the content
            if hasattr(response, 'content'):
                return response.content
            return response
            
        except Exception as e:
            import traceback
            print(f"Error in summarize_email: {e}")
            print(traceback.format_exc())
            return f"Error summarizing email: {str(e)}"
    
    def summarize_thread(self, thread_id: str) -> str:
        """
        Summarize an email thread/conversation.
        
        Args:
            thread_id: The ID of the thread to summarize
            
        Returns:
            A concise summary of the email thread
        """
        try:
            # First, explicitly fetch the thread using the email service
            thread_messages = self.email_service.get_thread(thread_id)
            
            if not thread_messages or len(thread_messages) == 0:
                return "Error: Could not retrieve the email thread. Please check the thread ID and try again."
            
            # Format the thread messages for the prompt
            thread_content = ""
            for i, message in enumerate(thread_messages):
                subject = message.get('subject', '(No Subject)')
                sender = message.get('from', 'Unknown Sender')
                body = message.get('body', '')
                date = message.get('date', '')
                
                thread_content += f"""
                MESSAGE {i+1}:
                From: {sender}
                Date: {date}
                Subject: {subject}
                
                {body}
                
                """
            
            # Create a prompt with the actual thread content
            prompt = f"""Summarize the following email thread/conversation:
            
            {thread_content}
            
            Focus on the key points, progression of the discussion, and any conclusions or action items.
            Format the summary in a clear and structured way, highlighting the most important parts of the conversation.
            """
            
            # Use the agent's run method to summarize the thread content
            response = self.agent.run(prompt)
            
            # Check if the response is a RunResponse object and extract the content
            if hasattr(response, 'content'):
                return response.content
            return response
            
        except Exception as e:
            import traceback
            print(f"Error in summarize_thread: {e}")
            print(traceback.format_exc())
            return f"Error summarizing thread: {str(e)}"
    
    def draft_reply(self, email_id: str, instructions: str) -> str:
        """
        Draft a reply to a specific email based on user instructions.
        
        Args:
            email_id: The ID of the email to reply to
            instructions: User instructions for the reply (e.g., "politely decline", "ask for more information")
            
        Returns:
            A drafted email reply
        """
        try:
            # First, explicitly fetch the email using the email service
            email = self.email_service.get_message(email_id)
            
            if not email:
                return "Error: Could not retrieve the email. Please check the email ID and try again."
            
            # Extract relevant parts of the email for drafting a reply
            subject = email.get('subject', '(No Subject)')
            sender = email.get('from', 'Unknown Sender')
            body = email.get('body', '')
            date = email.get('date', '')
            
            # Create a prompt with the actual email content
            prompt = f"""Draft a reply to the following email based on these instructions: {instructions}
            
            ORIGINAL EMAIL:
            From: {sender}
            Date: {date}
            Subject: {subject}
            
            {body}
            
            The reply should be professional, contextually appropriate, and address all relevant points from the original email.
            Format the reply as a complete email, ready to be sent.
            """
            
            # Use the agent's run method instead of get_response
            response = self.agent.run(prompt)
            
            # Check if the response is a RunResponse object and extract the content
            if hasattr(response, 'content'):
                return response.content
            return response
            
        except Exception as e:
            import traceback
            print(f"Error in draft_reply: {e}")
            print(traceback.format_exc())
            return f"Error drafting reply: {str(e)}"
    
    def prioritize_emails(self, max_results: int = 10) -> str:
        """
        Prioritize recent emails based on importance and urgency.
        
        Args:
            max_results: Maximum number of emails to prioritize
            
        Returns:
            Prioritized list of emails with explanations
        """
        try:
            # First, fetch the emails directly using the email_service
            if isinstance(self.email_service, GmailTools):
                emails = self.email_service.list_messages(query=None, max_results=max_results)
            else:  # MSGraphTools
                emails = self.email_service.list_messages(folder="inbox", query=None, max_results=max_results)
            
            if not emails or len(emails) == 0:
                return "No emails found to prioritize. Please refresh your inbox first."
            
            # Format the emails into a structured format for the agent
            formatted_emails = []
            for email in emails[:max_results]:
                # Extract snippet or use truncated body if snippet not available
                snippet = email.get('snippet', '')
                if not snippet and 'body' in email:
                    body = email.get('body', '')
                    snippet = body[:200] + '...' if len(body) > 200 else body
                
                email_info = {
                    'sender': email.get('from', 'Unknown'),
                    'subject': email.get('subject', 'No Subject'),
                    'date': email.get('date', 'Unknown date'),
                    'snippet': snippet or 'No content'
                }
                formatted_emails.append(email_info)
            
            # Build the email list as a string using proper string concatenation
            email_list_parts = []
            for i, email in enumerate(formatted_emails, 1):
                email_part = (
                    "Email {}:\n".format(i) +
                    "Sender: {}\n".format(email['sender']) +
                    "Subject: {}\n".format(email['subject']) +
                    "Date: {}\n".format(email['date']) +
                    "Preview: {}\n\n".format(email['snippet'])
                )
                email_list_parts.append(email_part)
            
            email_list_text = ''.join(email_list_parts)
            
            # Create the prompt for the agent with proper string formatting
            prompt_start = "Here are the {} most recent emails from the user's inbox:\n\n".format(len(formatted_emails))
            prompt_middle = "{}".format(email_list_text)
            prompt_end = (
                "\nPlease prioritize these emails based on importance and urgency.\n\n" +
                "For each email, assign a priority level (High, Medium, Low) and provide a brief reason for the prioritization.\n" +
                "Consider factors such as sender, subject, content, time sensitivity, and required actions.\n" +
                "Format the results in a clear, structured way that makes it easy to identify which emails need attention first."
            )
            
            prompt = prompt_start + prompt_middle + prompt_end
            
            # Use the agent's run method with the actual email data
            response = self.agent.run(prompt)
            
            # Check if the response is a RunResponse object and extract the content
            if hasattr(response, 'content'):
                return response.content
            return response
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print("Error in prioritize_emails: {}".format(e))
            print(error_details)
            return "Error prioritizing emails: {}. Please try refreshing your inbox first.".format(e)
    
    def extract_action_items(self, email_id: str) -> str:
        """
        Extract action items from a specific email.
        
        Args:
            email_id: The ID of the email to extract action items from
            
        Returns:
            List of action items extracted from the email
        """
        # Use the agent to get the email and extract action items
        prompt = f"""Retrieve the email with ID '{email_id}' and extract all action items from it.
        
        An action item is a task, request, or something that requires a response or action.
        List each action item separately and clearly, with any relevant details or deadlines.
        """
        
        # Use the agent's run method instead of get_response
        response = self.agent.run(prompt)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            return response.content
        return response
    
    def search_emails(self, query: str, max_results: int = 10) -> str:
        """
        Search for emails based on a natural language query.
        
        Args:
            query: Natural language search query
            max_results: Maximum number of results to return
            
        Returns:
            Search results with relevant email information
        """
        try:
            # Directly use the email service to search for emails
            if isinstance(self.email_service, GmailTools):
                emails = self.email_service.list_messages(query=query, max_results=max_results)
            else:  # MSGraphTools
                emails = self.email_service.list_messages(folder="inbox", query=query, max_results=max_results)
            
            if not emails or len(emails) == 0:
                return f"No emails found matching '{query}'. Please try a different search term."
            
            # Format the search results using triple-quoted strings
            result = f"""Found {len(emails)} emails matching '{query}':

"""
            
            for i, email in enumerate(emails[:max_results], 1):
                # Extract snippet or use truncated body if snippet not available
                snippet = email.get('snippet', '')
                if not snippet and 'body' in email:
                    body = email.get('body', '')
                    snippet = body[:200] + '...' if len(body) > 200 else body
                
                # Add each email to the result string using triple-quoted strings
                sender = email.get('from', 'Unknown')
                subject = email.get('subject', 'No Subject')
                date = email.get('date', 'Unknown date')
                preview = snippet or 'No content'
                
                email_text = f"""Email {i}:
Sender: {sender}
Subject: {subject}
Date: {date}
Preview: {preview}

"""
                result += email_text
            
            return result
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in search_emails: {e}")
            print(error_details)
            
            # Fall back to using the agent if direct search fails
            prompt = f"""Search for emails that match the query: "{query}"

Limit the results to {max_results} emails. For each matching email, provide:
1. The sender
2. The subject
3. The date
4. A brief snippet or summary of the content
5. Why it matches the search query

Format the results in a clear, structured way."""
            
            # Use the agent's run method as a fallback
            response = self.agent.run(prompt)
            
            # Check if the response is a RunResponse object and extract the content
            if hasattr(response, 'content'):
                return response.content
            return response
    
    def generate_template(self, template_type: str, customization: Optional[str] = None) -> str:
        """
        Generate an email template for common scenarios.
        
        Args:
            template_type: Type of template (e.g., "meeting request", "application acknowledgment")
            customization: Optional customization instructions
            
        Returns:
            Generated email template
        """
        # Use the agent to generate a template
        prompt = f"""Generate a professional email template for: {template_type}
        """
        
        if customization:
            prompt += f"\nCustomization requirements: {customization}"
        
        prompt += "\n\nThe template should include placeholders for variable information and be ready to use."
        
        # Use the agent's run method instead of get_response
        response = self.agent.run(prompt)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            return response.content
        return response
    
    def process_query(self, query: str) -> str:
        """
        Process a natural language query from the user.
        
        This is a general-purpose method that can handle various email-related tasks
        based on the user's query.
        
        Args:
            query: The user's natural language query or request
            
        Returns:
            The agent's response to the query
        """
        # Check if the query is about searching for emails
        search_keywords = ['show me', 'find', 'search for', 'get', 'display', 'retrieve', 'list']
        search_terms = ['email', 'emails', 'message', 'messages', 'mail']
        
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # Check if this is a search query
        is_search_query = (any(keyword in query_lower for keyword in search_keywords) and
                          any(term in query_lower for term in search_terms))
        
        if is_search_query:
            # Extract search parameters
            search_params = query_lower
            for keyword in search_keywords:
                search_params = search_params.replace(keyword, '')
            for term in search_terms:
                search_params = search_params.replace(term, '')
            
            # Clean up the search parameters
            search_params = search_params.strip().strip('from').strip()
            
            # If we have search parameters, use them to search emails
            if search_params:
                try:
                    # Use the email service to search for emails
                    results = self.search_emails(search_params)
                    if results:
                        return results
                except Exception as e:
                    print(f"Error searching emails: {e}")
        
        # If not a search query or search failed, use the agent to process the query
        response = self.agent.run(query)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            return response.content
        return response
