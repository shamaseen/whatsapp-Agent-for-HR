# Dynamic Tool System - Quick Reference

Complete template-based system for easy tool management. Add, edit, or remove tools without touching core code!

## 🎯 Quick Start (30 seconds)

### 1. Create New Tool

```bash
# Create file: tools/my_tool.py
```

```python
from tools.base_tool_template import BaseToolTemplate
from typing import Type
from pydantic import BaseModel, Field

class MyTool(BaseToolTemplate):
    name = "my_tool"
    description = "What it does"
    category = "utility"

    class InputSchema(BaseModel):
        input: str = Field(description="Input parameter")

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, input: str) -> str:
        return f"Result: {input}"
```

### 2. Configure

```yaml
# tools/tool_config.yaml
tools:
  my_tool:
    enabled: true
    category: utility
```

### 3. Use

```python
from agents.tool_factory_v2 import get_tools

tools = get_tools()  # Your tool is auto-loaded!
```

## 📁 File Structure

```
whatsapp_hr_assistant/
├── tools/
│   ├── base_tool_template.py      # Base template class
│   ├── tool_registry.py           # Auto-discovery system
│   ├── tool_config.yaml           # Configuration file
│   ├── example_custom_tool.py     # Working examples
│   │
│   └── your_tool.py               # Your new tool here!
│
├── agents/
│   ├── tool_factory.py            # Old system (legacy)
│   └── tool_factory_v2.py         # New dynamic system ✨
│
└── docs/
    └── HOW_TO_ADD_TOOLS.md        # Complete guide
```

## 🛠️ Tool Templates

### Simple Tool

```python
class SimpleTool(BaseToolTemplate):
    name = "simple"
    description = "Simple operation"

    class InputSchema(BaseModel):
        text: str = Field(description="Input text")

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, text: str) -> str:
        return text.upper()
```

### API Tool

```python
class APITool(BaseToolTemplate):
    name = "api_call"
    description = "Call external API"
    requires_auth = True

    class InputSchema(BaseModel):
        endpoint: str

    args_schema: Type[BaseModel] = InputSchema

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key

    def _run(self, endpoint: str) -> dict:
        # Call API with self.api_key
        return {"status": "success"}
```

### Database Tool

```python
class DBTool(BaseToolTemplate):
    name = "db_query"
    description = "Query database"
    category = "database"

    class InputSchema(BaseModel):
        query: str

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, query: str) -> list:
        # Execute query
        return [{"id": 1, "data": "result"}]
```

## ⚙️ Configuration

### Enable/Disable Tools

```yaml
# tools/tool_config.yaml
tools:
  gmail:
    enabled: true      # Tool is active

  old_tool:
    enabled: false     # Tool is disabled
```

### Categories

```yaml
tools:
  my_tool:
    category: email    # email, calendar, cv, utility, etc.
    tags: [email, communication]
    priority: high     # high, medium, low
```

## 📋 Management Commands

### List All Tools

```python
from agents.tool_factory_v2 import list_tools

for tool in list_tools():
    print(f"{tool['name']}: {tool['enabled']}")
```

### Enable/Disable Tool

```python
from agents.tool_factory_v2 import get_tool_factory

factory = get_tool_factory()
factory.disable_tool('my_tool')
factory.enable_tool('my_tool')
```

### Reload Tools

```python
from agents.tool_factory_v2 import reload_tools

reload_tools()  # Reload after changes
```

### Filter by Category

```python
from agents.tool_factory_v2 import get_tools

email_tools = get_tools(category='email')
cv_tools = get_tools(category='cv')
```

## 🔧 MCP Tools

### Create MCP Tool

```python
# mcp_tools/my_mcp_tool.py
from mcp_tools.base import BaseMCPTool

class MyMCPTool(BaseMCPTool):
    def __init__(self):
        super().__init__(
            name="my_mcp_tool",
            description="MCP tool",
            category="general"
        )

    def execute(self, **kwargs):
        return {"status": "success"}
```

### Register MCP Tool

Add to `agents/tool_factory_v2.py`:

```python
tools_to_register = [
    # ... existing
    ('my_mcp_tool', MyMCPTool),
]
```

## ✅ Benefits

### Before (Manual System)

```python
# agents/tool_factory.py
from tools.tool1 import Tool1
from tools.tool2 import Tool2
from tools.tool3 import Tool3
# ... 50 import statements

def get_tools():
    tools = [
        Tool1(),
        Tool2(),
        Tool3(),
        # ... 50 tool instantiations
    ]
    return tools

# To add tool: Edit 3+ files
# To disable: Comment out or delete
# Config: Hardcoded in Python
```

### After (Template System)

```python
# agents/tool_factory_v2.py
from agents.tool_factory_v2 import get_tools

tools = get_tools()  # Auto-discovers everything!

# To add tool: Create 1 file
# To disable: enabled: false in YAML
# Config: Centralized in tool_config.yaml
```

## 📊 Comparison

| Feature | Old System | New System |
|---------|-----------|------------|
| Add tool | Edit 3-5 files | Create 1 file |
| Remove tool | Delete + update imports | Set `enabled: false` |
| Configure | Modify Python code | Edit YAML |
| Discovery | Manual imports | Automatic |
| Hot reload | Restart server | `reload_tools()` |
| Categories | Hardcoded | Configurable |
| Enable/Disable | Delete code | Config toggle |

## 🎓 Examples

See complete examples in:
- `tools/example_custom_tool.py` - 3 working examples
- `docs/HOW_TO_ADD_TOOLS.md` - Detailed guide
- Existing tools in `tools/` - Real implementations

## 🔍 Troubleshooting

### Tool Not Loading

✅ Check file ends with `_tool.py`
✅ Check class inherits `BaseToolTemplate`
✅ Check `name` attribute is set
✅ Check `enabled: true` in config

### Test Tool Independently

```python
from tools.my_tool import MyTool

tool = MyTool()
result = tool._run(param="test")
print(result)
```

### Debug Registry

```python
from tools.tool_registry import tool_registry

print(tool_registry.list_tools())
print(f"Discovered: {len(tool_registry.tools)} tools")
```

## 🚀 Migration

### Update Existing Code

**Old:**
```python
from agents.tool_factory import get_tools
```

**New:**
```python
from agents.tool_factory_v2 import get_tools
```

That's it! Everything else works the same.

## 📚 Documentation

- **Complete Guide**: `docs/HOW_TO_ADD_TOOLS.md`
- **Examples**: `tools/example_custom_tool.py`
- **Base Template**: `tools/base_tool_template.py`
- **Registry System**: `tools/tool_registry.py`
- **Configuration**: `tools/tool_config.yaml`

---

**🎉 Now you can add/remove tools in seconds instead of minutes!**

For detailed examples and advanced usage, see `docs/HOW_TO_ADD_TOOLS.md`.
