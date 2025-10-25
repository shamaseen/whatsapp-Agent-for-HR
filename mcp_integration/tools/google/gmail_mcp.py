"""
Gmail MCP Tool
Provides email operations via Gmail API
"""

from typing import Dict, Any
from mcp_integration.tools.base import MCPTool
from services.google_drive import google_services
import base64
from email.mime.text import MIMEText
import json


class GmailMCPTool(MCPTool):
    """
    MCP tool for Gmail operations.
    Supports sending emails with future support for listing/reading.
    """

    def get_name(self) -> str:
        return "gmail"

    def get_description(self) -> str:
        return """Send and manage emails via Gmail API.

Operations:
- send_email: Send an email to one or more recipients
- get_emails: Get recent emails from inbox
- read_email: Read a specific email by ID
- reply_email: Reply to an email thread
- search_emails: Search emails by query

Use this tool to send email notifications, interview invitations, check inbox, and reply to candidates."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["send_email", "get_emails", "read_email", "reply_email", "search_emails"],
                    "description": "Operation to perform"
                },
                "to_email": {
                    "type": "string",
                    "description": "Recipient email address (for send_email)"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject (for send_email)"
                },
                "body": {
                    "type": "string",
                    "description": "Email body content (for send_email, reply_email)"
                },
                "cc": {
                    "type": "string",
                    "description": "CC recipients, comma-separated (optional)"
                },
                "bcc": {
                    "type": "string",
                    "description": "BCC recipients, comma-separated (optional)"
                },
                "message_id": {
                    "type": "string",
                    "description": "Email message ID (for read_email, reply_email)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of emails to retrieve (for get_emails, search_emails)"
                },
                "query": {
                    "type": "string",
                    "description": "Search query (for search_emails)"
                }
            },
            "required": ["operation"]
        }

    def execute(self, operation: str, to_email: str = None, subject: str = None,
                body: str = None, cc: str = None, bcc: str = None,
                message_id: str = None, max_results: int = 10, query: str = None, **kwargs) -> str:
        """Execute Gmail operation"""

        try:
            if operation == "send_email":
                if not all([to_email, subject, body]):
                    return json.dumps({
                        "error": "to_email, subject, and body required for send_email"
                    })
                return self._send_email(to_email, subject, body, cc, bcc)

            elif operation == "get_emails":
                return self._get_emails(max_results)

            elif operation == "read_email":
                if not message_id:
                    return json.dumps({"error": "message_id required for read_email"})
                return self._read_email(message_id)

            elif operation == "reply_email":
                if not all([message_id, body]):
                    return json.dumps({"error": "message_id and body required for reply_email"})
                return self._reply_email(message_id, body)

            elif operation == "search_emails":
                if not query:
                    return json.dumps({"error": "query required for search_emails"})
                return self._search_emails(query, max_results)

            else:
                return json.dumps({"error": f"Unknown operation: {operation}"})

        except Exception as e:
            return json.dumps({"error": str(e)})

    def _send_email(self, to_email: str, subject: str, body: str,
                    cc: str = None, bcc: str = None) -> str:
        """Send an email via Gmail API"""
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject

            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send via Gmail API
            send_message = google_services.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return json.dumps({
                "success": True,
                "message": f"Email sent successfully to {to_email}",
                "message_id": send_message.get('id'),
                "thread_id": send_message.get('threadId')
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            })

    def _get_emails(self, max_results: int = 10) -> str:
        """Get recent emails from inbox"""
        try:
            # List messages from inbox
            results = google_services.gmail_service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return json.dumps({
                    "success": True,
                    "emails": [],
                    "count": 0,
                    "message": "No emails found"
                })

            # Get details for each message
            emails = []
            for msg in messages:
                msg_data = google_services.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}

                emails.append({
                    "id": msg['id'],
                    "thread_id": msg_data.get('threadId'),
                    "from": headers.get('From', 'Unknown'),
                    "subject": headers.get('Subject', 'No Subject'),
                    "date": headers.get('Date', 'Unknown'),
                    "snippet": msg_data.get('snippet', '')[:200]
                })

            return json.dumps({
                "success": True,
                "emails": emails,
                "count": len(emails)
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to get emails: {str(e)}"
            })

    def _read_email(self, message_id: str) -> str:
        """Read a specific email by ID"""
        try:
            # Get full message
            msg_data = google_services.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            payload = msg_data.get('payload', {})
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}

            # Extract body
            body = ""
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_data = part.get('body', {}).get('data', '')
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                            break
            else:
                body_data = payload.get('body', {}).get('data', '')
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')

            return json.dumps({
                "success": True,
                "email": {
                    "id": message_id,
                    "thread_id": msg_data.get('threadId'),
                    "from": headers.get('From', 'Unknown'),
                    "to": headers.get('To', 'Unknown'),
                    "subject": headers.get('Subject', 'No Subject'),
                    "date": headers.get('Date', 'Unknown'),
                    "body": body,
                    "snippet": msg_data.get('snippet', '')
                }
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to read email: {str(e)}"
            })

    def _reply_email(self, message_id: str, body: str) -> str:
        """Reply to an email thread"""
        try:
            # Get original message to extract thread_id and subject
            original_msg = google_services.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['Subject', 'From', 'Message-ID']
            ).execute()

            headers = {h['name']: h['value'] for h in original_msg.get('payload', {}).get('headers', [])}
            thread_id = original_msg.get('threadId')
            original_subject = headers.get('Subject', '')
            original_from = headers.get('From', '')
            original_msg_id = headers.get('Message-ID', '')

            # Extract email from "Name <email>" format
            import re
            email_match = re.search(r'<(.+?)>', original_from)
            to_email = email_match.group(1) if email_match else original_from

            # Create reply subject
            reply_subject = original_subject if original_subject.startswith('Re:') else f"Re: {original_subject}"

            # Create reply message
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = reply_subject
            message['In-Reply-To'] = original_msg_id
            message['References'] = original_msg_id

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send as part of thread
            send_message = google_services.gmail_service.users().messages().send(
                userId='me',
                body={
                    'raw': raw_message,
                    'threadId': thread_id
                }
            ).execute()

            return json.dumps({
                "success": True,
                "message": f"Reply sent successfully to {to_email}",
                "message_id": send_message.get('id'),
                "thread_id": send_message.get('threadId')
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to reply to email: {str(e)}"
            })

    def _search_emails(self, query: str, max_results: int = 10) -> str:
        """Search emails by query"""
        try:
            # Search messages
            results = google_services.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return json.dumps({
                    "success": True,
                    "emails": [],
                    "count": 0,
                    "message": f"No emails found matching query: {query}"
                })

            # Get details for each message
            emails = []
            for msg in messages:
                msg_data = google_services.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}

                emails.append({
                    "id": msg['id'],
                    "thread_id": msg_data.get('threadId'),
                    "from": headers.get('From', 'Unknown'),
                    "subject": headers.get('Subject', 'No Subject'),
                    "date": headers.get('Date', 'Unknown'),
                    "snippet": msg_data.get('snippet', '')[:200]
                })

            return json.dumps({
                "success": True,
                "query": query,
                "emails": emails,
                "count": len(emails)
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to search emails: {str(e)}"
            })
