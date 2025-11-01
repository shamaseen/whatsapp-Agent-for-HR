# Google Credentials Setup Guide

## Overview

The application requires Google API credentials to access Gmail, Calendar, and Google Drive services. This guide explains how to set up the required credentials.

## Files Involved

### `client_secret.json` (Required for production)
- **Location**: Root directory
- **Purpose**: Contains OAuth2 credentials for Google APIs
- **Status**: ✅ **NOT tracked by git** (in .gitignore)
- **Template**: Provided as placeholder in repository

### `.env.example` (Reference only)
- Shows the required environment variables
- Contains placeholder values
- Safe to commit to git

## Setup Instructions

### Step 1: Get Credentials from Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **APIs & Services** > **Credentials**
4. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
5. Choose **Desktop application**
6. Download the JSON file
7. Save it as `client_secret.json` in the project root directory

### Step 2: Verify the File

Your `client_secret.json` should look like this:

```json
{
  "installed": {
    "client_id": "123456789-abcdefghijklmnopqrstuvwxyz1234567890.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

### Step 3: Set Environment Variables

1. Copy `.env.example` to `.env`
2. Update `.env` with your actual values:
   - `GOOGLE_API_KEY`: Your Gemini API key
   - Keep `GOOGLE_APPLICATION_CREDENTIALS=./client_secret.json`

## Security Notes

### ✅ What's Safe
- `client_secret.json` is in `.gitignore`
- Real credentials will NOT be committed to git
- Only the template with placeholder values is in the repository

### ⚠️ Important
- **Never commit** `client_secret.json` with real credentials
- **Never share** your actual `client_secret.json` file
- The file contains sensitive OAuth2 credentials
- It should only exist on your local machine

## Troubleshooting

### Error: "client_secret.json not found"
- Make sure the file exists in the project root directory
- Check that it's named exactly `client_secret.json`

### Error: "Invalid credentials"
- Verify the JSON file is valid
- Check that you downloaded it from Google Cloud Console
- Ensure the file hasn't been modified

### First Run Authentication
On the first run, the application will:
1. Open a browser for OAuth2 authorization
2. Request permission to access your Google account
3. Save the authentication token for future use

## What Services Require This?

- ✅ Gmail API (send emails)
- ✅ Google Calendar API (schedule interviews)
- ✅ Google Drive API (manage CVs and documents)

## Additional Resources

- [Google Cloud Console](https://console.cloud.google.com/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Calendar API Documentation](https://developers.google.com/calendar/api)
- [Drive API Documentation](https://developers.google.com/drive/api)

---

**Summary**: The `client_secret.json` file is present as a template, properly excluded from git, and ready for you to replace with real credentials from Google Cloud Console.
