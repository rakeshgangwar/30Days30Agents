from typing import List, Optional, Dict, Any
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude

class EmailAssistantAgent:
    """
    Email Assistant Agent that helps users manage their email inbox by summarizing emails,
    drafting replies, prioritizing messages, and automating email-related tasks.
    """
    
    def __init__(self, model_provider: str = "openai", model_id: Optional[str] = None):
        """
        Initialize the Email Assistant Agent.
        
        Args:
            model_provider: The model provider to use ("openai" or "anthropic")
            model_id: The specific model ID to use (if None, uses default)
        """
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
        self.agent = self._create_agent()
    
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
                "Always respect user privacy and handle email data securely."
            ],
            markdown=True,
        )
        
        return agent
    
    def summarize_email(self, email_content: str, max_length: int = 200) -> str:
        """
        Summarize the content of an email.
        
        Args:
            email_content: The full content of the email to summarize
            max_length: Maximum length of the summary in characters
            
        Returns:
            A concise summary of the email
        """
        prompt = f"""Summarize the following email in a concise way, focusing on key information and action items. 
        Keep the summary under {max_length} characters.
        
        EMAIL:
        {email_content}
        """
        
        response = self.agent.run(prompt)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            return response.content
        return response
    
    def draft_reply(self, email_content: str, instructions: str) -> str:
        """
        Draft a reply to an email based on the original content and user instructions.
        
        Args:
            email_content: The content of the email to reply to
            instructions: User instructions for the reply (e.g., "politely decline", "ask for more information")
            
        Returns:
            A drafted email reply
        """
        prompt = f"""Draft a reply to the following email based on these instructions: {instructions}
        
        ORIGINAL EMAIL:
        {email_content}
        """
        
        response = self.agent.run(prompt)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            return response.content
        return response
    
    def prioritize_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize a list of emails based on importance and urgency.
        
        Args:
            emails: List of email dictionaries containing at least 'subject', 'sender', and 'content'
            
        Returns:
            Prioritized list of emails with added 'priority' and 'reason' fields
        """
        # Convert emails to a format suitable for the prompt
        email_text = ""
        for i, email in enumerate(emails):
            email_text += f"EMAIL {i+1}:\nFrom: {email['sender']}\nSubject: {email['subject']}\n\n{email['content']}\n\n"
        
        prompt = f"""Prioritize the following emails based on importance and urgency. 
        For each email, assign a priority level (High, Medium, Low) and provide a brief reason.
        Return the results in a clear, structured format with the email number, priority level, and reason.
        
        {email_text}
        """
        
        response = self.agent.run(prompt)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            return response.content
        
        # Process the response to update the email list with priorities
        # This is a simplified implementation - in practice, you would parse the response more robustly
        prioritized_emails = emails.copy()
        
        # For now, we'll just return the original list with the agent's response
        # In a real implementation, you would parse the response and add priority fields to each email
        return prioritized_emails, response
    
    def extract_action_items(self, email_content: str) -> List[str]:
        """
        Extract action items from an email.
        
        Args:
            email_content: The content of the email
            
        Returns:
            List of action items extracted from the email
        """
        prompt = """Extract all action items from the following email. 
        An action item is a task, request, or something that requires a response or action.
        List each action item separately.
        
        EMAIL:
        {}
        """.format(email_content)
        
        response = self.agent.run(prompt)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            return response.content
        
        # In a real implementation, you would parse the response into a proper list
        # For now, we'll just return the raw response
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
        prompt = f"""Generate a professional email template for: {template_type}
        """
        
        if customization:
            prompt += f"\nCustomization requirements: {customization}"
        
        response = self.agent.run(prompt)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            return response.content
        return response
    
    def search_emails(self, query: str, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Search emails based on a natural language query.
        
        Args:
            query: Natural language search query
            emails: List of email dictionaries to search through
            
        Returns:
            List of emails matching the query
        """
        # This is a simplified implementation
        # In a real implementation, you would use vector search or other techniques
        
        # Convert emails to a format suitable for the prompt
        email_text = ""
        for i, email in enumerate(emails):
            email_text += f"EMAIL {i+1}:\nFrom: {email['sender']}\nSubject: {email['subject']}\n\n{email['content']}\n\n"
        
        prompt = f"""Find emails that match the following search query: "{query}"
        
        Return the numbers of the emails that match the query and briefly explain why each one matches.
        
        EMAILS:
        {email_text}
        """
        
        response = self.agent.run(prompt)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            return response.content
        
        # In a real implementation, you would parse the response and return the matching emails
        # For now, we'll just return the raw response
        return response
