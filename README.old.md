# WhatsApp HR Assistant with LangChain/LangGraph

A sophisticated HR recruitment assistant that processes CVs, schedules interviews, and manages candidate communications via WhatsApp. This is a Python/LangGraph implementation equivalent to the n8n workflow system.

## Features

- **WhatsApp Integration**: Supports both Chatwoot and Evolution API (configure one or both)
- **CV Processing**: Automatically extracts and analyzes CVs from Google Drive
- **Candidate Matching**: AI-powered candidate ranking for job positions
- **Interview Scheduling**: Google Calendar, Gmail, and Webex integration
- **Conversation Memory**: PostgreSQL-backed conversation history
- **Multi-Tool Agent**: LangGraph agent with 9+ integrated tools
- **Flexible Messaging**: Choose between Chatwoot (with UI) or Evolution API (direct)

## Architecture

**Option 1: Chatwoot Integration** (Recommended for teams)
```
WhatsApp → Chatwoot → FastAPI Webhook → LangGraph Agent → Tools → Response
                                                ↓
                                       PostgreSQL Memory
                                                ↓
                                       Google Services (Drive, Sheets, Calendar, Gmail)
```

**Option 2: Direct Evolution API Integration**
```
WhatsApp → Evolution API → FastAPI Webhook → LangGraph Agent → Tools → Response
                                                     ↓
                                            PostgreSQL Memory
                                                     ↓
                                            Google Services (Drive, Sheets, Calendar, Gmail)
```

You can configure **one or both** integrations:
- **Chatwoot**: Provides conversation UI, team collaboration, labels, and automation
- **Evolution API**: Direct WhatsApp integration for simpler setups

## Project Structure

```
whatsapp_hr_assistant/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration and environment variables
├── requirements.txt        # Python dependencies
│
├── agents/
│   ├── __init__.py
│   ├── hr_agent.py        # Main LangGraph agent
│   └── prompts.py         # System prompts
│
├── tools/
│   ├── __init__.py
│   ├── cv_tools.py        # CV processing tools
│   ├── sheet_tools.py     # Google Sheets tools
│   ├── calendar_tools.py  # Google Calendar tools
│   ├── gmail_tools.py     # Gmail tools
│   ├── webex_tools.py     # Webex tools
│   └── datetime_tools.py  # Date/time utilities
│
├── services/
│   ├── __init__.py
│   ├── whatsapp.py        # Evolution API client
│   ├── google_drive.py    # Google Drive integration
│   ├── google_sheets.py   # Google Sheets integration
│   └── memory.py          # PostgreSQL memory manager
│
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic models
│
└── utils/
    ├── __init__.py
    └── helpers.py         # Helper functions
```

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Step 1: Create Google Cloud Service Account

The application requires a Google Cloud service account for accessing Google Drive, Sheets, Calendar, and Gmail APIs.

1. **Create a service account in Google Cloud Console:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to **IAM & Admin** → **Service Accounts**
   - Click **Create Service Account**
   - Provide a name (e.g., "whatsapp-hr-assistant")
   - Click **Create and Continue**

2. **Grant necessary permissions:**
   - Add the following roles:
     - **Google Drive API** - Access to read/write Drive files
     - **Google Sheets API** - Create and manage spreadsheets
     - **Google Calendar API** - Schedule events
     - **Gmail API** - Send emails

3. **Create and download JSON key:**
   - Click on your newly created service account
   - Go to the **Keys** tab
   - Click **Add Key** → **Create new key**
   - Select **JSON** format
   - Click **Create** - this will download the JSON file

4. **Place the service account file:**
   - Save the downloaded JSON file as `service-account.json` in the project root directory:
     ```
     /home/your-username/whatsapp_hr_assistant/service-account.json
     ```
   - **Important:** This file contains sensitive credentials. Never commit it to version control.

5. **Enable required APIs:**
   - In Google Cloud Console, go to **APIs & Services** → **Library**
   - Enable the following APIs:
     - Google Drive API
     - Google Sheets API
     - Google Calendar API
     - Gmail API

6. **Share Google Drive folders with service account:**
   - Copy the service account email (e.g., `whatsapp-hr-assistant@project-id.iam.gserviceaccount.com`)
   - Share your CV folder and Sheets folder with this email address (Editor access)

### Step 2: Create Environment Configuration

