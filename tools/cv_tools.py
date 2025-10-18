import json
import re
import io
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import pymupdf4llm
import fitz  # PyMuPDF
from services.google_drive import google_services
from config import settings

@tool
def search_create_sheet(sheet_name: str) -> str:
    """Search for a Google Sheet by name, create if not found. Returns sheet_id.

    Args:
        sheet_name: Name of the sheet (should be sender's phone number)
    """
    sheet_id = google_services.search_sheet_by_name(sheet_name)
    if not sheet_id:
        sheet_id = google_services.create_sheet(sheet_name)
        print(f"Created new sheet: {sheet_name} with ID: {sheet_id}")
    else:
        print(f"Found existing sheet: {sheet_name} with ID: {sheet_id}")
    return json.dumps({"sheet_id": sheet_id})

@tool
def process_cvs(sheet_id: str) -> str:
    """Process all CVs from Google Drive and store in Google Sheet.

    Args:
        sheet_id: ID of the Google Sheet to store results
    """
    files = google_services.list_files_in_folder(settings.CV_FOLDER_ID)
    if not files:
        return "No CV files found in Google Drive folder."

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

            # Open PDF from BytesIO using PyMuPDF
            pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")

            # Extract text using pymupdf4llm
            text = pymupdf4llm.to_markdown(pdf_document)

            # Close the document
            pdf_document.close()

            prompt = f"""Analyze this CV and extract the following information in JSON format:

{{
  "fileName": "{filename}",
  "name": "full name",
  "email": "email address",
  "phone": "phone number (replace + with 00, digits only)",
  "skills": "comma-separated skills",
  "experienceYears": "number of years",
  "education": "highest education",
  "jobTitles": "previous job titles comma-separated",
  "summary": "brief 2-3 sentence summary"
}}

CV Text:
{text[:4000]}

Respond with ONLY the JSON object, no other text."""

            response = llm.invoke([HumanMessage(content=prompt)])
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                cv_data = json.loads(json_match.group(0))
                row = [
                    cv_data.get('fileName', filename),
                    cv_data.get('name', ''),
                    cv_data.get('education', ''),
                    cv_data.get('jobTitles', ''),
                    cv_data.get('skills', ''),
                    cv_data.get('experienceYears', ''),
                    cv_data.get('email', ''),
                    cv_data.get('phone', ''),
                    cv_data.get('summary', '')
                ]
                google_services.append_to_sheet(sheet_id, [row])
                processed_count += 1
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

    return f"Processed {processed_count} new CVs, skipped {skipped_count} existing CVs."

@tool
def search_candidates(sheet_id: str, job_position: str) -> str:
    """Search and rank candidates for a specific job position.

    Args:
        sheet_id: ID of the Google Sheet containing candidates
        job_position: Job position to match against
    """
    candidates = google_services.get_all_rows(sheet_id)
    if not candidates:
        return "No candidates found in the sheet."

    llm = ChatGoogleGenerativeAI(model=settings.MODEL_NAME, google_api_key=settings.GOOGLE_API_KEY, temperature=0.7)

    prompt = f"""Job Title: {job_position}

All Candidates:
{json.dumps(candidates, indent=2)}

Rank the TOP 5 candidates for this position based on:
1. Relevant skills match
2. Years of experience
3. Previous job titles relevance
4. Education background

Return a JSON array with exactly 5 candidates:
[
  {{
    "rank": 1,
    "candidate_name": "name",
    "email": "email",
    "phone": "phone",
    "match_score": 95,
    "reasoning": "brief reason"
  }}
]

Respond with ONLY the JSON array."""

    response = llm.invoke([HumanMessage(content=prompt)])
    json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
    if json_match:
        ranked_candidates = json.loads(json_match.group(0))
        return json.dumps(ranked_candidates, indent=2)
    return "Could not parse ranking results."
