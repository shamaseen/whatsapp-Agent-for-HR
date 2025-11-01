"""
Example: Fixed Calendar Tool with Proper Array Schema for Gemini
"""

from typing import Dict, Any
from src.mcp_integration.protocol import MCPTool
import json


class CalendarMCPTool(MCPTool):
    """MCP tool for calendar operations"""

    def get_name(self) -> str:
        return "calendar"

    def get_description(self) -> str:
        return """Manage calendar events and schedules.

Operations:
- create_event: Create a new calendar event
- list_events: List upcoming events
- update_event: Update an existing event
- delete_event: Delete an event
- check_availability: Check if time slots are available"""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["create_event", "list_events", "update_event", "delete_event", "check_availability"],
                    "description": "The calendar operation to perform"
                },
                "event_title": {
                    "type": "string",
                    "description": "Title of the event"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format (YYYY-MM-DDTHH:MM:SS)"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format (YYYY-MM-DDTHH:MM:SS)"
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},  # ← CRITICAL: Must specify items for Gemini
                    "description": "List of attendee email addresses"
                },
                "description": {
                    "type": "string",
                    "description": "Event description"
                },
                "location": {
                    "type": "string",
                    "description": "Event location"
                },
                "event_id": {
                    "type": "string",
                    "description": "Event ID for update/delete operations"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of events to return"
                },
                "time_min": {
                    "type": "string",
                    "description": "Start of time range for event listing"
                },
                "time_max": {
                    "type": "string",
                    "description": "End of time range for event listing"
                }
            },
            "required": ["operation"]
        }

    def execute(self, **kwargs) -> str:
        """Execute calendar operation"""
        try:
            operation = kwargs.get("operation")
            
            if not operation:
                return json.dumps({"error": "Missing required parameter: operation"})
            
            if operation == "create_event":
                return self._create_event(**kwargs)
            elif operation == "list_events":
                return self._list_events(**kwargs)
            elif operation == "update_event":
                return self._update_event(**kwargs)
            elif operation == "delete_event":
                return self._delete_event(**kwargs)
            elif operation == "check_availability":
                return self._check_availability(**kwargs)
            else:
                return json.dumps({"error": f"Unknown operation: {operation}"})
                
        except Exception as e:
            return json.dumps({"error": str(e), "type": type(e).__name__})

    def _create_event(self, **kwargs) -> str:
        """Create a calendar event"""
        event_title = kwargs.get("event_title")
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")
        attendees = kwargs.get("attendees", [])
        description = kwargs.get("description", "")
        location = kwargs.get("location", "")
        
        if not event_title or not start_time or not end_time:
            return json.dumps({
                "error": "Missing required fields: event_title, start_time, end_time"
            })
        
        # Your implementation here
        return json.dumps({
            "success": True,
            "message": "Event created successfully",
            "event_id": "mock_event_123",
            "event_title": event_title,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees,
            "location": location
        })

    def _list_events(self, **kwargs) -> str:
        """List calendar events"""
        max_results = kwargs.get("max_results", 10)
        time_min = kwargs.get("time_min")
        time_max = kwargs.get("time_max")
        
        # Your implementation here
        return json.dumps({
            "success": True,
            "events": [],
            "count": 0
        })

    def _update_event(self, **kwargs) -> str:
        """Update a calendar event"""
        event_id = kwargs.get("event_id")
        
        if not event_id:
            return json.dumps({"error": "Missing required field: event_id"})
        
        # Your implementation here
        return json.dumps({
            "success": True,
            "message": f"Event {event_id} updated successfully"
        })

    def _delete_event(self, **kwargs) -> str:
        """Delete a calendar event"""
        event_id = kwargs.get("event_id")
        
        if not event_id:
            return json.dumps({"error": "Missing required field: event_id"})
        
        # Your implementation here
        return json.dumps({
            "success": True,
            "message": f"Event {event_id} deleted successfully"
        })

    def _check_availability(self, **kwargs) -> str:
        """Check calendar availability"""
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")
        
        if not start_time or not end_time:
            return json.dumps({
                "error": "Missing required fields: start_time, end_time"
            })
        
        # Your implementation here
        return json.dumps({
            "success": True,
            "available": True,
            "conflicts": []
        })