# Dynamic Tool Configuration Guide

The WhatsApp HR Assistant now supports flexible, per-tool configuration using a YAML-based system. This allows you to mix and match internal MCP tools, external MCP clients, and direct tools - all configured in one place!

## 🎯 Why Dynamic Configuration?

**Before (Rigid):**
- All tools use the same mode (all MCP or all direct)
- Can't mix internal and external tools
- Hard to enable/disable individual tools
- Configuration scattered across code

**After (Flexible):**
- Each tool configured independently
- Mix internal MCP tools with external servers
- Easy enable/disable per tool
- All configuration in one YAML file
- Add new tools without code changes

## 🚀 Quick Start

### 1. Enable Dynamic Mode

In your `.env` file:
```env
TOOL_MODE=dynamic
```

### 2. Configure Tools

Edit `src/config/tool_config.yaml`:

```yaml
tools:
  # Use internal MCP implementation
  gmail:
    enabled: true
    mode: "internal_mcp"

  # Use external MCP server
  datetime:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-datetime"]

  # Use another external MCP server
  thinking:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]

  # Disable a tool
  brave_search:
    enabled: false
```

### 3. Run Your Application

```bash
python main.py
```

The system will automatically:
- Load enabled tools
- Connect to external MCP servers
- Mix internal and external tools seamlessly

## 📋 Configuration Options

### Tool Modes

Each tool supports three modes:

#### 1. `internal_mcp` - Internal MCP Tool
Use the built-in Python implementation:

```yaml
gmail:
  enabled: true
  mode: "internal_mcp"
```

**Available internal tools:**
- `gmail` - Gmail operations
- `calendar` - Calendar management
- `cv_manager` - CV sheet manager
- `cv_processing` - CV processing (multiple tools)
- `datetime` - DateTime utilities
- `webex` - Webex meetings

#### 2. `mcp_client` - External MCP Server
Connect to an external MCP server:

```yaml
thinking:
  enabled: true
  mode: "mcp_client"
  mcp_config:
    type: "stdio"  # or streamable_http, sse, websocket
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    retry_attempts: 3
    retry_delay: 2.0
```

**Supported transports:**
- `stdio` - Local subprocess (npx, python, node)
- `streamable_http` - Remote HTTP server (recommended)
- `sse` - Legacy HTTP+SSE (deprecated)
- `websocket` - WebSocket (experimental)

#### 3. `direct` - Direct LangChain Tool
Use direct tool implementation (legacy, not implemented yet):

```yaml
custom_tool:
  enabled: true
  mode: "direct"
```

### MCP Client Configuration

#### Stdio Transport (Local Servers)

```yaml
datetime:
  enabled: true
  mode: "mcp_client"
  mcp_config:
    type: "stdio"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-datetime"]
    env:
      DEBUG: "true"
    retry_attempts: 3
    retry_delay: 2.0
```

**Common stdio commands:**
- NPM packages: `npx -y @modelcontextprotocol/server-*`
- Python: `python /path/to/server.py`
- Node: `node /path/to/server.js`

#### Streamable HTTP Transport (Remote Servers)

```yaml
remote_api:
  enabled: true
  mode: "mcp_client"
  mcp_config:
    type: "streamable_http"
    url: "https://api.example.com/mcp/"
    headers:
      Authorization: "Bearer ${API_TOKEN}"
      X-API-Version: "v1"
    retry_attempts: 5
    retry_max_delay: 120.0
```

#### WebSocket Transport (Experimental)

```yaml
realtime:
  enabled: true
  mode: "mcp_client"
  mcp_config:
    type: "websocket"
    url: "wss://realtime.example.com/mcp"
    headers:
      Authorization: "Bearer ${WS_TOKEN}"
```

### Environment Variables in YAML

Use `${VAR}` syntax to reference environment variables:

```yaml
gmail:
  enabled: true
  mode: "mcp_client"
  mcp_config:
    type: "streamable_http"
    url: "${GMAIL_MCP_URL}"
    headers:
      Authorization: "Bearer ${GMAIL_MCP_TOKEN}"
```

Then in `.env`:
```env
GMAIL_MCP_URL=https://gmail-mcp.example.com/mcp/
GMAIL_MCP_TOKEN=your_secret_token
```

## 🎨 Usage Scenarios

### Scenario 1: All Internal Tools (Default)

**Best for:** Fast startup, no external dependencies

```yaml
tools:
  gmail:
    enabled: true
    mode: "internal_mcp"

  calendar:
    enabled: true
    mode: "internal_mcp"

  cv_manager:
    enabled: true
    mode: "internal_mcp"

  cv_processing:
    enabled: true
    mode: "internal_mcp"

  webex:
    enabled: true
    mode: "internal_mcp"
```

### Scenario 2: Hybrid (Recommended)

**Best for:** Balance between internal tools and advanced external features

```yaml
tools:
  # Internal tools for core HR functions
  gmail:
    enabled: true
    mode: "internal_mcp"

  calendar:
    enabled: true
    mode: "internal_mcp"

  cv_manager:
    enabled: true
    mode: "internal_mcp"

  cv_processing:
    enabled: true
    mode: "internal_mcp"

  webex:
    enabled: true
    mode: "internal_mcp"

  # External MCP servers for advanced features
  datetime:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-datetime"]

  thinking:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]
```

### Scenario 3: Maximum External MCP

**Best for:** Testing official MCP servers, distributed systems

