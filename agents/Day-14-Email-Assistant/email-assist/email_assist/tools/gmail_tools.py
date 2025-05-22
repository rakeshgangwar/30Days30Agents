from typing import List, Dict, Any, Optional
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import Resource

class GmailTools:
    """
    Tools for interacting with Gmail API.
    """
    
    def __init__(self, service: Resource):
        """
        Initialize Gmail tools with an authenticated Gmail service.
        
        Args:
            service: Authenticated Gmail API service
        """
        self.service = service
    
    def list_messages(self, query: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List messages in the user's mailbox matching the query.
        
        Args:
            query: Search query (Gmail search syntax)
            max_results: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        try:
            # Get message IDs matching the query
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full message details for each ID
            detailed_messages = []
            for msg in messages:
                msg_details = self.get_message(msg['id'])
                if msg_details:
                    detailed_messages.append(msg_details)
            
            return detailed_messages
        
        except Exception as e:
            print(f"Error listing messages: {e}")
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
            # Get the full message details
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {}
            for header in message['payload']['headers']:
                headers[header['name'].lower()] = header['value']
            
            # Extract body content
            body = self._get_message_body(message['payload'])
            
            # Create a structured message object
            structured_message = {
                'id': message['id'],
                'threadId': message['threadId'],
                'labelIds': message.get('labelIds', []),
                'snippet': message.get('snippet', ''),
                'subject': headers.get('subject', '(No Subject)'),
                'from': headers.get('from', ''),
                'to': headers.get('to', ''),
                'date': headers.get('date', ''),
                'body': body,
                'raw_message': message  # Include the raw message for advanced processing
            }
            
            return structured_message
        
        except Exception as e:
            print(f"Error getting message {msg_id}: {e}")
            return None
    
    def _get_message_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract the message body from the payload.
        
        Args:
            payload: Message payload dictionary
            
        Returns:
            Message body as text
        """
        body = ""
        
        # Check if the payload has a body
        if 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        # If no body found and there are parts, check the parts
        elif 'parts' in payload:
            for part in payload['parts']:
                # Look for text/plain or text/html parts
                if part['mimeType'] in ['text/plain', 'text/html']:
                    if 'data' in part['body']:
                        part_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        body += part_body
                # Recursively check for nested parts
                elif 'parts' in part:
                    body += self._get_message_body(part)
        
        return body
    
    def send_message(self, to: str, subject: str, body: str, cc: str = None, bcc: str = None) -> bool:
        """
        Send an email message.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Email body content
            cc: Carbon copy recipient(s)
            bcc: Blind carbon copy recipient(s)
            
        Returns:
            True if the message was sent successfully, False otherwise
        """
        try:
            # Create a MIMEText message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send the message
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return True
        
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages in a thread.
        
        Args:
            thread_id: The ID of the thread to retrieve
            
        Returns:
            List of message dictionaries in the thread
        """
        try:
            # Get the thread
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()
            
            # Process each message in the thread
            messages = []
            for message in thread['messages']:
                # Extract headers
                headers = {}
                for header in message['payload']['headers']:
                    headers[header['name'].lower()] = header['value']
                
                # Extract body content
                body = self._get_message_body(message['payload'])
                
                # Create a structured message object
                structured_message = {
                    'id': message['id'],
                    'threadId': message['threadId'],
                    'labelIds': message.get('labelIds', []),
                    'snippet': message.get('snippet', ''),
                    'subject': headers.get('subject', '(No Subject)'),
                    'from': headers.get('from', ''),
                    'to': headers.get('to', ''),
                    'date': headers.get('date', ''),
                    'body': body
                }
                
                messages.append(structured_message)
            
            return messages
        
        except Exception as e:
            print(f"Error getting thread {thread_id}: {e}")
            return []
    
    def modify_message(self, msg_id: str, add_labels: List[str] = None, remove_labels: List[str] = None) -> bool:
        """
        Modify the labels of a message (e.g., mark as read, archive, etc.).
        
        Args:
            msg_id: The ID of the message to modify
            add_labels: List of labels to add
            remove_labels: List of labels to remove
            
        Returns:
            True if the modification was successful, False otherwise
        """
        try:
            # Prepare the modification request
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
            
            # Execute the modification
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body=body
            ).execute()
            
            return True
        
        except Exception as e:
            print(f"Error modifying message {msg_id}: {e}")
            return False
    
    def search_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for messages using Gmail's search syntax.
        
        Args:
            query: Search query using Gmail search operators
            max_results: Maximum number of results to return
            
        Returns:
            List of message dictionaries matching the query
        """
        return self.list_messages(query=query, max_results=max_results)