Create a `.env` file in the project root:

```env
# Google API Keys
GOOGLE_API_KEY=your_google_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

# Chatwoot API (Primary - for WhatsApp integration)
CHATWOOT_API_URL=https://your-chatwoot-instance.com
CHATWOOT_API_KEY=your_chatwoot_api_key

# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/hr_assistant

# Google Drive Configuration
CV_FOLDER_ID=your_cv_folder_id
SHEETS_FOLDER_ID=your_sheets_folder_id

# Webex (OAuth2 - use Client ID and Secret)
WEBEX_CLIENT_ID=your_webex_client_id
WEBEX_CLIENT_SECRET=your_webex_client_secret
# Or if you have an access token directly:
# WEBEX_ACCESS_TOKEN=your_webex_access_token

# App Settings
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Agent Settings
TEMPERATURE=0.7
MODEL_NAME=gemini-1.5-pro
MAX_MESSAGES_PER_SESSION=5000
```

**Configuration Notes:**
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account JSON file (default: `./service-account.json`)
- `CHATWOOT_API_URL`: (Optional) Your Chatwoot instance URL (e.g., `https://app.chatwoot.com`)
- `CHATWOOT_API_KEY`: (Optional) Your Chatwoot API access token (get from Profile Settings → Access Token)
- `EVOLUTION_API_URL`: (Optional) Your Evolution API instance URL
- `EVOLUTION_API_KEY`: (Optional) Your Evolution API key
- `EVOLUTION_INSTANCE_NAME`: (Optional) Your Evolution API instance name
- `CV_FOLDER_ID`: Google Drive folder ID where CV PDFs are stored (get from folder URL)
- `SHEETS_FOLDER_ID`: Google Drive folder ID where output sheets will be stored
- `DATABASE_URL`: PostgreSQL connection string for conversation memory

**Important**: Configure at least one messaging service (Chatwoot OR Evolution API)

### Step 3: Configure Messaging Service

#### Option A: Chatwoot (Recommended)

1. **Get your Chatwoot API Key:**
   - Log in to your Chatwoot instance
   - Go to **Profile Settings** → **Access Token**
   - Copy the API access token

2. **Set up webhook in Chatwoot:**
   - Go to **Settings** → **Integrations** → **Webhooks**
   - Click **Add Webhook**
   - **Webhook URL**: `http://your-server:8000/webhook/whatsapp`
   - **Events**: Select `message_created`
   - Save webhook

3. **Label conversations:**
   - For the assistant to respond, conversations must have the **"hr"** label
   - Apply label in Chatwoot: Right sidebar → Labels → Add "hr"

#### Option B: Evolution API (Direct)

