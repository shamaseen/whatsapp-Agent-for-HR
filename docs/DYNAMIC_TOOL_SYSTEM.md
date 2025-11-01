# Dynamic Tool Discovery and Loading System

This document describes the new dynamic tool discovery and loading system for the WhatsApp HR Assistant.

## Overview

The system now automatically discovers and loads tools from multiple sources:
- **Internal MCP Tools**: Python implementations in `src/mcp_integration/tools/`
- **External MCP Servers**: Configuration files in `src/mcp_integration/servers/`

## Key Features

### 1. Auto-Discovery
- ✅ Internal MCP tools are auto-discovered by scanning Python files
- ✅ External MCP configs are auto-discovered from JSON files
- ✅ No manual registration required
- ✅ Add new tools by just creating files

### 2. Flexible Configuration
- ✅ YAML-based configuration (`src/config/tool_config.yaml`)
- ✅ Switch tools between internal/external modes
- ✅ Enable/disable tools individually
- ✅ Reference external configs by file name

### 3. Tool Inspection
- ✅ List all available tools
- ✅ Validate configuration
- ✅ Get detailed tool information
- ✅ Generate config templates

## Components

### Tool Discovery (`src/config/tool_discovery.py`)

Automatically discovers tools from various sources:

```python
from src.config.tool_discovery import ToolDiscovery

discovery = ToolDiscovery()

# Get all available tools
all_tools = discovery.get_all_available_tools()

# Internal MCP tools
internal_tools = discovery.discover_internal_mcp_tools()

# External MCP configs
mcp_configs = discovery.discover_mcp_configs()
```

**How it works:**
1. Scans `src/mcp_integration/tools/**/*.py` for classes inheriting from `MCPTool`
2. Instantiates each tool to get its name
3. Groups related tools (e.g., CV processing tools)
4. Scans `mcp_configs/` for `.json` and `.mcp.json` files
5. Validates MCP configuration format

### Tool Inspector (`src/config/tool_inspector.py`)

Provides utilities to inspect and validate tools:

```python
from src.config.tool_inspector import ToolInspector

inspector = ToolInspector()

# List all tools
print(inspector.list_all_tools(format="table"))

# Get tool details
details = inspector.get_tool_details("gmail")

# Validate configuration
validation = inspector.validate_tool_config()
```

**Use from command line:**
```bash
python -m src.config.tool_inspector
```

### Tool Loader (`src/config/tool_loader.py`)

Dynamically loads tools based on YAML configuration:

```python
from src.config.tool_loader import ToolLoader

loader = ToolLoader()

# Load all enabled tools
tools = loader.get_tools()

# Get summary
summary = loader.get_tool_summary()

# List available vs configured
available = loader.list_available_tools()
```

**Features:**
- Loads internal MCP tools by auto-discovering them
- Loads external MCP clients with retry logic
- Supports config file references (`mcp_config_file`)
- Handles environment variable substitution
- Manages MCP client lifecycle

## Usage

### Adding a New Internal MCP Tool

1. Create a new Python file in `src/mcp_integration/tools/`
   ```python
   # src/mcp_integration/tools/my_category/my_tool_mcp.py
   from src.mcp_integration.protocol.base import MCPTool

   class MyToolMCPTool(MCPTool):
       def get_name(self) -> str:
           return "my_tool"

       def get_description(self) -> str:
           return "Description of my tool"

       def get_input_schema(self) -> Dict[str, Any]:
           return {
               "type": "object",
               "properties": {
                   "param": {"type": "string"}
               },
               "required": ["param"]
           }

       def execute(self, param: str) -> Any:
           # Implementation
           return f"Result: {param}"
   ```

2. Add to `tool_config.yaml`:
   ```yaml
   tools:
     my_tool:
       enabled: true
       mode: "internal_mcp"  # Will be auto-discovered!
   ```

3. That's it! The tool will be automatically discovered and loaded.

### Adding a New External MCP Server

