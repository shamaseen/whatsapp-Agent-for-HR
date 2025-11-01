# WhatsApp HR Assistant - Comprehensive Test Suite

## 🎯 Overview

This comprehensive test suite validates every component of the WhatsApp HR Assistant system, from basic imports to end-to-end integrations. The suite consists of multiple specialized test modules that can be run individually or together.

## 📁 Test Suite Files

### Core Test Scripts

1. **`comprehensive_test_suite.py`** - Master test runner for all systems
   - Tests basic imports
   - Tests configuration
   - Tests MCP integration
   - Tests tools system
   - Tests Google integrations
   - Tests memory system
   - Tests agent system
   - Tests API system
   - Tests tool registry
   - Tests integration scenarios
   - Tests error handling
   - Tests performance metrics

2. **`test_mcp_comprehensive.py`** - MCP Protocol testing
   - Tests STDIO MCP client
   - Tests SSE MCP client
   - Tests Streamable HTTP client
   - Tests WebSocket client
   - Tests Multi-server client
   - Tests tool wrapper
   - Tests retry mechanism
   - Validates configuration files

3. **`test_agents_comprehensive.py`** - Agent system testing
   - Tests Simple ReAct Agent
   - Tests Complex LangGraph Agent
   - Tests Agent Factory
   - Tests Agent State management
   - Tests Agent-Memory integration
   - Tests agent with different tool combinations
   - Tests agent workflow
   - Tests reflection mechanism
   - Tests multiple conversation threads

4. **`test_tools_comprehensive.py`** - Tools system testing
   - Tests tool loading system
   - Validates all tools individually
   - Tests Gmail tools
   - Tests Calendar tools
   - Tests DateTime tools
   - Tests CV & Sheet tools
   - Tests Webex tools
   - Tests tool combinations
   - Tests schema validation
   - Tests tool loader
   - Tests tool registry

5. **`test_memory_comprehensive.py`** - Memory system testing
   - Tests memory system imports
   - Tests memory initialization
   - Tests checkpointer table setup
   - Tests conversation memory
   - Tests memory persistence
   - Tests memory configuration
   - Tests agent-memory integration
   - Tests memory operations
   - Tests multiple conversation threads
   - Tests memory cleanup
   - Tests database connection

## 🚀 Quick Start

### Run All Tests

```bash
# Run complete test suite
python comprehensive_test_suite.py

# Or run specific test modules
python test_mcp_comprehensive.py
python test_agents_comprehensive.py
python test_tools_comprehensive.py
python test_memory_comprehensive.py
```

### Test Output

Each test produces colored output:
- ✓ Green: Test passed
- ✗ Red: Test failed
- ○ Yellow: Test skipped

## 📊 Test Categories

### 1. Basic System Tests
- **Import Tests**: Verify all dependencies are available
- **Configuration Tests**: Validate environment and settings
- **API Tests**: Check FastAPI application and routes

### 2. MCP Protocol Tests
- **Transport Types**: STDIO, HTTP, WebSocket, SSE
- **Client Creation**: Factory pattern validation
- **Configuration**: YAML/JSON config validation
- **Tool Wrapping**: MCP to LangChain conversion

### 3. Tools System Tests
- **Tool Loading**: Dynamic loading from configuration
- **Individual Validation**: Each tool's properties and schema
- **Category Tests**: Gmail, Calendar, CV, Webex, DateTime
- **Combinations**: Tools working together
- **Schema Validation**: Pydantic model validation

### 4. Agent System Tests
- **Simple Agent**: Basic ReAct pattern
- **Complex Agent**: LangGraph with state management
- **Factory Pattern**: Agent creation and configuration
- **Memory Integration**: PostgreSQL checkpointer
- **Multi-tool Support**: Agents with various tool sets

### 5. Memory System Tests
- **PostgreSQL Integration**: Database connectivity
- **Checkpointing**: Conversation state persistence
- **Thread Management**: Multiple conversation support
- **Cleanup**: Resource management

### 6. Integration Tests
- **End-to-End**: Complete workflows
- **Error Handling**: Resilience testing
- **Performance**: Load time metrics

## 🔧 Configuration

### Test Configuration

Tests automatically detect and use:
- `.env` file for environment variables
- `config/tools.yaml` for tool configuration
- Database URL from environment
- Google API credentials

### Required Configuration

For full test coverage, configure:

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Google APIs
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=./client_secret.json

# WhatsApp (optional for tests)
CHATWOOT_API_URL=https://your-chatwoot.com
EVOLUTION_API_URL=https://your-evolution-api.com

