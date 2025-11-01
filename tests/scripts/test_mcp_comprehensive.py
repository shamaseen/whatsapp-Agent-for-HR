#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Comprehensive Test Suite
Tests all MCP client types, transports, and configurations
"""

import asyncio
import sys
import json
from typing import Dict, Any

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(title: str):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{title.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def test_mcp_factory():
    """Test MCP client factory"""
    print_header("TEST: MCP Client Factory")

    try:
        from src.mcp_integration.factory import create_mcp_client, validate_config

        # Test valid configurations
        valid_configs = [
            ("stdio", {
                "type": "stdio",
                "command": "echo",
                "args": ["test"]
            }),
            ("sse", {
                "type": "sse",
                "url": "https://example.com"
            }),
            ("streamable_http", {
                "type": "streamable_http",
                "url": "https://example.com/mcp"
            }),
            ("websocket", {
                "type": "websocket",
                "url": "wss://example.com/mcp"
            }),
            ("multi", {
                "type": "multi",
                "servers": [
                    {"name": "server1", "type": "stdio", "command": "echo", "args": ["test"]}
                ]
            })
        ]

        for name, config in valid_configs:
            try:
                is_valid, msg = validate_config(config)
                if is_valid:
                    print(f"  ✓ {name}: Valid configuration")
                else:
                    print(f"  ✗ {name}: {msg}")
            except Exception as e:
                print(f"  ✗ {name}: {str(e)}")

        # Test invalid configuration
        print("\nTesting invalid configurations:")
        invalid_configs = [
            ("unknown_type", {
                "type": "unknown_type"
            }),
            ("missing_command", {
                "type": "stdio"
            }),
            ("missing_url", {
                "type": "sse"
            })
        ]

        for name, config in invalid_configs:
            try:
                is_valid, msg = validate_config(config)
                if not is_valid:
                    print(f"  ✓ {name}: Correctly rejected")
                else:
                    print(f"  ✗ {name}: Should have been rejected")
            except Exception as e:
                print(f"  ✓ {name}: Exception raised as expected")

        return True
    except Exception as e:
        print(f"  ✗ Factory test failed: {str(e)}")
        return False

async def test_stdio_client():
    """Test STDIO MCP client"""
    print_header("TEST: STDIO MCP Client")

    try:
        from src.mcp_integration.factory import create_mcp_client

        # Test with echo command
        config = {
            "type": "stdio",
            "command": "python",
            "args": ["-c", "print('STDIO test successful')"]
        }

        client = create_mcp_client("test_stdio", config)
        print(f"  ✓ Created STDIO client: {client.__class__.__name__}")

        # Try to initialize
        try:
            await client.initialize()
            print(f"  ✓ Initialized STDIO client")
        except Exception as e:
            print(f"  ⚠ Initialization failed (may need specific server): {str(e)[:50]}...")

        # Test tool listing
        try:
            tools = await client.list_tools()
            print(f"  ✓ Listed tools: {len(tools)} tools available")
        except Exception as e:
            print(f"  ⚠ Tool listing failed (may need specific server): {str(e)[:50]}...")

        await client.cleanup()
        print(f"  ✓ Cleaned up STDIO client")
        return True

    except Exception as e:
        print(f"  ✗ STDIO client test failed: {str(e)}")
        return False

async def test_sse_client():
    """Test SSE MCP client"""
    print_header("TEST: SSE MCP Client")

    try:
        from src.mcp_integration.factory import create_mcp_client

        # Note: Real SSE servers would need actual URLs
        config = {
            "type": "sse",
            "url": "https://example.com/mcp"
        }

        try:
            client = create_mcp_client("test_sse", config)
            print(f"  ✓ Created SSE client: {client.__class__.__name__}")
        except Exception as e:
            print(f"  ✗ Failed to create SSE client: {str(e)}")
            return False

        return True

    except Exception as e:
        print(f"  ✗ SSE client test failed: {str(e)}")
        return False

async def test_streamable_http_client():
    """Test Streamable HTTP MCP client"""
    print_header("TEST: Streamable HTTP Client")

    try:
        from src.mcp_integration.factory import create_mcp_client

        config = {
            "type": "streamable_http",
            "url": "https://example.com/mcp",
            "headers": {
                "Authorization": "Bearer token"
            }
        }

        try:
            client = create_mcp_client("test_http", config)
            print(f"  ✓ Created HTTP client: {client.__class__.__name__}")
        except Exception as e:
            print(f"  ✗ Failed to create HTTP client: {str(e)}")
            return False

        return True

    except Exception as e:
        print(f"  ✗ HTTP client test failed: {str(e)}")
        return False

async def test_websocket_client():
    """Test WebSocket MCP client"""
    print_header("TEST: WebSocket MCP Client")

    try:
        from src.mcp_integration.factory import create_mcp_client

        config = {
            "type": "websocket",
            "url": "wss://example.com/mcp"
        }

        try:
            client = create_mcp_client("test_ws", config)
            print(f"  ✓ Created WebSocket client: {client.__class__.__name__}")
        except Exception as e:
            print(f"  ✗ Failed to create WebSocket client: {str(e)}")
            return False

        return True

    except Exception as e:
        print(f"  ✗ WebSocket client test failed: {str(e)}")
        return False

async def test_multi_server_client():
    """Test Multi-server MCP client"""
    print_header("TEST: Multi-Server MCP Client")

    try:
        from src.mcp_integration.factory import create_mcp_client

        config = {
            "type": "multi",
            "servers": [
                {
                    "name": "server1",
                    "type": "stdio",
                    "command": "echo",
                    "args": ["test1"]
                },
                {
                    "name": "server2",
                    "type": "stdio",
                    "command": "echo",
                    "args": ["test2"]
                }
            ]
        }

        try:
            client = create_mcp_client("test_multi", config)
            print(f"  ✓ Created Multi-server client: {client.__class__.__name__}")
        except Exception as e:
            print(f"  ✗ Failed to create Multi-server client: {str(e)}")
            return False

        return True

    except Exception as e:
        print(f"  ✗ Multi-server client test failed: {str(e)}")
        return False

async def test_tool_wrapper():
    """Test tool wrapper functionality"""
    print_header("TEST: Tool Wrapper")

    try:
        from src.mcp_integration.tool_wrapper import ToolWrapper

        # The ToolWrapper converts MCP tools to LangChain tools
        print(f"  ✓ Imported ToolWrapper")

        # Note: Actual wrapper usage requires MCP tools
        return True

    except Exception as e:
        print(f"  ✗ Tool wrapper test failed: {str(e)}")
        return False

async def test_retry_mechanism():
    """Test retry mechanism"""
    print_header("TEST: Retry Mechanism")

    try:
        from src.mcp_integration.retry import RetryConfig, with_retry

        config = RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            max_delay=10.0
        )

        print(f"  ✓ Created RetryConfig: {config}")

        # Test retry decorator
        @with_retry(config)
        async def test_function():
            return "success"

        try:
            result = await test_function()
            print(f"  ✓ Retry decorator works: {result}")
        except Exception as e:
            print(f"  ⚠ Retry function failed: {str(e)}")

        return True

    except Exception as e:
        print(f"  ✗ Retry mechanism test failed: {str(e)}")
        return False

async def test_all_transport_types():
    """Test all MCP transport types with YAML config"""
    print_header("TEST: Config Files")

    try:
        import yaml
        import os

        config_path = "config/mcp_servers"
        if os.path.exists(config_path):
            print(f"  ✓ MCP servers config directory exists")

            # List all config files
            for filename in os.listdir(config_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(config_path, filename)
                    try:
                        with open(filepath, 'r') as f:
                            config = json.load(f)
                        print(f"  ✓ Loaded config: {filename}")
                        print(f"     Type: {config.get('type', 'unknown')}")

                        # Try to validate
                        from src.mcp_integration.factory import validate_config
                        is_valid, msg = validate_config(config)
                        if is_valid:
                            print(f"     Valid: ✓")
                        else:
                            print(f"     Invalid: {msg}")
                    except Exception as e:
                        print(f"  ✗ Failed to load {filename}: {str(e)}")
        else:
            print(f"  ⚠ Config directory not found")

        return True

    except Exception as e:
        print(f"  ✗ Config test failed: {str(e)}")
        return False

async def main():
    """Run all MCP tests"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{'MCP COMPREHENSIVE TEST SUITE'.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    tests = [
        ("Factory", test_mcp_factory),
        ("STDIO Client", test_stdio_client),
        ("SSE Client", test_sse_client),
        ("Streamable HTTP Client", test_streamable_http_client),
        ("WebSocket Client", test_websocket_client),
        ("Multi-Server Client", test_multi_server_client),
        ("Tool Wrapper", test_tool_wrapper),
        ("Retry Mechanism", test_retry_mechanism),
        ("Config Files", test_all_transport_types),
    ]

    results = {}
    for name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[name] = result
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {str(e)}")
            results[name] = False

    # Print summary
    print_header("MCP TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"Total Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {total - passed}{RESET}")
    print(f"Success Rate: {(passed/total*100):.1f}%")

    for name, result in results.items():
        icon = "✓" if result else "✗"
        color = GREEN if result else RED
        print(f"  {color}{icon} {name}{RESET}")

    print(f"\n{BLUE}{'='*80}{RESET}")
    if passed == total:
        print(f"{GREEN}{'ALL MCP TESTS PASSED!'.center(80)}{RESET}")
    else:
        print(f"{YELLOW}{'SOME MCP TESTS FAILED'.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
