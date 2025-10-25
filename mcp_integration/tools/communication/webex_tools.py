from typing import List, Optional
from datetime import datetime
from langchain_core.tools import tool
from config import settings
import json
import os
from pathlib import Path

try:
    from webexteamssdk import WebexTeamsAPI
    from webexteamssdk.exceptions import ApiError
    WEBEX_SDK_AVAILABLE = True
except ImportError:
    WEBEX_SDK_AVAILABLE = False
    print("Warning: webexteamssdk not installed. Install with: pip install webexteamssdk")


class WebexClient:
    """Webex API client with OAuth2 support using webexteamssdk"""

    def __init__(self):
        if not WEBEX_SDK_AVAILABLE:
            raise ImportError("webexteamssdk is required. Install with: pip install webexteamssdk")

        self.token_file = Path(getattr(settings, 'WEBEX_TOKEN_FILE', '.webex_token.json'))
        self.client_id = settings.WEBEX_CLIENT_ID
        self.client_secret = settings.WEBEX_CLIENT_SECRET
        self.redirect_uri = getattr(settings, 'WEBEX_REDIRECT_URI', 'http://localhost:8000/oauth/webex/callback')

        # Try to load existing access token
        access_token = self._load_token()

        if not access_token:
            # Use direct access token if provided
            access_token = settings.WEBEX_ACCESS_TOKEN

        if not access_token and self.client_id and self.client_secret:
            raise ValueError(
                "Webex OAuth2 setup required:\n"
                "1. Run the OAuth flow to get an access token\n"
                "2. Or set WEBEX_ACCESS_TOKEN directly in .env\n"
                f"Authorization URL: https://webexapis.com/v1/authorize?client_id={self.client_id}&response_type=code&redirect_uri={self.redirect_uri}&scope=spark:all"
            )

        if not access_token:
            raise ValueError("No Webex credentials found. Set WEBEX_ACCESS_TOKEN or WEBEX_CLIENT_ID/SECRET")

        self.api = WebexTeamsAPI(access_token=access_token)

    def _load_token(self) -> Optional[str]:
        """Load access token from file"""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    return data.get('access_token')
            except Exception as e:
                print(f"Error loading token file: {e}")
        return None

    def _save_token(self, access_token: str, refresh_token: Optional[str] = None):
        """Save access token to file"""
        data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        with open(self.token_file, 'w') as f:
            json.dump(data, f)

    def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        import requests

        url = "https://webexapis.com/v1/access_token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(url, data=data)
        response.raise_for_status()
        token_data = response.json()

        # Save tokens
        self._save_token(
            token_data['access_token'],
            token_data.get('refresh_token')
        )

        # Reinitialize API with new token
        self.api = WebexTeamsAPI(access_token=token_data['access_token'])

        return token_data

    def create_meeting(
        self,
        title: str,
        start: str,
        end: str,
        invitees: Optional[List[str]] = None
    ) -> dict:
        """Create a Webex meeting"""
        try:
            meeting = self.api.meetings.create(
                title=title,
                start=start,
                end=end,
                timezone='UTC',
                invitees=[{'email': email} for email in invitees] if invitees else None
            )
            return meeting.to_dict()
        except ApiError as e:
            raise Exception(f"Webex API error: {e}")

    def get_meeting(self, meeting_id: str) -> dict:
        """Get meeting details"""
        try:
            meeting = self.api.meetings.get(meeting_id)
            return meeting.to_dict()
        except ApiError as e:
            raise Exception(f"Webex API error: {e}")

    def list_meetings(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        max_meetings: int = 100
    ) -> list:
        """List all meetings"""
        try:
            meetings = self.api.meetings.list(
                from_=from_date,
                to=to_date,
                max=max_meetings
            )
            return [meeting.to_dict() for meeting in meetings]
        except ApiError as e:
            raise Exception(f"Webex API error: {e}")

    def update_meeting(
        self,
        meeting_id: str,
        title: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        invitees: Optional[List[str]] = None
    ) -> dict:
        """Update an existing meeting"""
        try:
            update_data = {}
            if title:
                update_data['title'] = title
            if start:
                update_data['start'] = start
            if end:
                update_data['end'] = end
            if invitees:
                update_data['invitees'] = [{'email': email} for email in invitees]

            meeting = self.api.meetings.update(meeting_id, **update_data)
            return meeting.to_dict()
        except ApiError as e:
            raise Exception(f"Webex API error: {e}")

    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting"""
        try:
            self.api.meetings.delete(meeting_id)
            return True
        except ApiError as e:
            raise Exception(f"Webex API error: {e}")

    def send_meeting_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email notification about meeting using Gmail integration"""
        try:
            from mcp_integration.tools.google.gmail_tools import send_email
            result = send_email.invoke({"to": to_email, "subject": subject, "body": body})
            return "sent successfully" in result.lower()
        except Exception as e:
            print(f"Warning: Could not send email notification: {e}")
            return False

# Initialize client if credentials available
webex_client = None
if settings.WEBEX_ACCESS_TOKEN or (settings.WEBEX_CLIENT_ID and settings.WEBEX_CLIENT_SECRET):
    try:
        webex_client = WebexClient()
    except Exception as e:
        print(f"Warning: Could not initialize Webex client: {e}")

