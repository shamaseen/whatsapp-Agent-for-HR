# New Project Structure Guide

## Overview

The WhatsApp HR Assistant has been refactored for better organization, simpler maintenance, and unified memory management.

## Directory Structure

```
src/
├── config/
│   ├── settings.py                 # Configuration settings
│   ├── tools/                      # Tool configuration module
│   │   ├── __init__.py
│   │   ├── config.yaml            # Main tool configuration
│   │   └── loader.py              # Tool loading logic
│   ├── tool_inspector.py.deprecated
│   └── tool_discovery.py.deprecated
│
├── core/
│   ├── agents/
│   │   ├── __init__.py            # Main agent exports
│   │   ├── agent_factory.py       # Factory for creating agents
│   │   ├── core/                  # Core agent utilities
│   │   │   ├── __init__.py
│   │   │   ├── prompts.py        # Shared prompts
│   │   │   ├── state.py          # State definitions
│   │   │   └── tool_factory.py   # Tool loading wrapper
│   │   └── implementations/       # Agent implementations
│   │       ├── __init__.py
│   │       ├── hr_agent.py       # Original HR agent
│   │       ├── simple_react_agent.py
│   │       └── complex_langgraph_agent.py
│   │
│   └── memory/
│       ├── checkpointer.py        # Shared memory checkpointer
│       ├── openmemory_client.py
│       └── openmemory_langchain.py
│
└── mcp_integration/
    └── servers/                   # MCP server configurations
        ├── datetime.json
        ├── thinking.json
        └── README.md
```

## Key Changes

### 1. Simplified Tool Loading

**All tools are now configured in one place**: `src/config/tools/config.yaml`

```yaml
tools:
  gmail:
    enabled: true
    mode: "internal_mcp"  # Built-in Python implementation

  datetime:
    enabled: true
    mode: "mcp_client"    # External MCP server
    mcp_config_file: "datetime"  # Loads from src/mcp_integration/servers/datetime.json
```

**Benefits:**
- Single configuration file for all tools
- No complex auto-discovery logic
- Easy to enable/disable tools
- Clear separation of internal vs external tools

### 2. Better Agent Organization

**Core utilities separated from implementations:**

- `src/core/agents/core/` - Shared utilities (prompts, tools, state)
- `src/core/agents/implementations/` - Different agent types
- `src/core/agents/agent_factory.py` - Factory for creating agents

**Benefits:**
- Clear separation of concerns
- Easy to add new agent types
- Shared functionality in one place

### 3. Unified Memory System

**All agents use the same memory backend:**

```python
from src.core.memory.checkpointer import get_checkpointer

# All agents use this
checkpointer = get_checkpointer()
```

**Benefits:**
- Consistent memory across all agents
- Shared conversation history
- Easier debugging and testing

## Usage Examples

### Loading Tools

```python
from src.core.agents.core import get_tools

# Loads tools from src/config/tools/config.yaml
tools = get_tools()
print(f"Loaded {len(tools)} tools")
```

### Creating Agents

#### Simple Way (Recommended)
```python
from src.core.agents import create_hr_agent

# Creates HR agent with default configuration
agent = create_hr_agent()

# Use the agent
response = agent.invoke({
    "messages": [{"role": "user", "content": "Hello"}],
    "sender_phone": "+1234567890",
    "sender_identifier": "user_123"
})
```

#### Using Factory (Advanced)
```python
from src.core.agents import AgentFactory, AgentType, MemoryType
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import settings

# Create LLM
llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY
)

# Get tools
from src.core.agents.core import get_tools
tools = get_tools()

# Create agent
agent = AgentFactory.create_agent(
    agent_type=AgentType.SIMPLE_REACT,
    llm=llm,
    tools=tools,
    memory_type=MemoryType.BUFFER
)
```

### Configuring Tools

Edit `src/config/tools/config.yaml`:

```yaml
tools:
  # Enable/disable tools
  gmail:
    enabled: true
    mode: "internal_mcp"

  # Add external MCP server
  new_tool:
    enabled: true
    mode: "mcp_client"
    mcp_config_file: "new_tool"  # Create src/mcp_integration/servers/new_tool.json
```

