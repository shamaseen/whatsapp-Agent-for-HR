"""
Tool Factory - Dynamically load tools based on flexible YAML configuration
Uses dynamic mode exclusively for maximum flexibility
"""

from typing import List, Dict, Any
from src.config import settings


def get_tools() -> List:
    """
    Get tools using dynamic YAML configuration

    All tools are loaded from src/config/tool_config.yaml
    This allows mixing internal MCP tools, external MCP servers, and more

    Returns:
        List of tools to bind to the LLM
    """
    return _get_dynamic_tools()


def _get_dynamic_tools() -> List:
    """
    Get tools using dynamic YAML configuration

    This mode allows you to:
    - Mix internal MCP tools and external MCP clients
    - Configure each tool independently
    - Easily enable/disable tools
    - Add new tools without code changes

    Configuration file: src/config/tools.yaml

    Returns:
        List of dynamically loaded tools
    """
    from src.tools.loader import ToolLoader

    print("🔧 Loading tools from dynamic configuration")
    print("   Config: src/config/tools.yaml")

    loader = ToolLoader()
    tools = loader.get_tools()

    # Print summary
    summary = loader.get_tool_summary()
    print(f"\n✅ Loaded {summary['total_tools']} tools")
    print(f"   Active MCP clients: {', '.join(summary['active_clients']) if summary['active_clients'] else 'None'}")
    print(f"   Tool names: {', '.join([t.name for t in tools])}")

    # Store loader for cleanup
    if not hasattr(settings, '_tool_loader'):
        settings._tool_loader = loader

    return tools


def get_tool_summary() -> Dict[str, Any]:
    """
    Get information about loaded tools

    Returns:
        Dictionary with tool information
    """
    if hasattr(settings, '_tool_loader'):
        return settings._tool_loader.get_tool_summary()
    else:
        return {
            "mode": "dynamic",
            "description": "Dynamic YAML configuration",
            "tool_count": 0,
            "tools": [],
            "note": "Call get_tools() first to load tools"
        }


def list_available_tools() -> Dict[str, Any]:
    """
    List all available tools from registry (both internal and external)

    Returns:
        Dictionary with available tools and their providers
    """
    from src.tools import ToolLoader

    loader = ToolLoader()
    return loader.list_available_tools()


def print_available_tools() -> None:
    """
    Print a human-readable list of all available tools
    """
    from src.tools.registry import get_registry

    registry = get_registry()
    registry.print_summary()


# Backwards-compatibility for older notebooks
def get_tool_mode_info() -> Dict[str, Any]:
    """Compatibility shim: return available tools summary used by old notebooks."""
    return list_available_tools()