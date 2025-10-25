"""
Tool Factory - Dynamically load tools based on TOOL_MODE configuration
Supports both MCP tools and direct LangChain tools
"""

from typing import List, Dict, Any, Optional
from config import settings
from pydantic import BaseModel, Field


def get_tools() -> List:
    """
    Get tools based on TOOL_MODE configuration

    Returns:
        List of tools to bind to the LLM
    """
    tool_mode = settings.TOOL_MODE.lower()

    if tool_mode == "mcp":
        return _get_mcp_tools()
    elif tool_mode == "mcp_client":
        return _get_mcp_client_tools()
    elif tool_mode == "direct":
        return _get_direct_tools()
    else:
        raise ValueError(f"Invalid TOOL_MODE: {tool_mode}. Must be 'mcp', 'mcp_client', or 'direct'")


class ExecuteToolInput(BaseModel):
    """Input schema for execute_tool - handles both nested and direct parameters"""
    tool_name: str = Field(description="Name of the tool to execute")
    kwargs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Dictionary of parameters to pass to the tool (use this for nested parameters)"
    )
    # Allow additional fields for direct parameter passing
    class Config:
        extra = "allow"


def _get_mcp_tools() -> List:
    """
    Get MCP protocol tools (execute_tool wrapper)

    Returns:
        List containing execute_tool for MCP protocol
    """
    from mcp_integration.tools.google.cv_manager import CVSheetManagerTool
    from mcp_integration.tools.google.gmail_mcp import GmailMCPTool
    from mcp_integration.tools.google.calendar_mcp import CalendarMCPTool
    from mcp_integration.tools.communication.webex_mcp import WebexMCPTool
    from mcp_integration.tools.utilities.datetime_mcp import DateTimeMCPTool
    from mcp_integration.tools.google.cv_tools_mcp import CVProcessTool, SearchCandidatesTool, SearchCreateSheetTool
    from mcp_integration.tools.base import MCPToolRegistry
    from langchain_core.tools import StructuredTool

    mcp_registry = MCPToolRegistry()

    # Register all MCP tools (excluding SequentialThinkingTool - uses different architecture)
    mcp_registry.register(CVSheetManagerTool())
    mcp_registry.register(GmailMCPTool())
    mcp_registry.register(CalendarMCPTool())
    mcp_registry.register(WebexMCPTool())
    mcp_registry.register(DateTimeMCPTool())
    mcp_registry.register(CVProcessTool())
    mcp_registry.register(SearchCandidatesTool())
    mcp_registry.register(SearchCreateSheetTool())

    print(f"✅ Loaded MCP tools: {len(mcp_registry._tools)} tools registered")
    print(f"   Tool names: {', '.join(mcp_registry.get_tool_names())}")

    # Create a function that properly handles both parameter styles
    def execute_tool(tool_name: str, kwargs: Optional[Dict[str, Any]] = None, **extra_params) -> str:
        """
        Execute an MCP tool by name with parameters.
        
        Supports two calling styles:
        1. Nested: execute_tool(tool_name="datetime", kwargs={"operation": "get_current"})
        2. Direct: execute_tool(tool_name="datetime", operation="get_current")
        
        Args:
            tool_name: Name of the tool to execute
            kwargs: Dictionary of parameters (for nested style)
            **extra_params: Additional parameters (for direct style)
            
        Returns:
            Tool execution result as string
        """
        import json
        
        try:
            # Determine which parameters to use
            if kwargs:
                # Nested style: {"tool_name": "datetime", "kwargs": {"operation": "get_current"}}
                params = kwargs
            elif extra_params:
                # Direct style: {"tool_name": "datetime", "operation": "get_current"}
                params = extra_params
            else:
                # No parameters
                params = {}
            
            # Execute the tool with unpacked parameters
            result = mcp_registry.execute_tool(tool_name, **params)
            
            # Ensure result is a string
            if isinstance(result, str):
                return result
            else:
                return json.dumps(result)
                
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "tool_name": tool_name,
                "type": type(e).__name__,
                "hint": "Verify tool name and required parameters"
            })

    # Create a proper LangChain StructuredTool with explicit schema
    execute_tool_langchain = StructuredTool(
        name="execute_tool",
        description=(
            f"Execute any MCP tool by name. "
            f"Available tools: {', '.join(mcp_registry.get_tool_names())}. "
            f"Pass parameters either as 'kwargs' dict or as direct keyword arguments."
        ),
        func=execute_tool,
        args_schema=ExecuteToolInput,
        return_direct=False
    )

    return [execute_tool_langchain]


def _get_mcp_client_tools() -> List:
    """
    Get MCP client tools for external MCP servers

    Returns:
        List containing MCP client tools for communication with external servers
    """
    from mcp_integration.client import mcp_client_list_tools, mcp_client_execute_tool

    tools = [
        mcp_client_list_tools,
        mcp_client_execute_tool
    ]

    print(f"✅ Loaded MCP Client tools: {len(tools)} tools")
    print(f"   Tool names: {', '.join([t.name for t in tools])}")
    print(f"   MCP Server: {settings.MCP_SERVER_URL or 'Not configured'}")
    print(f"   Transport: {settings.MCP_SERVER_TRANSPORT}")

    return tools


def _get_direct_tools() -> List:
    """
    Get direct LangChain tools (legacy mode)
    NOTE: Direct tools are in tools_backup/integrations/ - copy to tools/ if needed

    Returns:
        List of LangChain tool functions
    """
    # TODO: Implement direct tools if needed
    # from tools.cv.cv_tools import search_create_sheet, process_cvs, search_candidates
    # from tools.calendar.calendar_tools import schedule_calendar_event
    # from tools.email.gmail_tools import send_email
    # from tools.utilities.datetime_tools import get_current_datetime
    # from tools.communication.webex_tools import schedule_webex_meeting, get_webex_meeting_details

    print("⚠️  Direct tools mode not implemented - use MCP mode instead")
    return []


def get_tool_mode_info() -> dict:
    """
    Get information about current tool mode

    Returns:
        Dictionary with mode information
    """
    tool_mode = settings.TOOL_MODE.lower()

    if tool_mode == "mcp":
        from mcp_integration.tools.base import mcp_registry
        return {
            "mode": "mcp",
            "description": "MCP Protocol (execute_tool wrapper)",
            "tool_count": len(mcp_registry._tools) if hasattr(mcp_registry, '_tools') else 0,
            "tools": mcp_registry.get_tool_names() if hasattr(mcp_registry, 'get_tool_names') else []
        }
    elif tool_mode == "mcp_client":
        return {
            "mode": "mcp_client",
            "description": "MCP Client (external server communication)",
            "tool_count": 2,
            "tools": ["mcp_client_list_tools", "mcp_client_execute_tool"],
            "server_url": settings.MCP_SERVER_URL,
            "transport": settings.MCP_SERVER_TRANSPORT
        }
    elif tool_mode == "direct":
        tools = _get_direct_tools()
        return {
            "mode": "direct",
            "description": "Direct LangChain tools",
            "tool_count": len(tools),
            "tools": [t.name for t in tools]
        }
    else:
        return {
            "mode": "unknown",
            "description": f"Invalid mode: {tool_mode}",
            "tool_count": 0,
            "tools": []
        }