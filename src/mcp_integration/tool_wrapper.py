"""
Tool Wrapper Utility
Provides utilities for wrapping MCP tools to support both sync and async invocation.
"""

import asyncio
from langchain_core.tools import StructuredTool


def make_sync_async_compatible(tool: StructuredTool) -> StructuredTool:
    """
    Wrap an async-only tool to support both sync and async invocation.

    This fixes the 'StructuredTool does not support sync invocation' error
    that occurs when LangGraph or agents try to invoke async-only tools synchronously.

    Args:
        tool: A StructuredTool that may only have async (coroutine) implementation

    Returns:
        The same tool with both sync (func) and async (coroutine) support
    """
    # Store the original async function
    original_coroutine = tool.coroutine

    if original_coroutine and not tool.func:
        # Create a sync wrapper that runs the async function
        def sync_wrapper(**kwargs):
            """Sync wrapper for async tool function"""
            try:
                loop = asyncio.get_running_loop()
                # If there's already a loop (e.g., in Jupyter), use nest_asyncio
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(original_coroutine(**kwargs))
            except RuntimeError:
                # No running loop, create a new one
                return asyncio.run(original_coroutine(**kwargs))

        # Set both sync and async versions
        tool.func = sync_wrapper
        tool.coroutine = original_coroutine

    return tool


def wrap_tools_list(tools: list[StructuredTool], prefix: str = "") -> list[StructuredTool]:
    """
    Wrap a list of tools to support both sync and async invocation.

    Args:
        tools: List of StructuredTool instances to wrap
        prefix: Optional prefix to add to tool names (e.g., server name)

    Returns:
        List of wrapped tools with sync and async support
    """
    wrapped_tools = []

    for tool in tools:
        # Add prefix if provided
        if prefix:
            tool.name = f"{prefix}_{tool.name}"

        # Make compatible with both sync and async invocation
        wrapped_tool = make_sync_async_compatible(tool)
        wrapped_tools.append(wrapped_tool)

    return wrapped_tools
