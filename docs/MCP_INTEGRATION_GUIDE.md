# MCP Server Integration Guide

## 🔍 Understanding MCP vs Custom Tools

### What are MCP Servers?

**MCP (Model Context Protocol)** is an open protocol that standardizes how applications provide tools and context to LLMs.

**Key Difference:**
- **MCP Servers**: External processes (separate applications) that provide tools via stdio or HTTP transport
- **Custom Tools**: Local Python functions in the `mcp/` directory

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph Agent                      │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│  MCP Servers  │   │ Custom Tools  │
│  (External)   │   │  (Local .py)  │
└───────────────┘   └───────────────┘
        │                   │
        │                   │
   stdio/HTTP          Direct Call
```

## 🎯 Dual-Mode Support

This project supports THREE modes:

### 1. Custom Mode (Default)
```env
USE_EXTERNAL_MCP_DATETIME=false
USE_EXTERNAL_MCP_GMAIL=false
USE_EXTERNAL_MCP_CALENDAR=false
USE_EXTERNAL_MCP_SHEETS=false
USE_EXTERNAL_MCP_DRIVE=false
```

**Benefits:**
- ✅ No external dependencies
- ✅ Full control over functionality
- ✅ CV-specific business logic
- ✅ Works offline
- ✅ Faster (no IPC overhead)

**Use when:** You want complete control and custom CV recruitment functionality

### 2. MCP Server Mode
```env
USE_EXTERNAL_MCP_DATETIME=true
USE_EXTERNAL_MCP_GMAIL=true
USE_EXTERNAL_MCP_CALENDAR=true
USE_EXTERNAL_MCP_SHEETS=true
USE_EXTERNAL_MCP_DRIVE=true
```

**Benefits:**
- ✅ Official protocol compliance
- ✅ Standardized tool interfaces
- ✅ Community-maintained servers
- ✅ Multi-language support (Python, TypeScript, etc.)

**Use when:** You want to use community MCP servers or need standardization

### 3. Hybrid Mode (Recommended)
```env
USE_EXTERNAL_MCP_DATETIME=true    # Use official time server
USE_EXTERNAL_MCP_GMAIL=false      # Use custom Gmail (CV-specific)
USE_EXTERNAL_MCP_CALENDAR=false   # Use custom Calendar
USE_EXTERNAL_MCP_SHEETS=false     # Use custom CV Sheet Manager
USE_EXTERNAL_MCP_DRIVE=false      # Use custom Drive
```

**Benefits:**
- ✅ Best of both worlds
- ✅ Official servers for generic tools
- ✅ Custom tools for business logic
- ✅ Gradual migration path

**Use when:** You want to leverage official MCP servers while keeping CV-specific logic

---

## 📦 Available MCP Servers

### Official MCP Servers

#### 1. DateTime Server (modelcontextprotocol/servers/time)
```env
USE_EXTERNAL_MCP_DATETIME=true
# No URL needed - uses stdio automatically
```

**Features:**
- Get current time in any timezone
- Convert time between timezones
- IANA timezone support

**Installation:** Auto-installed via `uvx mcp-server-time`

**Tools Provided:**
- `get_current_time(timezone)`
- `convert_time(time, from_tz, to_tz)`

---

### Community MCP Servers

#### 2. Gmail MCP Server

**Option A: jeremyjordan/mcp-gmail (Python, MCP SDK)**
```bash
pip install mcp-gmail
# Run as stdio server
python -m mcp_gmail.server
```

**Option B: GongRzhe/Gmail-MCP-Server (Python, Auto-auth)**
```bash
git clone https://github.com/GongRzhe/Gmail-MCP-Server
cd Gmail-MCP-Server
pip install -r requirements.txt
python server.py
```

**Configuration:**
```env
USE_EXTERNAL_MCP_GMAIL=true
MCP_GMAIL_SERVER_URL=http://localhost:3001/mcp  # If HTTP
# Or: MCP_GMAIL_SERVER_URL=python -m mcp_gmail.server  # If stdio
```

**Tools Provided:**
- `send_email`
- `get_messages`
- `read_message`
- `reply_to_message`
- `search_messages`

---

#### 3. Calendar MCP Server

**Option A: nspady/google-calendar-mcp (TypeScript, Feature-rich)**
```bash
npm install -g @cocal/google-calendar-mcp
# Configure in MCP settings
```

**Option B: guinacio/mcp-google-calendar (Python)**
```bash
git clone https://github.com/guinacio/mcp-google-calendar
cd mcp-google-calendar
pip install -r requirements.txt
python server.py
```

**Configuration:**
```env
USE_EXTERNAL_MCP_CALENDAR=true
MCP_CALENDAR_SERVER_URL=http://localhost:3002/mcp
```

**Tools Provided:**
- `create_event`
- `list_events`
- `get_event`
- `update_event`
- `delete_event`

---

#### 4. Sheets MCP Server

**Option: xing5/mcp-google-sheets (Python, Comprehensive)**
```bash
git clone https://github.com/xing5/mcp-google-sheets
cd mcp-google-sheets
pip install -r requirements.txt
python server.py --credentials service-account.json
```

**Configuration:**
```env
USE_EXTERNAL_MCP_SHEETS=true
MCP_SHEETS_SERVER_URL=http://localhost:3003/mcp
```

**Tools Provided:**
- `read_sheet`
- `append_values`
- `update_values`
- `clear_values`
- `batch_update`

---

#### 5. Drive MCP Server

**Option: piotr-agier/google-drive-mcp (Python, Full CRUD)**
```bash
git clone https://github.com/piotr-agier/google-drive-mcp
cd google-drive-mcp
pip install -r requirements.txt
python server.py
```

**Configuration:**
```env
USE_EXTERNAL_MCP_DRIVE=true
MCP_DRIVE_SERVER_URL=http://localhost:3004/mcp
```

**Tools Provided:**
- `list_files`
- `search_files`
- `read_file`
- `upload_file`
- `delete_file`

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Core MCP integration
pip install langchain-mcp-adapters

# Official DateTime MCP server (auto-installs when used)
# No manual installation needed

# Optional: Install community MCP servers
# See server-specific instructions above
```

