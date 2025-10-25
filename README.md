# WhatsApp HR Assistant

An intelligent HR recruitment assistant powered by LangGraph, Google Gemini, and PostgreSQL. Handles CV processing, candidate management, email communication, and interview scheduling through WhatsApp.

## 🎯 Features

- **Conversational Memory**: PostgreSQL-backed conversation history using LangGraph checkpointer
- **CV Processing**: Automatic extraction and management of candidate data from Google Drive
- **Email Integration**: Gmail API for candidate communication
- **Calendar Management**: Google Calendar for interview scheduling
- **Video Conferencing**: Webex meeting creation and management
- **Multi-Tool Architecture**: 8+ specialized tools for HR tasks
- **Real-time Dashboard**: Monitor requests, tool usage, and performance metrics
- **WhatsApp Integration**: Chatwoot and Evolution API support

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     WhatsApp Input                          │
│              (Chatwoot / Evolution API)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Server                             │
│                  (main.py)                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Agent                                │
│   ┌──────────────────────────────────────────────┐         │
│   │  State: Annotated[messages, add_messages]    │         │
│   │  - Automatic message accumulation            │         │
│   │  - PostgreSQL checkpointer                   │         │
│   └──────────────────────────────────────────────┘         │
│                                                             │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐       │
│   │  Agent   │─────▶│  Tools   │─────▶│  Agent   │       │
│   │  Node    │      │  Node    │      │  Node    │       │
│   └──────────┘      └──────────┘      └──────────┘       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Tool Layer                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Gmail    │  │  Calendar  │  │   Webex    │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ CV Manager │  │  DateTime  │  │CV Processor│           │
│  └────────────┘  └────────────┘  └────────────┘           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               PostgreSQL Database                           │
│  - Checkpoints (conversation memory)                        │
│  - Request logs                                             │
│  - Tool execution logs                                      │
│  - Candidate data                                           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL database (Supabase or local)
- Google Cloud credentials (Gmail, Calendar, Drive APIs)
- WhatsApp integration (Chatwoot or Evolution API)

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd whatsapp_hr_assistant
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Setup Google OAuth**
   ```bash
   python3 utils/oauth_setup.py
   ```

4. **Initialize database**
   ```bash
   python3 -c "
   from services.memory_langgraph import get_checkpointer
   checkpointer = get_checkpointer()
   print('✅ Database initialized')
   "
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

6. **Access dashboard**
   ```
   http://localhost:8000
   ```

## 🔧 Configuration

### Environment Variables

```env
# Google API Keys
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=./client_secret.json

# PostgreSQL Database (Direct connection required for checkpointer)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# WhatsApp Integration (choose one or both)
# Option 1: Chatwoot
CHATWOOT_API_URL=https://your-chatwoot.com
CHATWOOT_API_KEY=your_key

# Option 2: Evolution API
EVOLUTION_API_URL=https://your-evolution-api.com
EVOLUTION_API_KEY=your_key
EVOLUTION_INSTANCE_NAME=your_instance

# Google Drive
CV_FOLDER_ID=your_folder_id
SHEETS_FOLDER_ID=your_folder_id

# Agent Settings
MODEL_NAME=gemini-2.5-flash
TEMPERATURE=0.7
```

### Tool Configuration

The system supports multiple tool modes:

```env
# Direct LangChain tools (recommended for production)
GMAIL_MODE=tool
CALENDAR_MODE=tool
SHEETS_MODE=tool
DATETIME_MODE=tool
CV_MODE=tool
WEBEX_MODE=tool

# MCP protocol tools (advanced)
THINKING_MODE=mcp
```

## 📊 Memory System

### LangGraph PostgreSQL Checkpointer

The agent uses LangGraph's built-in checkpointer for conversation memory:

```python
from agents.hr_agent import create_agent

agent = create_agent()

