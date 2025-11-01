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

3. **Setup Google APIs** 📖 [Detailed Guide](docs/GOOGLE_OAUTH_SETUP.md)
   ```bash
   python3 utils/oauth_setup.py
   ```

4. **Setup Database** 📖 [Detailed Guide](docs/DATABASE_SETUP.md)
   ```bash
   python3 -c "
   from src.memory.postgres import get_checkpointer
   checkpointer = get_checkpointer()
   print('✅ Database initialized')
   "
   ```

5. **Setup WhatsApp** 📖 [Detailed Guide](docs/WHATSAPP_SETUP.md)
   ```bash
   # Choose either:
   # - Chatwoot: https://chatwoot.com
   # - Evolution API: Direct WhatsApp integration
   ```

6. **Run the server**
   ```bash
   python main.py
   # OR
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

7. **Access dashboard**
   ```
   http://localhost:8000
   ```

## 🔧 Configuration

### 📁 Configuration Structure

```
config/                          ← Easy to find!
├── README.md                   ← Configuration guide
├── tools.yaml                  ← Main tool configuration
└── mcp_servers/                ← External MCP server configs
```

### Environment Variables

```env
# Google API Keys
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=./client_secret.json

# PostgreSQL Database (Direct connection required for checkpointer)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# WhatsApp Integration (choose one or both)
CHATWOOT_API_URL=https://your-chatwoot.com
CHATWOOT_API_KEY=your_key
# OR
EVOLUTION_API_URL=https://your-evolution-api.com
EVOLUTION_API_KEY=your_key
EVOLUTION_INSTANCE_NAME=your_instance

# Google Drive
CV_FOLDER_ID=your_folder_id
SHEETS_FOLDER_ID=your_folder_id

# Agent Settings
MODEL_NAME=gemini-2.5-flash
TEMPERATURE=0.7

# Webex OAuth2 Configuration (Recommended for production)
WEBEX_CLIENT_ID=your_webex_client_id
WEBEX_CLIENT_SECRET=your_webex_client_secret
WEBEX_REDIRECT_URI=http://localhost:8000/oauth/webex/callback
```

### 🔐 Webex OAuth2

**Webex integration uses OAuth2 with automatic token refresh for production.**

📖 **Complete Setup & Troubleshooting Guide**: [docs/WEBEX_OAUTH2_GUIDE.md](docs/WEBEX_OAUTH2_GUIDE.md)

Quick reference:
```env
WEBEX_CLIENT_ID=your_client_id
WEBEX_CLIENT_SECRET=your_client_secret
WEBEX_REDIRECT_URI=http://localhost:8000/oauth/webex/callback
```

To clean saved token and re-authenticate:
```bash
rm -f .webex_token.json
```

### 🛠️ Tool Configuration

#### Dynamic Tool Loading

**Main configuration file**: `config/tools.yaml` (at project root!)

**View all available tools:**
```bash
python -m src.config.tools.registry
```

**Provider Types:**
- `internal_mcp`: Built-in Python implementations (faster, easier debugging)
- `mcp_client`: External MCP servers (more features, official implementations)
- `auto`: Automatically choose best available provider

See [config/README.md](config/README.md) for complete configuration guide.

## 🤖 Agent System

The WhatsApp HR Assistant uses two powerful agent types:

### Simple ReAct Agent
A lightweight agent perfect for testing and simple tasks.

### Complex LangGraph Agent
Production-grade agent with multi-node workflow, reflection, and persistent memory.

📖 **Full Agent Documentation**: [src/agents/README.md](src/agents/README.md)

**Quick Example:**
```python
from src.agents.complex_agent import create_complex_langgraph_agent
from src.agents.tool_factory import get_tools

agent = create_complex_langgraph_agent(llm=llm, tools=tools)
result = agent.invoke(
    input_text="Schedule an interview for tomorrow at 2pm",
    thread_id="user-phone-number"
)
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

📖 **Complete Tools Guide**: [docs/TOOLS_GUIDE.md](docs/TOOLS_GUIDE.md)

## 📝 Testing

### Interactive Jupyter Notebooks

Comprehensive testing and learning notebooks in `tests/notebooks/`:

1. **`01_tools_testing.ipynb`** ⭐ - Test all tools individually
2. **`02_agents_testing.ipynb`** - Test agent workflows and memory
3. **`03_custom_agent_tutorial.ipynb`** - Build custom agents from scratch
4. **`comprehensive_test.ipynb`** - Full system validation

```bash
# Launch notebooks
jupyter notebook tests/notebooks/
```

📖 **Complete Testing Guide**: [tests/README.md](tests/README.md)

### Command Line Testing

```bash
# Test imports
python -c "from src.agents.tool_factory import get_tools; print(f'Loaded {len(get_tools())} tools')"

# Test tools
python3 -c "
from src.agents.tool_factory import get_tools
tools = get_tools()
for tool in tools:
    print(f'✅ {tool.name}: {tool.description[:60]}...')
"
```

## 📚 Documentation

### Core Setup Guides

| Guide | Description |
|-------|-------------|
| **[📋 Documentation Index](docs/README.md)** | Complete navigation hub ⭐ Start here |
| **[🔑 Google OAuth Setup](docs/GOOGLE_OAUTH_SETUP.md)** | Gmail, Calendar, Drive, Sheets APIs |
| **[🗄️ Database Setup](docs/DATABASE_SETUP.md)** | PostgreSQL configuration |
| **[📱 WhatsApp Setup](docs/WHATSAPP_SETUP.md)** | Chatwoot or Evolution API integration |
| **[🔐 Webex OAuth2](docs/WEBEX_OAUTH2_GUIDE.md)** | Webex meeting integration |
| **[📧 Gmail Setup](docs/GMAIL_SETUP.md)** | Gmail API configuration |

### Advanced Guides

| Guide | Description |
|-------|-------------|
| **[🤖 Agent System](src/agents/README.md)** | Complete agent guide |
| **[🧠 Memory System](docs/MEMORY_SYSTEM.md)** | Conversation memory configuration |
| **[🔧 Troubleshooting](docs/TROUBLESHOOTING.md)** | Common issues and solutions |
| **[➕ How to Add Tools](docs/HOW_TO_ADD_TOOLS.md)** | Developer guide |
| **[🔌 MCP Integration](docs/MCP_INTEGRATION_GUIDE.md)** | MCP protocol guide |
| **[📊 Monitoring](docs/MONITORING_GUIDE.md)** | Logging and monitoring setup |

## 📞 Support

For issues and questions:

- **Setup Issues**: Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- **Agent Questions**: See [Agent Documentation](src/agents/README.md)
- **Testing Help**: Review [Testing Guide](tests/README.md)
- **Configuration**: Read [Configuration Guide](config/README.md)
- **GitHub Issues**: Create an issue for bugs or feature requests

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

---

**Built with ❤️ for modern HR recruitment**