@tool
def schedule_webex_meeting(
    title: str,
    start_time: str,
    end_time: str,
    invitees: List[str],
    send_email: bool = True
) -> str:
    """Create a Webex meeting and optionally send email notifications.

    Args:
        title: Meeting title
        start_time: Start time (ISO format, e.g., '2024-01-15T14:00:00Z')
        end_time: End time (ISO format)
        invitees: List of email addresses to invite
        send_email: Whether to send email notifications to invitees (default: True)
    """
    if not webex_client:
        return "Webex is not configured. Please set WEBEX_ACCESS_TOKEN or WEBEX_CLIENT_ID/SECRET."

    try:
        meeting = webex_client.create_meeting(title, start_time, end_time, invitees)
        meeting_url = meeting.get('webLink', 'N/A')
        meeting_id = meeting.get('id', 'N/A')

        result = f"✅ Webex meeting created!\nMeeting ID: {meeting_id}\nJoin URL: {meeting_url}"

        # Send email notifications if requested
        if send_email and invitees:
            email_subject = f"Webex Meeting Invitation: {title}"
            email_body = f"""
You have been invited to a Webex meeting.

Meeting: {title}
Start Time: {start_time}
End Time: {end_time}

Join URL: {meeting_url}

Meeting ID: {meeting_id}

Please join the meeting at the scheduled time.
"""
            for email in invitees:
                if webex_client.send_meeting_email(email, email_subject, email_body):
                    result += f"\n📧 Email sent to {email}"
                else:
                    result += f"\n⚠️  Failed to send email to {email}"

        return result
    except Exception as e:
        return f"Error creating Webex meeting: {str(e)}"


@tool
def list_webex_meetings(
    from_date: str = None,
    to_date: str = None,
    max_meetings: int = 10
) -> str:
    """List Webex meetings within a date range.

    Args:
        from_date: Start date (ISO format, optional)
        to_date: End date (ISO format, optional)
        max_meetings: Maximum number of meetings to return (default: 10)
    """
    if not webex_client:
        return "Webex is not configured."

    try:
        meetings = webex_client.list_meetings(from_date, to_date, max_meetings)

        if not meetings:
            return "No meetings found."

        result = f"📅 Found {len(meetings)} meeting(s):\n\n"
        for i, meeting in enumerate(meetings, 1):
            result += f"{i}. {meeting.get('title')}\n"
            result += f"   ID: {meeting.get('id')}\n"
            result += f"   Start: {meeting.get('start')}\n"
            result += f"   Join: {meeting.get('webLink')}\n\n"

        return result
    except Exception as e:
        return f"Error listing meetings: {str(e)}"


@tool
def get_webex_meeting_details(meeting_id: str) -> str:
    """Get details of a Webex meeting.

    Args:
        meeting_id: The Webex meeting ID
    """
    if not webex_client:
        return "Webex is not configured."

    try:
        meeting = webex_client.get_meeting(meeting_id)
        return f"""📋 Meeting Details:
Title: {meeting.get('title')}
Meeting ID: {meeting.get('id')}
Start: {meeting.get('start')}
End: {meeting.get('end')}
Join URL: {meeting.get('webLink')}
Status: {meeting.get('state', 'N/A')}
"""
    except Exception as e:
        return f"Error retrieving meeting: {str(e)}"


@tool
def update_webex_meeting(
    meeting_id: str,
    title: str = None,
    start_time: str = None,
    end_time: str = None,
    invitees: List[str] = None,
    send_email: bool = False
) -> str:
    """Update an existing Webex meeting.

    Args:
        meeting_id: The Webex meeting ID
        title: New meeting title (optional)
        start_time: New start time in ISO format (optional)
        end_time: New end time in ISO format (optional)
        invitees: New list of invitee emails (optional)
        send_email: Whether to send email notifications about the update (default: False)
    """
    if not webex_client:
        return "Webex is not configured."

    try:
        meeting = webex_client.update_meeting(meeting_id, title, start_time, end_time, invitees)
        result = f"✅ Meeting updated successfully!\n"
        result += f"Meeting ID: {meeting.get('id')}\n"
        result += f"Title: {meeting.get('title')}\n"
        result += f"Join URL: {meeting.get('webLink')}"

        # Send update notification emails if requested
        if send_email and invitees:
            email_subject = f"Webex Meeting Updated: {meeting.get('title')}"
            email_body = f"""
The Webex meeting has been updated.

Meeting: {meeting.get('title')}
Start Time: {meeting.get('start')}
End Time: {meeting.get('end')}

Join URL: {meeting.get('webLink')}

Please note the updated details.
"""
            for email in invitees:
                if webex_client.send_meeting_email(email, email_subject, email_body):
                    result += f"\n📧 Update notification sent to {email}"

        return result
    except Exception as e:
        return f"Error updating meeting: {str(e)}"


@tool
def delete_webex_meeting(meeting_id: str, send_email: bool = False, invitees: List[str] = None) -> str:
    """Delete/cancel a Webex meeting.

    Args:
        meeting_id: The Webex meeting ID to delete
        send_email: Whether to send cancellation email to invitees (default: False)
        invitees: List of emails to notify about cancellation (required if send_email=True)
    """
    if not webex_client:
        return "Webex is not configured."

    try:
        # Get meeting details before deletion for email notification
        meeting_title = "Meeting"
        if send_email and invitees:
            try:
                meeting = webex_client.get_meeting(meeting_id)
                meeting_title = meeting.get('title', 'Meeting')
            except:
                pass

        # Delete the meeting
        webex_client.delete_meeting(meeting_id)
        result = f"✅ Meeting {meeting_id} deleted successfully."

        # Send cancellation emails if requested
        if send_email and invitees:
            email_subject = f"Webex Meeting Cancelled: {meeting_title}"
            email_body = f"""
The following Webex meeting has been cancelled:

Meeting: {meeting_title}
Meeting ID: {meeting_id}

We apologize for any inconvenience.
"""
            for email in invitees:
                if webex_client.send_meeting_email(email, email_subject, email_body):
                    result += f"\n📧 Cancellation notice sent to {email}"
                else:
                    result += f"\n⚠️  Failed to send cancellation notice to {email}"

        return result
    except Exception as e:
        return f"Error deleting meeting: {str(e)}"
