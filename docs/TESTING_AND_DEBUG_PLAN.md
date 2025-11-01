# WhatsApp HR Assistant - Testing & Debugging Master Plan

## 🎯 Overview

This document provides a comprehensive testing and debugging plan for the WhatsApp HR Assistant system. It includes step-by-step instructions for testing every component, debugging common issues, and maintaining the system.

## 📁 Test Suite Files

### Core Test Scripts

1. **`comprehensive_test_suite.py`**
   - Master test runner
   - Tests all 12 major components
   - Generates detailed reports
   - Color-coded output

2. **`test_mcp_comprehensive.py`**
   - MCP Protocol validation
   - All transport types (STDIO, HTTP, WebSocket, SSE)
   - Client factory testing
   - Configuration validation

3. **`test_agents_comprehensive.py`**
   - Agent system testing
   - Simple and Complex agents
   - Memory integration
   - Tool combinations

4. **`test_tools_comprehensive.py`**
   - 36 tools individually validated
   - Category-based testing
   - Schema validation
   - Integration testing

5. **`test_memory_comprehensive.py`**
   - PostgreSQL checkpointer
   - Memory operations
   - Thread management
   - Database connectivity

6. **`run_all_tests.py`**
   - Master test orchestrator
   - Runs all test suites sequentially
   - Generates combined report
   - Exit code 0 if all pass

## 🚀 Quick Start Testing

### Run All Tests

```bash
# Option 1: Run master test runner (recommended)
python run_all_tests.py

# Option 2: Run individual test suites
python comprehensive_test_suite.py
python test_mcp_comprehensive.py
python test_agents_comprehensive.py
python test_tools_comprehensive.py
python test_memory_comprehensive.py
```

### Run Specific Test Categories

```bash
# Test MCP only
python test_mcp_comprehensive.py

# Test tools only
python test_tools_comprehensive.py

# Test agents only
python test_agents_comprehensive.py

# Test memory only
python test_memory_comprehensive.py
```

## 📋 Step-by-Step Testing Guide

### Phase 1: Environment Setup

#### Step 1.1: Verify Python Environment
```bash
python --version  # Should be 3.10+
pip --version
```

**Expected Output**: Python 3.10 or higher

#### Step 1.2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected Output**: All packages installed successfully

#### Step 1.3: Check Configuration Files
```bash
# Verify .env exists
ls -la .env

# Verify tools.yaml exists
ls -la config/tools.yaml

# Verify Google credentials
ls -la client_secret.json token.pickle
```

**Expected Output**: All files present

### Phase 2: Basic System Tests

#### Step 2.1: Test Imports
```bash
python -c "import sys; sys.path.insert(0, '.'); from src.config import settings; print('✅ Config loaded')"
```

**Expected**: No errors, "Config loaded" message

#### Step 2.2: Test Database Connection
```bash
python -c "from src.memory.postgres import LangGraphMemory; m = LangGraphMemory(); print('✅ Memory initialized')"
```

**Expected**: Memory initialized successfully

#### Step 2.3: Test Tool Loading
```bash
python -c "
import nest_asyncio
nest_asyncio.apply()
from src.agents.tool_factory import get_tools
tools = get_tools()
print(f'✅ Loaded {len(tools)} tools')
"
```

**Expected**: "Loaded 36 tools"

### Phase 3: Component Testing

#### Step 3.1: MCP Testing

**Test STDIO Client:**
```python
from src.mcp_integration.factory import create_mcp_client

config = {
    "type": "stdio",
    "command": "echo",
    "args": ["test"]
}

client = create_mcp_client("test", config)
print("✅ STDIO client created")
```

**Test HTTP Client:**
```python
config = {
    "type": "streamable_http",
    "url": "https://example.com/mcp"
}

client = create_mcp_client("test", config)
print("✅ HTTP client created")
```

**Test WebSocket Client:**
```python
config = {
    "type": "websocket",
    "url": "wss://example.com/mcp"
}

client = create_mcp_client("test", config)
print("✅ WebSocket client created")
```

#### Step 3.2: Tools Testing

**Test Gmail Tools:**
```python
import nest_asyncio
nest_asyncio.apply()
from src.agents.tool_factory import get_tools

tools = get_tools()
gmail_tools = [t for t in tools if 'gmail' in t.name.lower()]
print(f"✅ Found {len(gmail_tools)} Gmail tools")

for tool in gmail_tools[:3]:
    print(f"  - {tool.name}")
```

**Expected**: 19 Gmail tools listed

**Test Calendar Tools:**
```python
calendar_tools = [t for t in tools if 'calendar' in t.name.lower()]
print(f"✅ Found {len(calendar_tools)} Calendar tools")

for tool in calendar_tools[:3]:
    print(f"  - {tool.name}")
```

