import base64
import re
from email.mime.text import MIMEText
from langchain_core.tools import tool
from src.integrations.google import google_services

# Email validation pattern
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
    """
    # Validate email address
    if not re.match(EMAIL_PATTERN, to):
        return f"Error: Invalid email address format: {to}"

    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Execute send and verify result
        result = google_services.gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        # Verify message was sent successfully
        if not result or 'id' not in result:
            return f"Error: Failed to send email to {to} (no message ID returned)"

        return f"Email sent successfully to {to} (Message ID: {result.get('id')})"

    except Exception as e:
        return f"Error sending email to {to}: {str(e)}"
