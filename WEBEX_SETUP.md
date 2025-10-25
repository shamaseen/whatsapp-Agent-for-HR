# Webex Integration Setup Guide

## Overview
The Webex integration supports:
- ✅ Create meetings with automatic email invitations
- ✅ List all scheduled meetings
- ✅ Get meeting details
- ✅ Update meetings with optional email notifications
- ✅ Delete/cancel meetings with optional email notifications

## Prerequisites
1. Webex account
2. Webex Integration created at https://developer.webex.com/my-apps
3. Client ID and Client Secret from your integration

## Setup Steps

### 1. Configure Environment Variables

Edit `.env` and add:
```bash
WEBEX_CLIENT_ID="your_client_id_here"
WEBEX_CLIENT_SECRET="your_client_secret_here"
```

### 2. Update Redirect URI

In your Webex integration settings on the developer portal:
- Set Redirect URI to: `http://localhost:8000/oauth/webex/callback`
- Save changes

### 3. Authorize the Application

Run the authorization helper:
```bash
python authorize_webex.py
```

This will display an authorization URL. Follow the instructions:
1. Start your app: `python main.py`
2. Open the authorization URL in your browser
3. Click "Accept" to authorize
4. You'll be redirected back and the token will be saved to `.webex_token.json`

## Available Operations

### 1. Create Meeting (with email notifications)
```python
schedule_webex_meeting(
    title="Interview with John Doe",
    start_time="2024-01-15T14:00:00Z",
    end_time="2024-01-15T15:00:00Z",
    invitees=["john@example.com", "jane@example.com"],
    send_email=True  # Default: True
)
```

### 2. List Meetings
```python
list_webex_meetings(
    from_date="2024-01-01T00:00:00Z",  # Optional
    to_date="2024-12-31T23:59:59Z",     # Optional
    max_meetings=10                      # Default: 10
)
```

### 3. Get Meeting Details
```python
get_webex_meeting_details(
    meeting_id="meeting_id_here"
)
```

### 4. Update Meeting (with optional email)
```python
update_webex_meeting(
    meeting_id="meeting_id_here",
    title="Updated Meeting Title",       # Optional
    start_time="2024-01-15T15:00:00Z",  # Optional
    end_time="2024-01-15T16:00:00Z",    # Optional
    invitees=["new@example.com"],       # Optional
    send_email=False                     # Default: False
)
```

### 5. Delete Meeting (with optional email)
```python
delete_webex_meeting(
    meeting_id="meeting_id_here",
    send_email=True,                     # Default: False
    invitees=["john@example.com"]       # Required if send_email=True
)
```

## MCP Tool Usage

When using the MCP wrapper, operations are the same but use JSON format:

```json
{
  "operation": "create_meeting",
  "title": "Interview",
  "start_time": "2024-01-15T14:00:00Z",
  "end_time": "2024-01-15T15:00:00Z",
  "invitees": ["candidate@example.com"],
  "send_email": true
}
```

## Email Notifications

Email notifications use the Gmail integration. Make sure Gmail is configured in your `.env`:
- `GOOGLE_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS`

### Email Behavior:
- **Create Meeting**: Emails sent by default (can disable with `send_email=False`)
- **Update Meeting**: Emails NOT sent by default (enable with `send_email=True`)
- **Delete Meeting**: Emails NOT sent by default (enable with `send_email=True` and provide `invitees`)

## Troubleshooting

### Issue: "Webex not configured"
**Solution**: Make sure you have either:
- `WEBEX_CLIENT_ID` and `WEBEX_CLIENT_SECRET` in `.env`, OR
- `WEBEX_ACCESS_TOKEN` directly set

### Issue: "OAuth2 setup required"
**Solution**: Run `python authorize_webex.py` and complete the authorization flow

### Issue: Email notifications not working
**Solution**:
1. Verify Gmail integration is configured
2. Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
3. Make sure you've authorized Gmail API access

### Issue: Token expired
**Solution**: Re-run the authorization flow:
```bash
rm .webex_token.json
python authorize_webex.py
```

## Security Notes

1. **Never commit** `.webex_token.json` to version control
2. Add to `.gitignore`:
   ```
   .webex_token.json
   ```
3. Keep `WEBEX_CLIENT_SECRET` secure and never expose it publicly
4. Tokens expire - you may need to re-authorize periodically

## Example Use Cases

### Schedule Interview
```python
# Schedule a candidate interview and notify everyone
result = schedule_webex_meeting(
    title="Technical Interview - Senior Developer",
    start_time="2024-01-20T10:00:00Z",
    end_time="2024-01-20T11:00:00Z",
    invitees=[
        "candidate@example.com",
        "hiring_manager@company.com",
        "tech_lead@company.com"
    ],
    send_email=True
)
```

### Cancel Meeting and Notify
```python
# Cancel a meeting and inform all participants
result = delete_webex_meeting(
    meeting_id="abc123",
    send_email=True,
    invitees=[
        "candidate@example.com",
        "hiring_manager@company.com"
    ]
)
```

### List Upcoming Interviews
```python
from datetime import datetime, timedelta

# List meetings for next 7 days
start = datetime.utcnow().isoformat() + "Z"
end = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

meetings = list_webex_meetings(
    from_date=start,
    to_date=end,
    max_meetings=20
)
```