**Expected**: 10 Calendar tools listed

**Test CV Tools:**
```python
cv_tools = [t for t in tools if any(k in t.name.lower() for k in ['cv', 'sheet', 'candidate'])]
print(f"✅ Found {len(cv_tools)} CV/Sheet tools")

for tool in cv_tools:
    print(f"  - {tool.name}")
```

**Expected**: 4 CV/Sheet tools listed

#### Step 3.3: Agent Testing

**Test Simple Agent:**
```python
import nest_asyncio
nest_asyncio.apply()

from src.agents.tool_factory import get_tools
from src.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.simple_agent import create_simple_agent

tools = get_tools()
llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    temperature=settings.TEMPERATURE
)

agent = create_simple_agent(llm, tools)
print("✅ Simple agent created")
```

**Test Complex Agent:**
```python
from src.agents.complex_agent import ComplexLangGraphAgent
from src.memory.postgres import LangGraphMemory

memory = LangGraphMemory()
checkpointer = memory.get_checkpointer()

agent = ComplexLangGraphAgent(
    llm=llm,
    tools=tools,
    checkpointer=checkpointer
)

print("✅ Complex agent created")
```

#### Step 3.4: Memory Testing

**Test Memory Initialization:**
```python
from src.memory.postgres import LangGraphMemory

memory = LangGraphMemory()
checkpointer = memory.get_checkpointer()
print("✅ Checkpointer initialized")

# Test state
state = checkpointer.get("test-thread", "test")
print(f"✅ Memory state retrieved: {state}")
```

**Expected**: State retrieved (may be None for new threads)

### Phase 4: Integration Testing

#### Step 4.1: End-to-End Test

```python
import nest_asyncio
nest_asyncio.apply()

# Load components
from src.agents.tool_factory import get_tools
from src.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.simple_agent import create_simple_agent
from src.memory.postgres import LangGraphMemory

# Create agent
tools = get_tools()
llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    temperature=settings.TEMPERATURE
)
agent = create_simple_agent(llm, tools)

# Test conversation
result = agent.invoke("Test message", thread_id="test-thread")
print("✅ End-to-end test successful")
```

#### Step 4.2: Multiple Thread Test

```python
# Test multiple concurrent conversations
thread_ids = ["user-1", "user-2", "user-3"]

for thread_id in thread_ids:
    result = agent.invoke(f"Message for {thread_id}", thread_id=thread_id)
    print(f"✅ Thread {thread_id} successful")
```

**Expected**: All threads handled correctly

### Phase 5: Performance Testing

#### Step 5.1: Tool Loading Performance

```python
import time
import nest_asyncio
nest_asyncio.apply()

from src.agents.tool_factory import get_tools

start = time.time()
tools = get_tools()
elapsed = time.time() - start

print(f"⏱️  Tool loading time: {elapsed:.2f}s")
if elapsed < 10:
    print("✅ Performance OK")
else:
    print("⚠️  Performance slow")
```

**Benchmark**: < 10 seconds

#### Step 5.2: Memory Performance

```python
import time
from src.memory.postgres import LangGraphMemory

memory = LangGraphMemory()

start = time.time()
checkpointer = memory.get_checkpointer()
elapsed = time.time() - start

print(f"⏱️  Memory initialization time: {elapsed:.2f}s")
if elapsed < 3:
    print("✅ Performance OK")
else:
    print("⚠️  Performance slow")
```

**Benchmark**: < 3 seconds

## 🐛 Debugging Guide

### Common Issues and Solutions

#### Issue 1: Import Errors

**Symptoms:**
```
ImportError: No module named 'src'
ModuleNotFoundError: No module named 'langchain'
```

**Solutions:**
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python path
echo $PYTHONPATH

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Verification:**
```bash
python -c "import src; print('✅ src module imported')"
```

#### Issue 2: Tool Loading Fails

**Symptoms:**
```
✗ Tool loading failed: No tools found
```

**Solutions:**
```bash
# Check configuration
cat config/tools.yaml

# Verify MCP servers
ls config/mcp_servers/

# Check environment
cat .env
```

**Verification:**
```python
from src.tools.registry import get_registry
registry = get_registry()
registry.print_summary()
```

#### Issue 3: Database Connection Fails

**Symptoms:**
```
psycopg.OperationalError: could not connect to server
```

**Solutions:**
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1;"

# Check service status
sudo systemctl status postgresql
```

**Fix:**
```bash
# Update .env with correct DATABASE_URL
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Issue 4: Google API Errors

