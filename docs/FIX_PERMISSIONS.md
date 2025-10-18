# 🔧 Fix Google Sheets Permissions

## ❌ Problems Found

1. **Service account NOT shared with folders**
2. **Service account storage quota exceeded**

## ✅ Solution: Share Folders with Service Account

### Step 1: Get Your Service Account Email

Your service account email is:
```
web-client-1@n8n-rte-470608.iam.gserviceaccount.com
```

### Step 2: Share SHEETS_FOLDER_ID

1. **Open this link:**
   ```
   https://drive.google.com/drive/folders/1S6ueaa_kHGBc41I--Ase8LhbZBDl0Byo
   ```

2. **Share the folder:**
   - Click the **Share** button (top right)
   - In "Add people and groups", paste:
     ```
     web-client-1@n8n-rte-470608.iam.gserviceaccount.com
     ```
   - Set role to: **Editor**
   - **UNCHECK** "Notify people" (no need to send email to service account)
   - Click **Share**

3. **Verify:**
   - You should see the service account email in the list of people with access
   - Role should be "Editor"

### Step 3: Share CV_FOLDER_ID

1. **Open this link:**
   ```
   https://drive.google.com/drive/folders/1P2aT3zRRpPhBPDYO-nT0NOUidqMf7lTj
   ```

2. **Repeat the same sharing process:**
   - Share with: `web-client-1@n8n-rte-470608.iam.gserviceaccount.com`
   - Role: **Editor**
   - Uncheck "Notify people"
   - Click **Share**

### Step 4: Fix Storage Quota Issue

The service account's Drive storage is full. Here are your options:

#### Option A: Use Shared Folder (Recommended)

When you share a folder with the service account, **files created in that folder use YOUR storage, not the service account's storage**. This is the best solution.

After sharing the folders (Step 2 & 3), the issue should be resolved!

#### Option B: Clean Up Service Account Storage

If you need to clean up:

1. Go to: https://console.cloud.google.com/
2. Select project: **n8n-rte-470608**
3. Navigate to: **IAM & Admin** → **Service Accounts**
4. Find: `web-client-1@n8n-rte-470608.iam.gserviceaccount.com`
5. Check what files it owns and delete old ones

#### Option C: Create New Service Account

If the above doesn't work, create a fresh service account:

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **Create Service Account**
3. Name: `whatsapp-hr-assistant`
4. Grant roles:
   - Google Drive API
   - Google Sheets API
   - Gmail API
   - Google Calendar API
5. Create and download new JSON key
6. Replace `service-account.json` with the new file
7. Share folders with the new service account email

## 🧪 Test After Fixing

Run the debug script to verify:

```bash
python3 debug_permissions.py
```

You should see:
```
✅ Service account has access to folder
✅ Test sheet created successfully!
```

## 📝 Quick Summary

**What you need to do:**

1. Open: https://drive.google.com/drive/folders/1S6ueaa_kHGBc41I--Ase8LhbZBDl0Byo
2. Click **Share**
3. Add: `web-client-1@n8n-rte-470608.iam.gserviceaccount.com`
4. Role: **Editor**
5. Click **Share**

6. Open: https://drive.google.com/drive/folders/1P2aT3zRRpPhBPDYO-nT0NOUidqMf7lTj
7. Click **Share**
8. Add: `web-client-1@n8n-rte-470608.iam.gserviceaccount.com`
9. Role: **Editor**
10. Click **Share**

11. Run test: `python3 debug_permissions.py`

**That's it!** The storage issue will be resolved because files in shared folders use the folder owner's storage, not the service account's.

## ❓ Why This Happens

Service accounts have **very limited storage** (usually 15GB shared across all Google services). When you create files directly in the service account's Drive, it uses that limited quota.

**Solution:** Always create files in **your Drive** and share the folders with the service account. This way:
- Files use YOUR storage quota (usually much larger)
- Service account can still read/write/create files
- No storage quota issues

## 🎉 After Fixing

Once you've shared the folders, test the agent again:

```bash
python3 test_mcp_simple.py
```

Or use the full agent to create sheets - it should work now!
