"""
Calendar MCP Tool
Provides calendar event management via Google Calendar API
"""

from typing import Dict, Any
from .base import MCPTool
from services.google_drive import google_services
from datetime import datetime
import json


class CalendarMCPTool(MCPTool):
    """MCP tool for Google Calendar operations"""

    def get_name(self) -> str:
        return "calendar"

    def get_description(self) -> str:
        return """Manage calendar events via Google Calendar API.

Operations:
- create_event: Schedule a new calendar event
- list_events: List upcoming events
- get_event: Get details of specific event
- update_event: Modify existing event
- delete_event: Cancel an event

Use for scheduling interviews, meetings, and managing calendar."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["create_event", "list_events", "get_event", "update_event", "delete_event"]},
                "summary": {"type": "string", "description": "Event title"},
                "start_time": {"type": "string", "description": "Start time (ISO format)"},
                "end_time": {"type": "string", "description": "End time (ISO format)"},
                "attendees": {"type": "array", "items": {"type": "string"}, "description": "Attendee emails"},
                "description": {"type": "string", "description": "Event description"},
                "event_id": {"type": "string", "description": "Event ID (for get/update/delete)"}
            },
            "required": ["operation"]
        }

    def execute(self, operation: str, **kwargs) -> str:
        try:
            if operation == "create_event":
                return self._create_event(**kwargs)
            elif operation == "list_events":
                return self._list_events(**kwargs)
            elif operation == "get_event":
                return self._get_event(**kwargs)
            elif operation == "update_event":
                return self._update_event(**kwargs)
            elif operation == "delete_event":
                return self._delete_event(**kwargs)
            else:
                return json.dumps({"error": f"Unknown operation: {operation}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _create_event(self, summary: str, start_time: str, end_time: str,
                      attendees: list = None, description: str = "", **kwargs) -> str:
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        created = google_services.calendar_service.events().insert(
            calendarId='primary', body=event, sendUpdates='all'
        ).execute()

        return json.dumps({
            "success": True,
            "event_id": created['id'],
            "link": created.get('htmlLink'),
            "message": f"Event '{summary}' created successfully"
        })

    def _list_events(self, max_results: int = 10, **kwargs) -> str:
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = google_services.calendar_service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        return json.dumps({
            "success": True,
            "count": len(events),
            "events": [{
                "id": e['id'],
                "summary": e.get('summary', 'No title'),
                "start": e['start'].get('dateTime', e['start'].get('date')),
                "end": e['end'].get('dateTime', e['end'].get('date')),
                "attendees": [a.get('email') for a in e.get('attendees', [])]
            } for e in events]
        }, indent=2)

    def _get_event(self, event_id: str, **kwargs) -> str:
        """Get details of a specific event"""
        if not event_id:
            return json.dumps({"error": "event_id required for get_event"})

        try:
            event = google_services.calendar_service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()

            return json.dumps({
                "success": True,
                "event": {
                    "id": event['id'],
                    "summary": event.get('summary', 'No title'),
                    "description": event.get('description', ''),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "location": event.get('location', ''),
                    "attendees": [
                        {
                            "email": a.get('email'),
                            "response_status": a.get('responseStatus')
                        }
                        for a in event.get('attendees', [])
                    ],
                    "link": event.get('htmlLink'),
                    "status": event.get('status')
                }
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to get event: {str(e)}"
            })

    def _update_event(self, event_id: str, summary: str = None, start_time: str = None,
                      end_time: str = None, attendees: list = None, description: str = None,
                      **kwargs) -> str:
        """Update an existing event"""
        if not event_id:
            return json.dumps({"error": "event_id required for update_event"})

        try:
            # Get existing event
            event = google_services.calendar_service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()

            # Update fields if provided
            if summary:
                event['summary'] = summary
            if description:
                event['description'] = description
            if start_time:
                event['start'] = {'dateTime': start_time, 'timeZone': 'UTC'}
            if end_time:
                event['end'] = {'dateTime': end_time, 'timeZone': 'UTC'}
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            # Update event
            updated = google_services.calendar_service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()

            return json.dumps({
                "success": True,
                "event_id": updated['id'],
                "link": updated.get('htmlLink'),
                "message": f"Event updated successfully"
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to update event: {str(e)}"
            })

    def _delete_event(self, event_id: str, **kwargs) -> str:
        """Delete/cancel an event"""
        if not event_id:
            return json.dumps({"error": "event_id required for delete_event"})

        try:
            google_services.calendar_service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()

            return json.dumps({
                "success": True,
                "message": f"Event deleted successfully",
                "event_id": event_id
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to delete event: {str(e)}"
            })