**Symptoms:**
```
google.auth.exceptions.RefreshError: Invalid grant
```

**Solutions:**
```bash
# Check credentials
ls -la client_secret.json token.pickle

# Re-authenticate
python3 utils/oauth_setup.py
```

**Alternative:**
```bash
# Clean and re-authenticate
rm -f token.pickle
python3 utils/oauth_setup.py
```

#### Issue 5: MCP Client Fails

**Symptoms:**
```
ValueError: Unknown MCP client type
```

**Solutions:**
```python
from src.mcp_integration.factory import validate_config

config = {
    "type": "stdio",
    "command": "echo",
    "args": ["test"]
}

is_valid, msg = validate_config(config)
print(f"Valid: {is_valid}, Message: {msg}")
```

**Fix:** Use valid config types:
- `stdio`
- `streamable_http`
- `websocket`
- `multi`

#### Issue 6: Agent Creation Fails

**Symptoms:**
```
TypeError: create_simple_agent() missing required arguments
```

**Solutions:**
```python
# Verify all required arguments
from src.agents.tool_factory import get_tools
from src.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.simple_agent import create_simple_agent

tools = get_tools()
llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    temperature=settings.TEMPERATURE
)

agent = create_simple_agent(llm, tools)
```

**Ensure:**
- Tools list is not empty
- LLM is properly configured
- Settings are loaded

#### Issue 7: OAuth Browser Issues

**Symptoms:**
```
Browser not opening automatically
OAuth URL not accessible
```

**Solutions:**
```bash
# Check DISPLAY variable (Linux)
echo $DISPLAY

# Set DISPLAY if needed
export DISPLAY=:0

# Manual OAuth
python3 utils/oauth_setup.py
```

### Debug Mode

Enable verbose logging:
```python
import logging

# Set logging level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Debug specific components:
```python
# Debug MCP
logging.getLogger('src.mcp_integration').setLevel(logging.DEBUG)

# Debug tools
logging.getLogger('src.tools').setLevel(logging.DEBUG)

# Debug agents
logging.getLogger('src.agents').setLevel(logging.DEBUG)

# Debug memory
logging.getLogger('src.memory').setLevel(logging.DEBUG)
```

### Diagnostic Scripts

#### Script 1: System Health Check

Create `diagnostic.py`:
```python
#!/usr/bin/env python3
"""System health diagnostic script"""

import sys

def check_python():
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    assert version.major == 3 and version.minor >= 10, "Python 3.10+ required"
    print("✅ Python version OK\n")

def check_dependencies():
    deps = [
        'fastapi', 'langchain', 'langgraph', 'google',
        'psycopg2', 'httpx', 'yaml'
    ]
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep} imported")
        except ImportError:
            print(f"❌ {dep} missing")
    print()

def check_files():
    files = ['.env', 'config/tools.yaml', 'client_secret.json']
    for f in files:
        try:
            open(f, 'r').close()
            print(f"✅ {f} exists")
        except FileNotFoundError:
            print(f"❌ {f} missing")
    print()

if __name__ == "__main__":
    print("="*80)
    print("SYSTEM HEALTH DIAGNOSTIC")
    print("="*80 + "\n")

    try:
        check_python()
        check_dependencies()
        check_files()
        print("="*80)
        print("DIAGNOSTIC COMPLETE")
        print("="*80)
    except Exception as e:
        print(f"\n❌ DIAGNOSTIC FAILED: {e}")
        sys.exit(1)
```

Run:
```bash
python diagnostic.py
```

#### Script 2: Component Test

Create `component_test.py`:
```python
#!/usr/bin/env python3
"""Component-specific diagnostic"""

import asyncio
import nest_asyncio
nest_asyncio.apply()

async def test_component(name, test_func):
    print(f"\nTesting {name}...")
    try:
        result = await test_func() if asyncio.iscoroutinefunction(test_func) else test_func()
        print(f"✅ {name}: PASS")
        return True
    except Exception as e:
        print(f"❌ {name}: FAIL - {e}")
        return False

async def main():
    results = []

    # Test tool loading
    async def test_tools():
        from src.agents.tool_factory import get_tools
        tools = get_tools()
        assert len(tools) > 0, "No tools loaded"
        print(f"  Loaded {len(tools)} tools")

    results.append(await test_component("Tool Loading", test_tools))

    # Test memory
    async def test_memory():
        from src.memory.postgres import LangGraphMemory
        memory = LangGraphMemory()
        checkpointer = memory.get_checkpointer()
        print(f"  Memory initialized")

    results.append(await test_component("Memory", test_memory))

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{'='*80}")
    print(f"COMPONENT TEST SUMMARY: {passed}/{total} passed")
    print(f"{'='*80}")

    return passed == total

