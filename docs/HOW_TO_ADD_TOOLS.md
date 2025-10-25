# How to Add New Tools - Dynamic Template System

This guide shows you how to easily add, edit, or remove tools using the new template-based system.

## 📋 Table of Contents

- [Quick Start - Add a New Tool](#quick-start---add-a-new-tool)
- [Tool Templates](#tool-templates)
- [Configuration](#configuration)
- [MCP Tools](#mcp-tools)
- [Examples](#examples)
- [Best Practices](#best-practices)

---

## Quick Start - Add a New Tool

### Step 1: Create Tool File

Create a new file in `tools/` directory with naming pattern `*_tool.py`:

```bash
touch tools/my_custom_tool.py
```

### Step 2: Use the Template

```python
from typing import Type
from pydantic import BaseModel, Field
from tools.base_tool_template import BaseToolTemplate

class MyCustomTool(BaseToolTemplate):
    """Description of what your tool does"""

    name = "my_custom_tool"
    description = "Brief description for the LLM"
    category = "general"  # or email, calendar, cv, utility, etc.

    class InputSchema(BaseModel):
        param1: str = Field(description="First parameter")
        param2: int = Field(default=10, description="Optional parameter")

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, param1: str, param2: int = 10) -> str:
        """Your tool logic here"""
        result = f"Processed {param1} with value {param2}"
        return result
```

### Step 3: Configure the Tool

Add to `tools/tool_config.yaml`:

```yaml
tools:
  my_custom_tool:
    enabled: true
    category: general
    requires_auth: false
    tags: [custom, utility]
    priority: medium
```

### Step 4: Done!

The tool is automatically discovered and loaded. No manual registration needed!

```python
from agents.tool_factory_v2 import get_tools

# Your tool is automatically available
tools = get_tools()
```

---

## Tool Templates

### 1. Simple Tool Template

For basic operations:

```python
from tools.base_tool_template import BaseToolTemplate
from typing import Type
from pydantic import BaseModel, Field

class SimpleTool(BaseToolTemplate):
    name = "simple_tool"
    description = "Does something simple"

    class InputSchema(BaseModel):
        text: str = Field(description="Input text")

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, text: str) -> str:
        return text.upper()
```

### 2. API Tool Template

For external API calls:

```python
from tools.base_tool_template import BaseToolTemplate
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import requests

class APITool(BaseToolTemplate):
    name = "api_tool"
    description = "Calls external API"
    requires_auth = True

    class InputSchema(BaseModel):
        endpoint: str = Field(description="API endpoint")
        params: Dict[str, Any] = Field(default_factory=dict)

    args_schema: Type[BaseModel] = InputSchema

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key

    def _run(self, endpoint: str, params: Dict = None) -> Dict:
        try:
            response = requests.get(
                f"https://api.example.com/{endpoint}",
                params=params,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
```

### 3. Database Tool Template

For database operations:

```python
from tools.base_tool_template import BaseToolTemplate
from typing import Type, List, Dict
from pydantic import BaseModel, Field
import psycopg

class DatabaseTool(BaseToolTemplate):
    name = "db_tool"
    description = "Queries database"
    category = "database"

    class InputSchema(BaseModel):
        table: str = Field(description="Table name")
        filters: Dict = Field(default_factory=dict)
        limit: int = Field(default=10)

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, table: str, filters: Dict = None, limit: int = 10) -> List[Dict]:
        try:
            conn = psycopg.connect(DATABASE_URL)
            cur = conn.cursor()

            query = f"SELECT * FROM {table} LIMIT {limit}"
            cur.execute(query)
            results = cur.fetchall()

            conn.close()
            return [dict(row) for row in results]
        except Exception as e:
            return [{"error": str(e)}]
```

---

## Configuration

### Tool Configuration (tool_config.yaml)

```yaml
tools:
  your_tool_name:
    enabled: true              # Enable/disable tool
    category: general          # Category for organization
    requires_auth: false       # Requires authentication
    tags: [tag1, tag2]        # Tags for filtering
    priority: high            # high, medium, low
```

### Enable/Disable Tools Programmatically

```python
from agents.tool_factory_v2 import get_tool_factory

factory = get_tool_factory()

# Disable a tool
factory.disable_tool('my_custom_tool')

# Enable a tool
factory.enable_tool('my_custom_tool')

# List all tools
tools = factory.list_available_tools()
for tool in tools:
    print(f"{tool['name']}: enabled={tool['enabled']}")
```

### Filter Tools by Category

```python
from agents.tool_factory_v2 import get_tools

# Get only email tools
email_tools = get_tools(category='email')

# Get only CV tools
cv_tools = get_tools(category='cv')
```

---

## MCP Tools

### Create MCP Tool

Create in `mcp_tools/` directory:

```python
from mcp_tools.base import BaseMCPTool
from typing import Dict, Any

class MyMCPTool(BaseMCPTool):
    """MCP-compatible tool"""

    def __init__(self):
        super().__init__(
            name="my_mcp_tool",
            description="MCP tool description",
            category="general"
        )

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool"""
        return {"status": "success", "data": "result"}
```

### Register MCP Tool

MCP tools are auto-registered in `tool_factory_v2.py`. Add to the list:

```python
tools_to_register = [
    # ... existing tools
    ('my_mcp_tool', MyMCPTool),
]
```

---

## Examples

### Example 1: Weather Tool

```python
# tools/weather_tool.py
from tools.base_tool_template import BaseToolTemplate
from typing import Type
from pydantic import BaseModel, Field
import requests

class WeatherTool(BaseToolTemplate):
    name = "get_weather"
    description = "Get current weather for a city"
    category = "utility"

    class InputSchema(BaseModel):
        city: str = Field(description="City name")
        units: str = Field(default="metric", description="Temperature units")

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, city: str, units: str = "metric") -> str:
        try:
            api_key = "your_api_key"
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {"q": city, "appid": api_key, "units": units}

            response = requests.get(url, params=params)
            data = response.json()

            temp = data['main']['temp']
            description = data['weather'][0]['description']

            return f"Weather in {city}: {temp}°{'C' if units=='metric' else 'F'}, {description}"
        except Exception as e:
            return f"Error: {str(e)}"
```

Configuration:

```yaml
tools:
  get_weather:
    enabled: true
    category: utility
    requires_auth: false
    tags: [weather, api, utility]
    priority: low
```

### Example 2: Send SMS Tool

```python
# tools/sms_tool.py
from tools.base_tool_template import BaseToolTemplate
from typing import Type
from pydantic import BaseModel, Field
from twilio.rest import Client

class SMSTool(BaseToolTemplate):
    name = "send_sms"
    description = "Send SMS message via Twilio"
    category = "communication"
    requires_auth = True

    class InputSchema(BaseModel):
        to: str = Field(description="Recipient phone number")
        message: str = Field(description="Message to send")

    args_schema: Type[BaseModel] = InputSchema

    def __init__(self, account_sid: str = None, auth_token: str = None, **kwargs):
        super().__init__(**kwargs)
        self.client = Client(account_sid, auth_token)
        self.from_number = "+1234567890"

    def _run(self, to: str, message: str) -> str:
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to
            )
            return f"SMS sent successfully. SID: {msg.sid}"
        except Exception as e:
            return self.handle_error(e)
```

### Example 3: Database Query Tool

```python
# tools/db_query_tool.py
from tools.base_tool_template import BaseToolTemplate
from typing import Type, List, Dict
from pydantic import BaseModel, Field
import psycopg
from config import settings

class DBQueryTool(BaseToolTemplate):
    name = "query_database"
    description = "Query the database with natural language"
    category = "database"

    class InputSchema(BaseModel):
        query: str = Field(description="SQL query to execute")
        limit: int = Field(default=10, description="Maximum rows to return")

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, query: str, limit: int = 10) -> List[Dict]:
        try:
            # Security: validate query is SELECT only
            if not query.strip().upper().startswith('SELECT'):
                return [{"error": "Only SELECT queries allowed"}]

            conn = psycopg.connect(settings.DATABASE_URL)
            cur = conn.cursor()

            cur.execute(f"{query} LIMIT {limit}")
            columns = [desc[0] for desc in cur.description]
            results = cur.fetchall()

            conn.close()

            return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            return [{"error": self.handle_error(e)}]
```

---

## Best Practices

### 1. Naming Conventions

- **File names**: `{feature}_tool.py` (e.g., `weather_tool.py`)
- **Class names**: `{Feature}Tool` (e.g., `WeatherTool`)
- **Tool names**: `{action}_{noun}` (e.g., `get_weather`, `send_email`)

### 2. Documentation

Always provide clear descriptions:

```python
class MyTool(BaseToolTemplate):
    name = "my_tool"
    description = "Clear, concise description that LLM will use to decide when to use this tool"

    class InputSchema(BaseModel):
        param: str = Field(description="Describe what this parameter does")
```

### 3. Error Handling

Use the built-in error handler:

```python
def _run(self, param: str) -> str:
    try:
        # Your logic
        return result
    except Exception as e:
        return self.handle_error(e)
```

### 4. Input Validation

Use Pydantic for validation:

```python
from pydantic import BaseModel, Field, validator

class InputSchema(BaseModel):
    email: str = Field(description="Email address")

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
```

### 5. Testing

Test your tool before deployment:

```python
# Test your tool
tool = MyCustomTool()
result = tool._run(param1="test", param2=5)
print(result)
```

### 6. Categories

Use standard categories for consistency:

- `email` - Email operations
- `calendar` - Calendar/scheduling
- `cv` - CV/candidate management
- `communication` - Messaging/meetings
- `utility` - General utilities
- `database` - Database operations

---

## Tool Management CLI

### List Tools

```python
from agents.tool_factory_v2 import list_tools

tools = list_tools()
for tool in tools:
    status = "✅" if tool['enabled'] else "❌"
    print(f"{status} {tool['name']} ({tool['category']})")
```

### Reload Tools

```python
from agents.tool_factory_v2 import reload_tools

# Reload after making changes
reload_tools()
```

### Get Tool Info

```python
from agents.tool_factory_v2 import get_tool_factory

factory = get_tool_factory()
info = factory.get_tool_info('my_custom_tool')
print(info)
```

---

## Troubleshooting

### Tool Not Loading

1. Check file naming: `*_tool.py`
2. Check class inherits from `BaseToolTemplate`
3. Check `name` attribute is set
4. Check `enabled: true` in config

### Tool Not Working

1. Test tool independently:
   ```python
   tool = MyTool()
   result = tool._run(**params)
   print(result)
   ```

2. Check logs for errors

3. Validate input schema:
   ```python
   schema = MyTool.InputSchema
   schema(param="value")  # Should not raise error
   ```

### Hot Reload Not Working

Set in config:

```yaml
development:
  hot_reload: true
```

Then:

```python
from agents.tool_factory_v2 import reload_tools
reload_tools()
```

---

## Migration Guide

### From Manual Registration

**Before:**

```python
# agents/tool_factory.py
from tools.my_tool import MyTool

def get_tools():
    return [MyTool(), OtherTool(), ...]  # Manual list
```

**After:**

```python
# Just use the new system
from agents.tool_factory_v2 import get_tools

tools = get_tools()  # Auto-discovered!
```

### From MCP Manual Registration

**Before:**

```python
mcp_registry.register(Tool1())
mcp_registry.register(Tool2())
# ... many lines
```

**After:**

```yaml
# tools/tool_config.yaml
tools:
  tool1:
    enabled: true
  tool2:
    enabled: true
```

---

## Summary

✅ **Create** tool file in `tools/` with `*_tool.py` naming
✅ **Inherit** from `BaseToolTemplate`
✅ **Configure** in `tool_config.yaml`
✅ **Done** - automatically discovered and loaded!

No manual registration needed. No code changes to `tool_factory.py`. Just create, configure, and use!

---

For more examples, see the existing tools in `tools/` directory.
