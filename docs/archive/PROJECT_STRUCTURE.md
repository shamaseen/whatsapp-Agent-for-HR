# WhatsApp HR Assistant - Project Structure

## 📁 Core Directories

### `/agents`
- **hr_agent.py** - Main LangGraph agent with PostgresSaver checkpointer
- **tool_factory.py** - Configurable tool loading (MCP/MCP_CLIENT modes)
- **prompts.py** - Agent system prompts

### `/services`
- **memory_langgraph.py** - PostgresSaver checkpointer setup
- **whatsapp.py** - Evolution API integration
- **google_drive.py** - Google Drive operations
- **request_logger.py** - Request/response logging

### `/mcp_tools`
MCP-based tools for agent:
- **cv_manager.py** - CV/Sheet management
- **gmail_mcp.py** - Gmail operations
- **calendar_mcp.py** - Calendar management
- **webex_mcp.py** - Webex meetings
- **datetime_mcp.py** - Date/time operations
- **cv_tools_mcp.py** - CV processing and candidate search

### `/mcp_clients`
MCP client implementations for external servers

### `/models`
Database models (request logs, tool executions)

### `/tools`
Legacy direct tools (not used when TOOL_MODE=mcp)

### `/docs`
Detailed documentation and guides

## 📄 Root Files

### Essential
- **main.py** - FastAPI application entry point
- **config.py** - Configuration management
- **requirements.txt** - Python dependencies
- **.env.example** - Environment template

### Documentation
- **README.md** - Main documentation
- **START_HERE.md** - Quick start guide
- **READY_TO_USE.md** - Current status
- **CHECKPOINTER_SETUP.md** - Memory system details
- **MEMORY_TROUBLESHOOTING.md** - Debugging guide

### Utilities
- **check_memory.py** - Database checkpoint inspector
- **verify_structure.py** - Syntax verification
- **test_simple.py** - Simple agent test
- **test_tool_modes.py** - Tool mode testing

### Scripts
- **install_deps.sh** - Dependency installation
- **cleanup.sh** - Original cleanup script
- **cleanup_repo.sh** - Repository organization

### Notebooks
- **test_updated_agent.ipynb** - Updated agent tests
- **test_agent.ipynb** - Original tests
- **test_components.ipynb** - Component tests

## 🗄️ Database Tables

### Active
- **checkpoints** - LangGraph conversation memory
- **checkpoint_writes** - LangGraph intermediate states
- **request_logs** - HTTP request logging
- **tool_executions** - Tool execution tracking

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Google API
GOOGLE_API_KEY=your_key
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
CV_FOLDER_ID=folder_id
SHEETS_FOLDER_ID=folder_id

# Tool Mode
TOOL_MODE=mcp  # or mcp_client

# WhatsApp (Evolution API)
EVOLUTION_API_URL=your_url
EVOLUTION_API_KEY=your_key
EVOLUTION_INSTANCE_NAME=your_instance
```

## 🚀 Quick Commands

```bash
# Install dependencies
./install_deps.sh

# Run application
python3 main.py

# Check memory/checkpoints
python3 check_memory.py
python3 check_memory.py <thread_id>

# Verify structure
python3 verify_structure.py

# Test agent
python3 test_simple.py
```

## 📦 Dependencies

### Core
- fastapi>=0.100.0
- uvicorn>=0.23.0
- langchain>=0.3.0
- langgraph>=0.2.0
- langchain-google-genai>=2.0.5

### Database
- psycopg>=3.1.0
- sqlalchemy>=2.0.0

### Google APIs
- google-auth>=2.23.0
- google-api-python-client>=2.100.0
- google-auth-oauthlib>=1.1.0
- google-auth-httplib2>=0.1.1

### MCP
- mcp>=1.0.0

## 🏗️ Architecture

```
main.py (FastAPI)
  │
  ├── agents/hr_agent.py (LangGraph)
  │   ├── Tool Loading (agents/tool_factory.py)
  │   │   └── 8 MCP tools (TOOL_MODE=mcp)
  │   └── Memory (services/memory_langgraph.py)
  │       └── PostgresSaver (DATABASE_URL)
  │
  └── Services
      ├── WhatsApp (Evolution API)
      ├── Request Logger
      └── Google Drive
```

## 🧪 Testing

1. **Unit Tests**: `python3 test_simple.py`
2. **Tool Modes**: `python3 test_tool_modes.py`
3. **Notebooks**: Open `.ipynb` files in Jupyter
4. **Memory**: `python3 check_memory.py`

## 📝 Memory System

- **Type**: LangGraph PostgresSaver checkpointer
- **Storage**: PostgreSQL (DATABASE_URL)
- **Thread ID**: Phone number (e.g., "962776241974")
- **Auto-save**: Yes, on every message
- **Manual management**: Not needed

## 🔍 Troubleshooting

See `MEMORY_TROUBLESHOOTING.md` for detailed debugging steps.

Quick checks:
```bash
# Verify checkpointer tables exist
psql $DATABASE_URL -c "\\dt"

# Check checkpoint count
python3 check_memory.py

# Test memory persistence
python3 test_simple.py
```
