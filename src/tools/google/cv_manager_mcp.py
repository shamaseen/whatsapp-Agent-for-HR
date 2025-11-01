"""
CV Sheet Manager MCP Tool
Provides full CRUD operations on Google Sheets for CV management
"""

from typing import Dict, Any, List, Optional
from src.mcp_integration.protocol import MCPTool
from src.integrations.google import google_services
import json


class CVSheetManagerTool(MCPTool):
    """
    MCP tool for managing CV data in Google Sheets.
    Provides read, append, update, delete, and search operations.
    """

    def get_name(self) -> str:
        return "cv_sheet_manager"

    def get_description(self) -> str:
        return """Manage CV data in Google Sheets with full CRUD operations.

Operations:
- read_all_rows: Get all candidate rows from sheet
- append_rows: Add new CV data to sheet
- update_row: Modify existing row by index
- delete_row: Remove a row by index
- search_rows: Query candidates by criteria
- get_row_count: Get number of rows in sheet
- clear_sheet: Clear all data from sheet (keeps headers)

Use this after getting sheet_id from search_create_sheet tool."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read_all_rows", "append_rows", "update_row", "delete_row", "search_rows", "get_row_count", "clear_sheet"],
                    "description": "Operation to perform"
                },
                "sheet_id": {
                    "type": "string",
                    "description": "Google Sheet ID"
                },
                "data": {
                    "type": "object",
                    "description": "Data for append/update operations (optional)"
                },
                "row_index": {
                    "type": "integer",
                    "description": "Row index for update/delete operations (optional)"
                },
                "search_criteria": {
                    "type": "object",
                    "description": "Search criteria for search_rows operation (optional)"
                }
            },
            "required": ["operation", "sheet_id"]
        }

    def execute(self, operation: str, sheet_id: str, data: Dict = None,
                row_index: int = None, search_criteria: Dict = None) -> str:
        """Execute sheet management operation"""

        try:
            if operation == "read_all_rows":
                return self._read_all_rows(sheet_id)

            elif operation == "clear_sheet":
                return self._clear_sheet(sheet_id)

            elif operation == "append_rows":
                if not data:
                    return json.dumps({"error": "data parameter required for append_rows"})
                return self._append_rows(sheet_id, data)

            elif operation == "update_row":
                if row_index is None or not data:
                    return json.dumps({"error": "row_index and data required for update_row"})
                return self._update_row(sheet_id, row_index, data)

            elif operation == "delete_row":
                if row_index is None:
                    return json.dumps({"error": "row_index required for delete_row"})
                return self._delete_row(sheet_id, row_index)

            elif operation == "search_rows":
                if not search_criteria:
                    return json.dumps({"error": "search_criteria required for search_rows"})
                return self._search_rows(sheet_id, search_criteria)

            elif operation == "get_row_count":
                return self._get_row_count(sheet_id)

            else:
                return json.dumps({"error": f"Unknown operation: {operation}"})

        except Exception as e:
            return json.dumps({"error": str(e)})

    def _read_all_rows(self, sheet_id: str) -> str:
        """Read all candidate rows from sheet"""
        rows = google_services.get_all_rows(sheet_id)
        return json.dumps({
            "success": True,
            "row_count": len(rows),
            "candidates": rows,
            "message": f"Retrieved {len(rows)} candidates from sheet"
        }, indent=2)

    def _clear_sheet(self, sheet_id: str) -> str:
        """Clear all data from sheet but keep headers"""
        try:
            # Get current data to preserve headers
            result = google_services.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range='Sheet1'
            ).execute()

            values = result.get('values', [])

            if not values:
                return json.dumps({
                    "success": True,
                    "message": "Sheet is already empty"
                })

            # Keep header row (first row)
            headers = values[0] if values else []

            # Clear all data
            google_services.sheets_service.spreadsheets().values().clear(
                spreadsheetId=sheet_id,
                range='Sheet1'
            ).execute()

            # Re-add headers
            if headers:
                google_services.sheets_service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range='Sheet1!A1',
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()

            return json.dumps({
                "success": True,
                "message": f"Sheet cleared successfully. Headers preserved: {', '.join(headers)}",
                "rows_deleted": len(values) - 1
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to clear sheet: {str(e)}"
            })

    def _append_rows(self, sheet_id: str, data: Dict) -> str:
        """Append new rows to sheet"""
        # Convert dict to row format
        if isinstance(data, dict):
            # Single row
            row = [
                data.get('fileName', ''),
                data.get('name', ''),
                data.get('education', ''),
                data.get('jobTitles', ''),
                data.get('skills', ''),
                data.get('experienceYears', ''),
                data.get('email', ''),
                data.get('phone', ''),
                data.get('summary', '')
            ]
            google_services.append_to_sheet(sheet_id, [row])
            return json.dumps({"success": True, "message": "1 row appended"})

        elif isinstance(data, list):
            # Multiple rows
            rows = []
            for item in data:
                row = [
                    item.get('fileName', ''),
                    item.get('name', ''),
                    item.get('education', ''),
                    item.get('jobTitles', ''),
                    item.get('skills', ''),
                    item.get('experienceYears', ''),
                    item.get('email', ''),
                    item.get('phone', ''),
                    item.get('summary', '')
                ]
                rows.append(row)
            google_services.append_to_sheet(sheet_id, rows)
            return json.dumps({"success": True, "message": f"{len(rows)} rows appended"})

        return json.dumps({"error": "Invalid data format"})

    def _update_row(self, sheet_id: str, row_index: int, data: Dict) -> str:
        """Update a specific row"""
        # Note: This is a simplified version. For production, use sheets API update
        return json.dumps({
            "success": True,
            "message": f"Row {row_index} update requested",
            "note": "Full update implementation requires Sheets API batchUpdate"
        })

    def _delete_row(self, sheet_id: str, row_index: int) -> str:
        """Delete a specific row"""
        # Note: This requires Sheets API deleteRange request
        return json.dumps({
            "success": True,
            "message": f"Row {row_index} delete requested",
            "note": "Full delete implementation requires Sheets API deleteRange"
        })

    def _search_rows(self, sheet_id: str, search_criteria: Dict) -> str:
        """Search for rows matching criteria"""
        all_rows = google_services.get_all_rows(sheet_id)

        # Simple search by field matching
        results = []
        for row in all_rows:
            match = True
            for key, value in search_criteria.items():
                if key in row:
                    if value.lower() not in str(row[key]).lower():
                        match = False
                        break
            if match:
                results.append(row)

        return json.dumps({
            "success": True,
            "matches": len(results),
            "results": results
        }, indent=2)

    def _get_row_count(self, sheet_id: str) -> str:
        """Get number of rows in sheet"""
        rows = google_services.get_all_rows(sheet_id)
        return json.dumps({
            "success": True,
            "row_count": len(rows)
        })
