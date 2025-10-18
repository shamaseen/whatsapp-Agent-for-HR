# WhatsApp HR Assistant 🤖

An intelligent HR recruitment assistant powered by **LangGraph**, **Google Gemini**, and **MCP (Model Context Protocol)**. Automates CV processing, candidate screening, interview scheduling, and communication via WhatsApp.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Features

### **Core Capabilities**
- ✅ **CV Processing**: Extract and analyze CVs from Google Drive automatically
- ✅ **Smart Search**: AI-powered candidate ranking for job positions
- ✅ **Interview Scheduling**: Automated calendar event creation
- ✅ **Email Management**: Send invitations, read, and reply to candidates
- ✅ **Conversation Memory**: Context-aware multi-turn conversations
- ✅ **Real-time Dashboard**: Monitor all requests and AI decisions

### **MCP Tools (Full CRUD)**
- 📧 **Gmail** (5 ops): Send, Get, Read, Reply, Search emails
- 📅 **Calendar** (5 ops): Create, List, Get, Update, Delete events
- 📊 **CV Sheet Manager** (7 ops): Read, Append, Update, Delete, Search, Count, Clear
- 💼 **CV Processing** (3 ops): Search/Create Sheet, Process CVs, Search Candidates
- 📞 **Webex** (4 ops): Create, Get, Update, Delete meetings
- 🕐 **DateTime** (3 ops): Get current, Add time, Format datetime
- 🧠 **Sequential Thinking**: AI planning for complex workflows

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    WhatsApp / Chatwoot                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Webhook Handler                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Request Logger & Dashboard            │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 LangGraph Agent                         │
│  ┌──────────────────────────────────────────────┐      │
│  │         Google Gemini 2.5 Flash              │      │
│  └──────────────────────────────────────────────┘      │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────┐       │
│  │         MCP Protocol (execute_tool)          │       │
│  └──────────────────┬──────────────────────────┘       │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│  Gmail MCP   │          │ Calendar MCP │
└──────────────┘          └──────────────┘
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│  Sheet MCP   │          │  Webex MCP   │
└──────────────┘          └──────────────┘
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│ CV Tools MCP │          │ DateTime MCP │
└──────────────┘          └──────────────┘
```

## 📁 Project Structure

```
whatsapp_hr_assistant/
├── agents/                  # LangGraph agent implementation
│   ├── hr_agent.py         # Main agent logic
│   └── prompts.py          # System prompts
├── mcp/                     # MCP Tools (separated for easy monitoring)
│   ├── gmail_mcp.py        # Email operations (5 ops)
│   ├── calendar_mcp.py     # Calendar CRUD (5 ops)
│   ├── cv_manager.py       # Sheet CRUD (7 ops)
│   ├── cv_tools_mcp.py     # CV processing (3 ops)
│   ├── webex_mcp.py        # Webex meetings (4 ops)
│   ├── datetime_mcp.py     # Time utilities (3 ops)
│   ├── thinking.py         # Sequential thinking
│   └── base.py             # MCP infrastructure
├── models/                  # Database models
│   └── request_logs.py     # Request logging schemas
├── services/                # Core services
│   ├── google_drive.py     # Google APIs integration
│   ├── whatsapp.py         # WhatsApp/Chatwoot client
│   ├── memory.py           # Conversation memory
│   └── request_logger.py   # Request logging service
├── tools/                   # LangChain tools (legacy)
├── docs/                    # Documentation
│   ├── MCP_MIGRATION.md
│   ├── OAUTH_MIGRATION_GUIDE.md
│   └── FIX_PERMISSIONS.md
├── main.py                  # FastAPI application + Dashboard
├── config.py                # Configuration management
├── test_components.ipynb    # Component testing
├── test_agent.ipynb         # Agent workflow testing
├── MCP_TOOLS_OVERVIEW.md    # Complete MCP reference
└── requirements.txt         # Python dependencies
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+
- PostgreSQL database
- Google Cloud Project with APIs enabled:
  - Gmail API
  - Google Calendar API
  - Google Drive API
  - Google Sheets API
- Google Gemini API key
- Chatwoot/Evolution API (for WhatsApp)

### 2. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd whatsapp_hr_assistant

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configuration

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/hr_assistant

# Google APIs
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

# WhatsApp/Chatwoot
CHATWOOT_API_URL=https://your-chatwoot.com
CHATWOOT_API_KEY=your_api_key
CHATWOOT_ACCOUNT_ID=your_account_id

# Evolution API (optional)
EVOLUTION_API_URL=https://your-evolution-api.com
EVOLUTION_API_KEY=your_api_key

# Google Drive
CV_FOLDER_ID=your_google_drive_folder_id

# Server
HOST=0.0.0.0
PORT=8000
```

### 4. Google OAuth Setup

```bash
# Place your OAuth credentials
cp /path/to/client_secret.json .

# Run OAuth flow (opens browser)
python -c "from services.google_drive import google_services; print('OAuth completed')"
```

### 5. Run Application

```bash
# Start server
python main.py

# Access dashboard
open http://localhost:8000
```

## 📊 Dashboard

The built-in monitoring dashboard provides:

- **Real-time Statistics**
  - Total requests
  - Success rate
  - Average processing time
  - Failed requests count

- **Request Logs**
  - Timestamp and sender info
  - User messages and AI responses
  - Processing time per request
  - Tools used in each workflow

- **Detailed Views**
  - Complete request information
  - Tool execution breakdown
  - Error tracking
  - Conversation history context

**Access:** `http://localhost:8000`

