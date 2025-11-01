# Dynamic Tool Configuration - Quick Summary

## 🎉 What's New?

You can now configure each tool individually! Mix internal MCP tools with external MCP clients in one YAML file.

## 🚀 Quick Start

### 1. Enable Dynamic Mode

`.env`:
```env
TOOL_MODE=dynamic
```

### 2. Configure Your Tools

`src/config/tool_config.yaml`:
```yaml
tools:
  # Internal MCP tools (fast, built-in)
  gmail:
    enabled: true
    mode: "internal_mcp"

  cv_processing:
    enabled: true
    mode: "internal_mcp"

  # External MCP servers (official implementations)
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

### 3. Run
```bash
python main.py
```

## 📋 Available Tool Modes

| Mode | Use Case | Example |
|------|----------|---------|
| `internal_mcp` | Built-in Python tools | gmail, calendar, cv_processing |
| `mcp_client` | External MCP servers | thinking, datetime, brave_search |
| `direct` | Direct tools | Not implemented yet |

## 🎯 Your Exact Use Case

**Want to use Gmail as internal MCP, CV tools as internal, and thinking as external client?**

```yaml
tools:
  gmail:
    enabled: true
    mode: "internal_mcp"  # ✅ Internal

  cv_processing:
    enabled: true
    mode: "internal_mcp"  # ✅ Internal

  thinking:
    enabled: true
    mode: "mcp_client"    # ✅ External client
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]
```

Perfect! Each tool configured exactly how you want it.

## 🔧 Common Tasks

### Enable/Disable a Tool
```yaml
brave_search:
  enabled: false  # ← Just change this
```

### Add New External Tool
```yaml
new_tool:
  enabled: true
  mode: "mcp_client"
  mcp_config:
    type: "stdio"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-new-tool"]
```

### Use Remote HTTP Server
```yaml
remote_api:
  enabled: true
  mode: "mcp_client"
  mcp_config:
    type: "streamable_http"
    url: "https://api.example.com/mcp/"
    headers:
      Authorization: "Bearer ${API_TOKEN}"
```

### Environment Variables
```yaml
# In YAML:
headers:
  Authorization: "Bearer ${MY_TOKEN}"

# In .env:
MY_TOKEN=secret_value_here
```

## 📚 Full Documentation

- [Complete Guide](./DYNAMIC_TOOL_CONFIG.md) - All options and examples
- [MCP Integration](../src/mcp_integration/README.md) - MCP system overview
- [MCP Client](../src/mcp_integration/client/README.md) - External client guide

## 💡 Benefits

| Before | After |
|--------|-------|
| All tools same mode | Each tool independent |
| Can't mix internal/external | Mix freely |
| Hard to add tools | Just edit YAML |
| Configuration in code | Configuration in YAML |

## ⚡ Performance Tips

1. **Use internal for core tools** - Faster startup
2. **Use external for specialized** - Better features
3. **Disable unused tools** - Faster loading
4. **Enable retry for external** - Better reliability

## 🎨 Recommended Setup

```yaml
tools:
  # Core HR tools - Internal (fast)
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

  # Advanced features - External (specialized)
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

This gives you:
- ✅ Fast core functionality (internal)
- ✅ Advanced features (external)
- ✅ Best of both worlds!

---

**Questions?** See [DYNAMIC_TOOL_CONFIG.md](./DYNAMIC_TOOL_CONFIG.md) for complete documentation!
