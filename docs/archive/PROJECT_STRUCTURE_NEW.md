# Project Structure (Reorganized)

Clean, maintainable directory structure for WhatsApp HR Assistant.

## 📁 Root Structure

```
whatsapp_hr_assistant/
├── agents/              # LangGraph agent implementation
├── config/              # Configuration files
├── docs/                # Documentation
├── mcp_tools/           # MCP protocol tools
├── models/              # Database models
├── scripts/             # Utility scripts
├── services/            # Core services
├── tests/               # All tests
├── tools/               # LangChain tools
├── utils/               # Utilities
├── .archive/            # Archived old files (can be deleted)
│
├── main.py              # FastAPI server
├── config.py            # App configuration
├── requirements.txt     # Dependencies
├── README.md            # Main documentation
└── .env                 # Environment variables (not in git)
```

## 📂 Detailed Structure

### `/agents` - Agent Implementation
```
agents/
├── hr_agent.py          # Main LangGraph agent
├── prompts.py           # System prompts
├── tool_factory.py      # Legacy tool loader
└── tool_factory_v2.py   # New dynamic tool loader
```

### `/config` - Configuration Files
```
config/
└── tool_config.yaml     # Tool configuration
```

### `/docs` - Documentation
```
docs/
├── README.md            # Documentation index
├── START_HERE.md        # Quick start guide
├── PROJECT_STRUCTURE.md # This file
│
├── guides/              # User guides
│   ├── DYNAMIC_TOOLS_SUMMARY.md
│   ├── MEMORY_TROUBLESHOOTING.md
│   ├── TOOL_SYSTEM_GUIDE.md
│   └── HOW_TO_ADD_TOOLS.md
│
├── setup/               # Setup guides
│   └── CHECKPOINTER_SETUP.md
│
└── api/                 # API documentation
```

### `/mcp_tools` - MCP Tools
```
mcp_tools/
├── base.py              # MCP base classes
├── gmail_mcp.py         # Gmail MCP tool
├── calendar_mcp.py      # Calendar MCP tool
├── cv_manager.py        # CV sheet manager
├── cv_tools_mcp.py      # CV processing tools
├── datetime_mcp.py      # DateTime tool
├── webex_mcp.py         # Webex meeting tool
└── thinking.py          # Sequential thinking
```

### `/models` - Database Models
```
models/
└── request_logs.py      # Request logging models
```

### `/scripts` - Utility Scripts
```
scripts/
├── README.md
│
├── setup/               # Setup scripts
│   └── install_deps.sh
│
└── maintenance/         # Maintenance scripts
    ├── cleanup.sh
    └── cleanup_repo.sh
```

### `/services` - Core Services
```
services/
├── google_services.py   # Google API clients
├── memory_langgraph.py  # PostgreSQL checkpointer
├── request_logger.py    # Request logging
└── whatsapp.py          # WhatsApp integration
```

### `/tests` - Tests
```
tests/
├── README.md            # Test documentation
│
├── unit/                # Unit tests
│
├── integration/         # Integration tests
│   ├── check_memory.py
│   ├── test_memory_diagnostic.py
│   ├── test_simple.py
│   ├── test_tool_modes.py
│   └── verify_structure.py
│
└── notebooks/           # Jupyter notebooks
    ├── test_agent.ipynb
    ├── test_components.ipynb
    └── just_test.ipynb
```

### `/tools` - LangChain Tools
```
tools/
├── base_tool_template.py    # Base template for tools
├── tool_registry.py         # Auto-discovery system
├── tool_config.yaml         # → symlink to config/
├── example_custom_tool.py   # Example tools
│
├── gmail_tool.py
├── calendar_tool.py
├── cv_sheet_manager.py
├── cv_processor_tool.py
├── cv_search_tool.py
├── datetime_tool.py
└── webex_tool.py
```

### `/utils` - Utilities
```
utils/
└── oauth_setup.py       # OAuth configuration
```

### `/.archive` - Archived Files
```
.archive/
├── old_docs/            # Old documentation
├── old_tests/           # Old test files
├── old_scripts/         # Old scripts
└── old_logs/            # Old logs
```

## 🎯 Key Files

### Main Application
- **`main.py`** - FastAPI server with webhook handlers and dashboard
- **`config.py`** - Application configuration and settings

### Agent
- **`agents/hr_agent.py`** - LangGraph agent with PostgreSQL checkpointer
- **`agents/tool_factory_v2.py`** - Dynamic tool loading system

