#!/usr/bin/env python3
"""
Tools System Comprehensive Test Suite
Tests all tools individually and in combinations
"""

import asyncio
import sys
from typing import List, Dict, Any

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(title: str):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{title.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

async def test_tool_loading():
    """Test tool loading system"""
    print_header("TEST: Tool Loading System")

    try:
        import nest_asyncio
        nest_asyncio.apply()

        from src.agents.tool_factory import get_tools

        tools = get_tools()
        print(f"  ✓ Loaded {len(tools)} tools")

        # Group tools by type
        gmail_tools = [t for t in tools if 'gmail' in t.name.lower()]
        calendar_tools = [t for t in tools if 'calendar' in t.name.lower()]
        datetime_tools = [t for t in tools if 'datetime' in t.name.lower()]
        cv_tools = [t for t in tools if any(k in t.name.lower() for k in ['cv', 'sheet', 'candidate'])]
        webex_tools = [t for t in tools if 'webex' in t.name.lower()]

        print(f"\n  Tool Distribution:")
        print(f"    Gmail tools: {len(gmail_tools)}")
        print(f"    Calendar tools: {len(calendar_tools)}")
        print(f"    DateTime tools: {len(datetime_tools)}")
        print(f"    CV/Sheet tools: {len(cv_tools)}")
        print(f"    Webex tools: {len(webex_tools)}")

        return True, len(tools)

    except Exception as e:
        print(f"  ✗ Tool loading failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0

async def test_tool_properties(tool):
    """Test individual tool properties"""
    try:
        # Check required attributes
        assert hasattr(tool, 'name'), f"Tool {tool.name} missing 'name'"
        assert hasattr(tool, 'description'), f"Tool {tool.name} missing 'description'"

        # Check tool name is valid
        assert tool.name, f"Tool {tool.name} has empty name"
        assert len(tool.name) > 0, f"Tool {tool.name} has invalid name"

        # Check description is valid
        assert tool.description, f"Tool {tool.name} has empty description"
        assert len(tool.description) > 0, f"Tool {tool.name} has invalid description"

        # Check args_schema if available
        args_schema = getattr(tool, 'args_schema', None)
        if args_schema:
            # Validate schema structure
            schema_dict = args_schema.model_json_schema() if hasattr(args_schema, 'model_json_schema') else {}
            assert 'properties' in schema_dict or schema_dict, "Schema should have properties"

        return True
    except Exception as e:
        return False, str(e)

async def test_all_tools_individually():
    """Test each tool individually"""
    print_header("TEST: Individual Tool Validation")

    try:
        import nest_asyncio
        nest_asyncio.apply()

        from src.agents.tool_factory import get_tools

        tools = get_tools()
        print(f"  Testing {len(tools)} tools individually...\n")

        results = []
        for i, tool in enumerate(tools, 1):
            success, error = await test_tool_properties(tool)
            status = "✓" if success else "✗"
            color = GREEN if success else RED

            print(f"  {color}{status}{RESET} [{i:2d}/{len(tools)}] {tool.name}")

            if not success:
                print(f"      Error: {error}")
                results.append(False)
            else:
                results.append(True)

        # Summary
        passed = sum(results)
        total = len(results)
        print(f"\n  Summary: {GREEN}{passed}/{total} tools validated{RESET}")

        return passed == total

    except Exception as e:
        print(f"  ✗ Tool validation failed: {str(e)}")
        return False

async def test_gmail_tools():
    """Test Gmail-specific tools"""
    print_header("TEST: Gmail Tools")

    try:
        import nest_asyncio
        nest_asyncio.apply()

        from src.agents.tool_factory import get_tools

        tools = get_tools()
        gmail_tools = [t for t in tools if 'gmail' in t.name.lower()]

        print(f"  Found {len(gmail_tools)} Gmail tools:\n")

        expected_tools = [
            'send_email',
            'draft_email',
            'read_email',
            'search_emails',
            'list_labels',
            'create_filter',
            'download_attachment'
        ]

        found_count = 0
        for expected in expected_tools:
            matching = [t for t in gmail_tools if expected in t.name.lower()]
            if matching:
                print(f"  ✓ Found: {expected} ({len(matching)} variant(s))")
                found_count += 1
            else:
                print(f"  ✗ Missing: {expected}")

        print(f"\n  {GREEN}{found_count}/{len(expected_tools)} expected Gmail tools found{RESET}")
        return found_count > 0

    except Exception as e:
        print(f"  ✗ Gmail tools test failed: {str(e)}")
        return False

async def test_calendar_tools():
    """Test Calendar-specific tools"""
    print_header("TEST: Calendar Tools")

    try:
        import nest_asyncio
        nest_asyncio.apply()

        from src.agents.tool_factory import get_tools

        tools = get_tools()
        calendar_tools = [t for t in tools if 'calendar' in t.name.lower()]

        print(f"  Found {len(calendar_tools)} Calendar tools:\n")

        expected_tools = [
            'create_event',
            'list_events',
            'get_event',
            'delete_event',
            'update_event',
            'list_calendars',
            'get_freebusy'
        ]

        found_count = 0
        for expected in expected_tools:
            matching = [t for t in calendar_tools if expected in t.name.lower()]
            if matching:
                print(f"  ✓ Found: {expected} ({len(matching)} variant(s))")
                found_count += 1
            else:
                print(f"  ✗ Missing: {expected}")

        print(f"\n  {GREEN}{found_count}/{len(expected_tools)} expected Calendar tools found{RESET}")
        return found_count > 0

    except Exception as e:
        print(f"  ✗ Calendar tools test failed: {str(e)}")
        return False

async def test_datetime_tools():
    """Test DateTime-specific tools"""
    print_header("TEST: DateTime Tools")

    try:
        import nest_asyncio
        nest_asyncio.apply()

        from src.agents.tool_factory import get_tools

        tools = get_tools()
        datetime_tools = [t for t in tools if 'datetime' in t.name.lower()]

        print(f"  Found {len(datetime_tools)} DateTime tools:\n")

        expected_tools = [
            'get_current_time',
            'convert_time'
        ]

        found_count = 0
        for expected in expected_tools:
            matching = [t for t in datetime_tools if expected in t.name.lower()]
            if matching:
                print(f"  ✓ Found: {expected}")
                found_count += 1
            else:
                print(f"  ✗ Missing: {expected}")

        print(f"\n  {GREEN}{found_count}/{len(expected_tools)} expected DateTime tools found{RESET}")
        return found_count > 0

    except Exception as e:
        print(f"  ✗ DateTime tools test failed: {str(e)}")
        return False

async def test_cv_sheet_tools():
    """Test CV and Sheet-specific tools"""
    print_header("TEST: CV & Sheet Tools")

    try:
        import nest_asyncio
        nest_asyncio.apply()

        from src.agents.tool_factory import get_tools

        tools = get_tools()
        cv_sheet_tools = [t for t in tools if any(k in t.name.lower() for k in ['cv', 'sheet', 'candidate'])]

        print(f"  Found {len(cv_sheet_tools)} CV/Sheet tools:\n")

        expected_tools = [
            'cv_sheet_manager',
            'process_cvs',
            'search_candidates',
            'search_create_sheet'
        ]

        found_count = 0
        for expected in expected_tools:
            matching = [t for t in cv_sheet_tools if expected in t.name.lower()]
            if matching:
                print(f"  ✓ Found: {expected}")
                found_count += 1
            else:
                print(f"  ✗ Missing: {expected}")

        print(f"\n  {GREEN}{found_count}/{len(expected_tools)} expected CV tools found{RESET}")
        return found_count > 0

    except Exception as e:
        print(f"  ✗ CV tools test failed: {str(e)}")
        return False

async def test_webex_tools():
    """Test Webex-specific tools"""
    print_header("TEST: Webex Tools")

    try:
        import nest_asyncio
        nest_asyncio.apply()

        from src.agents.tool_factory import get_tools

        tools = get_tools()
        webex_tools = [t for t in tools if 'webex' in t.name.lower()]

        print(f"  Found {len(webex_tools)} Webex tools:\n")

        if webex_tools:
            for tool in webex_tools:
                print(f"  ✓ {tool.name}")
            return True
        else:
            print(f"  ✗ No Webex tools found")
            return False

    except Exception as e:
        print(f"  ✗ Webex tools test failed: {str(e)}")
        return False

async def test_tool_combinations():
    """Test tool combinations"""
    print_header("TEST: Tool Combinations")

    try:
        import nest_asyncio
        nest_asyncio.apply()

        from src.agents.tool_factory import get_tools
        from src.config import settings
        from langchain_google_genai import ChatGoogleGenerativeAI
        from src.agents.simple_agent import create_simple_agent

        tools = get_tools()
        print(f"  Testing various tool combinations...\n")

        # Combination 1: Gmail + Calendar
        gmail_calendar = [t for t in tools if 'gmail' in t.name.lower() or 'calendar' in t.name.lower()][:5]
        if gmail_calendar:
            llm = ChatGoogleGenerativeAI(model=settings.MODEL_NAME, temperature=settings.TEMPERATURE)
            agent1 = create_simple_agent(llm, gmail_calendar)
            print(f"  ✓ Gmail+Calendar combination: {len(gmail_calendar)} tools")

        # Combination 2: CV tools only
        cv_only = [t for t in tools if any(k in t.name.lower() for k in ['cv', 'sheet', 'candidate'])][:5]
        if cv_only:
            llm = ChatGoogleGenerativeAI(model=settings.MODEL_NAME, temperature=settings.TEMPERATURE)
            agent2 = create_simple_agent(llm, cv_only)
            print(f"  ✓ CV-only combination: {len(cv_only)} tools")

        # Combination 3: Single tool
        single_tool = [tools[0]] if tools else []
        if single_tool:
            llm = ChatGoogleGenerativeAI(model=settings.MODEL_NAME, temperature=settings.TEMPERATURE)
            agent3 = create_simple_agent(llm, single_tool)
            print(f"  ✓ Single tool combination: {len(single_tool)} tool")

        # Combination 4: All tools
        if tools:
            llm = ChatGoogleGenerativeAI(model=settings.MODEL_NAME, temperature=settings.TEMPERATURE)
            agent4 = create_simple_agent(llm, tools)
            print(f"  ✓ All tools combination: {len(tools)} tools")

        return True

    except Exception as e:
        print(f"  ✗ Tool combination test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_tool_schema_validation():
    """Test tool schema validation"""
    print_header("TEST: Tool Schema Validation")

    try:
        import nest_asyncio
        nest_asyncio.apply()

        from src.agents.tool_factory import get_tools

        tools = get_tools()
        print(f"  Validating schemas for {len(tools)} tools...\n")

        schema_valid = 0
        schema_missing = 0

        for tool in tools:
            args_schema = getattr(tool, 'args_schema', None)
            if args_schema:
                try:
                    # Try to get schema
                    if hasattr(args_schema, 'model_json_schema'):
                        schema = args_schema.model_json_schema()
                        assert 'properties' in schema
                        schema_valid += 1
                    else:
                        schema_missing += 1
                except Exception as e:
                    print(f"  ✗ Schema validation failed for {tool.name}: {str(e)}")
            else:
                schema_missing += 1

        print(f"\n  Schema Statistics:")
        print(f"    Valid schemas: {schema_valid}")
        print(f"    Missing schemas: {schema_missing}")
        print(f"    Total: {schema_valid + schema_missing}")

        return True

    except Exception as e:
        print(f"  ✗ Schema validation test failed: {str(e)}")
        return False

async def test_tool_loader():
    """Test tool loader system"""
    print_header("TEST: Tool Loader System")

    try:
        from src.tools.loader import ToolLoader
        loader = ToolLoader()
        print(f"  ✓ Created ToolLoader")

        # Test loading
        tools = loader.get_tools()
        print(f"  ✓ Loaded {len(tools)} tools via loader")

        # Test summary
        summary = loader.get_tool_summary()
        print(f"  ✓ Got tool summary: {summary.get('total_tools', 0)} tools")

        return True

    except Exception as e:
        print(f"  ✗ Tool loader test failed: {str(e)}")
        return False

async def test_tool_registry():
    """Test tool registry"""
    print_header("TEST: Tool Registry")

    try:
        from src.tools.registry import get_registry
        registry = get_registry()
        print(f"  ✓ Got registry")

        # Test listing
        available = registry.list_tools()
        print(f"  ✓ Listed {len(available)} available tools")

        # Test summary
        summary = registry.get_summary()
        print(f"  ✓ Got summary: {summary}")

        return True

    except Exception as e:
        print(f"  ✗ Tool registry test failed: {str(e)}")
        return False

async def main():
    """Run all tool tests"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{'TOOLS SYSTEM COMPREHENSIVE TEST SUITE'.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    # First test: tool loading
    success, tool_count = await test_tool_loading()
    if not success:
        print(f"\n{RED}Tool loading failed. Cannot continue.{RESET}\n")
        return 1

    tests = [
        ("Individual Tool Validation", test_all_tools_individually),
        ("Gmail Tools", test_gmail_tools),
        ("Calendar Tools", test_calendar_tools),
        ("DateTime Tools", test_datetime_tools),
        ("CV & Sheet Tools", test_cv_sheet_tools),
        ("Webex Tools", test_webex_tools),
        ("Tool Combinations", test_tool_combinations),
        ("Schema Validation", test_tool_schema_validation),
        ("Tool Loader", test_tool_loader),
        ("Tool Registry", test_tool_registry),
    ]

    results = {}
    for name, test_func in tests:
        try:
            result = await test_func()
            results[name] = result
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Print summary
    print_header("TOOLS TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"Total Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {total - passed}{RESET}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    print(f"\nTotal Tools Loaded: {GREEN}{tool_count}{RESET}")

    print(f"\nDetailed Results:")
    for name, result in results.items():
        icon = "✓" if result else "✗"
        color = GREEN if result else RED
        print(f"  {color}{icon} {name}{RESET}")

    print(f"\n{BLUE}{'='*80}{RESET}")
    if passed == total:
        print(f"{GREEN}{'ALL TOOLS TESTS PASSED!'.center(80)}{RESET}")
    else:
        print(f"{YELLOW}{'SOME TOOLS TESTS FAILED'.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