if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
```

Run:
```bash
python component_test.py
```

## 📊 Test Results Interpretation

### Understanding Test Output

#### Success Indicators
- ✅ Green checkmarks: Tests passed
- ✓ White checkmarks: Optional tests passed
- Numbers shown for counts (e.g., "Loaded 36 tools")

#### Warning Indicators
- ⚠️ Yellow warnings: Non-critical issues
- Deprecation warnings: Update recommended

#### Failure Indicators
- ❌ Red X marks: Tests failed
- Error messages: Specific failure details
- Stack traces: Detailed error information

### Interpreting Specific Tests

#### Tool Loading Test
```
✅ Loaded 36 tools
```
**Meaning**: All tools loaded successfully

```
⚠️ Loaded 30 tools
```
**Meaning**: Some tools missing (check configuration)

```
❌ No tools loaded
```
**Meaning**: Major configuration issue (check tools.yaml)

#### Memory Test
```
✅ Checkpointer ready with autocommit=True
```
**Meaning**: Database connected and configured

```
❌ Database connection failed
```
**Meaning**: DATABASE_URL or PostgreSQL not configured

#### Agent Test
```
✅ Simple agent created
```
**Meaning**: Agent system functional

```
✅ Complex agent created
✅ Graph compiled successfully
```
**Meaning**: LangGraph system working

```
❌ Graph compilation failed
```
**Meaning**: Agent configuration issue

### Exit Codes

- **0**: All tests passed
- **1**: One or more tests failed
- **130**: Interrupted by user (Ctrl+C)

## 🎯 Maintenance Tasks

### Daily Checks

```bash
# Quick health check
python diagnostic.py

# Test tool loading
python -c "
import nest_asyncio
nest_asyncio.apply()
from src.agents.tool_factory import get_tools
tools = get_tools()
print(f'✅ {len(tools)} tools loaded')
"
```

### Weekly Checks

```bash
# Full test suite
python run_all_tests.py

# Database connectivity
python -c "
from src.memory.postgres import LangGraphMemory
m = LangGraphMemory()
m.get_checkpointer()
print('✅ Database OK')
"
```

### Monthly Checks

```bash
# OAuth token refresh
python3 utils/oauth_setup.py

# Dependency updates
pip install --upgrade -r requirements.txt

# Documentation review
# Check all README files
```

## 📚 Additional Resources

### Documentation Files
- `README.md` - Main project documentation
- `docs/README.md` - Documentation index
- `TEST_SUITE_README.md` - Test suite documentation
- `COMPREHENSIVE_TEST_RESULTS.md` - Test results
- `src/agents/README.md` - Agent documentation

### Test Notebooks
- `tests/notebooks/comprehensive_test.ipynb`
- `tests/notebooks/01_tools_testing.ipynb`
- `tests/notebooks/02_agents_testing.ipynb`
- `tests/notebooks/04_mcp_integration.ipynb`

### Configuration Guides
- `docs/DATABASE_SETUP.md`
- `docs/GOOGLE_OAUTH_SETUP.md`
- `docs/WHATSAPP_SETUP.md`
- `docs/WEBEX_OAUTH2_GUIDE.md`

## 🎓 Best Practices

### Testing Best Practices

1. **Always run full test suite after changes**
2. **Test in development before deploying to production**
3. **Keep logs of test runs for comparison**
4. **Document any non-standard test results**

### Debugging Best Practices

1. **Start with diagnostic scripts**
2. **Check logs before making changes**
3. **Test fixes in isolation**
4. **Verify configuration files**

### Maintenance Best Practices

1. **Regular dependency updates**
2. **Monitor performance metrics**
3. **Keep documentation current**
4. **Back up configuration files**

## 📞 Getting Help

### Resources

1. **Read Documentation**: Start with README files
2. **Check Logs**: Review error messages carefully
3. **Run Diagnostics**: Use provided diagnostic scripts
4. **Test Components**: Isolate issues to specific components

### Support Checklist

Before asking for help:
- [ ] Read this document
- [ ] Checked existing documentation
- [ ] Ran diagnostic scripts
- [ ] Checked logs
- [ ] Tested in isolation
- [ ] Documented the issue

### Reporting Issues

When reporting issues, include:
1. Error message (full)
2. Steps to reproduce
3. Environment details (Python version, OS)
4. Log output
5. Configuration files (sanitized)

---

**Remember**: The system has been thoroughly tested and is production-ready. Most issues are configuration-related and easily fixable.

**Last Updated**: 2025-11-01
**Version**: 1.0
