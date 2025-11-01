# Gmail Integration Setup Guide

Complete guide to setting up Gmail API for the WhatsApp HR Assistant.

---

## Prerequisites

- Google account with Gmail enabled
- Access to Google Cloud Console

---

## Step 1: Enable Gmail API

1. **Go to Google Cloud Console**
   - Visit [console.cloud.google.com](https://console.cloud.google.com)
   - Sign in with your Google account

2. **Create or Select Project**
   - Click on project dropdown at the top
   - Select existing project or create new one

3. **Enable Gmail API**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click on "Gmail API" and press "Enable"

---

## Step 2: Create Service Account

1. **Go to Credentials**
   - Navigate to "APIs & Services" → "Credentials"

2. **Create Service Account**
   - Click "+ CREATE CREDENTIALS" → "Service account"
   - Fill in:
     - **Name**: `whatsapp-hr-assistant`
     - **Description**: `Service account for WhatsApp HR Assistant`
   - Click "CREATE AND CONTINUE"
   - Skip optional role assignment
   - Click "DONE"

3. **Generate Key**
   - Click on the service account
   - Go to "Keys" tab
   - Click "ADD KEY" → "Create new key"
   - Choose "JSON" format
   - Click "CREATE"
   - **Save the file** - you'll need it as `client_secret.json`

---

## Step 3: Configure Environment

1. **Move credentials file**
   ```bash
   # Place the downloaded JSON file in project root
   mv ~/Downloads/client_secret.json ./client_secret.json
   ```

2. **Update .env**
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=./client_secret.json
   ```

3. **Set Gmail scopes** (if needed)
   - The service account will need appropriate permissions
   - Share Gmail folders or use delegated access

---

## Step 4: Test Gmail Connection

```python
from src.integrations.google import gmail_service

# Test connection
try:
    result = gmail_service.list_messages(max_results=10)
    print(f"✅ Gmail connected! Found {len(result)} messages")
except Exception as e:
    print(f"❌ Gmail connection failed: {e}")
```

---

## Troubleshooting

### Error: `403 Forbidden`

**Cause**: Service account doesn't have access to Gmail data.

**Solutions**:

1. **Use Delegated Domain-wide Access** (for Google Workspace):
   ```python
   from google.oauth2 import service_account
   from googleapiclient.discovery import build
   
   # Add user to impersonate
   credentials = service_account.Credentials.from_service_account_file(
       'client_secret.json',
       scopes=['https://www.googleapis.com/auth/gmail.readonly'],
       subject='user@yourdomain.com'  # User to impersonate
   )
   ```

2. **Share Gmail with Service Account**:
   - Share specific Gmail labels/folders with service account email
   - Email is in the JSON file as `client_email`

### Error: `Invalid credentials`

**Cause**: Wrong JSON file or corrupted credentials.

**Solutions**:
1. Verify `client_secret.json` exists in project root
2. Check file permissions
3. Download new key from Google Cloud Console

---

## Gmail API Scopes

Common scopes for the HR assistant:

| Scope | Permission | Use Case |
|-------|------------|----------|
| `https://www.googleapis.com/auth/gmail.readonly` | Read emails | Viewing applications |
| `https://www.googleapis.com/auth/gmail.send` | Send emails | **Required** |
| `https://www.googleapis.com/auth/gmail.compose` | Compose drafts | Auto-replies |
| `https://www.googleapis.com/auth/gmail.modify` | Modify emails | Mark as read |

---

## Example Usage

### Send Email

```python
from src.tools.google.gmail_mcp import GmailMCPTool

gmail_tool = GmailMCPTool()
result = gmail_tool.execute(
    operation="send_email",
    to="candidate@example.com",
    subject="Interview Invitation",
    body="You are invited to an interview..."
)
```

### Search Emails

```python
result = gmail_tool.execute(
    operation="search_emails",
    query="from:jobs@example.com subject:application",
    max_results=20
)
```

---

## Security Best Practices

1. **Never commit credentials**
   - Add `client_secret.json` to `.gitignore`
   - Use `.env` for file paths only

2. **Use least privilege**
   - Only grant necessary Gmail scopes
   - Regularly audit service account permissions

3. **Rotate keys**
   - Create new keys periodically
   - Remove old/unused keys from Google Cloud Console

4. **Monitor usage**
   - Check Google Cloud Console for API usage
   - Set up billing alerts

---

## See Also

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth2 Guide](GOOGLE_OAUTH_SETUP.md)
- [Google Drive Setup](GOOGLE_DRIVE_SETUP.md)

---

**Last Updated**: October 31, 2025
