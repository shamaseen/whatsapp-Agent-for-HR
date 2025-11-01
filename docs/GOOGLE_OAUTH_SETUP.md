# Google OAuth Setup Guide

Complete guide to setting up Google OAuth for Gmail, Calendar, Drive, and Sheets APIs.

---

## Overview

The WhatsApp HR Assistant uses Google OAuth for accessing:
- Gmail API (email sending/receiving)
- Google Calendar API (scheduling)
- Google Drive API (CV storage)
- Google Sheets API (candidate data)

---

## Prerequisites

- Google account
- Access to Google Cloud Console
- Python 3.10+

---

## Step 1: Enable Required APIs

1. **Visit Google Cloud Console**
   - Go to [console.cloud.google.com](https://console.cloud.google.com)

2. **Select/Create Project**
   - Create new project or select existing one

3. **Enable APIs**
   Go to "APIs & Services" → "Library" and enable:
   - ✅ Gmail API
   - ✅ Google Calendar API
   - ✅ Google Drive API
   - ✅ Google Sheets API

---

## Step 2: Create OAuth 2.0 Credentials

1. **Go to Credentials**
   - Navigate to "APIs & Services" → "Credentials"

2. **Create OAuth Consent Screen**
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   - First time? Click "CONFIGURE CONSENT SCREEN"
   - Choose "External" user type
   - Fill required fields:
     - **App name**: WhatsApp HR Assistant
     - **User support email**: Your email
     - **Developer contact**: Your email
   - Click "SAVE AND CONTINUE"
   - Skip "Scopes" for now
   - Add test users (your email)
   - Click "SAVE AND CONTINUE"

3. **Create OAuth Credentials**
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   - **Application type**: Desktop application
   - **Name**: WhatsApp HR Assistant
   - Click "CREATE"
   - Download JSON file
   - **Save as**: `client_secret.json` in project root

---

## Step 3: Configure Environment

**Update .env file:**
```env
GOOGLE_APPLICATION_CREDENTIALS=./client_secret.json
```

---

## Step 4: Authenticate

### Automatic Setup Script

```bash
python3 utils/oauth_setup.py
```

This script will:
1. Open your browser
2. Ask you to sign in to Google
3. Request permissions for the APIs
4. Save credentials to `token.pickle`

### Manual Authentication

```python
from src.integrations.google import initialize_google_services

# Initialize all services
services = initialize_google_services()

# Test each service
for service_name, service in services.items():
    print(f"✅ {service_name} initialized")
```

---

## Step 5: Test Connection

```python
from src.integrations.google import gmail_service, calendar_service, drive_service

# Test Gmail
try:
    gmail_service.list_messages(max_results=5)
    print("✅ Gmail: OK")
except Exception as e:
    print(f"❌ Gmail: {e}")

# Test Calendar
try:
    calendar_service.list_calendars()
    print("✅ Calendar: OK")
except Exception as e:
    print(f"❌ Calendar: {e}")

# Test Drive
try:
    drive_service.list_files(pageSize=5)
    print("✅ Drive: OK")
except Exception as e:
    print(f"❌ Drive: {e}")
```

---

## Troubleshooting

### Error: `invalid_grant`

**Cause**: Authorization code expired or already used.

**Solution**:
1. Delete `token.pickle`
2. Re-run authentication
3. Complete authorization quickly

### Error: `access_denied`

**Cause**: User denied permissions.

**Solution**:
1. Delete `token.pickle`
2. Re-authenticate and grant all permissions
3. Ensure test users are added in OAuth consent screen

### Error: `insufficient_scope`

**Cause**: Not all required APIs are enabled.

**Solution**:
1. Verify all 4 APIs are enabled in Google Cloud Console
2. Wait 5-10 minutes for propagation
3. Delete `token.pickle` and re-authenticate

### Error: `token_expired`

**Cause**: Access token expired.

**Solution**:
```python
# Refresh token (automatic)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.oauth2 import Credentials

# Load existing credentials
creds = Credentials.from_authorized_user_file("token.pickle")

# Refresh if needed
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    # Save refreshed credentials
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)
```

---

## Token Management

### Stored Files

- `client_secret.json` - OAuth client credentials (keep secure)
- `token.pickle` - Access/refresh tokens (auto-generated)

### Re-authenticate

```bash
# Delete tokens
rm -f token.pickle

# Re-run setup
python3 utils/oauth_setup.py
```

### Multiple Accounts

To use different Google accounts:

```python
import pickle

# Load token for account A
with open("token_account_a.pickle", "rb") as f:
    creds_a = pickle.load(f)

# Load token for account B
with open("token_account_b.pickle", "rb") as f:
    creds_b = pickle.load(f)
```

---

## Security Best Practices

### Protect Credentials

1. **Never commit sensitive files**
   ```bash
   # .gitignore should include:
   client_secret.json
   token.pickle
   ```

2. **Restrict OAuth scopes**
   - Only enable APIs you need
   - Use minimal permissions

3. **Rotate credentials**
   - Regenerate `client_secret.json` periodically
   - Delete old OAuth clients

### Monitor Usage

1. **Check API Quotas**
   - Google Cloud Console → "APIs & Services" → "Quotas"
   - Set up billing alerts
   - Monitor daily usage

2. **Audit Access**
   - Google Account → Security → Third-party apps
   - Review connected apps
   - Revoke unused access

---

## Production Deployment

### OAuth Consent Screen

1. **Verify domain** (for production)
   - Add your domain in "Authorized domains"
   - Update redirect URIs

2. **Publish app**
   - Submit for Google verification (optional)
   - Required for >100 external users

### Service Account Alternative

For server-to-server authentication:

```python
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    'service_account.json',
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)
```

Use this when:
- Running on a server
- No user interaction available
- Using Google Workspace

---

## API Permissions

| Service | Scopes | Usage |
|---------|--------|-------|
| Gmail | `gmail.send`, `gmail.readonly` | Send/receive emails |
| Calendar | `calendar` | Schedule meetings |
| Drive | `drive.readonly` | Access CVs |
| Sheets | `spreadsheets` | Manage candidate data |

---

## See Also

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Gmail Setup Guide](GMAIL_SETUP.md)
- [Google Drive Setup](GOOGLE_DRIVE_SETUP.md)

---

**Last Updated**: October 31, 2025
