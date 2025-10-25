#!/usr/bin/env python3
"""
Test script to verify all three tool modes work correctly
Run this without .env to avoid configuration errors
"""

import sys
import os

# Mock settings to avoid .env dependency
class MockSettings:
    TOOL_MODE = "mcp"
    MCP_SERVER_URL = None
    MCP_SERVER_TRANSPORT = "stdio"
    GOOGLE_API_KEY = "test"
    MODEL_NAME = "gemini-1.5-pro"

# Mock the settings before importing
sys.modules['config'] = type(sys)('config')
sys.modules['config'].settings = MockSettings()

def test_mode(mode_name: str):
    """Test a specific tool mode"""
    print(f"\n{'='*60}")
    print(f"Testing {mode_name.upper()} Mode")
    print(f"{'='*60}")

    # Update mode
    MockSettings.TOOL_MODE = mode_name

    try:
        from agents.tool_factory import get_tools, get_tool_mode_info
        import importlib
        import agents.tool_factory
        importlib.reload(agents.tool_factory)

        # Get tool mode info
        info = get_tool_mode_info()
        print(f"\n✅ Mode: {info['mode']}")
        print(f"   Description: {info['description']}")
        print(f"   Tool Count: {info['tool_count']}")

        if info.get('tools'):
            print(f"   Tools: {', '.join(info['tools'][:5])}")
            if len(info['tools']) > 5:
                print(f"         ... and {len(info['tools']) - 5} more")

        if mode_name == "mcp_client":
            print(f"   Server URL: {info.get('server_url', 'Not configured')}")
            print(f"   Transport: {info.get('transport', 'Not configured')}")

        print(f"\n✅ {mode_name.upper()} mode loaded successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error loading {mode_name} mode:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run tests for all three modes"""
    print("\n" + "="*60)
    print("Tool Mode Verification Test")
    print("="*60)

    results = {}

    # Test MCP mode
    results['mcp'] = test_mode('mcp')

    # Test MCP Client mode
    results['mcp_client'] = test_mode('mcp_client')

    # Test Direct mode
    results['direct'] = test_mode('direct')

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for mode, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {mode.upper()} mode")

    all_passed = all(results.values())
    print("\n" + "="*60)

    if all_passed:
        print("✅ All tool modes verified successfully!")
        print("="*60)
        return 0
    else:
        print("❌ Some tool modes failed verification")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
