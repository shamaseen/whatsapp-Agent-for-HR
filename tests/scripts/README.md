# Test Scripts Directory

This directory contains comprehensive test scripts for the WhatsApp HR Assistant system.

## 📜 Available Scripts

### Master Test Runner
- **`run_all_tests.py`** - Master orchestrator that runs all test suites and generates combined reports

### Individual Test Suites
- **`comprehensive_test_suite.py`** - Complete system test suite (tests all 12 major components)
- **`test_mcp_comprehensive.py`** - MCP protocol testing (all transport types: STDIO, HTTP, WebSocket, SSE)
- **`test_agents_comprehensive.py`** - Agent system testing (Simple & Complex agents)
- **`test_tools_comprehensive.py`** - Tools system testing (all 36 tools individually)
- **`test_memory_comprehensive.py`** - Memory system testing (PostgreSQL checkpointer)

## 🚀 Quick Start

### Run All Tests
```bash
# From project root
python tests/scripts/run_all_tests.py
```

### Run Specific Test Suite
```bash
# Test MCP only
python tests/scripts/test_mcp_comprehensive.py

# Test tools only
python tests/scripts/test_tools_comprehensive.py

# Test agents only
python tests/scripts/test_agents_comprehensive.py

# Test memory only
python tests/scripts/test_memory_comprehensive.py

# Run comprehensive test suite
python tests/scripts/comprehensive_test_suite.py
```

## 📊 Test Coverage

### System Components Tested
✅ Basic imports and dependencies
✅ Configuration loading
✅ MCP protocol (all transports)
✅ Tools system (36 tools)
✅ Google integrations
✅ Memory system (PostgreSQL checkpointer)
✅ Agent system (Simple & Complex)
✅ API system (FastAPI)
✅ Tool registry
✅ Integration tests
✅ Error handling
✅ Performance metrics

### Test Results
- **Total Tools**: 36 (Gmail 19, Calendar 10, CV 4, Webex 1, DateTime 2)
- **MCP Transports**: 4 (STDIO, HTTP, WebSocket, SSE)
- **Agent Types**: 2 (Simple, Complex)
- **Coverage**: 100% of major components

## 📚 Documentation

For detailed information, see:
- `docs/TEST_SUITE_README.md` - Complete test suite documentation
- `docs/TESTING_AND_DEBUG_PLAN.md` - Step-by-step testing and debugging guide
- `docs/COMPREHENSIVE_TEST_RESULTS.md` - Detailed test results and metrics
- `docs/PROJECT_SUMMARY.md` - Complete project summary
- `docs/RESOURCE_INDEX.md` - Master index of all resources

## 🎯 Requirements

All test scripts require:
- Python 3.10+
- All dependencies from `requirements.txt`
- `.env` file configured
- `config/tools.yaml` present
- Google API credentials (`client_secret.json`, `token.pickle`)

## ⚠️ Notes

- Tests requiring external services (Google APIs, PostgreSQL) may need proper configuration
- OAuth tokens will be refreshed automatically when needed
- Tool loading time: < 10 seconds for all 36 tools
- Memory initialization time: < 3 seconds

## 🔧 Troubleshooting

If tests fail:
1. Check configuration files (`.env`, `config/tools.yaml`)
2. Verify database connection
3. Check Google API credentials
4. Review error messages in test output
5. See `docs/TESTING_AND_DEBUG_PLAN.md` for detailed troubleshooting

## 🏆 Success Criteria

All tests should pass with:
- ✅ All imports successful
- ✅ Configuration validated
- ✅ All 36 tools loaded
- ✅ Database connected
- ✅ Agents created successfully
- ✅ Performance benchmarks met

---

**Status**: All systems operational and tested
**Last Updated**: 2025-11-01
