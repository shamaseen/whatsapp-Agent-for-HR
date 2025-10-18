from typing import List, Optional
from datetime import datetime
from langchain_core.tools import tool
from config import settings
import requests

class WebexClient:
    """Webex API client with OAuth2 support"""

    def __init__(self):
        self.base_url = "https://webexapis.com/v1"
        self.access_token = settings.WEBEX_ACCESS_TOKEN

        # If using Client ID/Secret, you'd implement OAuth2 flow here
        if not self.access_token and settings.WEBEX_CLIENT_ID:
            # Note: Full OAuth2 implementation requires user authorization flow
            # For production, use webexteamssdk or implement full OAuth2
            raise ValueError("Webex requires either ACCESS_TOKEN or full OAuth2 implementation")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def create_meeting(
        self,
        title: str,
        start: str,
        end: str,
        invitees: Optional[List[str]] = None
    ) -> dict:
        """Create a Webex meeting"""
        url = f"{self.base_url}/meetings"
        payload = {
            "title": title,
            "start": start,
            "end": end,
            "timezone": "UTC"
        }

        if invitees:
            payload["invitees"] = [{"email": email} for email in invitees]

        response = requests.post(url, json=payload, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def get_meeting(self, meeting_id: str) -> dict:
        """Get meeting details"""
        url = f"{self.base_url}/meetings/{meeting_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting"""
        url = f"{self.base_url}/meetings/{meeting_id}"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()
        return True

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
    invitees: List[str]
) -> str:
    """Create a Webex meeting.

    Args:
        title: Meeting title
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        invitees: List of email addresses to invite
    """
    if not webex_client:
        return "Webex is not configured. Please set WEBEX_ACCESS_TOKEN or WEBEX_CLIENT_ID/SECRET."

    try:
        meeting = webex_client.create_meeting(title, start_time, end_time, invitees)
        meeting_url = meeting.get('webLink', 'N/A')
        meeting_id = meeting.get('id', 'N/A')
        return f"Webex meeting created!\nMeeting ID: {meeting_id}\nJoin URL: {meeting_url}"
    except Exception as e:
        return f"Error creating Webex meeting: {str(e)}"

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
        return f"""Meeting Details:
Title: {meeting.get('title')}
Start: {meeting.get('start')}
End: {meeting.get('end')}
Join URL: {meeting.get('webLink')}
"""
    except Exception as e:
        return f"Error retrieving meeting: {str(e)}"
