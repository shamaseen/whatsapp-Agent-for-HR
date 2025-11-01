from typing import List, Optional
from datetime import datetime
from src.config import settings
import json
import requests
from pathlib import Path
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

try:
    from webexteamssdk import WebexTeamsAPI
    from webexteamssdk.exceptions import ApiError
    WEBEX_SDK_AVAILABLE = True
except ImportError:
    WEBEX_SDK_AVAILABLE = False
    print("Warning: webexteamssdk not installed. Install with: pip install webexteamssdk")


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth callback"""
    
    auth_code = None
    
    def do_GET(self):
        """Handle OAuth callback"""
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            OAuthCallbackHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = b"""
                <html>
                <head><title>Authorization Successful</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: green;">&#10003; Authorization Successful!</h1>
                    <p>You can close this window and return to your application.</p>
                </body>
                </html>
            """
            self.wfile.write(html_content)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = b"""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">&#10007; Authorization Failed</h1>
                    <p>No authorization code received.</p>
                </body>
                </html>
            """
            self.wfile.write(html_content)
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass


class WebexClient:
    """Webex API client with automatic OAuth2 setup"""

    def __init__(self, auto_auth: bool = True):
        if not WEBEX_SDK_AVAILABLE:
            raise ImportError("webexteamssdk is required. Install with: pip install webexteamssdk")

        # Initialize with safe defaults
        self.token_file = Path(getattr(settings, 'WEBEX_TOKEN_FILE', '.webex_token.json'))
        self.client_id = getattr(settings, 'WEBEX_CLIENT_ID', None)
        self.client_secret = getattr(settings, 'WEBEX_CLIENT_SECRET', None)
        
        redirect_uri_raw = getattr(settings, 'WEBEX_REDIRECT_URI', None)
        self.redirect_uri = (
            redirect_uri_raw.strip() 
            if redirect_uri_raw 
            else 'http://localhost:8000/oauth/webex/callback'
        )

        # Track authentication method
        self.using_oauth = False
        self.using_direct_token = False

        # Try to load existing access token
        access_token = self._load_token()
        if access_token:
            self.using_oauth = True  # Loaded from file means OAuth was used

        if not access_token:
            access_token = getattr(settings, 'WEBEX_ACCESS_TOKEN', None)
            if access_token:
                self.using_direct_token = True

        # Auto-authenticate if no token exists
        if not access_token and self.client_id and self.client_secret and auto_auth:
            print("🔐 No valid token found. Starting OAuth2 flow...")
            access_token = self._auto_authenticate()
            if access_token:
                self.using_oauth = True

        if not access_token:
            auth_url = self._build_authorization_url() if self.client_id else None
            if auth_url:
                raise ValueError(
                    "Webex OAuth2 setup required:\n"
                    "Initialize with: WebexClient(auto_auth=True)\n"
                    "Or manually visit:\n"
                    f"{auth_url}"
                )
            else:
                raise ValueError(
                    "No Webex credentials found. Please set one of:\n"
                    "- WEBEX_ACCESS_TOKEN (direct token)\n"
                    "- WEBEX_CLIENT_ID + WEBEX_CLIENT_SECRET (OAuth2)"
                )

        self.api = WebexTeamsAPI(access_token=access_token)
        self._log_auth_method()

    def _log_auth_method(self):
        """Log which authentication method is being used"""
        if self.using_oauth:
            print("✓ Using OAuth2 authentication (supports token refresh)")
        elif self.using_direct_token:
            print("⚠️  Using direct access token (no refresh support)")
            print("   Note: Direct tokens expire after 12 hours")
            print("   For long-term use, switch to OAuth2 with WEBEX_CLIENT_ID/SECRET")

    def _auto_authenticate(self) -> Optional[str]:
        """Automatically handle OAuth2 flow with browser and local server"""
        try:
            # Parse redirect URI to get port
            parsed = urlparse(self.redirect_uri)
            port = parsed.port or 8000
            
            # Start local server to capture callback
            server = HTTPServer(('localhost', port), OAuthCallbackHandler)
            
            # Build and open authorization URL
            auth_url = self._build_authorization_url()
            print(f"\n{'='*80}")
            print("🌐 Opening browser for Webex authorization...")
            print(f"{'='*80}")
            print(f"If browser doesn't open, visit: {auth_url}")
            print(f"{'='*80}\n")
            
            # Open browser
            webbrowser.open(auth_url)
            
            # Wait for callback (with timeout)
            print("⏳ Waiting for authorization...")
            
            def timeout_handler():
                server.shutdown()
            
            timer = threading.Timer(120, timeout_handler)  # 2 minute timeout
            timer.start()
            
            server.handle_request()  # Handle single request
            timer.cancel()
            
            if OAuthCallbackHandler.auth_code:
                print("✓ Authorization code received!")
                # Exchange code for token
                token_data = self.exchange_code_for_token(OAuthCallbackHandler.auth_code)
                return token_data['access_token']
            else:
                print("✗ Authorization timeout or failed")
                return None
                
        except Exception as e:
            print(f"⚠️  Auto-authentication failed: {e}")
            print("Please authorize manually using exchange_code_for_token()")
            return None

    def _build_authorization_url(self) -> str:
        """Build OAuth2 authorization URL"""
        base_url = "https://webexapis.com/v1/authorize"
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'spark:all'
        }
        query_string = '&'.join(f"{k}={requests.utils.quote(str(v))}" for k, v in params.items())
        return f"{base_url}?{query_string}"

    def _load_token(self) -> Optional[str]:
        """Load access token from file"""
        if not self.token_file.exists():
            return None
            
        try:
            with open(self.token_file, 'r') as f:
                data = json.load(f)
                return data.get('access_token')
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Error loading token file: {e}")
            return None

    def _save_token(self, access_token: str, refresh_token: Optional[str] = None):
        """Save access token to file"""
        try:
            data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'saved_at': datetime.now().isoformat()
            }
            with open(self.token_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Token saved to: {self.token_file}")
        except IOError as e:
            print(f"Warning: Could not save token to file: {e}")

    def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        if not self.client_id or not self.client_secret:
            raise ValueError("WEBEX_CLIENT_ID and WEBEX_CLIENT_SECRET must be set for OAuth2")

        url = "https://webexapis.com/v1/access_token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code.strip(),
            'redirect_uri': self.redirect_uri
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()

            # Save token for future use
            self._save_token(
                token_data['access_token'],
                token_data.get('refresh_token')
            )
            
            # Update API client with new token
            self.api = WebexTeamsAPI(access_token=token_data['access_token'])
            self.using_oauth = True
            self.using_direct_token = False
            print("✅ Successfully authenticated with Webex!")
            return token_data
            
        except requests.HTTPError as e:
            error_detail = {}
            try:
                error_detail = response.json()
            except (ValueError, requests.JSONDecodeError):
                pass
            raise Exception(
                f"Failed to exchange code for token: {e}\n"
                f"Webex error: {error_detail}\n"
                f"Make sure redirect_uri matches your Webex app configuration: {self.redirect_uri}"
            )
        except requests.RequestException as e:
            raise Exception(f"Network error during token exchange: {e}")

    def refresh_access_token(self) -> dict:
        """Refresh access token using refresh token"""
        # Check if using direct token
        if self.using_direct_token:
            raise ValueError(
                "Cannot refresh direct access token.\n"
                "Direct tokens from WEBEX_ACCESS_TOKEN expire after 12 hours.\n"
                "To use auto-refresh, switch to OAuth2:\n"
                "1. Set WEBEX_CLIENT_ID and WEBEX_CLIENT_SECRET in .env\n"
                "2. Remove or comment out WEBEX_ACCESS_TOKEN\n"
                "3. Run: webex_client = WebexClient(auto_auth=True)"
            )

        if not self.token_file.exists():
            raise ValueError(
                "No saved token found to refresh.\n"
                "Please re-authenticate using WebexClient(auto_auth=True)"
            )

        try:
            with open(self.token_file, 'r') as f:
                data = json.load(f)
                refresh_token = data.get('refresh_token')
                
            if not refresh_token:
                raise ValueError(
                    "No refresh token available.\n"
                    "Please re-authenticate using WebexClient(auto_auth=True)"
                )

            url = "https://webexapis.com/v1/access_token"
            post_data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token
            }

            response = requests.post(url, data=post_data, timeout=10)
            response.raise_for_status()
            token_data = response.json()

            self._save_token(
                token_data['access_token'],
                token_data.get('refresh_token')
            )
            
            self.api = WebexTeamsAPI(access_token=token_data['access_token'])
            print("✅ Token refreshed successfully!")
            return token_data
            
        except Exception as e:
            raise Exception(f"Failed to refresh token: {e}")

    def _handle_token_refresh(self):
        """Helper to handle token refresh on 401 errors"""
        if self.using_direct_token:
            print("\n" + "="*80)
            print("❌ TOKEN EXPIRED")
            print("="*80)
            print("Your direct access token has expired (they last 12 hours).")
            print("\nOption 1: Get a new direct token")
            print("  1. Visit: https://developer.webex.com/docs/getting-started")
            print("  2. Copy your new Personal Access Token")
            print("  3. Update WEBEX_ACCESS_TOKEN in your .env file")
            print("  4. Restart your application")
            print("\nOption 2: Switch to OAuth2 (recommended for long-term use)")
            print("  1. Set WEBEX_CLIENT_ID and WEBEX_CLIENT_SECRET in .env")
            print("  2. Remove WEBEX_ACCESS_TOKEN from .env")
            print("  3. Run: webex_client = WebexClient(auto_auth=True)")
            print("="*80)
            raise Exception("Direct access token expired. See instructions above.")
        
        print("🔄 Token expired, attempting refresh...")
        try:
            self.refresh_access_token()
        except Exception as refresh_error:
            print(f"⚠️  Token refresh failed: {refresh_error}")
            print("\n💡 Please re-authenticate:")
            print("   webex_client = WebexClient(auto_auth=True)")
            raise

    def create_meeting(
        self,
        title: str,
        start: str,
        end: str,
        invitees: Optional[List[str]] = None
    ) -> dict:
        """Create a new Webex meeting"""
        try:
            meeting = self.api.meetings.create(
                title=title,
                start=start,
                end=end,
                timezone='UTC',
                invitees=[{'email': email} for email in invitees] if invitees else None
            )
            return meeting.to_dict()
        except ApiError as e:
            if '401' in str(e):
                self._handle_token_refresh()
                meeting = self.api.meetings.create(
                    title=title,
                    start=start,
                    end=end,
                    timezone='UTC',
                    invitees=[{'email': email} for email in invitees] if invitees else None
                )
                return meeting.to_dict()
            raise Exception(f"Webex API error creating meeting: {e}")

    def get_meeting(self, meeting_id: str) -> dict:
        """Get details of a specific meeting"""
        try:
            meeting = self.api.meetings.get(meeting_id)
            return meeting.to_dict()
        except ApiError as e:
            if '401' in str(e):
                self._handle_token_refresh()
                meeting = self.api.meetings.get(meeting_id)
                return meeting.to_dict()
            raise Exception(f"Webex API error getting meeting: {e}")

    def list_meetings(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        max_meetings: int = 100
    ) -> list:
        """List meetings within date range"""
        try:
            meetings = self.api.meetings.list(
                from_=from_date,
                to=to_date,
                max=max_meetings
            )
            return [meeting.to_dict() for meeting in meetings]
        except ApiError as e:
            if '401' in str(e):
                self._handle_token_refresh()
                meetings = self.api.meetings.list(
                    from_=from_date,
                    to=to_date,
                    max=max_meetings
                )
                return [meeting.to_dict() for meeting in meetings]
            raise Exception(f"Webex API error listing meetings: {e}")

    def update_meeting(
        self,
        meeting_id: str,
        title: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        invitees: Optional[List[str]] = None
    ) -> dict:
        """Update an existing meeting"""
        try:
            update_data = {}
            if title:
                update_data['title'] = title
            if start:
                update_data['start'] = start
            if end:
                update_data['end'] = end
            if invitees:
                update_data['invitees'] = [{'email': email} for email in invitees]

            meeting = self.api.meetings.update(meeting_id, **update_data)
            return meeting.to_dict()
        except ApiError as e:
            if '401' in str(e):
                self._handle_token_refresh()
                meeting = self.api.meetings.update(meeting_id, **update_data)
                return meeting.to_dict()
            raise Exception(f"Webex API error updating meeting: {e}")

    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting"""
        try:
            self.api.meetings.delete(meeting_id)
            return True
        except ApiError as e:
            if '401' in str(e):
                self._handle_token_refresh()
                self.api.meetings.delete(meeting_id)
                return True
            raise Exception(f"Webex API error deleting meeting: {e}")

    def send_meeting_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email notification about meeting (requires Gmail integration)"""
        try:
            from src.tools.google.gmail_tools import send_email
            result = send_email.invoke({"to": to_email, "subject": subject, "body": body})
            return "sent successfully" in result.lower()
        except Exception as e:
            print(f"Warning: Could not send email notification: {e}")
            return False


def initialize_webex_client() -> Optional[WebexClient]:
    """
    Safely initialize Webex client with automatic OAuth.
    Returns None if credentials are not configured.
    """
    has_access_token = bool(getattr(settings, 'WEBEX_ACCESS_TOKEN', None))
    has_oauth_creds = bool(
        getattr(settings, 'WEBEX_CLIENT_ID', None) and 
        getattr(settings, 'WEBEX_CLIENT_SECRET', None)
    )
    
    if not (has_access_token or has_oauth_creds):
        print("Info: Webex client not initialized - no credentials configured")
        return None
    
    try:
        return WebexClient(auto_auth=True)
    except ValueError as e:
        print(f"Info: Webex initialization info:\n{e}")
        return None
    except Exception as e:
        print(f"Warning: Could not initialize Webex client: {e}")
        return None


# Initialize client if credentials available
webex_client = initialize_webex_client()