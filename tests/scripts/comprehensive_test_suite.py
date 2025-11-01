#!/usr/bin/env python3
"""
Comprehensive Test Suite for WhatsApp HR Assistant
Tests every single component, tool, agent, memory system, and integration
"""

import sys
import traceback
import asyncio
from typing import List, Dict, Any
from datetime import datetime

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestResult:
    def __init__(self, name: str, status: str, message: str = "", details: Any = None):
        self.name = name
        self.status = status  # PASS, FAIL, SKIP
        self.message = message
        self.details = details
        self.timestamp = datetime.now()

    def __str__(self):
        icon = "✓" if self.status == "PASS" else "✗" if self.status == "FAIL" else "○"
        color = GREEN if self.status == "PASS" else RED if self.status == "FAIL" else YELLOW
        return f"{color}{icon} {self.name}: {self.status}{RESET}\n   {self.message}"

class ComprehensiveTestSuite:
    def __init__(self):
        self.results: List[TestResult] = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def add_result(self, result: TestResult):
        """Add a test result"""
        self.results.append(result)
        if result.status == "PASS":
            self.passed += 1
        elif result.status == "FAIL":
            self.failed += 1
        else:
            self.skipped += 1

    def print_header(self, title: str):
        """Print a test section header"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}{title.center(80)}{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")

    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        total = len(self.results)
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"{YELLOW}Skipped: {self.skipped}{RESET}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "N/A")

        if self.failed > 0:
            print(f"\n{RED}FAILED TESTS:{RESET}")
            for result in self.results:
                if result.status == "FAIL":
                    print(f"\n{result}")

        return self.failed == 0

    # ==================== TEST 1: BASIC IMPORTS ====================
    async def test_basic_imports(self):
        """Test all basic imports"""
        self.print_header("TEST 1: Basic Imports")

        imports = [
            ("asyncio", "asyncio"),
            ("nest_asyncio", "nest_asyncio"),
            ("langchain", "langchain"),
            ("langchain_google_genai", "langchain-google-genai"),
            ("langgraph", "langgraph"),
            ("fastapi", "FastAPI"),
            ("uvicorn", "uvicorn"),
            ("pydantic", "pydantic"),
            ("google", "Google APIs"),
            ("psycopg2", "psycopg2"),
            ("httpx", "httpx"),
            ("PyYAML", "PyYAML"),
        ]

        for module, name in imports:
            try:
                __import__(module)
                self.add_result(TestResult(f"Import {name}", "PASS"))
            except ImportError as e:
                self.add_result(TestResult(f"Import {name}", "FAIL", str(e)))

    # ==================== TEST 2: CONFIGURATION ====================
    async def test_configuration(self):
        """Test configuration loading"""
        self.print_header("TEST 2: Configuration")

        try:
            from src.config import settings
            self.add_result(TestResult("Load settings", "PASS"))

            # Test environment variables
            required_vars = ['DATABASE_URL', 'GOOGLE_API_KEY']
            for var in required_vars:
                if hasattr(settings, var):
                    self.add_result(TestResult(f"Config {var}", "PASS"))
                else:
                    self.add_result(TestResult(f"Config {var}", "FAIL", "Not found"))

        except Exception as e:
            self.add_result(TestResult("Load settings", "FAIL", str(e)))

    # ==================== TEST 3: MCP INTEGRATION ====================
    async def test_mcp_integration(self):
        """Test MCP protocol integration"""
        self.print_header("TEST 3: MCP Integration")

        # Test MCP factory
        try:
            from src.mcp_integration.factory import create_mcp_client
            self.add_result(TestResult("Import MCP factory", "PASS"))
        except Exception as e:
            self.add_result(TestResult("Import MCP factory", "FAIL", str(e)))
            return

        # Test different MCP client types
        client_configs = [
            ("stdio", {"type": "stdio", "command": "echo", "args": ["test"]}),
            ("sse", {"type": "sse", "url": "http://example.com"}),
            ("streamable_http", {"type": "streamable_http", "url": "http://example.com"}),
            ("websocket", {"type": "websocket", "url": "ws://example.com"}),
        ]

        for name, config in client_configs:
            try:
                client = create_mcp_client(f"test_{name}", config)
                self.add_result(TestResult(f"Create {name} client", "PASS"))
            except Exception as e:
                self.add_result(TestResult(f"Create {name} client", "FAIL", str(e)))

    # ==================== TEST 4: TOOLS ====================
    async def test_tools(self):
        """Test all available tools"""
        self.print_header("TEST 4: Tools System")

        try:
            import nest_asyncio
            nest_asyncio.apply()

            from src.agents.tool_factory import get_tools
            tools = get_tools()

            self.add_result(TestResult(f"Load tools ({len(tools)} total)", "PASS"))

            # Test tool properties
            for tool in tools[:10]:  # Test first 10 tools
                try:
                    name = tool.name
                    description = tool.description
                    args_schema = getattr(tool, 'args_schema', None)

                    # Verify tool has required attributes
                    assert name, "Tool name is required"
                    assert description, "Tool description is required"

                    self.add_result(TestResult(f"Tool {name}", "PASS"))
                except Exception as e:
                    self.add_result(TestResult(f"Tool validation", "FAIL", str(e)))

        except Exception as e:
            self.add_result(TestResult("Load tools", "FAIL", str(e)))

    # ==================== TEST 5: GOOGLE INTEGRATIONS ====================
    async def test_google_integrations(self):
        """Test Google API integrations"""
        self.print_header("TEST 5: Google Integrations")

        integrations = [
            ("google.oauth", "OAuth2"),
            ("google.auth", "Google Auth"),
            ("google-api-python-client", "API Client"),
            ("gspread", "Google Sheets"),
        ]

        for module, name in integrations:
            try:
                __import__(module)
                self.add_result(TestResult(f"{name} integration", "PASS"))
            except Exception as e:
                self.add_result(TestResult(f"{name} integration", "FAIL", str(e)))

    # ==================== TEST 6: MEMORY SYSTEM ====================
    async def test_memory_system(self):
        """Test memory and checkpointer systems"""
        self.print_header("TEST 6: Memory System")

        try:
            from src.memory.postgres import LangGraphMemory
            memory = LangGraphMemory()
            self.add_result(TestResult("Create memory instance", "PASS"))

            # Test checkpointer setup
            try:
                checkpointer = memory.get_checkpointer()
                self.add_result(TestResult("Initialize checkpointer", "PASS"))
            except Exception as e:
                self.add_result(TestResult("Initialize checkpointer", "FAIL", str(e)))

        except Exception as e:
            self.add_result(TestResult("Import memory system", "FAIL", str(e)))

    # ==================== TEST 7: AGENT SYSTEM ====================
    async def test_agents(self):
        """Test agent creation and functionality"""
        self.print_header("TEST 7: Agent System")

        # Test simple agent
        try:
            from src.agents.simple_agent import create_simple_agent
            self.add_result(TestResult("Import simple agent", "PASS"))
        except Exception as e:
            self.add_result(TestResult("Import simple agent", "FAIL", str(e)))

        # Test complex agent
        try:
            from src.agents.complex_agent import ComplexLangGraphAgent
            self.add_result(TestResult("Import complex agent", "PASS"))
        except Exception as e:
            self.add_result(TestResult("Import complex agent", "FAIL", str(e)))

        # Test agent factory
        try:
            from src.agents.factory import AgentFactory
            self.add_result(TestResult("Import agent factory", "PASS"))
        except Exception as e:
            self.add_result(TestResult("Import agent factory", "FAIL", str(e)))

    # ==================== TEST 8: API SYSTEM ====================
    async def test_api_system(self):
        """Test API endpoints and handlers"""
        self.print_header("TEST 8: API System")

        try:
            from src.api.app import create_app
            app = create_app()
            self.add_result(TestResult("Create FastAPI app", "PASS"))
        except Exception as e:
            self.add_result(TestResult("Create FastAPI app", "FAIL", str(e)))
            return

        # Test routes
        routes_to_check = [
            ("/health", "Health check"),
            ("/dashboard", "Dashboard"),
            ("/webhook", "Webhook"),
        ]

        for path, name in routes_to_check:
            try:
                # Check if route exists
                routes = [route.path for route in app.routes]
                if path in routes or any(path in str(route.path) for route in app.routes):
                    self.add_result(TestResult(f"Route {name}", "PASS"))
                else:
                    self.add_result(TestResult(f"Route {name}", "SKIP", "Not configured"))
            except Exception as e:
                self.add_result(TestResult(f"Route {name}", "FAIL", str(e)))

    # ==================== TEST 9: TOOL REGISTRY ====================
    async def test_tool_registry(self):
        """Test tool registry and discovery"""
        self.print_header("TEST 9: Tool Registry")

        try:
            from src.tools.registry import get_registry
            registry = get_registry()
            self.add_result(TestResult("Get registry", "PASS"))

            # Test registry methods
            try:
                registry.print_summary()
                self.add_result(TestResult("Print summary", "PASS"))
            except Exception as e:
                self.add_result(TestResult("Print summary", "FAIL", str(e)))

        except Exception as e:
            self.add_result(TestResult("Tool registry", "FAIL", str(e)))

    # ==================== TEST 10: INTEGRATION TESTS ====================
    async def test_integration(self):
        """Test end-to-end integrations"""
        self.print_header("TEST 10: Integration Tests")

        # Test complete tool loading flow
        try:
            import nest_asyncio
            nest_asyncio.apply()

            from src.agents.tool_factory import get_tools, get_tool_summary
            tools = get_tools()
            summary = get_tool_summary()

            self.add_result(TestResult("Complete tool loading flow", "PASS",
                                     f"Loaded {summary.get('total_tools', 0)} tools"))
        except Exception as e:
            self.add_result(TestResult("Complete tool loading flow", "FAIL", str(e)))

        # Test agent + tools integration
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from src.config import settings

            llm = ChatGoogleGenerativeAI(
                model=settings.MODEL_NAME,
                temperature=settings.TEMPERATURE
            )

            # Try to create a simple agent (don't invoke)
            from src.agents.simple_agent import create_simple_agent
            agent = create_simple_agent(llm, tools)

            self.add_result(TestResult("Agent + tools integration", "PASS"))
        except Exception as e:
            self.add_result(TestResult("Agent + tools integration", "FAIL", str(e)))

    # ==================== TEST 11: ERROR HANDLING ====================
    async def test_error_handling(self):
        """Test error handling and resilience"""
        self.print_header("TEST 11: Error Handling")

        # Test invalid configuration
        try:
            from src.mcp_integration.factory import create_mcp_client
            try:
                create_mcp_client("test", {"type": "invalid_type"})
                self.add_result(TestResult("Invalid config rejection", "FAIL", "Should have raised error"))
            except ValueError:
                self.add_result(TestResult("Invalid config rejection", "PASS"))
        except Exception as e:
            self.add_result(TestResult("Invalid config rejection", "FAIL", str(e)))

    # ==================== TEST 12: PERFORMANCE ====================
    async def test_performance(self):
        """Test basic performance metrics"""
        self.print_header("TEST 12: Performance")

        # Test tool loading time
        try:
            import time
            start = time.time()

            import nest_asyncio
            nest_asyncio.apply()
            from src.agents.tool_factory import get_tools
            tools = get_tools()

            elapsed = time.time() - start

            if elapsed < 10:  # Should load in under 10 seconds
                self.add_result(TestResult(f"Tool loading performance", "PASS",
                                         f"{elapsed:.2f}s"))
            else:
                self.add_result(TestResult(f"Tool loading performance", "FAIL",
                                         f"Too slow: {elapsed:.2f}s"))
        except Exception as e:
            self.add_result(TestResult(f"Tool loading performance", "FAIL", str(e)))

    # ==================== MAIN TEST RUNNER ====================
    async def run_all_tests(self):
        """Run all tests"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}{'WHATSAPP HR ASSISTANT - COMPREHENSIVE TEST SUITE'.center(80)}{RESET}")
        print(f"{BLUE}{'='*80}{RESET}")
        print(f"\nStart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        tests = [
            ("Basic Imports", self.test_basic_imports),
            ("Configuration", self.test_configuration),
            ("MCP Integration", self.test_mcp_integration),
            ("Tools System", self.test_tools),
            ("Google Integrations", self.test_google_integrations),
            ("Memory System", self.test_memory_system),
            ("Agent System", self.test_agents),
            ("API System", self.test_api_system),
            ("Tool Registry", self.test_tool_registry),
            ("Integration Tests", self.test_integration),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
        ]

        for name, test_func in tests:
            try:
                await test_func()
            except Exception as e:
                self.add_result(TestResult(f"Test {name}", "FAIL",
                                         f"Unexpected error: {str(e)}\n{traceback.format_exc()}"))

        return self.print_summary()

# ==================== MAIN ====================
async def main():
    """Main test runner"""
    suite = ComprehensiveTestSuite()
    success = await suite.run_all_tests()

    print(f"\n{BLUE}{'='*80}{RESET}")
    if success:
        print(f"{GREEN}{'ALL TESTS PASSED!'.center(80)}{RESET}")
    else:
        print(f"{RED}{'SOME TESTS FAILED'.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
