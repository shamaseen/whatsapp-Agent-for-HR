"""
DateTime MCP Tool
Provides date/time utilities
"""

from typing import Dict, Any
from mcp_integration.tools.base import MCPTool
from datetime import datetime, timezone
import json


class DateTimeMCPTool(MCPTool):
    """MCP tool for date/time operations"""

    def get_name(self) -> str:
        return "datetime"

    def get_description(self) -> str:
        return """Get current date/time and perform time operations.

Operations:
- get_current: Get current date and time
- parse_datetime: Parse datetime string
- convert_timezone: Convert between timezones
- calculate_duration: Calculate time between dates

Always use this to get current time before scheduling."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string", 
                    "enum": ["get_current", "parse_datetime", "convert_timezone", "calculate_duration"],
                    "description": "The operation to perform"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Datetime string to parse (ISO format preferred)"
                },
                "from_tz": {
                    "type": "string",
                    "description": "Source timezone (e.g., 'UTC', 'America/New_York')"
                },
                "to_tz": {
                    "type": "string",
                    "description": "Target timezone (e.g., 'UTC', 'America/New_York')"
                },
                "start_datetime": {
                    "type": "string",
                    "description": "Start datetime for duration calculation"
                },
                "end_datetime": {
                    "type": "string",
                    "description": "End datetime for duration calculation"
                }
            },
            "required": ["operation"]
        }

    def execute(self, **kwargs) -> str:
        """
        Execute datetime operation with keyword arguments
        
        Args:
            **kwargs: All parameters passed as keyword arguments
                - operation: The operation to perform (required)
                - datetime_str: DateTime string for parsing
                - from_tz: Source timezone
                - to_tz: Target timezone
                - start_datetime: Start time for duration
                - end_datetime: End time for duration
        """
        try:
            # Extract operation from kwargs
            operation = kwargs.get("operation")
            
            if not operation:
                return json.dumps({
                    "error": "Missing required parameter: operation",
                    "available_operations": [
                        "get_current",
                        "parse_datetime", 
                        "convert_timezone",
                        "calculate_duration"
                    ]
                })
            
            # Handle different operations
            if operation == "get_current":
                return self._get_current()
            
            elif operation == "parse_datetime":
                datetime_str = kwargs.get("datetime_str")
                if not datetime_str:
                    return json.dumps({"error": "datetime_str is required for parse_datetime operation"})
                return self._parse_datetime(datetime_str)
            
            elif operation == "convert_timezone":
                datetime_str = kwargs.get("datetime_str")
                from_tz = kwargs.get("from_tz", "UTC")
                to_tz = kwargs.get("to_tz")
                
                if not datetime_str or not to_tz:
                    return json.dumps({
                        "error": "datetime_str and to_tz are required for convert_timezone operation"
                    })
                return self._convert_timezone(datetime_str, from_tz, to_tz)
            
            elif operation == "calculate_duration":
                start_datetime = kwargs.get("start_datetime")
                end_datetime = kwargs.get("end_datetime")
                
                if not start_datetime or not end_datetime:
                    return json.dumps({
                        "error": "start_datetime and end_datetime are required for calculate_duration operation"
                    })
                return self._calculate_duration(start_datetime, end_datetime)
            
            else:
                return json.dumps({
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "get_current",
                        "parse_datetime",
                        "convert_timezone", 
                        "calculate_duration"
                    ]
                })
                
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "type": type(e).__name__
            })

    def _get_current(self) -> str:
        """Get current date and time"""
        now = datetime.now(timezone.utc)
        return json.dumps({
            "success": True,
            "current_datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timezone": "UTC",
            "timestamp": int(now.timestamp()),
            "formatted": now.strftime("%A, %B %d, %Y at %H:%M:%S UTC")
        })

    def _parse_datetime(self, datetime_str: str) -> str:
        """Parse a datetime string"""
        try:
            # Try ISO format first
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            
            return json.dumps({
                "success": True,
                "parsed_datetime": dt.isoformat(),
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M:%S"),
                "timestamp": int(dt.timestamp()),
                "formatted": dt.strftime("%A, %B %d, %Y at %H:%M:%S")
            })
        except ValueError as e:
            return json.dumps({
                "error": f"Could not parse datetime: {str(e)}",
                "hint": "Use ISO format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD"
            })

    def _convert_timezone(self, datetime_str: str, from_tz: str, to_tz: str) -> str:
        """Convert datetime between timezones"""
        try:
            from zoneinfo import ZoneInfo
            
            # Parse datetime
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            
            # If datetime is naive, assume it's in from_tz
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo(from_tz))
            
            # Convert to target timezone
            dt_converted = dt.astimezone(ZoneInfo(to_tz))
            
            return json.dumps({
                "success": True,
                "original_datetime": datetime_str,
                "original_timezone": from_tz,
                "converted_datetime": dt_converted.isoformat(),
                "converted_timezone": to_tz,
                "formatted": dt_converted.strftime("%A, %B %d, %Y at %H:%M:%S %Z")
            })
        except Exception as e:
            return json.dumps({
                "error": f"Timezone conversion failed: {str(e)}",
                "hint": "Use IANA timezone names like 'America/New_York' or 'Europe/London'"
            })

    def _calculate_duration(self, start_datetime: str, end_datetime: str) -> str:
        """Calculate duration between two datetimes"""
        try:
            start = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            
            duration = end - start
            total_seconds = int(duration.total_seconds())
            
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            return json.dumps({
                "success": True,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "duration": {
                    "total_seconds": total_seconds,
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                    "formatted": f"{days}d {hours}h {minutes}m {seconds}s"
                }
            })
        except Exception as e:
            return json.dumps({
                "error": f"Duration calculation failed: {str(e)}"
            })