```yaml
tools:
  # All external MCP servers
  gmail:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "streamable_http"
      url: "https://gmail-mcp.example.com/mcp/"
      headers:
        Authorization: "Bearer ${GMAIL_TOKEN}"

  calendar:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "streamable_http"
      url: "https://calendar-mcp.example.com/mcp/"
      headers:
        Authorization: "Bearer ${CALENDAR_TOKEN}"

  datetime:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-datetime"]

  thinking:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]
```

### Scenario 4: Custom Mix (Your Use Case!)

**Best for:** Specific requirements

```yaml
tools:
  # Use internal Gmail (optimized for HR workflows)
  gmail:
    enabled: true
    mode: "internal_mcp"

  # Use internal CV tools (custom logic)
  cv_manager:
    enabled: true
    mode: "internal_mcp"

  cv_processing:
    enabled: true
    mode: "internal_mcp"

  # Use external datetime (official server with better timezone handling)
  datetime:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-datetime"]

  # Use external thinking (complex reasoning)
  thinking:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]

  # Add external search capability
  brave_search:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-brave-search"]
      env:
        BRAVE_API_KEY: "${BRAVE_API_KEY}"
```

## 🔧 Adding New Tools

### Add Internal MCP Tool

1. Create your tool class:
```python
# src/mcp_integration/tools/custom/my_tool.py
from src.mcp_integration.protocol.base import MCPTool

class MyCustomTool(MCPTool):
    def get_name(self) -> str:
        return "my_custom_tool"

    def get_description(self) -> str:
        return "My custom tool description"

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            }
        }

    def execute(self, **kwargs):
        return f"Executed with: {kwargs}"
```

2. Register in `tool_loader.py`:
```python
tool_map = {
    ...
    "my_custom": "src.mcp_integration.tools.custom.my_tool.MyCustomTool"
}
```

3. Add to `tool_config.yaml`:
```yaml
tools:
  my_custom:
    enabled: true
    mode: "internal_mcp"
```

### Add External MCP Server

Just add to `tool_config.yaml`:

```yaml
tools:
  new_external_tool:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-new-tool"]
```

## 📊 Multi-Server Configuration

Group related tools into suites:

```yaml
multi_servers:
  analytics_suite:
    enabled: true
    tools:
      - name: "data_processor"
        type: "streamable_http"
        url: "http://localhost:8001/mcp/"

      - name: "visualizer"
        type: "streamable_http"
        url: "http://localhost:8002/mcp/"

      - name: "reporter"
        type: "stdio"
        command: "python"
        args: ["./custom_servers/reporter.py"]
```

## 🔐 Security Best Practices

### 1. Use Environment Variables
```yaml
# ❌ Bad - Hardcoded secrets
mcp_config:
  headers:
    Authorization: "Bearer sk_live_123456"

# ✅ Good - Environment variables
mcp_config:
  headers:
    Authorization: "Bearer ${API_TOKEN}"
```

### 2. Enable HTTPS/WSS in Production
```yaml
# ✅ Production
mcp_config:
  type: "streamable_http"
  url: "https://api.example.com/mcp/"  # HTTPS

# ❌ Development only
mcp_config:
  type: "streamable_http"
  url: "http://localhost:8000/mcp/"  # HTTP
```

### 3. Configure Retry Limits
```yaml
mcp_config:
  retry_attempts: 3
  retry_max_delay: 60.0  # Prevent infinite retries
```

## 🐛 Troubleshooting

### Tool Not Loading

**Check logs:**
```bash
python main.py
# Look for: "Loading MCP client tool: tool_name"
```

**Verify configuration:**
```python
from src.config.tool_loader import ToolLoader

loader = ToolLoader()
summary = loader.get_tool_summary()
print(summary)
```

### MCP Server Connection Failed

1. **Verify server is running**
   ```bash
   npx -y @modelcontextprotocol/server-datetime
   ```

2. **Check configuration**
   - Correct command/URL?
   - Environment variables set?
   - Firewall/network issues?

3. **Increase retry attempts**
   ```yaml
   mcp_config:
     retry_attempts: 5
     retry_delay: 3.0
   ```

### Environment Variables Not Working

1. **Check .env file**
   ```bash
   cat .env | grep API_TOKEN
   ```

2. **Verify YAML syntax**
   ```yaml
   # ✅ Correct
   Authorization: "Bearer ${API_TOKEN}"

   # ❌ Wrong
   Authorization: Bearer ${API_TOKEN}  # Missing quotes
   ```

3. **Reload environment**
   ```bash
   source .env
   python main.py
   ```

## 📚 Additional Resources

- [MCP Client Documentation](../src/mcp_integration/client/README.md)
- [MCP Protocol Guide](../src/mcp_integration/README.md)
- [Transport Types](../src/mcp_integration/client/mcp_transports_readme.md)
- [Official MCP Docs](https://modelcontextprotocol.io/)

## 💡 Tips

1. **Start with internal tools** - Fast and reliable
2. **Add external servers gradually** - Test one at a time
3. **Use hybrid mode** - Best balance
4. **Monitor logs** - Watch for connection issues
5. **Keep YAML clean** - Comment out disabled tools
6. **Version control** - Commit your tool_config.yaml

---

**Quick Example - Your Exact Use Case:**

```yaml
tools:
  # Internal MCP tools
  gmail:
    enabled: true
    mode: "internal_mcp"

  cv_processing:
    enabled: true
    mode: "internal_mcp"

  # External MCP clients
  thinking:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]
```

Perfect mix of internal and external tools! 🎉