1. **Set up Evolution API:**
   - Deploy Evolution API instance (see [Evolution API docs](https://github.com/EvolutionAPI/evolution-api))
   - Create WhatsApp instance
   - Get API key and instance name

2. **Configure webhook:**
   - Set webhook URL in Evolution API: `http://your-server:8000/webhook/whatsapp`
   - Enable message events

3. **Update `.env`:**
   ```env
   EVOLUTION_API_URL=https://your-evolution-api.com
   EVOLUTION_API_KEY=your_key
   EVOLUTION_INSTANCE_NAME=your_instance
   ```

## Usage

```bash
# Run the application
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

### Test Individual Components

Use the provided Jupyter notebook to test each component:

```bash
jupyter notebook test_components.ipynb
```

### Test Webhook Locally

Use the test script to simulate Chatwoot webhooks:

```bash
# Start the server first
python main.py

# In another terminal, run the test
python test_webhook.py
```

## API Endpoints

### Webhooks

- `POST /webhook/whatsapp` - Receives messages from Chatwoot
  - Accepts Chatwoot webhook format
  - Filters by "hr" label and "incoming" message type
  - Processes through LangGraph agent
  - Sends response back to Chatwoot

### Health

- `GET /health` - Health check endpoint

## Key Components

### 1. LangGraph Agent

The main AI agent uses Google Gemini and implements:
- Tool verification protocol (list_tools → execute_tool)
- Sequential thinking for complex tasks
- Automatic sheet name derivation from phone numbers
- Conversation memory with PostgreSQL

### 2. Tools

**CV Processing**:
- Extract text from PDFs
- AI-powered CV analysis (9 fields)
- Deduplication by filename

**Candidate Search**:
- AI ranking based on job requirements
- Match score calculation
- Top candidate selection

**Communication**:
- Schedule calendar events
- Send emails via Gmail
- Create Webex meetings

### 3. Memory Management

- PostgreSQL-backed conversation history
- Session-based storage (keyed by WhatsApp ID)
- Automatic cleanup (max 5000 messages per session)
- Context window of 1 exchange

## Workflow Example

```python
# User sends: "Start process cvs"

1. Webhook receives message
2. Filter: Check "hr" label and "incoming" type
3. Agent processes:
   a. List available tools
   b. Use thinking tool to plan
   c. Derive sheet name from phone: "962776241974"
   d. Call search_create_sheet(sheet_name="962776241974") → get sheet_id
   e. Call process_cvs(sheet_id) → extract and store CVs
   f. Generate response
4. Save to memory
5. Send response via Evolution API
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Format

```bash
black .
isort .
flake8 .
```

## Deployment

### Docker

```bash
# Build image
docker build -t whatsapp-hr-assistant .

# Run container
docker run -d -p 8000:8000 --env-file .env whatsapp-hr-assistant
```

### Production Considerations

- Use Gunicorn/Uvicorn with multiple workers
- Set up reverse proxy (Nginx)
- Configure SSL certificates
- Enable monitoring (Prometheus/Grafana)
- Set up log aggregation
- Use managed PostgreSQL database
- Implement rate limiting
- Add authentication for webhooks

## Differences from n8n Version

| Aspect | n8n Version | LangChain/LangGraph Version |
|--------|-------------|---------------------------|
| Language | Visual workflow (JavaScript runtime) | Python |
| Agent Framework | n8n AI Agent | LangGraph with Google Gemini |
| Memory | Built-in Postgres node | Custom PostgreSQL implementation |
| Tools | HTTP Request Tools + MCP Clients | Python functions as LangChain Tools |
| Execution | Webhook-triggered workflow | FastAPI + LangGraph agent |
| Deployment | n8n server | Standalone Python app |
| Extensibility | Visual editor | Code-based |

## Troubleshooting

### Common Issues

1. **`FileNotFoundError: [Errno 2] No such file or directory: './service-account.json'`**
   - **Cause**: The Google Cloud service account JSON file is missing
   - **Solution**:
     - Follow the "Create Google Cloud Service Account" steps above
     - Download the JSON key file from Google Cloud Console
     - Place it as `service-account.json` in the project root directory
     - Ensure the path in `.env` matches: `GOOGLE_APPLICATION_CREDENTIALS=./service-account.json`

2. **Google API Errors (403 Forbidden)**
   - **Cause**: Service account lacks proper permissions
   - **Solution**:
     - Verify the service account has enabled all required APIs (Drive, Sheets, Calendar, Gmail)
     - Share your Google Drive folders with the service account email
     - Check that service account roles include necessary permissions

3. **PostgreSQL Connection Errors**
   - **Cause**: Database not running or incorrect connection string
   - **Solution**:
     - Check DATABASE_URL format: `postgresql://user:password@localhost:5432/hr_assistant`
     - Ensure PostgreSQL is running: `sudo systemctl status postgresql`
     - Create database if needed: `createdb hr_assistant`
     - Verify network access and firewall settings

4. **Evolution API Timeout**
   - **Cause**: Invalid API endpoint or credentials
   - **Solution**:
     - Verify EVOLUTION_API_URL is accessible
     - Check EVOLUTION_API_KEY and EVOLUTION_INSTANCE_NAME are correct
     - Test the endpoint manually with curl or Postman

5. **PDF Extraction Fails**
   - **Cause**: Missing system dependencies
   - **Solution**:
     - Install poppler-utils: `sudo apt-get install poppler-utils` (Ubuntu/Debian)
     - Or on macOS: `brew install poppler`

6. **No CVs processed**
   - **Cause**: Service account cannot access Google Drive folder
   - **Solution**:
     - Share the CV folder (CV_FOLDER_ID) with the service account email
     - Grant "Editor" permissions
     - Verify folder ID in `.env` is correct

### Logs

```bash
# View application logs
tail -f logs/app.log

# Enable debug mode
export DEBUG=true
python main.py

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Credits

Based on the n8n workflow system "CV Screening & Interview Scheduler" by Hamza Shamaseen.