### Step 2: Configure .env

```bash
# Copy example
cp .env.example .env

# Edit .env
nano .env
```

**Example Configuration:**

```env
# Use official DateTime server
USE_EXTERNAL_MCP_DATETIME=true

# Use custom tools for the rest
USE_EXTERNAL_MCP_GMAIL=false
USE_EXTERNAL_MCP_CALENDAR=false
USE_EXTERNAL_MCP_SHEETS=false
USE_EXTERNAL_MCP_DRIVE=false
```

### Step 3: Start Application

```bash
python main.py
```

**Expected Output:**
```
Initializing MCP servers: ['datetime']
Successfully loaded 2 tools from MCP servers
  - get_current_time: Get current time in a specific timezone
  - convert_time: Convert time between timezones
Agent configured with 2 MCP server tools + 8 custom tools
MCP servers enabled: ['datetime']
Custom tools enabled: ['gmail', 'calendar', 'cv_manager', 'cv_tools', 'webex', 'thinking']
```

---

## 🔧 How It Works

### Architecture Flow

1. **Initialization** (`agents/hr_agent.py`)
   ```python
   from services.mcp_integration import mcp_manager

   # Initialize MCP servers based on config
   mcp_tools = await mcp_manager.get_tools()

   # Register custom tools based on config
   custom_enabled = mcp_manager.get_custom_tool_names()
   ```

2. **Tool Selection**
   - If `USE_EXTERNAL_MCP_GMAIL=true` → Use MCP server
   - If `USE_EXTERNAL_MCP_GMAIL=false` → Use custom `mcp/gmail_mcp.py`

3. **Agent Binding**
   ```python
   # Combine MCP server tools and custom tools
   all_tools = mcp_tools + [execute_tool]
   llm_with_tools = llm.bind_tools(all_tools)
   ```