# Each user has separate conversation history via thread_id
result = agent.invoke(
    {"messages": [HumanMessage(content="Your message")]},
    config={"configurable": {"thread_id": user_phone_number}}
)
```

**Key features:**
- ✅ Automatic message persistence
- ✅ Thread-based isolation (per user)
- ✅ No manual memory management needed
- ✅ Full conversation history access

### Database Schema

```sql
-- Checkpoint tables (auto-created)
CREATE TABLE checkpoints (
    thread_id TEXT,
    checkpoint_ns TEXT DEFAULT '',
    checkpoint_id TEXT,
    parent_checkpoint_id TEXT,
    checkpoint JSONB,
    metadata JSONB,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

CREATE TABLE checkpoint_blobs (
    thread_id TEXT,
    checkpoint_ns TEXT,
    channel TEXT,
    data BYTEA
);

CREATE TABLE checkpoint_writes (
    thread_id TEXT,
    checkpoint_ns TEXT,
    checkpoint_id TEXT,
    task_id TEXT,
    data JSONB
);
```

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| **cv_sheet_manager** | Create, read, update Google Sheets for candidate data |
| **gmail** | Send, read, reply to emails |
| **calendar** | Create, list, update calendar events |
| **webex** | Create and manage video meetings |
| **datetime** | Get current time, timezone conversions |
| **process_cvs** | Extract data from CVs in Google Drive |
| **search_candidates** | Find and rank candidates by criteria |
| **search_create_sheet** | Find or create candidate sheets |

## 📝 Testing

### Interactive Jupyter Notebooks (Recommended)

Comprehensive testing and learning notebooks in `tests/notebooks/`:

1. **`01_tools_testing.ipynb`** ⭐ - Test all tools individually
2. **`02_agents_testing.ipynb`** - Test agent workflows and memory
3. **`03_custom_agent_tutorial.ipynb`** - Build custom agents from scratch
4. **`04_mcp_integration.ipynb`** - MCP protocol deep dive
5. **`comprehensive_test.ipynb`** - Full system validation

```bash
# Launch notebooks
jupyter notebook tests/notebooks/
```

See [tests/notebooks/README.md](tests/notebooks/README.md) for detailed guide.

### Command Line Testing

```bash
# Quick tests
python tests/unit/test_basic_imports.py
python tests/integration/test_simple.py

# Memory diagnostics
python tests/integration/check_memory.py

# Test specific tools
python3 -c "
from agents.tool_factory import get_tools
tools = get_tools()
print(f'Loaded {len(tools)} tools')
"
```

## 🔍 Monitoring & Logging

### Dashboard

Access the real-time dashboard at `http://localhost:8000`:

- **Request Statistics**: Total requests, success rate, avg processing time
- **Recent Requests**: View all incoming messages and responses
- **Tool Usage**: Track which tools are being used
- **Error Tracking**: Monitor failed requests
- **Request Details**: Drill down into individual conversations

### Database Queries

```python
from services.request_logger import request_logger

# Get statistics
stats = request_logger.get_statistics()

# Get recent requests
requests = request_logger.get_recent_requests(limit=50)

# Get specific request details
details = request_logger.get_request_details(request_id)
```

## 🔐 Security & Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **OAuth Tokens**: Stored in `token.pickle`, excluded from git
3. **Database Credentials**: Use environment variables only
4. **API Keys**: Rotate regularly, use secrets management
5. **Direct DB Connection**: Port 5432 required for checkpointer (not pooler 6543)

## 🐛 Troubleshooting

### Memory Not Working

```bash
# Check checkpoints
python3 check_memory.py

# Verify tables exist
python3 -c "
import psycopg
from config import settings
conn = psycopg.connect(settings.DATABASE_URL)
cur = conn.cursor()
cur.execute(\"SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'checkpoint%'\")
print([r[0] for r in cur.fetchall()])
"
```

**Common issues:**
- ❌ Using pooler port (6543) instead of direct port (5432)
- ❌ Missing `add_messages` annotation in state
- ❌ Tables not created properly

### Tool Errors

```bash
# Test individual tool
python3 -c "
from agents.tool_factory import get_tools
tools = get_tools()
tool = next(t for t in tools if 'gmail' in t.name.lower())
print(tool.invoke({'action': 'search_emails', 'query': 'test'}))
"
```

### Google API Issues

```bash
# Refresh OAuth token
python3 utils/oauth_setup.py
```

## 📚 Project Structure

```
whatsapp_hr_assistant/
├── agents/
│   ├── hr_agent.py          # Main agent with LangGraph
│   ├── prompts.py           # System prompts
│   └── tool_factory.py      # Tool loading and management
├── services/
│   ├── memory_langgraph.py  # PostgreSQL checkpointer
│   ├── request_logger.py    # Request logging
│   ├── whatsapp.py          # WhatsApp integration
│   └── google_services.py   # Google API clients
├── tools/
│   ├── gmail_tool.py
│   ├── calendar_tool.py
│   ├── cv_sheet_manager.py
│   └── ...
├── models/
│   └── request_logs.py      # Database models
├── main.py                  # FastAPI server
├── config.py                # Configuration
├── test_agent.ipynb         # Testing notebook
└── check_memory.py          # Memory verification script
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

[Your License]

## 🙏 Acknowledgments

- **LangGraph**: For the agent framework and checkpointer
- **Google Gemini**: For the LLM capabilities
- **LangChain**: For tool abstractions
- **Chatwoot/Evolution API**: For WhatsApp integration

## 📚 Documentation

Comprehensive documentation available in `docs/`:

- **[📋 Documentation Index](docs/DOCS_INDEX.md)** - Complete navigation hub ⭐ Start here
- **[🔧 Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[➕ How to Add Tools](docs/HOW_TO_ADD_TOOLS.md)** - Developer guide
- **[🔌 MCP Integration](docs/MCP_INTEGRATION_GUIDE.md)** - MCP protocol guide
- **[💾 Checkpointer Setup](docs/setup/CHECKPOINTER_SETUP.md)** - Memory configuration
- **[📱 Webex Setup](WEBEX_SETUP.md)** - Webex OAuth configuration
- **[🧪 Test Notebooks](tests/notebooks/README.md)** - Interactive testing guide

See [docs/README.md](docs/README.md) for full documentation index.

## 📞 Support

For issues and questions:
- **Documentation**: [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Test Notebooks**: [tests/notebooks/](tests/notebooks/)
- **GitHub Issues**: Create an issue for bugs or feature requests

---

**Built with ❤️ for modern HR recruitment**