# Agent Settings
MODEL_NAME=gemini-2.0-flash-exp
TEMPERATURE=0.7
```

## 📝 Test Details

### MCP Tests

**Tested Transports:**
- **STDIO**: Local subprocess communication
  - Validates command/args configuration
  - Tests process initialization
  - Verifies tool listing

- **SSE**: Server-Sent Events (deprecated)
  - URL validation
  - Header configuration
  - Connection handling

- **Streamable HTTP**: Modern HTTP transport
  - REST API integration
  - Streaming support
  - Authentication headers

- **WebSocket**: Real-time communication
  - WebSocket connection
  - Message handling
  - Reconnection logic

- **Multi-Server**: Multiple MCP servers
  - Server aggregation
  - Tool combination
  - Load balancing

**Tested Configurations:**
- Configuration validation
- Error handling
- Retry mechanisms
- Cleanup procedures

### Tools Tests

**Gmail Tools (19+ tools):**
- send_email, draft_email, read_email
- search_emails, modify_email, delete_email
- list_labels, create_label, delete_label
- create_filter, list_filters, get_filter
- download_attachment
- Batch operations

**Calendar Tools (10+ tools):**
- list-calendars, list-events, search-events
- get-event, create-event, update-event
- delete-event, get-freebusy
- get-current-time, list-colors

**CV/Sheet Tools (4+ tools):**
- cv_sheet_manager
- process_cvs
- search_candidates
- search_create_sheet

**DateTime Tools (2+ tools):**
- get_current_time
- convert_time

**Webex Tools (1+ tool):**
- Video meeting creation and management

**Tool Validation:**
- Name and description presence
- Schema validation
- Property validation
- Integration compatibility

### Agent Tests

**Simple Agent:**
- Lightweight ReAct pattern
- Direct LLM + tools binding
- Basic workflow execution

**Complex Agent:**
- LangGraph state management
- Multi-node workflow graph
- Conditional routing
- Reflection and self-critique
- Checkpointer integration
- Human-in-the-loop support

**Agent Capabilities:**
- Tool selection and execution
- State persistence
- Error handling and recovery
- Iterative refinement
- Memory-backed conversations

### Memory Tests

**PostgreSQL Checkpointer:**
- Connection management
- Table initialization
- Checkpoint operations (get, put, list)
- Transaction handling
- Connection pooling

**Conversation Management:**
- Thread-based conversations
- State persistence across sessions
- Multi-user support
- Cleanup and archival

## 📈 Test Metrics

### Performance Benchmarks
- Tool loading time: < 10 seconds
- Agent creation time: < 5 seconds
- Memory initialization: < 3 seconds
- Graph compilation: < 2 seconds

### Success Criteria
- All imports successful
- All tools loaded and validated
- All agents created successfully
- Memory system initialized
- Configuration validated
- Integration tests passed

## 🎓 Learning Resources

### Understanding MCP
- Model Context Protocol enables secure, controlled access to external resources
- Supports multiple transports (STDIO, HTTP, WebSocket)
- Provides standardized tool interface for LLMs

### Understanding LangGraph
- State-based agent framework
- Built-in checkpointing and memory
- Conditional routing and workflow graphs
- Production-ready agent patterns

### Understanding the Architecture
```
┌─────────────┐
│   Tests     │
└──────┬──────┘
       │
       ├── MCP Tests → Validate protocol implementation
       ├── Tools Tests → Validate all tool integrations
       ├── Agent Tests → Validate agent behavior
       └── Memory Tests → Validate persistence
```

## 🐛 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

**Tool Loading Fails:**
```bash
# Check configuration
cat config/tools.yaml

# Verify MCP servers
ls config/mcp_servers/

# Check environment
cat .env
```

**Database Connection Fails:**
```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1;"

# Check service status
sudo systemctl status postgresql
```

**Google API Errors:**
```bash
# Verify credentials
ls -la client_secret.json

# Check OAuth token
ls -la token.pickle

# Re-authenticate
python3 utils/oauth_setup.py
```

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. Check the main [README.md](README.md)
2. Review [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Run diagnostic tests
4. Check logs and error messages

## 📋 Test Checklist

Use this checklist to ensure full coverage:

- [ ] Basic imports successful
- [ ] Configuration loaded
- [ ] Database connected
- [ ] Google APIs authenticated
- [ ] MCP clients created
- [ ] All tools loaded
- [ ] Gmail tools validated
- [ ] Calendar tools validated
- [ ] CV tools validated
- [ ] Webex tools validated
- [ ] DateTime tools validated
- [ ] Simple agent created
- [ ] Complex agent created
- [ ] Agent factory working
- [ ] Memory system initialized
- [ ] Checkpointer configured
- [ ] FastAPI app created
- [ ] Routes registered
- [ ] Tool combinations tested
- [ ] Error handling verified
- [ ] Performance benchmarks met
- [ ] Cleanup procedures tested

## 🤝 Contributing

When adding new features:

1. Create corresponding tests
2. Update test documentation
3. Run full test suite
4. Verify all tests pass
5. Update this README

## 📊 Test Results

After running tests, review:

1. **Summary Section**: Overall pass/fail ratio
2. **Failed Tests**: Specific errors and stack traces
3. **Performance Metrics**: Load times and benchmarks
4. **Integration Results**: End-to-end workflow status

## 🎯 Next Steps

After tests pass:

1. ✅ Start the server: `python main.py`
2. ✅ Access dashboard: `http://localhost:8000`
3. ✅ Test WhatsApp integration
4. ✅ Configure Google APIs
5. ✅ Set up monitoring

## 📚 References

- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/)
- [MCP Protocol](https://modelcontextprotocol.io)
- [LangChain](https://python.langchain.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)

---

**🎉 The comprehensive test suite ensures your WhatsApp HR Assistant is production-ready!**
