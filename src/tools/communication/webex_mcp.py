"""
Webex MCP Tool
Provides Webex meeting management
"""

from typing import Dict, Any
from src.mcp_integration.protocol import MCPTool
from src.tools.communication.webex_tools import webex_client
import json


class WebexMCPTool(MCPTool):
    """MCP tool for Webex operations"""

    def get_name(self) -> str:
        return "webex"

    def get_description(self) -> str:
        return """Manage Webex meetings with email notifications.

Operations:
- create_meeting: Schedule a new Webex meeting (auto-sends email invitations)
- list_meetings: List all scheduled meetings
- get_meeting: Get meeting details
- update_meeting: Modify existing meeting (optional email notifications)
- delete_meeting: Cancel a meeting (optional email notifications)

All operations support optional email notifications to invitees.
Use for scheduling video interviews and meetings."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["create_meeting", "list_meetings", "get_meeting", "update_meeting", "delete_meeting"]
                },
                "title": {"type": "string", "description": "Meeting title"},
                "start_time": {"type": "string", "description": "Start time in ISO format"},
                "end_time": {"type": "string", "description": "End time in ISO format"},
                "invitees": {"type": "array", "items": {"type": "string"}, "description": "List of invitee emails"},
                "meeting_id": {"type": "string", "description": "Meeting ID for get/update/delete operations"},
                "send_email": {"type": "boolean", "description": "Send email notifications (default: true for create, false for update/delete)"},
                "from_date": {"type": "string", "description": "Start date for listing meetings (ISO format)"},
                "to_date": {"type": "string", "description": "End date for listing meetings (ISO format)"},
                "max_meetings": {"type": "integer", "description": "Maximum meetings to return when listing (default: 10)"}
            },
            "required": ["operation"]
        }

    def execute(self, operation: str, **kwargs) -> str:
        if not webex_client:
            return json.dumps({"error": "Webex not configured"})

        try:
            if operation == "create_meeting":
                meeting = webex_client.create_meeting(
                    kwargs['title'],
                    kwargs['start_time'],
                    kwargs['end_time'],
                    kwargs.get('invitees')
                )
                result = {
                    "success": True,
                    "meeting_id": meeting.get('id'),
                    "join_url": meeting.get('webLink'),
                    "title": meeting.get('title'),
                    "start": meeting.get('start'),
                    "end": meeting.get('end')
                }

                # Send email notifications
                send_email = kwargs.get('send_email', True)
                invitees = kwargs.get('invitees', [])
                if send_email and invitees:
                    emails_sent = []
                    for email in invitees:
                        subject = f"Webex Meeting Invitation: {kwargs['title']}"
                        body = f"""
You have been invited to a Webex meeting.

Meeting: {kwargs['title']}
Start Time: {kwargs['start_time']}
End Time: {kwargs['end_time']}

Join URL: {meeting.get('webLink')}
Meeting ID: {meeting.get('id')}

Please join the meeting at the scheduled time.
"""
                        if webex_client.send_meeting_email(email, subject, body):
                            emails_sent.append(email)
                    result['emails_sent'] = emails_sent

                return json.dumps(result)

            elif operation == "list_meetings":
                meetings = webex_client.list_meetings(
                    kwargs.get('from_date'),
                    kwargs.get('to_date'),
                    kwargs.get('max_meetings', 10)
                )
                return json.dumps({
                    "success": True,
                    "count": len(meetings),
                    "meetings": [{
                        "id": m.get('id'),
                        "title": m.get('title'),
                        "start": m.get('start'),
                        "end": m.get('end'),
                        "join_url": m.get('webLink')
                    } for m in meetings]
                })

            elif operation == "get_meeting":
                meeting = webex_client.get_meeting(kwargs['meeting_id'])
                return json.dumps({"success": True, "meeting": meeting})

            elif operation == "update_meeting":
                meeting = webex_client.update_meeting(
                    kwargs['meeting_id'],
                    kwargs.get('title'),
                    kwargs.get('start_time'),
                    kwargs.get('end_time'),
                    kwargs.get('invitees')
                )
                result = {
                    "success": True,
                    "meeting_id": meeting.get('id'),
                    "updated": True
                }

                # Send update notifications
                send_email = kwargs.get('send_email', False)
                invitees = kwargs.get('invitees')
                if send_email and invitees:
                    emails_sent = []
                    for email in invitees:
                        subject = f"Webex Meeting Updated: {meeting.get('title')}"
                        body = f"""
The Webex meeting has been updated.

Meeting: {meeting.get('title')}
Start Time: {meeting.get('start')}
End Time: {meeting.get('end')}

Join URL: {meeting.get('webLink')}

Please note the updated details.
"""
                        if webex_client.send_meeting_email(email, subject, body):
                            emails_sent.append(email)
                    result['emails_sent'] = emails_sent

                return json.dumps(result)

            elif operation == "delete_meeting":
                meeting_id = kwargs['meeting_id']

                # Get meeting details before deletion if needed
                meeting_title = "Meeting"
                send_email = kwargs.get('send_email', False)
                invitees = kwargs.get('invitees')

                if send_email and invitees:
                    try:
                        meeting = webex_client.get_meeting(meeting_id)
                        meeting_title = meeting.get('title', 'Meeting')
                    except Exception:
                        # If we can't get meeting details, use generic title
                        pass

                # Delete meeting
                webex_client.delete_meeting(meeting_id)
                result = {
                    "success": True,
                    "meeting_id": meeting_id,
                    "deleted": True
                }

                # Send cancellation notifications
                if send_email and invitees:
                    emails_sent = []
                    for email in invitees:
                        subject = f"Webex Meeting Cancelled: {meeting_title}"
                        body = f"""
The following Webex meeting has been cancelled:

Meeting: {meeting_title}
Meeting ID: {meeting_id}

We apologize for any inconvenience.
"""
                        if webex_client.send_meeting_email(email, subject, body):
                            emails_sent.append(email)
                    result['emails_sent'] = emails_sent

                return json.dumps(result)

            else:
                return json.dumps({"error": f"{operation} not implemented"})

        except Exception as e:
            return json.dumps({"error": str(e)})
