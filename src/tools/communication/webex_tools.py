"""
Webex Tools - LangChain tool wrappers for Webex meetings
Uses WebexClient from src.integrations.webex_sdk (single source of truth)
"""

from typing import List, Optional
from langchain_core.tools import tool

# Import webex_client from the integrations module (avoid code duplication)
from src.integrations.webex_sdk import webex_client


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
            except Exception as e:
                # If we can't get meeting details, continue with generic title
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
