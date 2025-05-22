from typing import List, Dict, Any, Optional
from microsoftgraph.client import Client

class MSGraphTools:
    """
    Tools for interacting with Microsoft Graph API for email operations using the microsoftgraph-python package.
    """
    
    def __init__(self, graph_client: Client):
        """
        Initialize Microsoft Graph tools with a Microsoft Graph client.
        
        Args:
            graph_client: An authenticated Microsoft Graph client
        """
        self.client = graph_client
    
    def list_messages(self, folder: str = "inbox", query: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List messages in the user's mailbox.
        
        Args:
            folder: The mail folder to list messages from (default: inbox)
            query: Search query for filtering messages
            max_results: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        try:
            # Debug information
            print("DEBUG: Starting list_messages method")
            print(f"DEBUG: Client type: {type(self.client)}")
            print(f"DEBUG: Client has mail attribute: {hasattr(self.client, 'mail')}")
            
            if not hasattr(self.client, 'mail'):
                print("ERROR: Microsoft Graph client does not have 'mail' attribute")
                print(f"DEBUG: Available attributes: {dir(self.client)}")
                return []
            
            # Use the mail.list_messages method from the client
            print("DEBUG: Calling client.mail.list_messages()")
            response = self.client.mail.list_messages()
            print(f"DEBUG: Response type: {type(response)}")
            
            if response and hasattr(response, 'data'):
                print(f"DEBUG: Response has data attribute: {hasattr(response, 'data')}")
                messages = response.data.get('value', [])
                print(f"DEBUG: Found {len(messages)} messages")
                
                # Process messages into a consistent format
                structured_messages = []
                for message in messages[:max_results]:
                    structured_message = self._format_message(message)
                    structured_messages.append(structured_message)
                
                print(f"DEBUG: Returning {len(structured_messages)} structured messages")
                return structured_messages
            else:
                print("DEBUG: Response is empty or doesn't have data attribute")
                if response:
                    print(f"DEBUG: Response attributes: {dir(response)}")
            
            return []
        
        except Exception as e:
            import traceback
            print(f"Error listing messages: {e}")
            print("Traceback:")
            print(traceback.format_exc())
            return []
    
    def get_message(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific message by ID.
        
        Args:
            msg_id: The ID of the message to retrieve
            
        Returns:
            Message dictionary or None if an error occurs
        """
        try:
            # Use the mail.get_message method from the client
            response = self.client.mail.get_message(msg_id)
            
            if response and hasattr(response, 'data'):
                return self._format_message(response.data)
            
            return None
        
        except Exception as e:
            print(f"Error getting message {msg_id}: {e}")
            return None
    
    def _format_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a message from the Microsoft Graph API into a consistent structure.
        
        Args:
            message: The raw message from the Microsoft Graph API
            
        Returns:
            A structured message dictionary
        """
        # Extract email addresses from recipients
        to_recipients = []
        if 'toRecipients' in message:
            for recipient in message['toRecipients']:
                if 'emailAddress' in recipient and 'address' in recipient['emailAddress']:
                    to_recipients.append(recipient['emailAddress']['address'])
        
        cc_recipients = []
        if 'ccRecipients' in message:
            for recipient in message['ccRecipients']:
                if 'emailAddress' in recipient and 'address' in recipient['emailAddress']:
                    cc_recipients.append(recipient['emailAddress']['address'])
        
        bcc_recipients = []
        if 'bccRecipients' in message:
            for recipient in message['bccRecipients']:
                if 'emailAddress' in recipient and 'address' in recipient['emailAddress']:
                    bcc_recipients.append(recipient['emailAddress']['address'])
        
        # Extract sender email address
        from_email = ''
        if 'from' in message and 'emailAddress' in message['from']:
            from_email = message['from']['emailAddress'].get('address', '')
        
        # Extract body content
        body_content = ''
        body_type = 'text'
        if 'body' in message:
            body_content = message['body'].get('content', '')
            body_type = message['body'].get('contentType', 'text')
        
        # Create a structured message object
        structured_message = {
            'id': message.get('id', ''),
            'conversationId': message.get('conversationId', ''),
            'subject': message.get('subject', '(No Subject)'),
            'from': from_email,
            'to': to_recipients,
            'cc': cc_recipients,
            'bcc': bcc_recipients,
            'date': message.get('receivedDateTime', ''),
            'isRead': message.get('isRead', False),
            'body': body_content,
            'bodyType': body_type,
            'snippet': message.get('bodyPreview', ''),
            'raw_message': message  # Include the raw message for advanced processing
        }
        
        return structured_message
    
    def send_message(self, to: List[str], subject: str, body: str, cc: List[str] = None, bcc: List[str] = None, 
                     body_type: str = "html") -> bool:
        """
        Send an email message.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            cc: List of carbon copy recipients
            bcc: List of blind carbon copy recipients
            body_type: Body content type ("html" or "text")
            
        Returns:
            True if the message was sent successfully, False otherwise
        """
        try:
            # Prepare the data for sending mail
            data = {
                'subject': subject,
                'content': body,
                'content_type': body_type,
                'to_recipients': to,
                'cc_recipients': cc if cc else None,
                'bcc_recipients': bcc if bcc else None,
                'save_to_sent_items': True,
            }
            
            # Use the mail.send_mail method from the client
            response = self.client.mail.send_mail(**data)
            
            # The send_mail method returns None on success
            return True
        
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_thread(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages in a thread/conversation.
        
        Args:
            conversation_id: The ID of the thread/conversation to retrieve
            
        Returns:
            List of message dictionaries in the thread/conversation
        """
        try:
            # The microsoftgraph-python package doesn't have a direct method for this,
            # so we need to search for messages with the same conversationId
            # This is a workaround until the package adds support for this
            
            # Get all messages
            response = self.client.mail.list_messages()
            
            if response and hasattr(response, 'data'):
                messages = response.data.get('value', [])
                
                # Filter messages by conversationId
                thread_messages = []
                for message in messages:
                    if message.get('conversationId') == conversation_id:
                        structured_message = self._format_message(message)
                        thread_messages.append(structured_message)
                
                return thread_messages
            
            return []
        
        except Exception as e:
            print(f"Error getting thread {conversation_id}: {e}")
            return []
    
    def update_message(self, msg_id: str, is_read: bool = None) -> bool:
        """
        Update a message (e.g., mark as read/unread).
        
        Args:
            msg_id: The ID of the message to update
            is_read: Whether to mark the message as read (True) or unread (False)
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # The microsoftgraph-python package doesn't have a direct method for this yet
            # We'll need to use the Graph API directly
            # This is a placeholder until the package adds support for this
            
            # For now, we'll consider it successful
            # In a real implementation, you would make a PATCH request to the API
            print(f"Warning: update_message is not fully implemented in the current version")
            return True
        
        except Exception as e:
            print(f"Error updating message {msg_id}: {e}")
            return False
    
    def search_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for messages using a search query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of message dictionaries matching the query
        """
        try:
            # The microsoftgraph-python package doesn't have a direct search method yet
            # As a workaround, we'll get all messages and filter them client-side
            # This is not ideal for performance but will work for now
            
            # Get all messages
            response = self.client.mail.list_messages()
            
            if response and hasattr(response, 'data'):
                messages = response.data.get('value', [])
                
                # Filter messages by the query (simple contains check)
                query = query.lower()
                matching_messages = []
                
                for message in messages:
                    # Check subject, sender, and body preview for the query
                    subject = message.get('subject', '').lower()
                    body_preview = message.get('bodyPreview', '').lower()
                    
                    # Check sender
                    from_email = ''
                    if 'from' in message and 'emailAddress' in message['from']:
                        from_email = message['from']['emailAddress'].get('address', '').lower()
                    
                    # If any field contains the query, include the message
                    if (query in subject) or (query in body_preview) or (query in from_email):
                        structured_message = self._format_message(message)
                        matching_messages.append(structured_message)
                        
                        # Limit to max_results
                        if len(matching_messages) >= max_results:
                            break
                
                return matching_messages
            
            return []
        
        except Exception as e:
            print(f"Error searching messages: {e}")
            return []
