from typing import List
from langchain_core.tools import tool
from src.integrations.google import google_services

@tool
def schedule_calendar_event(title: str, start_time: str, end_time: str, attendees: List[str]) -> str:
    """Create a Google Calendar event.

    Args:
        title: Event title
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        attendees: List of email addresses
    """
    event = {
        'summary': title,
        'start': {'dateTime': start_time, 'timeZone': 'UTC'},
        'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        'attendees': [{'email': email} for email in attendees]
    }
    result = google_services.calendar_service.events().insert(calendarId='primary', body=event).execute()
    return f"Event created: {result.get('htmlLink')}"
