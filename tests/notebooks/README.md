# WhatsApp HR Assistant - Jupyter Notebooks

Comprehensive Jupyter notebooks for testing, learning, and developing with the WhatsApp HR Assistant system.

## 📚 Available Notebooks

### `01_tools_testing.ipynb` ⭐ Start Here
**Test all available tools individually**

Complete testing of each tool:
- DateTime, Gmail, Calendar, Webex, CV Manager, CV Processing
- Individual tool APIs and execution
- Error handling and validation

**Use when**: Testing tools, learning tool APIs, debugging

### `02_agents_testing.ipynb`
**Test HR agent and workflows**

Comprehensive agent testing:
- Agent creation, simple queries, tool calls
- Memory persistence across conversations
- Complex workflows, error handling
- Real HR scenarios

**Use when**: Testing agents, verifying memory, debugging conversations

### `03_custom_agent_tutorial.ipynb` 📖 Tutorial
**Step-by-step guide to building custom agents**

Learn to build LangGraph agents from scratch:
1. Load and configure tools
2. Create and bind LLM
3. Define agent state and logic
4. Build LangGraph workflow
5. Add memory with PostgreSQL
6. Test and customize

**Use when**: Building new agents, learning LangGraph

### `04_mcp_integration.ipynb`
**Test MCP (Model Context Protocol) integration**

Deep dive into MCP architecture:
- MCP Tool Registry and individual tools
- execute_tool wrapper and schemas
- LangChain conversion and tool modes
- Protocol compliance

**Use when**: Understanding MCP, adding tools, debugging integration

### `comprehensive_test.ipynb`
**Complete system test suite**

Full system validation:
1. **Import Tests** - All modules load correctly
2. **MCP Tool Tests** - Tool initialization and execution
3. **Agent Tests** - Factory and custom agents
4. **Integration Tests** - End-to-end workflows
5. **Configuration Tests** - Environment validation

**Use when**: System health check, CI/CD, comprehensive debugging

## 🚀 Getting Started

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Install Jupyter
pip install jupyter notebook

# Set up environment
cp .env.example .env
# Edit .env with your credentials
```

### Launch Jupyter
```bash
# From project root
jupyter notebook tests/notebooks/
```

### Recommended Order
1. **Start**: `01_tools_testing.ipynb` - Learn tools
2. **Then**: `02_agents_testing.ipynb` - Understand agents
3. **Next**: `03_custom_agent_tutorial.ipynb` - Build your own
4. **Advanced**: `04_mcp_integration.ipynb` - MCP deep dive
5. **Verify**: `comprehensive_test.ipynb` - Full system test

## 🔑 Key Concepts

### Thread ID for Memory
**IMPORTANT**: Agents with memory require `thread_id` in config:

```python
config = {"configurable": {"thread_id": "user_phone"}}

result = agent.invoke({
    "messages": [HumanMessage(content="Hello")],
    "sender_phone": "123456789",
    "sender_identifier": "user@example.com"
}, config=config)
```

Without config: `Checkpointer requires 'thread_id'` error.

## Test Structure

```
Setup
  └─> Test 1: Imports
       └─> Test 2: MCP Tools  
            └─> Test 3: Agent Import
                 └─> Test 4: Build from Scratch
                      └─> Test 5: Test Custom Agent
                           └─> Test 6: Integration
                                └─> Test 7: Configuration
                                     └─> Summary
```

## What Each Test Validates

### Test 1: Import Tests
- All MCP tool classes import
- Base classes load correctly
- Agent factory imports
- Config loads properly

### Test 2: MCP Tool Initialization
- Tools instantiate without errors
- Tool registry works
- Tools can execute operations
- Datetime tool returns valid data

### Test 3: Agent Import Test
- Agent factory creates agent
- Agent responds to simple queries
- Message flow works correctly

### Test 4: Build Agent from Scratch
- All components (LLM, tools, graph) integrate
- Manual agent construction works
- Verifies repo code structure

### Test 5: Test Custom Agent
- Custom-built agent processes queries
- Tool calling works
- Responses are coherent

### Test 6: Full Integration
- Multi-step workflows execute
- Multiple tools coordinate
- Email and datetime tools work together

### Test 7: Configuration
- Environment variables loaded
- Tool config file exists
- Required settings present

## Troubleshooting

### Import Errors
```python
# Make sure project root is in path
import sys
sys.path.insert(0, '../..')
```

### Google API Errors
- Check `.env` file has `GOOGLE_API_KEY`
- Verify `credentials.json` exists
- Run OAuth flow if needed

### Tool Execution Errors
- Ensure `TOOL_MODE=mcp` in `.env`
- Check Google services initialized
- Verify OAuth token is valid

## Adding New Tests

To add new test cells:

1. Create a new markdown cell with test description
2. Add code cell with test logic
3. Include success/failure indicators (✅/❌)
4. Update this README

Example:
```python
print("Testing new feature...\\n")

try:
    # Test code here
    result = some_function()
    print(f"✅ Test passed: {result}")
except Exception as e:
    print(f"❌ Test failed: {e}")
```

## Notes

- Notebooks use the actual production code from `../../`
- Changes to repo code are reflected immediately
- Great for development and debugging
- Can be used for documentation/demos

---

**Last Updated**: October 22, 2025