1. Create a config file in `src/mcp_integration/servers/`:
   ```json
   // src/mcp_integration/servers/my_server.json
   {
     "name": "my_server",
     "description": "My Custom MCP Server",
     "transport": "stdio",
     "command": "npx",
     "args": ["-y", "@example/mcp-server"],
     "enabled": true
   }
   ```

2. Add to `tool_config.yaml`:
   ```yaml
   tools:
     my_server:
       enabled: true
       mode: "mcp_client"
       mcp_config_file: "my_server"  # References my_server.mcp.json
   ```

3. Done! The config will be auto-discovered and the server will be connected.

### Switching Tool Modes

To switch a tool from internal to external (or vice versa):

**Option 1: Switch to external MCP server**
```yaml
gmail:
  enabled: true
  mode: "mcp_client"  # Changed from internal_mcp
  mcp_config_file: "gmail_external"  # Add MCP config reference
```

**Option 2: Switch back to internal**
```yaml
gmail:
  enabled: true
  mode: "internal_mcp"  # Changed from mcp_client
  # Remove mcp_config_file or mcp_config
```

## Configuration Reference

### tool_config.yaml Structure

```yaml
# Tool configurations
tools:
  tool_name:
    enabled: true|false          # Enable/disable tool
    mode: "internal_mcp"         # internal_mcp, mcp_client, direct
    # For mcp_client mode:
    mcp_config_file: "config"    # Reference to mcp_configs/config.mcp.json
    # OR inline config:
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@package/server"]

# Global MCP settings
global_mcp_settings:
  retry_attempts: 3
  retry_delay: 1.0
  connection_timeout: 30.0
```

### MCP Config File Format

**stdio Transport (Local Servers):**
```json
{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-example"],
  "env": {
    "API_KEY": "${MY_API_KEY}"
  },
  "retry_attempts": 3,
  "retry_delay": 2.0
}
```

**streamable_http Transport (Remote Servers):**
```json
{
  "type": "streamable_http",
  "url": "http://localhost:3000/mcp/",
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  },
  "retry_attempts": 3,
  "retry_delay": 2.0
}
```

## Testing

### Run Tool Inspector
```bash
python -m src.config.tool_inspector
```

### Run Tool Discovery Test
```bash
python -m src.config.tool_discovery
```

### Run Comprehensive Tests (Jupyter)
```bash
jupyter notebook tests/notebooks/05_pipeline_testing.ipynb
```

## Benefits

1. **No Code Changes Required**: Add tools by creating files
2. **Flexible Deployment**: Switch between internal and external implementations
3. **Easy Testing**: Test with different tool combinations
4. **Better Organization**: Tools are auto-discovered and grouped
5. **Validation**: Built-in config validation
6. **Environment-Specific**: Use different tools in dev/prod

## Migration Guide

If you have existing tools that aren't being discovered:

1. **Check file naming**: Tools should be in `*_mcp.py` files or inherit from `MCPTool`
2. **Check imports**: Make sure the tool file can be imported (no missing dependencies)
3. **Check tool name**: Use `tool.get_name()` to see the actual name
4. **Update config**: Match the tool name in `tool_config.yaml`

## Troubleshooting

### Tool not discovered
- Check if the file is in `src/mcp_integration/tools/`
- Make sure class inherits from `MCPTool`
- Check if there are import errors (run discovery with logging)

### MCP config not found
- Check file is in `mcp_configs/` directory
- Make sure file ends with `.json` or `.mcp.json`
- Verify JSON is valid
- Check `mcp_config_file` matches filename (without extension)

### Tool fails to load
- Check tool dependencies are installed
- Verify MCP server is available (for external)
- Check environment variables are set
- Review logs for detailed error messages

## Future Enhancements

- [ ] Hot-reload configuration changes
- [ ] Tool versioning and compatibility checks
- [ ] Performance metrics per tool
- [ ] Tool dependency resolution
- [ ] Visual configuration editor
