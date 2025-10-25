# Troubleshooting Guide

Common issues and solutions for the WhatsApp HR Assistant.

## Table of Contents
- [Tool Not Found Errors](#tool-not-found-errors)
- [MCP Registry Issues](#mcp-registry-issues)
- [Configuration Errors](#configuration-errors)
- [Notebook Issues](#notebook-issues)
- [Tool Mode Switching](#tool-mode-switching)

---

## Tool Not Found Errors

### Error: "Tool 'sequential_thinking' not found in registry"

**Symptoms:**
```
✅ Tool result: {"error": "Tool 'sequential_thinking' not found in registry", ...}
```

**Cause:**
The MCP registry is empty or tools weren't registered before execution.

**Solutions:**

#### Solution 1: Use Pre-built Agent (Recommended)

Instead of manually building the agent, use the pre-built version:

```python
from agents.hr_agent import create_agent

# This automatically registers all tools based on TOOL_MODE
agent_app = create_agent()

# Now test
result = agent_app.invoke({
    "messages": [HumanMessage(content="List available tools")],
    "sender_phone": "1234567890",
    "sender_identifier": "test@example.com"
})
```

#### Solution 2: Manual Registration (In Notebooks)

If building manually in notebooks, ensure tools are registered:

```python
from mcp.base import mcp_registry
from mcp import (
    SequentialThinkingTool,
    CVSheetManagerTool,
    GmailMCPTool,
    CalendarMCPTool,
    WebexMCPTool,
    DateTimeMCPTool,
    CVProcessTool,
    SearchCandidatesTool,
    SearchCreateSheetTool
)

# Clear any existing tools (important for notebook re-runs)
mcp_registry._tools.clear()

# Register all tools
mcp_registry.register(SequentialThinkingTool())
mcp_registry.register(CVSheetManagerTool())
mcp_registry.register(GmailMCPTool())
mcp_registry.register(CalendarMCPTool())
mcp_registry.register(WebexMCPTool())
mcp_registry.register(DateTimeMCPTool())
mcp_registry.register(CVProcessTool())
mcp_registry.register(SearchCandidatesTool())
mcp_registry.register(SearchCreateSheetTool())

print(f"✅ Registered {len(mcp_registry._tools)} tools")
print(f"Tools: {', '.join(mcp_registry.get_tool_names())}")
```

#### Solution 3: Check Tool Mode

Verify your tool mode is correct:

```python
from agents.tool_factory import get_tool_mode_info

info = get_tool_mode_info()
print(f"Mode: {info['mode']}")
print(f"Tools: {info['tools']}")
```

---

## MCP Registry Issues

### Registry Cleared Between Calls

**Symptoms:**
- Tools work first time but fail on re-run
- Registry shows 0 tools after it was populated

**Cause:**
Registry was cleared (e.g., `mcp_registry._tools.clear()`) but not re-populated.

**Solution:**
Always re-register tools after clearing:

```python
# In notebooks, do this in a single cell:
mcp_registry._tools.clear()  # Clear old
# ... register all tools ...  # Re-register
# ... then build agent ...     # Use agent
```

Or better, use `create_agent()` which handles this automatically.

---

## Configuration Errors

### Error: "Field required" (Pydantic Validation)

**Symptoms:**
```
ValidationError: 4 validation errors for Settings
GOOGLE_API_KEY
  Field required
```

**Cause:**
Missing or incorrect `.env` file.

**Solution:**

1. Copy the example:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```bash
   GOOGLE_API_KEY=your_api_key_here
   DATABASE_URL=postgresql://...
   CV_FOLDER_ID=your_folder_id
   SHEETS_FOLDER_ID=your_sheets_folder_id
   ```

3. Restart your application/kernel

### Invalid TOOL_MODE

**Symptoms:**
```
ValueError: Invalid TOOL_MODE: xyz. Must be 'mcp', 'mcp_client', or 'direct'
```

**Solution:**
Set valid TOOL_MODE in `.env`:
```bash
TOOL_MODE=mcp  # or mcp_client or direct
```

---

## Notebook Issues

### Notebooks Show Old Results

**Cause:**
Jupyter caches variables between runs.

**Solution:**
1. **Restart Kernel**: Kernel → Restart Kernel
2. **Clear Output**: Cell → All Output → Clear
3. **Re-run All**: Cell → Run All

### Imports Fail in Notebooks

**Cause:**
Python path not set correctly or wrong working directory.

**Solution:**
Add this at the top of your notebook:
```python
import sys
import os

# Ensure project root is in path
project_root = os.path.abspath('..')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
```

---

## Tool Mode Switching

### Switching Modes Doesn't Work

**Symptoms:**
- Changed TOOL_MODE in .env but still see old tools

**Solution:**

1. **Update .env**:
   ```bash
   TOOL_MODE=mcp_client
   MCP_SERVER_URL=http://localhost:3000
   ```

2. **Restart application**:
   ```bash
   # Kill the process
   # Then restart
   python main.py
   ```

3. **In notebooks, restart kernel**:
   - Kernel → Restart Kernel
   - Re-run cells

### MCP Client Mode - Connection Refused

**Symptoms:**
```
Error: Failed to connect to MCP server
```

**Solutions:**

1. **Check server is running**:
   ```bash
   curl http://localhost:3000/tools
   ```

2. **Verify URL in .env**:
   ```bash
   MCP_SERVER_URL=http://localhost:3000  # Check port
   ```

3. **Check firewall**:
   - Allow connections to MCP server port
   - Check network/VPN settings

4. **Use SSE transport**:
   ```bash
   MCP_SERVER_TRANSPORT=sse  # Not stdio
   ```

---

## Google API Issues

### Permission Denied Errors

**Symptoms:**
```
HttpError 403: Permission denied
```

**Solutions:**

1. **Check service account permissions**:
   - Share Google Sheets with service account email
   - Share Google Drive folder with service account

2. **Verify OAuth scopes**:
   ```python
   from services.google_drive import google_services
   google_services.test_permissions()
   ```

3. **Re-authenticate**:
   ```bash
   rm token.pickle
   python main.py  # Will prompt for OAuth
   ```

### Gmail/Calendar API Not Enabled

**Symptoms:**
```
HttpError 403: Gmail API has not been used
```

**Solution:**

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable required APIs:
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Sheets API
3. Wait a few minutes for propagation
4. Restart application

---

## Database Issues

### Connection Failed

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Solutions:**

1. **Check PostgreSQL is running**:
   ```bash
   systemctl status postgresql
   # or
   brew services list | grep postgresql
   ```

2. **Verify DATABASE_URL**:
   ```bash
   # Format:
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

3. **For Supabase**:
   - Use connection pooler URL
   - Check IP allowlist

4. **Test connection**:
   ```bash
   psql postgresql://user:pass@host:port/dbname -c "SELECT 1;"
   ```

---

## Agent Not Responding

### Agent Gives Empty Responses

**Symptoms:**
- Agent processes but returns empty/no response
- Final message is blank

**Causes & Solutions:**

1. **Check message filtering**:
   - Ensure agent has system prompt
   - Verify messages aren't being filtered out

2. **Check tool execution**:
   - Tools may be failing silently
   - Add logging to tool_node

3. **Check LLM quota**:
   - Gemini API quota exhausted
   - Check Google Cloud Console

---

## Performance Issues

### Slow Response Times

**Solutions:**

1. **Check tool mode**:
   - MCP mode: ~100-200ms (fastest)
   - MCP Client: +100-300ms network overhead
   - Direct: ~100-200ms

2. **Optimize MCP Client**:
   - Use connection pooling
   - Enable result caching
   - Reduce network latency

3. **Check database**:
   - Add indexes
   - Use connection pooling

---

## Testing Issues

### Test Script Fails

**Symptoms:**
```bash
$ python test_tool_modes.py
# Errors...
```

**Solution:**
The test script uses mock settings. For real testing:

1. **Use notebooks**:
   - `test_components.ipynb`
   - `test_agent.ipynb`

2. **Or create .env.test**:
   ```bash
   cp .env .env.test
   # Edit with test values
   ```

---

## Getting Help

### Debug Mode

Enable detailed logging:

```python
# In config.py or .env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Check Versions

```bash
python --version  # Should be 3.9+
pip list | grep langchain
pip list | grep google
```

### Collect Information

When asking for help, provide:

1. **Tool mode**: `echo $TOOL_MODE`
2. **Error message**: Full stack trace
3. **Configuration**: Redacted .env
4. **Versions**: Python, LangChain versions
5. **Steps to reproduce**: What you did

### Resources

- **Documentation**: See `/docs` folder
- **Examples**: Check notebooks
- **Issues**: GitHub Issues
- **Mode Comparison**: `docs/TOOL_MODES_COMPARISON.md`
- **MCP Client**: `docs/MCP_CLIENT_GUIDE.md`

---

## Quick Fixes Checklist

When something doesn't work:

- [ ] Restart application/kernel
- [ ] Check .env file exists and is complete
- [ ] Verify TOOL_MODE is valid
- [ ] Ensure tools are registered (use `create_agent()`)
- [ ] Check logs for actual error
- [ ] Test with simple query first
- [ ] Verify API credentials are valid
- [ ] Check network connectivity (for MCP Client)
- [ ] Clear cache (notebooks: restart kernel)
- [ ] Review recent code changes

---

## Common Patterns

### Safe Tool Registration (Notebooks)

```python
# Safe pattern for notebooks
from mcp.base import mcp_registry

# Always clear first
mcp_registry._tools.clear()

# Register all tools
# ... registration code ...

# Verify
assert len(mcp_registry._tools) > 0, "No tools registered!"
print(f"✅ {len(mcp_registry._tools)} tools ready")
```

### Safe Agent Creation

```python
# Always use the factory
from agents.hr_agent import create_agent

# This handles everything
agent = create_agent()

# Verify it worked
assert agent is not None
print("✅ Agent ready")
```

### Safe Configuration Loading

```python
import os
from dotenv import load_dotenv

# Load from specific file
load_dotenv('.env')

# Verify critical settings
assert os.getenv('GOOGLE_API_KEY'), "Missing GOOGLE_API_KEY"
assert os.getenv('TOOL_MODE') in ['mcp', 'mcp_client', 'direct']
print("✅ Configuration loaded")
```

---

**Last Updated:** v1.1.0 - 2025-10-22