4. **Runtime Execution**
   - MCP server tools: Called directly via HTTP/stdio
   - Custom tools: Called via `execute_tool` wrapper

---

## 📊 Comparison Matrix

| Feature | Custom Tools | MCP Servers |
|---------|-------------|-------------|
| **Setup** | ✅ No setup | ⚠️ Requires installation |
| **Performance** | ✅ Faster (local) | ⚠️ IPC overhead |
| **Customization** | ✅ Full control | ❌ Limited |
| **CV-specific** | ✅ Yes | ❌ Generic only |
| **Maintenance** | ⚠️ Manual | ✅ Community |
| **Standards** | ❌ Custom | ✅ MCP protocol |
| **Multi-lang** | ❌ Python only | ✅ Any language |

---

## 🎓 Best Practices

### Recommended Configuration

```env
# Use official MCP server for datetime (better timezone support)
USE_EXTERNAL_MCP_DATETIME=true

# Use custom tools for everything else (CV-specific logic)
USE_EXTERNAL_MCP_GMAIL=false
USE_EXTERNAL_MCP_CALENDAR=false
USE_EXTERNAL_MCP_SHEETS=false
USE_EXTERNAL_MCP_DRIVE=false
```

### When to Use MCP Servers

✅ **Use MCP servers when:**
- Official server available (e.g., datetime)
- Need standardized interface
- Want community maintenance
- Multi-language support needed

❌ **Use custom tools when:**
- Need CV-specific business logic
- Performance is critical
- Want full control
- Offline operation required

---

## 🐛 Troubleshooting

### MCP Server Not Starting

**Symptom:**
```
Error initializing MCP servers: Connection refused
```

**Solution:**
1. Check if MCP server is running
2. Verify URL/command in `.env`
3. Check server logs
4. Test with `curl http://localhost:3001/mcp`

### Tools Not Appearing

**Symptom:**
```
Agent configured with 0 MCP server tools
```

**Solution:**
1. Check `USE_EXTERNAL_MCP_*` settings
2. Verify MCP server is accessible
3. Check `langchain-mcp-adapters` installed
4. Review application startup logs

### Fallback to Custom Tools

**Symptom:**
```
MCP initialization warning: ... Using custom tools only.
```

**Solution:**
This is expected behavior! The system automatically falls back to custom tools if MCP servers fail. No action needed unless you specifically want MCP servers.

---

## 📚 Additional Resources

- [MCP Servers Directory](https://mcpservers.org/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [LangChain MCP Integration](https://docs.langchain.com/oss/python/langchain/mcp)
- [MCP Servers Analysis](../MCP_SERVERS_ANALYSIS.md)

---

## 🔄 Migration Path

### Phase 1: Start with Custom (Current)
```env
# All custom tools
USE_EXTERNAL_MCP_DATETIME=false
USE_EXTERNAL_MCP_GMAIL=false
# ...
```

### Phase 2: Add Official DateTime
```env
# Hybrid mode
USE_EXTERNAL_MCP_DATETIME=true  # Official server
USE_EXTERNAL_MCP_GMAIL=false    # Custom
# ...
```

### Phase 3: Evaluate Community Servers
```env
# Test community servers
USE_EXTERNAL_MCP_DATETIME=true
USE_EXTERNAL_MCP_GMAIL=true  # Test gmail MCP server
# ...
```

### Phase 4: Optimize
```env
# Keep what works best
USE_EXTERNAL_MCP_DATETIME=true   # Official (better timezones)
USE_EXTERNAL_MCP_GMAIL=false     # Custom (CV-specific)
USE_EXTERNAL_MCP_CALENDAR=false  # Custom (integrated workflow)
USE_EXTERNAL_MCP_SHEETS=false    # Custom (CV manager)
# ...
```

---

**Status:** Dual-mode MCP integration complete ✅

**Last Updated:** 2025-10-18
