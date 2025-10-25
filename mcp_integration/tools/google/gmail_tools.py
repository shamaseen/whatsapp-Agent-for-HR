import base64
from email.mime.text import MIMEText
from langchain_core.tools import tool
from services.google_drive import google_services

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
    """
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    google_services.gmail_service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
    return f"Email sent to {to}"
