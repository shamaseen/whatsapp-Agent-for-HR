# Fix Google Sheets Permission Error

## Error
```
HttpError 403: The caller does not have permission
```

## Solution

### Step 1: Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** → **Library**
4. Search for **"Google Sheets API"**
5. Click on it and press **Enable**

### Step 2: Enable Other Required APIs

While you're there, enable these APIs too:

- ✅ **Google Drive API**
- ✅ **Google Sheets API** (if not already enabled)
- ✅ **Google Calendar API**
- ✅ **Gmail API**
- ✅ **Google Cloud Storage API** (optional)

### Step 3: Verify Service Account Permissions

1. Go to **IAM & Admin** → **Service Accounts**
2. Find your service account (e.g., `whatsapp-hr-assistant@...`)
3. Make sure it has these roles:
   - Editor (or)
   - Service Account User

### Step 4: Share Google Drive Folders

Your service account needs access to your Drive folders:

1. **Copy the service account email**:
   - Format: `your-service-account@project-id.iam.gserviceaccount.com`

2. **Share CV folder**:
   - Open Google Drive
   - Right-click your CV folder → Share
   - Paste the service account email
   - Give **Editor** access
   - Click Share

3. **Share Sheets folder**:
   - Repeat the same process for the folder where sheets will be created
   - Use the folder ID from `SHEETS_FOLDER_ID` in your `.env`

### Step 5: Test Again

Run the notebook cell again. It should work now!

## Quick Checklist

- [ ] Google Sheets API is enabled in Cloud Console
- [ ] Google Drive API is enabled
- [ ] Service account has Editor role
- [ ] CV folder is shared with service account email
- [ ] Sheets folder is shared with service account email
- [ ] `.env` has correct SHEETS_FOLDER_ID

## Alternative: Create Sheet in Shared Folder

If you don't want to create sheets programmatically, you can:

1. Manually create a Google Sheet
2. Share it with the service account
3. Use the sheet ID directly in your code

## Still Getting Errors?

Check the service account email in your `service-account.json`:

```bash
cat service-account.json | grep client_email
```

Make sure this exact email is shared on your Google Drive folders.
