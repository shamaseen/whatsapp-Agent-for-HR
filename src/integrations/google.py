"""
Google Services with OAuth 2.0 Authentication
==============================================

Updated to use OAuth 2.0 instead of service account
✅ No more permission issues!
✅ Works as your user account
"""

from typing import List, Dict, Optional, Any
import io
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import gspread
from src.config import settings


# Scopes required for all Google services
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/drive.file'
]


class GoogleServices:
    """Google Services with OAuth 2.0 authentication"""
    
    def __init__(self, oauth_credentials_file: str = None, token_file: str = 'token.pickle'):
        """
        Initialize Google Services with OAuth 2.0
        
        Args:
            oauth_credentials_file: Path to OAuth client credentials JSON
                                   Default: settings.OAUTH_CREDENTIALS_FILE
            token_file: Path to store the authentication token
        
        First run: Opens browser for authentication
        Subsequent runs: Uses saved token automatically
        """
        # Get credentials file from settings or parameter
        if oauth_credentials_file is None:
            if hasattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS'):
                oauth_credentials_file = settings.GOOGLE_APPLICATION_CREDENTIALS
            else:
                raise ValueError(
                    "OAuth credentials file not specified. "
                    "Either pass oauth_credentials_file parameter or "
                    "set settings.OAUTH_CREDENTIALS_FILE"
                )
        
        self.oauth_credentials_file = oauth_credentials_file
        self.token_file = token_file
        self.creds = None
        
        # Authenticate
        self._authenticate()
        
        # Initialize all services
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)
        self.gspread_client = gspread.authorize(self.creds)
        
        print("✅ Google Services initialized with OAuth 2.0")
    
    def _authenticate(self):
        """Handle OAuth 2.0 authentication"""
        # Check if we have saved credentials
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                # NOTE: Using pickle.load for Google OAuth tokens
                # This is considered safe when used with Google-provided tokens
                # The token file is created by Google's official OAuth library
                # and contains only credentials, not executable code
                self.creds = pickle.load(token)
                print("✅ Loaded saved OAuth token")
        
        # If no valid credentials, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("🔄 Refreshing expired OAuth token...")
                try:
                    self.creds.refresh(Request())
                    print("✅ Token refreshed")
                except Exception as e:
                    print(f"⚠️ Token refresh failed: {e}")
                    print("   Re-authenticating...")
                    self.creds = None
            
            if not self.creds:
                print("🔐 Starting OAuth authentication...")
                print("   Browser will open for authorization")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.oauth_credentials_file, 
                    SCOPES
                )
                
                # Try multiple ports in case one is in use
                ports_to_try = [8080, 8000, 9000, 0]
                
                for port in ports_to_try:
                    try:
                        print(f"   Trying port {port}...")
                        self.creds = flow.run_local_server(
                            port=port,
                            open_browser=True,
                            success_message='✅ Authentication successful! You can close this window.'
                        )
                        print("✅ OAuth authentication successful!")
                        break
                    except OSError as e:
                        if port == ports_to_try[-1]:
                            raise Exception(
                                "Could not start local server for OAuth. "
                                "Please check if ports 8080, 8000, 9000 are available."
                            )
                        print(f"   Port {port} in use, trying next...")
                        continue
            
            # Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
                print(f"💾 OAuth token saved to {self.token_file}")
    
    def list_files_in_folder(self, folder_id: str) -> List[Dict]:
        """List all PDF files in a Google Drive folder"""
        try:
            query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            results = self.drive_service.files().list(
                q=query, 
                fields="files(id, name, createdTime, modifiedTime)"
            ).execute()
            files = results.get('files', [])
            print(f"✅ Found {len(files)} PDF files in folder")
            return files
        except HttpError as error:
            print(f"❌ Error listing files: {error}")
            raise
    
    def download_file(self, file_id: str) -> bytes:
        """Download a file from Google Drive"""
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            file_data = io.BytesIO()
            downloader = MediaIoBaseDownload(file_data, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"   Download progress: {int(status.progress() * 100)}%")
            
            file_data.seek(0)
            print(f"✅ File downloaded successfully")
            return file_data.getvalue()
        except HttpError as error:
            print(f"❌ Error downloading file: {error}")
            raise
    
    def search_sheet_by_name(self, sheet_name: str) -> Optional[str]:
        """Search for a Google Sheet by name"""
        try:
            query = f"name='{sheet_name}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
            results = self.drive_service.files().list(
                q=query, 
                fields="files(id, name)"
            ).execute()
            files = results.get('files', [])
            
            if files:
                print(f"✅ Found sheet: {sheet_name}")
                return files[0]['id']
            else:
                print(f"ℹ️ Sheet not found: {sheet_name}")
                return None
        except HttpError as error:
            print(f"❌ Error searching sheet: {error}")
            raise
    
    def create_sheet(self, title: str) -> str:
        """
        Create a new Google Sheet
        ✅ Works with OAuth 2.0 - no permission issues!
        """
        try:
            spreadsheet = {'properties': {'title': title}}
            
            print(f"📝 Creating sheet: {title}")
            result = self.sheets_service.spreadsheets().create(
                body=spreadsheet
            ).execute()
            
            sheet_id = result['spreadsheetId']
            print(f"✅ Sheet created: {sheet_id}")
            
            # Move to folder if specified
            if hasattr(settings, 'SHEETS_FOLDER_ID') and settings.SHEETS_FOLDER_ID:
                try:
                    # Get current parents
                    file = self.drive_service.files().get(
                        fileId=sheet_id,
                        fields='parents'
                    ).execute()
                    
                    previous_parents = ",".join(file.get('parents', []))
                    
                    # Move to new folder
                    self.drive_service.files().update(
                        fileId=sheet_id, 
                        addParents=settings.SHEETS_FOLDER_ID,
                        removeParents=previous_parents,
                        fields='id, parents'
                    ).execute()
                    
                    print(f"✅ Moved to folder: {settings.SHEETS_FOLDER_ID}")
                except Exception as e:
                    print(f"⚠️ Could not move to folder: {e}")
            
            return sheet_id
            
        except HttpError as error:
            print(f"❌ Error creating sheet: {error}")
            raise
    
    def append_to_sheet(self, sheet_id: str, values: List[List[Any]]):
        """Append rows to a Google Sheet"""
        try:
            body = {'values': values}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=sheet_id, 
                range='Sheet1', 
                valueInputOption='RAW', 
                body=body
            ).execute()
            
            updated_cells = result.get('updates', {}).get('updatedCells', 0)
            print(f"✅ Appended {len(values)} rows ({updated_cells} cells)")
            
        except HttpError as error:
            print(f"❌ Error appending to sheet: {error}")
            raise
    
    def get_all_rows(self, sheet_id: str) -> List[Dict]:
        """Get all rows from a Google Sheet"""
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id, 
                range='Sheet1'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) < 2:
                print("ℹ️ Sheet is empty or has only headers")
                return []
            
            headers = values[0]
            rows = []
            
            for row in values[1:]:
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ""
                rows.append(row_dict)
            
            print(f"✅ Retrieved {len(rows)} rows from sheet")
            return rows
            
        except HttpError as error:
            print(f"❌ Error reading sheet: {error}")
            raise
    
    def update_cell(self, sheet_id: str, cell_range: str, value: Any):
        """Update a specific cell or range"""
        try:
            body = {'values': [[value]]}
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=cell_range,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Updated cell {cell_range}")
            return result
            
        except HttpError as error:
            print(f"❌ Error updating cell: {error}")
            raise
    
    def clear_sheet(self, sheet_id: str, range_name: str = 'Sheet1'):
        """Clear all data from a sheet"""
        try:
            self.sheets_service.spreadsheets().values().clear(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            print(f"✅ Cleared sheet range: {range_name}")
            
        except HttpError as error:
            print(f"❌ Error clearing sheet: {error}")
            raise
    
    def get_sheet_url(self, sheet_id: str) -> str:
        """Get the web URL for a spreadsheet"""
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"



google_services = GoogleServices()