## 🛠️ Usage Examples

### Process CVs via WhatsApp

```
User: Start processing CVs

Agent:
✅ Found/created sheet: 962776241974
✅ Processing 5 CVs from Google Drive...
✅ Extracted data from 5 CVs
📊 Candidates stored in sheet
```

### Search Candidates

```
User: Find top 5 candidates for Senior Python Developer

Agent:
🔍 Searching candidates...
📊 Top 5 candidates ranked:
1. John Doe - 92% match (10 years Python, Django, AWS)
2. Jane Smith - 87% match (8 years Python, FastAPI)
...
```

### Schedule Interview

```
User: Schedule interview with john@example.com tomorrow at 2 PM

Agent:
📅 Interview scheduled!
✉️ Calendar invite sent to john@example.com
🔗 Meeting link: https://meet.google.com/abc-xyz
```

### Check Emails

```
User: Show me recent emails about interviews

Agent:
📧 Found 3 emails:
1. From: candidate@example.com
   Subject: Re: Interview Invitation
   Date: 2025-10-18
   Snippet: "Thank you for the invitation..."
```

## 🧪 Testing

### Component Tests

```bash
# Open test_components.ipynb in Jupyter
jupyter notebook test_components.ipynb

# Tests include:
# - Gmail operations (get, read, reply, search)
# - Calendar CRUD (create, get, update, delete)
# - CV Sheet Manager (read all, search, clear)
# - Memory management
# - Complete workflows
```

### Agent Tests

```bash
# Open test_agent.ipynb
jupyter notebook test_agent.ipynb

# Tests include:
# - MCP protocol tools
# - Sequential thinking
# - CV processing workflows
# - Communication tools
# - End-to-end scenarios
```

## 📚 Documentation

- **[MCP_TOOLS_OVERVIEW.md](MCP_TOOLS_OVERVIEW.md)** - Complete MCP tools reference
- **[docs/MCP_MIGRATION.md](docs/MCP_MIGRATION.md)** - Migration guide to MCP architecture
- **[docs/OAUTH_MIGRATION_GUIDE.md](docs/OAUTH_MIGRATION_GUIDE.md)** - OAuth setup guide
- **[docs/FIX_PERMISSIONS.md](docs/FIX_PERMISSIONS.md)** - Google permissions troubleshooting

## 🔧 MCP Tools Reference

### Gmail MCP (5 Operations)
- `send_email` - Send emails
- `get_emails` - Get recent inbox emails
- `read_email` - Read specific email by ID
- `reply_email` - Reply to email threads
- `search_emails` - Search emails by query

### Calendar MCP (5 Operations)
- `create_event` - Schedule new events
- `list_events` - List upcoming events
- `get_event` - Get event details
- `update_event` - Modify existing events
- `delete_event` - Cancel/delete events

### CV Sheet Manager (7 Operations)
- `read_all_rows` - Get all candidate data
- `append_rows` - Add new candidates
- `update_row` - Modify entries
- `delete_row` - Remove entries
- `search_rows` - Query by criteria
- `get_row_count` - Count entries
- `clear_sheet` - Clear all data (preserves headers)

**See [MCP_TOOLS_OVERVIEW.md](MCP_TOOLS_OVERVIEW.md) for complete documentation.**

## 🐛 Troubleshooting

### Common Issues

**1. Google API Permission Denied**
```bash
# Check service account permissions
python -c "from services.google_drive import google_services; google_services.test_permissions()"
```

**2. Database Connection Error**
```bash
# Verify PostgreSQL is running
psql -U user -d hr_assistant -c "SELECT 1;"
```

**3. OAuth Token Issues**
```bash
# Remove old token and re-authenticate
rm token.pickle
python -c "from services.google_drive import google_services; print('Re-authenticated')"
```

**4. WhatsApp Webhook Not Receiving**
- Check webhook URL is publicly accessible
- Verify Chatwoot webhook configuration
- Check firewall/ngrok settings

### Debug Mode

Enable detailed logging:
```python
# In config.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

## 📈 Performance

- **Average response time**: ~2-3 seconds
- **CV processing**: ~5 seconds per CV
- **Concurrent requests**: Supports 10+ simultaneous users
- **Database**: PostgreSQL with indexed queries
- **Caching**: OAuth tokens cached, reduces API calls

## 🔐 Security

- ✅ OAuth 2.0 for Google APIs
- ✅ Environment variables for secrets
- ✅ Service account credentials
- ✅ Request logging for audit trails
- ✅ No credentials in version control

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **LangChain/LangGraph** - Agent framework
- **Google Gemini** - LLM model
- **Chatwoot** - WhatsApp integration
- **FastAPI** - Web framework
- **PostgreSQL** - Database

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Docs: [MCP_TOOLS_OVERVIEW.md](MCP_TOOLS_OVERVIEW.md)

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Voice message processing
- [ ] Advanced analytics dashboard
- [ ] Integration with more ATS systems
- [ ] Automated interview question generation
- [ ] Video interview scheduling (Zoom, Teams)

---

**Built with ❤️ using LangGraph, Google Gemini, and MCP**
