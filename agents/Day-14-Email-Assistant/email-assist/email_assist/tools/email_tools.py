from typing import Dict, Any, List, Optional, Union
from agno.tools import tool
from email_assist.tools.gmail_tools import GmailTools
from email_assist.tools.ms_graph_tools import MSGraphTools

class EmailTools:
    """
    Email tools for interacting with Gmail or Microsoft Graph APIs.
    """
    
    def __init__(self, email_service: Union[GmailTools, MSGraphTools]):
        """
        Initialize the email tools with an email service.
        
        Args:
            email_service: An instance of GmailTools or MSGraphTools
        """
        self.email_service = email_service
        self.is_gmail = isinstance(email_service, GmailTools)
    
    @tool(show_result=True)
    def list_messages(self, query: Optional[str] = None, folder: str = "inbox", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List messages in the user's mailbox.
        
        Args:
            query: Search query for filtering messages (optional)
            folder: The mail folder to list messages from (default: inbox, only used for Microsoft Graph)
            max_results: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        if self.is_gmail:
            return self.email_service.list_messages(query=query, max_results=max_results)
        else:  # Microsoft Graph
            return self.email_service.list_messages(folder=folder, query=query, max_results=max_results)
    
    @tool(show_result=True)
    def get_message(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific message by ID.
        
        Args:
            msg_id: The ID of the message to retrieve
            
        Returns:
            Message dictionary or None if an error occurs
        """
        return self.email_service.get_message(msg_id)
    
    @tool(show_result=True)
    def send_message(self, to: str, subject: str, body: str, cc: Optional[str] = None, bcc: Optional[str] = None) -> bool:
        """
        Send an email message.
        
        Args:
            to: Recipient email address(es) - comma-separated string for multiple recipients
            subject: Email subject
            body: Email body content
            cc: Carbon copy recipient(s) - comma-separated string for multiple recipients
            bcc: Blind carbon copy recipient(s) - comma-separated string for multiple recipients
            
        Returns:
            True if the message was sent successfully, False otherwise
        """
        if self.is_gmail:
            return self.email_service.send_message(to=to, subject=subject, body=body, cc=cc, bcc=bcc)
        else:  # Microsoft Graph
            # Convert comma-separated strings to lists for Microsoft Graph API
            to_list = [email.strip() for email in to.split(',')] if to else []
            cc_list = [email.strip() for email in cc.split(',')] if cc else None
            bcc_list = [email.strip() for email in bcc.split(',')] if bcc else None
            return self.email_service.send_message(to=to_list, subject=subject, body=body, cc=cc_list, bcc=bcc_list)
    
    @tool(show_result=True)
    def get_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages in an email thread/conversation.
        
        Args:
            thread_id: The ID of the thread/conversation to retrieve
            
        Returns:
            List of message dictionaries in the thread/conversation
        """
        if self.is_gmail:
            return self.email_service.get_thread(thread_id)
        else:  # Microsoft Graph
            return self.email_service.get_conversation(thread_id)
    
    @tool(show_result=True)
    def update_message(self, msg_id: str, is_read: Optional[bool] = None, add_labels: Optional[List[str]] = None, remove_labels: Optional[List[str]] = None) -> bool:
        """
        Update an email message (e.g., mark as read/unread, add/remove labels).
        
        Args:
            msg_id: The ID of the message to update
            is_read: Whether to mark the message as read (True) or unread (False)
            add_labels: List of labels to add (Gmail only)
            remove_labels: List of labels to remove (Gmail only)
            
        Returns:
            True if the update was successful, False otherwise
        """
        if self.is_gmail:
            return self.email_service.modify_message(msg_id=msg_id, add_labels=add_labels, remove_labels=remove_labels)
        else:  # Microsoft Graph
            return self.email_service.update_message(msg_id=msg_id, is_read=is_read)
    
    @tool(show_result=True)
    def search_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for email messages using a search query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of message dictionaries matching the query
        """
        return self.email_service.search_messages(query=query, max_results=max_results)