### Adding New MCP Server

1. Create server config: `src/mcp_integration/servers/my_server.json`
```json
{
  "name": "my_server",
  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "@example/mcp-server"],
  "enabled": true
}
```

2. Add to tool config: `src/config/tools/config.yaml`
```yaml
tools:
  my_server:
    enabled: true
    mode: "mcp_client"
    mcp_config_file: "my_server"
```

3. Restart application - tool is automatically loaded!

### Using OpenMemory

```python
from src.core.agents.implementations import create_simple_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
tools = get_tools()

# Create agent with OpenMemory
agent = create_simple_react_agent(
    llm=llm,
    tools=tools,
    memory_type="openmemory",
    memory_config={
        "user_id": "user_123",
        "max_context_messages": 20
    }
)
```

## Agent Types

### 1. HR Agent (Original)
- **Best for**: Production HR tasks
- **Features**: Conversation memory, tool usage, WhatsApp integration
- **Memory**: PostgreSQL checkpointer

```python
from src.core.agents import create_hr_agent
agent = create_hr_agent()
```

### 2. Simple ReAct Agent
- **Best for**: Quick tasks, debugging, learning
- **Features**: Clear reasoning steps, simple memory
- **Memory**: Buffer, Summary, or OpenMemory

```python
from src.core.agents import create_simple_react_agent
agent = create_simple_react_agent(llm, tools, memory_type="buffer")
```

### 3. Complex LangGraph Agent
- **Best for**: Complex workflows, multi-step tasks
- **Features**: Multi-node graph, reflection, conditional routing
- **Memory**: PostgreSQL checkpointer

```python
from src.core.agents import ComplexLangGraphAgent
agent = ComplexLangGraphAgent(llm, tools, checkpointer)
```

## Memory Types

| Type | Persistence | Best For |
|------|-------------|----------|
| Buffer | None | Short conversations, testing |
| Summary | None | Long conversations, token optimization |
| Postgres | Yes | Production, multi-user |
| SQLite | Yes | Development, single-user |
| Memory Saver | None | Testing, demos |
| OpenMemory | Yes | Advanced semantic search |

## Testing

### Test Tool Loading
```bash
python -c "from src.core.agents.core import get_tools; print(len(get_tools()))"
```

### Test Agent Creation
```bash
python -c "from src.core.agents import create_hr_agent; create_hr_agent()"
```

### Run Application
```bash
python main.py
```

### Run Notebooks
```bash
jupyter notebook tests/notebooks/
```

## Troubleshooting

### Tools Not Loading
1. Check `src/config/tools/config.yaml` syntax
2. Verify MCP server configs in `src/mcp_integration/servers/`
3. Check tool enabled status in config.yaml

### Import Errors
Run the notebook update script:
```bash
python scripts/update_notebooks.py
```

### Memory Issues
All agents now use shared checkpointer from `src.core.memory.checkpointer`

## Migration from Old Structure

### Update Imports
```bash
# Run the update script
python scripts/update_notebooks.py
```

### Manual Updates
- `src.core.agents.hr_agent.create_agent` → `src.core.agents.create_hr_agent`
- `src.core.agents.tool_factory` → `src.core.agents.core`
- `src.config.tool_loader` → `src.config.tools`

### Tool Configuration
Move all tool settings to `src/config/tools/config.yaml`

## Best Practices

1. **Use config.yaml for tools** - Don't hardcode tool configurations
2. **Use factory for complex setups** - AgentFactory handles all the details
3. **Keep MCP configs in servers/** - Centralized server management
4. **Test after changes** - Run test script to verify everything works

## Additional Resources

- [Refactoring Summary](../REFACTORING_SUMMARY.md) - Detailed changes made
- [Agent Factory Guide](../QUICK_REFERENCE_AGENTS.md) - Agent creation examples
- [Tool Configuration](../src/config/tools/config.yaml) - Tool settings
- [MCP Servers](../src/mcp_integration/servers/README.md) - Server configurations
