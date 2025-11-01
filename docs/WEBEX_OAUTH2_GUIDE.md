# Webex OAuth2 Integration Guide

Complete guide for setting up and troubleshooting Webex OAuth2 authentication.

---

## Table of Contents

1. [Quick Setup](#quick-setup)
2. [OAuth2 Flow Explained](#oauth2-flow-explained)
3. [Troubleshooting](#troubleshooting)
4. [Advanced Usage](#advanced-usage)
5. [Token Management](#token-management)

---

## Quick Setup

### Step 1: Create Webex App

1. Visit [Webex Developer Portal](https://developer.webex.com/)
2. Sign in to your Webex account
3. Go to **"My Apps"** → **"Create a New App"**
4. Choose **"OAuth 2.0 Application"**
5. Fill in:
   - **App Name:** WhatsApp HR Assistant
   - **Redirect URI:** `http://localhost:8000/oauth/webex/callback`
   - **Scopes:** `spark:all`
6. Save the app
7. **Copy your Client ID and Client Secret** ✅

### Step 2: Configure Environment

Add to your `.env` file:

```env
# Webex OAuth2 Configuration
WEBEX_CLIENT_ID=your_client_id_here
WEBEX_CLIENT_SECRET=your_client_secret_here
WEBEX_REDIRECT_URI=http://localhost:8000/oauth/webex/callback
```

### Step 3: Authenticate

```python
from src.integrations.webex_sdk import WebexClient

# First time: Browser opens automatically
client = WebexClient(auto_auth=True)

# Token saved to .webex_token.json with auto-refresh!
print("✅ Webex OAuth2 configured successfully!")
```

---

## OAuth2 Flow Explained

### What Happens During Authentication

1. **Browser Opens**: Automatic OAuth2 authorization URL generation
2. **User Authorizes**: Webex asks you to authorize the app
3. **Code Callback**: Webex redirects to your callback URL with authorization code
4. **Token Exchange**: Your app exchanges code for access + refresh tokens
5. **Token Saved**: Tokens saved to `.webex_token.json`
6. **Auto-Refresh**: Token automatically refreshed when expired

### Token Storage

Tokens are saved in `.webex_token.json`:
```json
{
  "access_token": "ZTA2NDkyYTkt...",
  "refresh_token": "RzdiMDBiMGIt...",
  "saved_at": "2025-10-31T22:54:13.135722"
}
```

**Important:**
- File is excluded from git (in .gitignore)
- Contains both access_token (12h) and refresh_token (indefinite)
- Automatically refreshed when access_token expires

---

## Troubleshooting

### Error: `redirect_uri_mismatch`

**Full Error:**
```
Error: redirect_uri_mismatch
The redirection URI provided does not match a pre-registered value.
```

**Cause:** Redirect URI in your Webex app doesn't match your `.env` file.

**Solutions:**

#### Solution 1: Update Webex App Redirect URI (Recommended)

1. Go to [Webex Developer Portal](https://developer.webex.com/)
2. Sign in → **"My Apps"** → Find your app → **Edit**
3. **Change the Redirect URI** to:
   ```
   http://localhost:8000/oauth/webex/callback
   ```
4. **Save the changes**
5. Restart your application
6. Try authentication again

#### Solution 2: Update .env to Match Webex App

If you prefer to use a different URI (e.g., for production):

1. Note the redirect URI from your Webex app
2. Update `.env`:
   ```env
   WEBEX_REDIRECT_URI=https://your-domain.com/webex/callback
   ```
3. Ensure this URI is added to your Webex app
4. Restart and try again

**Note:** The redirect URI must match **exactly** - including protocol (http/https), host, port, and path.

---

### Error: `TypeError: a bytes-like object is required, not 'str'`

**Full Error:**
```python
TypeError: a bytes-like object is required, not 'str'
  File "/home/shamaseen/.../webex_sdk.py", line 36, in do_GET
    self.wfile.write(f"""
```

**Cause:** HTTP server expects bytes but received a string for response body.

**Status:** ✅ **FIXED** - This bug was in `src/integrations/webex_sdk.py` and has been corrected.

**If you still see this error:**
1. Ensure you have the latest code
2. Restart your application
3. The response handler now correctly uses byte strings

---

### Error: `Using direct access token (no refresh support)`

**Warning Message:**
```
⚠️  Using direct access token (no refresh support)
   Note: Direct tokens expire after 12 hours
   For long-term use, switch to OAuth2 with WEBEX_CLIENT_ID/SECRET
```

**Cause:** You're using `WEBEX_ACCESS_TOKEN` instead of OAuth2 credentials.

**Solution:**
1. Remove/comment out `WEBEX_ACCESS_TOKEN` from `.env`
2. Add OAuth2 credentials:
   ```env
   WEBEX_CLIENT_ID=your_client_id
   WEBEX_CLIENT_SECRET=your_client_secret
   WEBEX_REDIRECT_URI=http://localhost:8000/oauth/webex/callback
   ```
3. Clean saved token:
   ```bash
   rm -f .webex_token.json
   ```
4. Re-authenticate:
   ```python
   from src.integrations.webex_sdk import WebexClient
   client = WebexClient(auto_auth=True)
   ```

---

### Error: `Browser doesn't open`

**Problem:** OAuth flow starts but browser doesn't open automatically.

**Solutions:**

1. **Copy URL Manually**:
   ```python
   from src.integrations.webex_sdk import WebexClient
   client = WebexClient(auto_auth=False)
   print(client._build_authorization_url())
   ```
   Copy this URL to your browser.

2. **Check Browser Configuration**:
   - Ensure default browser is set
   - Try opening URL manually

---

### Error: `Insufficient parameters for OAuth2 callback`

**Full Error:**
```
Insufficient parameters for OAuth2 callback.
Received following query parameters: {"code":"Y2Vm..."}
```

**Cause:** OAuth callback server had an error processing the request.

**This error was caused by the bytes/string bug which is now fixed.**

If you still see this:
1. Ensure you have the latest code
2. Restart application
3. Clean token: `rm -f .webex_token.json`
4. Try again

---

### Error: `Connection refused` during callback

**Problem:** Callback URL not accessible.

**Solutions:**

1. **Check Application is Running**:
   ```bash
   # Ensure your app is running on port 8000
   curl http://localhost:8000/health
   ```

2. **Check Redirect URI Port**:
   - Webex app redirect URI: `http://localhost:8000/oauth/webex/callback`
   - Your app must be running on port 8000
   - Or update both to use the same port

---

### Error: `Failed to exchange code for token`

**Cause:** Authorization code expired or invalid.

**Solution:**
1. Clean token: `rm -f .webex_token.json`
2. Restart OAuth flow
3. Authorize quickly (codes expire in 1-2 minutes)

---

## Advanced Usage

### Manual Token Refresh

```python
# Force refresh token (if needed)
token_data = webex_client.refresh_access_token()
print(f"New token expires in: {token_data.get('expires_in')} seconds")
```

### Custom Callback Handler

```python
from src.integrations.webex_sdk import WebexClient

# Disable auto-auth
client = WebexClient(auto_auth=False)

# Get authorization URL
auth_url = client._build_authorization_url()
print(f"Visit: {auth_url}")

# Manually handle callback
code = input("Enter authorization code: ")
token_data = client.exchange_code_for_token(code)
```

### Check Authentication Status

```python
from src.integrations.webex_sdk import webex_client

if webex_client:
    print(f"Using OAuth2: {webex_client.using_oauth}")
    print(f"Using direct token: {webex_client.using_direct_token}")
else:
    print("Webex not configured")
```

---

## Token Management

### Token Expiration

- **Access Token**: 8-12 hours, auto-refreshed
- **Refresh Token**: Indefinite, used to get new access tokens

### Clean Token (Re-authenticate)

```bash
rm -f .webex_token.json
```

Then re-run `WebexClient(auto_auth=True)`.

### Check Token Info

```python
import json
from pathlib import Path

token_file = Path(".webex_token.json")
if token_file.exists():
    with open(token_file) as f:
        data = json.load(f)
    print(f"Token saved: {data['saved_at']}")
    print(f"Has refresh token: {bool(data.get('refresh_token'))}")
```

### Multiple Environments

For different environments (dev/staging/prod), use different token files:

```python
import os
from pathlib import Path
from src.integrations.webex_sdk import WebexClient

# Set token file path
token_file = os.getenv("WEBEX_TOKEN_FILE", ".webex_token.json")
client = WebexClient(auto_auth=True)
client.token_file = Path(token_file)
```

---

## Authentication Methods Comparison

| Method | Configuration | Token Lifespan | Refresh Support | Best For |
|--------|---------------|----------------|-----------------|----------|
| **WEBEX_ACCESS_TOKEN** | Simple (just token) | 12 hours | ❌ No | Testing only |
| **WEBEX_CLIENT_ID/SECRET** | Requires app setup | 8-12 hours | ✅ Yes | **Production** ✅ |

**Recommendation:** Always use OAuth2 (`WEBEX_CLIENT_ID/SECRET`) for production. The direct token method is only for quick testing.

---

## FAQ

**Q: Can I use multiple Webex accounts?**  
A: Yes, create multiple apps with different redirect URIs and use separate token files.

**Q: Do I need to re-authenticate after server restart?**  
A: No! Token is saved to file and loaded automatically on restart.

**Q: What's the redirect URI for production?**  
A: Use your domain: `https://your-domain.com/oauth/webex/callback`

**Q: Can I use this with testing?**  
A: Yes, but you'll need to update the redirect URI in your Webex app or use a tool like ngrok for local testing.

**Q: Token expired unexpectedly?**  
A: If using `WEBEX_ACCESS_TOKEN`, this is normal (12h limit). Switch to OAuth2.

---

## See Also

- [Webex Developer Portal](https://developer.webex.com/)
- [Webex API Reference](https://webex.github.io/webex-js-sdk/api/)
- Source code: `src/integrations/webex_sdk.py`

---

**Last Updated:** October 31, 2025  
**Version:** 1.0
