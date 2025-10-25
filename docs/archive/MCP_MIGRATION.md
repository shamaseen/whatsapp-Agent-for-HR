# MCP Architecture Migration

## Overview
Migrating from direct API calls to Model Context Protocol (MCP) for standardized tool interface.

## Architecture

```
┌─────────────────────────────────────────┐
│         LangGraph Agent                 │
│  (with MCP-aware system prompt)         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        MCP Protocol Layer               │
│  • list_tools()   - Tool discovery      │
│  • execute_tool() - Unified execution   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         MCP Tool Registry               │
│  (Manages all MCP-compatible tools)     │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴──────────────────┬──────────┬──────────┬──────────┐
       ▼                          ▼          ▼          ▼          ▼
┌─────────────┐  ┌──────────────────────────────────────────────────┐
│ Sequential  │  │            MCP Tools                              │
│  Thinking   │  │  • CV Sheet Manager  • Gmail                     │
│    Tool     │  │  • Calendar          • Webex                     │
└─────────────┘  │  • Process CVs       • Search Candidates         │
                 │  • DateTime          • Create Sheet              │
                 └──────────────────────────────────────────────────┘
```

## Implementation Status

### ✅ Completed
- [x] MCP base classes (`mcp/base.py`)
- [x] MCP protocol tools (`list_tools`, `execute_tool`)
- [x] Sequential Thinking tool (`mcp/thinking.py`)
- [x] Tool registry system

### 🚧 In Progress
- [ ] Migrate existing tools to MCP
- [ ] Update agent configuration
- [ ] Update system prompt
- [ ] Fix test_agent notebook

### 📋 Pending
- [ ] CV Sheet Manager MCP
- [ ] Gmail MCP
- [ ] Calendar MCP
- [ ] Webex MCP
- [ ] Integration testing

## Tool Migration Plan

### 1. Sequential Thinking (NEW)
**Purpose:** AI reasoning before actions
**Status:** ✅ Implemented
**Usage:** Agent calls this first for complex tasks

### 2. CV Tools → MCP
**Files to migrate:**
- `tools/cv_tools.py` → `mcp/cv_manager.py`
**Tools:**
- search_create_sheet
- process_cvs
- search_candidates

### 3. Gmail → Gmail MCP
**Files to migrate:**
- `tools/gmail_tools.py` → `mcp/gmail_mcp.py`
**Tools:**
- send_email
- (future: list_emails, read_email, delete_email)

### 4. Calendar → Calendar MCP
**Files to migrate:**
- `tools/calendar_tools.py` → `mcp/calendar_mcp.py`
**Tools:**
- schedule_calendar_event
- (future: list_events, update_event, delete_event)

### 5. Webex → Webex MCP
**Files to migrate:**
- `tools/webex_tools.py` → `mcp/webex_mcp.py`
**Tools:**
- schedule_webex_meeting
- get_webex_meeting_details

### 6. DateTime → DateTime MCP
**Files to migrate:**
- `tools/datetime_tools.py` → `mcp/datetime_mcp.py`
**Tools:**
- get_current_datetime

## Agent Updates

### New System Prompt (from n8n)
Key additions:
1. Always call `list_tools` first
2. Use `sequential_thinking` for complex tasks
3. All tools via `execute_tool` wrapper
4. Automatic context extraction (phone → sheet_name)

### Agent Configuration
```python
from mcp.base import list_tools, execute_tool, mcp_registry
from mcp import (
    SequentialThinkingTool,
    CVSheetManagerTool,
    GmailMCPTool,
    CalendarMCPTool,
    WebexMCPTool
)

# Register tools
mcp_registry.register(SequentialThinkingTool())
mcp_registry.register(CVSheetManagerTool())
# ... register all tools

# Get LangChain tools
tools = [list_tools, execute_tool]
# Protocol tools only - actual tools registered in MCP
```

## Testing Strategy

### Unit Tests
- Test each MCP tool independently
- Test tool registration/discovery
- Test execute_tool wrapper

### Integration Tests
- Test agent with list_tools
- Test agent with execute_tool
- Test sequential thinking workflow
- Test multi-tool orchestration

### Test Agent Notebook Updates
Remove `create_agent` import, build agent inline:
```python
# Don't import create_agent
# Build agent step-by-step in notebook
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp.base import mcp_registry, list_tools, execute_tool

# Show tool registration
# Show agent build
# Test workflows
```

## Benefits

### 1. Standardization
- All tools follow MCP protocol
- Consistent interface
- Easier to add new tools

### 2. Discovery
- Agent can query available tools
- Dynamic tool loading
- Better error handling

### 3. Reasoning
- Sequential thinking before actions
- Better planning
- Fewer errors

### 4. Maintainability
- Single protocol layer
- Clear separation of concerns
- Easier debugging

## Migration Steps

1. ✅ Create MCP infrastructure
2. Create MCP tools (one by one)
3. Update agent to use MCP
4. Update system prompt
5. Test everything
6. Deprecate old tools

## Next Actions

1. Implement CV Manager MCP
2. Implement Gmail MCP
3. Implement Calendar MCP
4. Implement Webex MCP
5. Implement DateTime MCP
6. Update agent configuration
7. Update system prompt
8. Fix test notebook
9. Run integration tests
10. Update documentation
