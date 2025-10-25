"""
Stdio MCP Client
Connects to MCP servers via stdio (standard input/output)
"""

import asyncio
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import create_model, Field
from langchain_core.tools import StructuredTool

from .base import BaseMCPClient
from .tool_builder import build_langchain_tool


class StdioMCPClient(BaseMCPClient):
    """MCP client using stdio connection"""
    
    def __init__(self, server_name: str, config: Dict[str, Any]):
        super().__init__(server_name, config)
        self._client_context = None
        self._session_context = None
    
    async def connect(self) -> List[StructuredTool]:
        """Connect to MCP server via stdio"""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.config["command"],
                args=self.config["args"],
                env=self.config.get("env")
            )
            
            # Connect to server
            self._client_context = stdio_client(server_params)
            read, write = await self._client_context.__aenter__()
            
            self._session_context = ClientSession(read, write)
            self.session = await self._session_context.__aenter__()
            await self.session.initialize()
            
            # Get available tools
            tool_list = await self.session.list_tools()
            
            for mcp_tool in tool_list.tools:
                langchain_tool = build_langchain_tool(
                    mcp_tool=mcp_tool,
                    server_name=self.server_name,
                    session=self.session
                )
                self.tools.append(langchain_tool)
            
            self._is_connected = True
            print(f"   ✓ Stdio connected: {len(self.tools)} tool(s) loaded")
            return self.tools
            
        except Exception as e:
            print(f"   ✗ Stdio connection failed: {str(e)}")
            raise
    
    async def close(self):
        """Close stdio connection"""
        if self._session_context:
            try:
                await self._session_context.__aexit__(None, None, None)
            except Exception as e:
                print(f"   ⚠️  Error closing session: {e}")
        
        if self._client_context:
            try:
                await self._client_context.__aexit__(None, None, None)
            except Exception as e:
                print(f"   ⚠️  Error closing client: {e}")
        
        self._is_connected = False
