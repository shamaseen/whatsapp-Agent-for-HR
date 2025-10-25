# WhatsApp HR Assistant - Documentation Index

> **Last Updated**: January 2025
> **Status**: ✅ Production Ready

## 📖 Quick Navigation

### 🚀 Getting Started (Start Here!)
1. **[Main README](../README.md)** - Project overview and setup
2. **[Webex Setup](../WEBEX_SETUP.md)** - Webex OAuth configuration
3. **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### 🧪 Testing & Development
- **[Test Suite](../tests/README.md)** - Unit and integration tests
- **[Jupyter Notebooks](../tests/notebooks/README.md)** - Interactive testing notebooks
  - `01_tools_testing.ipynb` - Test individual tools
  - `02_agents_testing.ipynb` - Test agent workflows
  - `03_custom_agent_tutorial.ipynb` - Build custom agents
  - `04_mcp_integration.ipynb` - MCP protocol testing

### 🔧 Developer Guides
- **[How to Add Tools](HOW_TO_ADD_TOOLS.md)** - Create new tools
- **[Tool Modes Comparison](TOOL_MODES_COMPARISON.md)** - MCP vs Direct tools
- **[MCP Integration Guide](MCP_INTEGRATION_GUIDE.md)** - Comprehensive MCP guide

### ⚙️ Configuration & Setup
- **[Checkpointer Setup](setup/CHECKPOINTER_SETUP.md)** - PostgreSQL memory setup
- **[OAuth Migration](OAUTH_MIGRATION_GUIDE.md)** - Google OAuth 2.0 setup
- **[Fix Permissions](FIX_PERMISSIONS.md)** - Permission issues
- **[Fix Google APIs](fix_google_apis.md)** - Google API setup

### 📚 Advanced Topics
- **[Memory System](guides/MEMORY_TROUBLESHOOTING.md)** - Memory troubleshooting
- **[Tool System](guides/TOOL_SYSTEM_GUIDE.md)** - Deep dive into tools
- **[MCP Client Guide](MCP_CLIENT_GUIDE.md)** - External MCP servers

### 📦 Archive (Historical Reference)
Located in `docs/archive/` - Historical documentation from project evolution:
- Migration guides
- Old structure documentation
- Test results
- Transformation notes

## 🎯 Common Tasks

### I want to...

#### ...get started quickly
1. Read [Main README](../README.md)
2. Set up `.env` file
3. Run `python main.py`

#### ...test the system
1. Check [Test Suite](../tests/README.md)
2. Run `python tests/unit/test_basic_imports.py`
3. Or use [Jupyter Notebooks](../tests/notebooks/README.md)

#### ...add a new tool
1. Read [How to Add Tools](HOW_TO_ADD_TOOLS.md)
2. Create tool class in `mcp_integration/tools/`
3. Register in `__init__.py`
4. Test with notebooks

#### ...configure Webex
1. Read [Webex Setup](../WEBEX_SETUP.md)
2. Set OAuth credentials in `.env`
3. Run `python authorize_webex.py`

#### ...troubleshoot issues
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review error messages
3. Check configuration

#### ...understand MCP
1. Read [MCP Integration Guide](MCP_INTEGRATION_GUIDE.md)
2. Check [Tool Modes Comparison](TOOL_MODES_COMPARISON.md)
3. Try `04_mcp_integration.ipynb` notebook

## 📂 Documentation Structure

```
docs/
├── DOCS_INDEX.md               # This file - navigation hub
├── TROUBLESHOOTING.md          # Common issues and solutions
├── HOW_TO_ADD_TOOLS.md         # Developer guide for new tools
├── MCP_INTEGRATION_GUIDE.md    # Comprehensive MCP guide
├── TOOL_MODES_COMPARISON.md    # MCP vs Direct comparison
├── MCP_CLIENT_GUIDE.md         # External MCP servers
├── OAUTH_MIGRATION_GUIDE.md    # Google OAuth setup
├── FIX_PERMISSIONS.md          # Permission fixes
├── fix_google_apis.md          # Google API setup
│
├── setup/
│   └── CHECKPOINTER_SETUP.md   # Memory configuration
│
├── guides/
│   ├── MEMORY_TROUBLESHOOTING.md
│   ├── TOOL_SYSTEM_GUIDE.md
│   └── DYNAMIC_TOOLS_SUMMARY.md
│
└── archive/                     # Historical docs
    ├── MCP_MIGRATION.md
    ├── PROJECT_STRUCTURE.md
    └── ... (other historical files)
```

## 🔑 Key Concepts

### Tools
The system has 8+ tools for different tasks:
- **Gmail** - Send and read emails
- **Calendar** - Manage Google Calendar
- **Webex** - Schedule meetings
- **CV Manager** - Manage candidate data
- **DateTime** - Time operations
- **And more...**

### Agents
LangGraph agents orchestrate tool usage:
- Memory-enabled conversations
- Multi-tool workflows
- PostgreSQL checkpointer for persistence

### MCP (Model Context Protocol)
Standardized tool interface:
- Unified `execute_tool` wrapper
- Dynamic tool registration
- Flexible tool modes

## 📝 Documentation Guidelines

### When to Read What

**New to the project?**
→ Start with [Main README](../README.md)

**Setting up development?**
→ [Test Suite](../tests/README.md) + [Notebooks](../tests/notebooks/README.md)

**Adding features?**
→ [How to Add Tools](HOW_TO_ADD_TOOLS.md)

**Having issues?**
→ [Troubleshooting](TROUBLESHOOTING.md)

**Understanding architecture?**
→ [MCP Integration Guide](MCP_INTEGRATION_GUIDE.md) + Notebooks

## 🚀 Quick Start Commands

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Test
python tests/unit/test_basic_imports.py
python tests/integration/test_simple.py

# Run notebooks
jupyter notebook tests/notebooks/

# Start server
python main.py
```

## 🆘 Need Help?

1. Check [Troubleshooting](TROUBLESHOOTING.md)
2. Review relevant guide above
3. Check error logs
4. Test with notebooks
5. Create GitHub issue

---

**Start here**: [Main README](../README.md) → [Webex Setup](../WEBEX_SETUP.md) → [Test Notebooks](../tests/notebooks/README.md)

**Happy Building! 🎉**
