# Configuration Directory

This directory contains all configuration files for the WhatsApp HR Assistant.

## Files

### `tools.yaml`
**Main tool configuration file** - Configure which tools are enabled and how they're loaded.

- **Location**: `config/tools.yaml` (easy to find at project root)
- **Purpose**: Enable/disable tools, choose between internal and external providers
- **Auto-discovery**: Tools are automatically discovered, you just enable/configure them here

**Quick Start:**
```bash
# View all available tools
python -m src.config.tools.registry

# Edit tool configuration
vim config/tools.yaml  # or your favorite editor
```

**Example Configuration:**
```yaml
tools:
  gmail:
    enabled: true
    provider: "internal_mcp"  # or "mcp_client" or "auto"

  datetime:
    enabled: true
    provider: "mcp_client"  # Use external MCP server
    mcp_config_file: "datetime"  # References mcp_servers/datetime.json
```

### `mcp_servers/` Directory
**External MCP server configurations** - JSON files defining external MCP servers.

Each JSON file defines an external MCP server that can be connected to:

```json
{
  "name": "datetime",
  "transport": "stdio",
  "command": "uvx",
  "args": ["mcp-server-time"],
  "enabled": true
}
```

**Available Servers:**
- `datetime.json` - Anthropic's official time/datetime MCP server
- `thinking.json` - Sequential thinking MCP server
- `gmail.json` - Gmail MCP server (alternative to internal)
- `calendar.json` - Google Calendar MCP server (alternative to internal)
- `example_sse.json` - Example SSE/HTTP server configuration (disabled by default)

## Tool Providers

The system supports three provider types:

### 1. `internal_mcp`
- **What**: Built-in Python implementations
- **Location**: `src/tools/**/*_mcp.py`
- **Pros**: Fast, no subprocess overhead, easier debugging
- **Cons**: Limited to what's implemented
- **Use when**: Available and sufficient for your needs

### 2. `mcp_client`
- **What**: External MCP servers via subprocess
- **Location**: Configured in `config/mcp_servers/*.json`
- **Pros**: Access to external tools, official implementations
- **Cons**: Subprocess overhead, potential connectivity issues
- **Use when**: Need features not in internal tools

### 3. `auto`
- **What**: Automatically choose best available provider
- **Logic**: Prefers `internal_mcp` → falls back to `mcp_client`
- **Use when**: Want automatic selection

## Adding New Tools

### Add External MCP Server

1. Create `config/mcp_servers/my_tool.json`:
   ```json
   {
     "name": "my_tool",
     "transport": "stdio",
     "command": "npx",
     "args": ["-y", "@example/mcp-server"],
     "enabled": true
   }
   ```

2. Add to `config/tools.yaml`:
   ```yaml
   my_tool:
     enabled: true
     provider: "mcp_client"
     mcp_config_file: "my_tool"
   ```

3. Done! System auto-discovers it.

### Add Internal Tool

1. Create `src/tools/category/my_tool_mcp.py`:
   ```python
   from src.mcp.protocol import MCPTool

   class MyTool(MCPTool):
       def get_name(self) -> str:
           return "my_tool"

       def get_description(self) -> str:
           return "My tool description"

       def get_input_schema(self) -> dict:
           return {...}

       def execute(self, **kwargs):
           # Tool logic here
           pass
   ```

2. Add to `config/tools.yaml`:
   ```yaml
   my_tool:
     enabled: true
     provider: "internal_mcp"
   ```

3. Done! System auto-discovers it.

## Environment Variables

Both YAML and JSON configs support environment variable expansion:

```yaml
custom_api:
  enabled: true
  provider: "mcp_client"
  mcp_config:
    type: "streamable_http"
    url: "https://api.example.com/mcp/"
    headers:
      Authorization: "Bearer ${MY_API_TOKEN}"
```

Set in `.env`:
```bash
MY_API_TOKEN=your_secret_token_here
```

## Troubleshooting

### "Tool not found in registry"
```bash
# Check what tools are discovered
python -m src.config.tools.registry
```

### "MCP config file not found"
- Check file exists: `config/mcp_servers/your_tool.json`
- Check file is valid JSON
- Check `enabled: true` in the JSON file

### "Failed to connect to MCP server"
- Check command is installed: `which uvx` or `which npx`
- Check args are correct
- Try running command manually to test

## CLI Commands

```bash
# List all discovered tools
python -m src.config.tools.registry

# Test tool loading
python -m src.config.tools.loader

# Run with specific config
python -m src.config.tools.loader --config config/tools.yaml
```

## Structure Overview

```
config/
├── README.md              ← You are here
├── tools.yaml             ← Main tool configuration
└── mcp_servers/           ← External MCP server configs
    ├── datetime.json
    ├── thinking.json
    ├── gmail.json
    ├── calendar.json
    └── example_sse.json
```

## See Also

- [Tool Development Guide](../docs/guides/tool_development.md)
- [MCP Integration Guide](../docs/guides/mcp_integration.md)
- [API Documentation](../docs/api/)