### Tools
- **`tools/base_tool_template.py`** - Template for creating new tools
- **`tools/tool_registry.py`** - Automatic tool discovery
- **`config/tool_config.yaml`** - Tool configuration

### Services
- **`services/memory_langgraph.py`** - Conversation memory with checkpointer
- **`services/google_services.py`** - Google API integration
- **`services/request_logger.py`** - Request logging and monitoring

## 📊 Comparison

### Before Restructure
```
Root: 40+ files (docs, tests, scripts mixed)
├── 15 markdown files in root
├── 6 test files in root
├── 4 script files in root
└── Difficult to navigate
```

### After Restructure
```
Root: 8 core files
├── docs/          # All documentation
├── tests/         # All tests
├── scripts/       # All scripts
├── config/        # All configuration
└── Easy to navigate
```

## 🗂️ File Counts

| Directory | Files | Purpose |
|-----------|-------|---------|
| `/agents` | 4 | Agent implementation |
| `/config` | 1 | Configuration |
| `/docs` | 10+ | Documentation |
| `/mcp_tools` | 8 | MCP tools |
| `/models` | 1 | Database models |
| `/scripts` | 3 | Utility scripts |
| `/services` | 4 | Core services |
| `/tests` | 8+ | Tests |
| `/tools` | 10+ | LangChain tools |
| `/utils` | 1 | Utilities |
| **Total** | **~50** | **Organized** |

## 🚀 Benefits

### ✅ Clean Root Directory
- Only essential files in root
- Easy to find main components
- Clear entry points

### ✅ Organized Documentation
- All docs in `docs/`
- Categorized by purpose
- Easy to maintain

### ✅ Separated Tests
- All tests in `tests/`
- Organized by type
- Clear test structure

### ✅ Consolidated Scripts
- All scripts in `scripts/`
- Grouped by purpose
- Easy to find and run

### ✅ Archived Old Files
- Old files in `.archive/`
- Safe to delete when confident
- Doesn't clutter main structure

## 📝 Navigation Guide

### Quick Access

| Want to... | Go to... |
|------------|----------|
| **Start using the app** | `README.md` → `docs/START_HERE.md` |
| **Add a new tool** | `docs/guides/HOW_TO_ADD_TOOLS.md` |
| **Configure tools** | `config/tool_config.yaml` |
| **Run tests** | `tests/` → `pytest tests/` |
| **Setup environment** | `scripts/setup/install_deps.sh` |
| **View documentation** | `docs/` |
| **Understand structure** | This file |

### Development Workflow

1. **Setup**: `scripts/setup/install_deps.sh`
2. **Configure**: Edit `config/tool_config.yaml` and `.env`
3. **Develop**: Work in `agents/`, `tools/`, `services/`
4. **Test**: Run tests in `tests/`
5. **Document**: Update docs in `docs/`
6. **Deploy**: Run `main.py`

## 🔄 Migration Notes

### Import Updates

Most imports remain the same:
```python
from agents.hr_agent import create_agent
from agents.tool_factory_v2 import get_tools
from services.memory_langgraph import get_checkpointer
```

### Path Updates

Test files moved:
```python
# Old
from test_memory_diagnostic import ...

# New
from tests.integration.test_memory_diagnostic import ...
```

Config file moved:
```python
# Old
config_path = "tools/tool_config.yaml"

# New
config_path = "config/tool_config.yaml"
# Or use symlink: "tools/tool_config.yaml" still works
```

## 🗑️ Cleanup

### Safe to Delete

After verifying everything works:
```bash
rm -rf .archive/
rm restructure_plan.sh
```

### Keep These
- All directories except `.archive/`
- All files in root (main.py, config.py, etc.)
- README.md
- .env (your credentials)
- token.pickle (OAuth token)

## 📈 Statistics

- **Total files**: ~100 files
- **Root files**: 15 → 8 (reduced by 47%)
- **Documentation**: Organized into 3 categories
- **Tests**: All in one place
- **Scripts**: Organized by purpose
- **Size**: 1.3 MB (same, just organized)

## 🎉 Summary

The repository is now:
- ✅ **Clean** - Root directory has only essential files
- ✅ **Organized** - Everything has its place
- ✅ **Maintainable** - Easy to find and update files
- ✅ **Scalable** - Room for growth
- ✅ **Professional** - Industry-standard structure

---

**Last updated**: October 22, 2025
**Restructure version**: 2.0
