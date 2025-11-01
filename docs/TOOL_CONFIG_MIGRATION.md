# Tool Configuration Migration Guide

## ✅ What Changed?

### Before (Old System - Confusing)
```env
# In .env file:
GMAIL_MODE=tool
CALENDAR_MODE=tool
DATETIME_MODE=mcp
THINKING_MODE=mcp
...
```

❌ Problems:
- Too many environment variables
- Can't configure MCP server details
- Hard to add new tools
- Configuration scattered

### After (New System - Clean & Simple)
```env
# In .env file:
TOOL_MODE=dynamic
```

```yaml
# In src/config/tool_config.yaml:
tools:
  gmail:
    enabled: true
    mode: "internal_mcp"

  thinking:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]
```

✅ Benefits:
- Single `TOOL_MODE` variable
- All configuration in one YAML file
- Easy to configure MCP servers
- Simple to add/remove tools
- Clear and organized

---

## 🚀 How to Use New System

### Step 1: Update `.env`

**Old:**
```env
GMAIL_MODE=tool
CALENDAR_MODE=tool
DATETIME_MODE=mcp
THINKING_MODE=mcp
```

**New:**
```env
TOOL_MODE=dynamic
```

That's it! Just one line.

### Step 2: Configure Tools in YAML

Edit `src/config/tool_config.yaml`:

```yaml
tools:
  # Use internal implementation (fast, built-in)
  gmail:
    enabled: true
    mode: "internal_mcp"

  calendar:
    enabled: true
    mode: "internal_mcp"

  cv_processing:
    enabled: true
    mode: "internal_mcp"

  webex:
    enabled: true
    mode: "internal_mcp"

  # Use external MCP server (official implementation)
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

### Step 3: Run Your App

```bash
python main.py
```

The system will automatically:
- Load tools from YAML config
- Connect to external MCP servers
- Mix internal and external tools seamlessly

---

## 📋 Quick Reference

### Enable/Disable a Tool
```yaml
gmail:
  enabled: false  # ← Just change this
```

### Switch Mode
```yaml
# From internal to external:
gmail:
  mode: "mcp_client"  # Changed from "internal_mcp"
  mcp_config:
    type: "streamable_http"
    url: "http://localhost:3001/mcp/"
```

### Add New Tool
```yaml
brave_search:
  enabled: true
  mode: "mcp_client"
  mcp_config:
    type: "stdio"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-brave-search"]
```

---

## 🎯 Your Configuration (As Requested)

> "I may use gmail mcp and cv_tool as tool and thinking as client"

**Perfect setup:**

```yaml
tools:
  # Gmail - internal MCP implementation
  gmail:
    enabled: true
    mode: "internal_mcp"

  # CV tools - internal MCP implementation
  cv_processing:
    enabled: true
    mode: "internal_mcp"

  cv_manager:
    enabled: true
    mode: "internal_mcp"

  # Thinking - external MCP client
  thinking:
    enabled: true
    mode: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]
```

Done! Each tool configured exactly as you want.

---

## ❓ FAQ

**Q: Do I need to change my code?**
A: No! Just update `.env` and `tool_config.yaml`.

**Q: What if I want all internal tools?**
A: Set all tools to `mode: "internal_mcp"` in YAML.

**Q: What if I want all external MCP?**
A: Set all tools to `mode: "mcp_client"` in YAML.

**Q: Can I mix internal and external?**
A: Yes! That's the whole point. Each tool independent.

**Q: Where's the old tool_config.yaml?**
A: Backed up as `tool_config.yaml.backup`

**Q: I want the old system back!**
A: Just set `TOOL_MODE=mcp` in `.env` (legacy mode)

---

## 🔄 Compatibility

| Mode | Status | Usage |
|------|--------|-------|
| `TOOL_MODE=dynamic` | ✅ **Recommended** | Use YAML config |
| `TOOL_MODE=mcp` | ⚠️ Legacy | All internal MCP tools |
| `TOOL_MODE=mcp_client` | ⚠️ Legacy | Single external server |
| `TOOL_MODE=direct` | ❌ Not implemented | - |

The old individual `*_MODE` variables are **ignored** when using `TOOL_MODE=dynamic`.

---

## 📚 More Info

- **Complete Guide**: [DYNAMIC_TOOL_CONFIG.md](./DYNAMIC_TOOL_CONFIG.md)
- **Quick Summary**: [DYNAMIC_TOOL_SUMMARY.md](./DYNAMIC_TOOL_SUMMARY.md)
- **MCP Integration**: [../src/mcp_integration/README.md](../src/mcp_integration/README.md)

---

**Bottom Line:**

**Old:** Many environment variables, scattered config
**New:** One environment variable (`TOOL_MODE=dynamic`), one YAML file

**Much cleaner!** 🎉
