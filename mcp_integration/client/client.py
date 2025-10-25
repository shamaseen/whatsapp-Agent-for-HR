"""
MCP Client Implementation
Provides client interface to connect to external MCP servers
"""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
import json
import httpx
import asyncio


class MCPClient:
    """
    Client for connecting to external MCP servers.
    Supports both stdio and SSE transport protocols.
    """

    def __init__(self, server_url: Optional[str] = None, transport: str = "stdio"):
        """
        Initialize MCP Client

        Args:
            server_url: URL of MCP server (for SSE transport)
            transport: Transport protocol - "stdio" or "sse"
        """
        self.server_url = server_url
        self.transport = transport
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        self._client = httpx.AsyncClient(timeout=30.0)

    async def list_tools_async(self) -> List[Dict[str, Any]]:
        """
        List all available tools from MCP server

        Returns:
            List of tool definitions
        """
        if self._tools_cache:
            return self._tools_cache

        if self.transport == "sse" and self.server_url:
            try:
                response = await self._client.get(f"{self.server_url}/tools")
                tools = response.json()
                self._tools_cache = tools
                return tools
            except Exception as e:
                raise Exception(f"Failed to list tools from MCP server: {e}")
        else:
            # For stdio transport, return empty list
            # In production, this would use subprocess communication
            return []

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Synchronous wrapper for list_tools_async

        Returns:
            List of tool definitions
        """
        return asyncio.run(self.list_tools_async())

    async def execute_tool_async(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Execute a tool on the MCP server asynchronously

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result as string
        """
        if self.transport == "sse" and self.server_url:
            try:
                response = await self._client.post(
                    f"{self.server_url}/execute",
                    json={"tool_name": tool_name, "parameters": parameters}
                )
                result = response.json()
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to execute tool '{tool_name}': {str(e)}"})
        else:
            # For stdio transport
            # In production, this would use subprocess communication
            return json.dumps({"error": "stdio transport not yet implemented"})

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Synchronous wrapper for execute_tool_async

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result as string
        """
        return asyncio.run(self.execute_tool_async(tool_name, parameters))

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client(server_url: Optional[str] = None, transport: str = "stdio") -> MCPClient:
    """
    Get or create global MCP client instance

    Args:
        server_url: URL of MCP server
        transport: Transport protocol

    Returns:
        MCPClient instance
    """
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient(server_url=server_url, transport=transport)
    return _mcp_client


@tool
def mcp_client_list_tools() -> str:
    """
    List all available tools from the external MCP server.
    Use this to discover what tools are available before executing them.

    Returns:
        JSON string containing list of available tools with their schemas
    """
    from config import settings

    client = get_mcp_client(
        server_url=settings.MCP_SERVER_URL,
        transport=settings.MCP_SERVER_TRANSPORT
    )

    try:
        tools = client.list_tools()
        return json.dumps({
            "success": True,
            "tools": tools,
            "count": len(tools)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def mcp_client_execute_tool(tool_name: str, parameters: Dict[str, Any]) -> str:
    """
    Execute a tool on the external MCP server.
    Call mcp_client_list_tools first to see available tools.

    Args:
        tool_name: Name of the tool to execute
        parameters: Dictionary of parameters for the tool

    Returns:
        Result from tool execution as JSON string
    """
    from config import settings

    client = get_mcp_client(
        server_url=settings.MCP_SERVER_URL,
        transport=settings.MCP_SERVER_TRANSPORT
    )

    try:
        result = client.execute_tool(tool_name, parameters)
        return result
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error executing tool '{tool_name}': {str(e)}"
        })
