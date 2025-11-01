"""
CV Tools MCP
Migrated from tools/cv_tools.py to MCP format
"""

from typing import Dict, Any
from src.mcp_integration.protocol import MCPTool
from src.integrations.google import google_services
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.config import settings
import json, re, io, fitz
import pymupdf4llm


class CVProcessTool(MCPTool):
    """Process CVs from Google Drive"""

    def get_name(self) -> str:
        return "process_cvs"

    def get_description(self) -> str:
        return """Process all CVs from Google Drive folder and extract data to sheet.

Requires sheet_id from search_create_sheet tool first."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "sheet_id": {"type": "string", "description": "Google Sheet ID"}
            },
            "required": ["sheet_id"]
        }

    def execute(self, sheet_id: str) -> str:
        files = google_services.list_files_in_folder(settings.CV_FOLDER_ID)
        if not files:
            return json.dumps({"success": True, "message": "No CV files found"})

        existing_rows = google_services.get_all_rows(sheet_id)

        # Add header row if sheet is empty
        if not existing_rows:
            header = ['fileName', 'name', 'education', 'jobTitles', 'skills', 'experienceYears', 'email', 'phone', 'summary']
            google_services.append_to_sheet(sheet_id, [header])
            print("Added header row to new sheet")

        existing_filenames = {row.get('fileName', '') for row in existing_rows}

        processed_count = 0
        skipped_count = 0
        llm = ChatGoogleGenerativeAI(model=settings.MODEL_NAME, google_api_key=settings.GOOGLE_API_KEY, temperature=0.1)

        for file in files:
            filename = file['name']
            if filename in existing_filenames:
                skipped_count += 1
                continue
            try:
                file_data = google_services.download_file(file['id'])
                pdf_stream = io.BytesIO(file_data)
                pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
                text = pymupdf4llm.to_markdown(pdf_document)
                pdf_document.close()

                prompt = f"""Analyze this CV and extract JSON:
                {{"fileName": "{filename}", "name": "full name", "email": "email", "phone": "phone (digits only)",
                "skills": "comma-separated", "experienceYears": "number", "education": "highest",
                "jobTitles": "comma-separated", "summary": "2-3 sentences"}}
                CV: {text}
                Respond with ONLY JSON."""

                response = llm.invoke([HumanMessage(content=prompt)])
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    cv_data = json.loads(json_match.group(0))
                    row = [cv_data.get(k, '') for k in ['fileName', 'name', 'education', 'jobTitles', 'skills', 'experienceYears', 'email', 'phone', 'summary']]
                    google_services.append_to_sheet(sheet_id, [row])
                    processed_count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

        return json.dumps({"success": True, "processed": processed_count, "skipped": skipped_count})


class SearchCandidatesTool(MCPTool):
    """Search and rank candidates"""

    def get_name(self) -> str:
        return "search_candidates"

    def get_description(self) -> str:
        return """Search candidates in sheet and rank by job position match."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "sheet_id": {"type": "string"},
                "job_position": {"type": "string"}
            },
            "required": ["sheet_id", "job_position"]
        }

    def execute(self, sheet_id: str, job_position: str) -> str:
        candidates = google_services.get_all_rows(sheet_id)
        if not candidates:
            return json.dumps({"success": False, "message": "No candidates found"})

        llm = ChatGoogleGenerativeAI(model=settings.MODEL_NAME, google_api_key=settings.GOOGLE_API_KEY, temperature=0.7)
        prompt = f"""Job: {job_position}
Candidates: {json.dumps(candidates, indent=2)}
Rank TOP 5 by skills, experience, job titles, education.
Return JSON array: [{{"rank": 1, "candidate_name": "name", "email": "email", "phone": "phone", "match_score": 95, "reasoning": "reason"}}]"""

        response = llm.invoke([HumanMessage(content=prompt)])
        json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return json.dumps({"error": "Could not parse ranking"})


class SearchCreateSheetTool(MCPTool):
    """Search/create CV sheet"""

    def get_name(self) -> str:
        return "search_create_sheet"

    def get_description(self) -> str:
        return """Search for sheet by name, create if not found. Returns sheet_id."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "sheet_name": {"type": "string", "description": "Sheet name (use sender phone number)"}
            },
            "required": ["sheet_name"]
        }

    def execute(self, sheet_name: str) -> str:
        try:
            sheet_id = google_services.search_sheet_by_name(sheet_name)
            if not sheet_id:
                sheet_id = google_services.create_sheet(sheet_name)
            return json.dumps({"sheet_id": sheet_id, "success": True})
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "success": False,
                "message": f"Failed to create/find sheet: {str(e)}"
            })
