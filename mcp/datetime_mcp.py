"""
DateTime MCP Tool
Provides date/time utilities
"""

from typing import Dict, Any
from .base import MCPTool
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
                "operation": {"type": "string", "enum": ["get_current", "parse_datetime", "convert_timezone", "calculate_duration"]},
                "datetime_str": {"type": "string"},
                "from_tz": {"type": "string"},
                "to_tz": {"type": "string"}
            },
            "required": ["operation"]
        }

    def execute(self, operation: str, **kwargs) -> str:
        try:
            if operation == "get_current":
                now = datetime.now(timezone.utc)
                return json.dumps({
                    "success": True,
                    "current_datetime": now.isoformat(),
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S"),
                    "timezone": "UTC",
                    "timestamp": int(now.timestamp())
                })
            else:
                return json.dumps({"error": f"{operation} not yet implemented"})
        except Exception as e:
            return json.dumps({"error": str(e)})
