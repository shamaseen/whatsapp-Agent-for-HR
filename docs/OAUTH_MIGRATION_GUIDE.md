# OAuth 2.0 Migration Guide

## Why Migrate to OAuth 2.0?

### Service Account Issues:
- ❌ Limited storage (15GB shared)
- ❌ Storage quota exceeded errors
- ❌ Need to share every folder manually
- ❌ Files created use service account's storage

### OAuth 2.0 Benefits:
- ✅ Uses YOUR Google Drive storage
- ✅ No storage quota issues
- ✅ Access your own files directly
- ✅ Better for personal applications
- ✅ Standard user consent flow

## Step 1: Get OAuth 2.0 Credentials

### 1.1 Go to Google Cloud Console
https://console.cloud.google.com/

### 1.2 Select Your Project
Project: **n8n-rte-470608**

### 1.3 Enable APIs (if not already enabled)
- Google Drive API
- Google Sheets API
- Google Calendar API
- Gmail API

### 1.4 Create OAuth 2.0 Credentials

1. Go to: **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS**
3. Select **OAuth client ID**
4. Application type: **Desktop app**
5. Name: `WhatsApp HR Assistant`
6. Click **CREATE**

### 1.5 Download Credentials

1. Click the download button (⬇) next to your new OAuth client
2. Save as: `credentials.json` in project root
3. This file contains:
   - `client_id`
   - `client_secret`
   - `auth_uri`
   - `token_uri`

### 1.6 Configure OAuth Consent Screen

1. Go to: **OAuth consent screen**
2. User Type: **External** (or Internal if G Workspace)
3. Fill in:
   - App name: `WhatsApp HR Assistant`
   - User support email: Your email
   - Developer contact: Your email
4. Click **SAVE AND CONTINUE**

5. **Scopes:** Add these scopes:
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/drive.file`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/gmail.send`

6. **Test users:** Add your email address

7. Click **SAVE AND CONTINUE**

## Step 2: Update Code to Use OAuth 2.0

The code changes are already prepared in the migration script.

## Step 3: Run OAuth Flow

```bash
python3 setup_oauth.py
```

This will:
1. Open browser for Google login
2. Ask for consent to access Drive/Sheets/Calendar/Gmail
3. Save the token to `token.json`

## Step 4: Update .env

Add to `.env`:
```bash
# OAuth 2.0 (replaces service account)
USE_OAUTH=true
OAUTH_CREDENTIALS_FILE=./credentials.json
OAUTH_TOKEN_FILE=./token.json
```

## Step 5: Test

```bash
python3 debug_permissions.py
```

Should show:
```
✅ OAuth credentials loaded
✅ Token valid
✅ Drive API accessible
✅ Test sheet created successfully!
```

## Migration Checklist

- [ ] Create OAuth 2.0 Client ID in Google Cloud Console
- [ ] Download `credentials.json`
- [ ] Configure OAuth consent screen
- [ ] Add test users (your email)
- [ ] Run `python3 setup_oauth.py`
- [ ] Complete browser consent flow
- [ ] Verify `token.json` created
- [ ] Update `.env` with `USE_OAUTH=true`
- [ ] Test with `python3 debug_permissions.py`
- [ ] Test agent functionality

## Token Management

### Token Storage
- `token.json` contains your access/refresh tokens
- **DO NOT commit to git** (already in .gitignore)
- Keep secure like passwords

### Token Refresh
- Tokens expire after 1 hour
- Refresh token automatically renews them
- No user intervention needed after initial consent

### Token Revocation
To revoke access:
1. Go to: https://myaccount.google.com/permissions
2. Find "WhatsApp HR Assistant"
3. Click "Remove access"
4. Delete `token.json`

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Go to OAuth client settings
- Add redirect URI: `http://localhost:8080/`

### Error: "access_denied"
- Make sure your email is in test users list
- Check OAuth consent screen is configured

### Error: "invalid_grant"
- Delete `token.json`
- Run `python3 setup_oauth.py` again

### Error: "insufficient_permissions"
- Check scopes in OAuth consent screen
- Make sure all required scopes are added

## Security Notes

1. **credentials.json** contains client secret
   - Keep secure but can be in git (not private key)
   - If leaked, revoke and create new client

2. **token.json** contains access tokens
   - NEVER commit to git
   - If leaked, revoke at myaccount.google.com/permissions

3. **Refresh tokens** don't expire
   - User stays authenticated
   - Revoke if compromised

## Production Deployment

For production:
1. Verify OAuth app in Google Cloud Console
2. Remove from "Testing" mode
3. Add privacy policy URL
4. Add terms of service URL
5. Go through Google verification process

For now (development):
- Keep in "Testing" mode
- Limited to test users only
- No verification needed
