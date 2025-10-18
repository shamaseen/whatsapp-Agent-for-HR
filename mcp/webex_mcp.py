"""
Webex MCP Tool
Provides Webex meeting management
"""

from typing import Dict, Any
from .base import MCPTool
from tools.webex_tools import webex_client
import json


class WebexMCPTool(MCPTool):
    """MCP tool for Webex operations"""

    def get_name(self) -> str:
        return "webex"

    def get_description(self) -> str:
        return """Manage Webex meetings.

Operations:
- create_meeting: Schedule a new Webex meeting
- get_meeting: Get meeting details
- update_meeting: Modify existing meeting
- delete_meeting: Cancel a meeting

Use for scheduling video interviews and meetings."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["create_meeting", "get_meeting", "update_meeting", "delete_meeting"]},
                "title": {"type": "string"},
                "start_time": {"type": "string"},
                "end_time": {"type": "string"},
                "invitees": {"type": "array", "items": {"type": "string"}},
                "meeting_id": {"type": "string"}
            },
            "required": ["operation"]
        }

    def execute(self, operation: str, **kwargs) -> str:
        if not webex_client:
            return json.dumps({"error": "Webex not configured"})

        try:
            if operation == "create_meeting":
                meeting = webex_client.create_meeting(
                    kwargs['title'], kwargs['start_time'],
                    kwargs['end_time'], kwargs.get('invitees')
                )
                return json.dumps({
                    "success": True,
                    "meeting_id": meeting.get('id'),
                    "join_url": meeting.get('webLink')
                })
            elif operation == "get_meeting":
                meeting = webex_client.get_meeting(kwargs['meeting_id'])
                return json.dumps({"success": True, "meeting": meeting})
            else:
                return json.dumps({"error": f"{operation} not implemented"})
        except Exception as e:
            return json.dumps({"error": str(e)})
