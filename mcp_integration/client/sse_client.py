"""
SSE MCP Client
Connects to MCP servers via Server-Sent Events (HTTP)
"""

from typing import List, Dict, Any
from mcp import ClientSession
from langchain_core.tools import StructuredTool

from .base import BaseMCPClient
from .tool_builder import build_langchain_tool


class SSEMCPClient(BaseMCPClient):
    """MCP client using SSE (HTTP) connection"""
    
    def __init__(self, server_name: str, config: Dict[str, Any]):
        super().__init__(server_name, config)
        self.url = config.get("url")
        self.headers = config.get("headers", {})
    
    async def connect(self) -> List[StructuredTool]:
        """Connect to MCP server via SSE"""
        try:
            # Import SSE client (requires mcp[sse] package)
            try:
                from mcp_integration.client.sse import sse_client
            except ImportError:
                raise ImportError(
                    "SSE client not available. Install with: pip install mcp[sse]"
                )
            
            if not self.url:
                raise ValueError("SSE client requires 'url' in config")
            
            # Connect via SSE
            async with sse_client(self.url, headers=self.headers) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    await session.initialize()
                    
                    # Get available tools
                    tool_list = await session.list_tools()
                    
                    for mcp_tool in tool_list.tools:
                        langchain_tool = build_langchain_tool(
                            mcp_tool=mcp_tool,
                            server_name=self.server_name,
                            session=session
                        )
                        self.tools.append(langchain_tool)
                    
                    self._is_connected = True
                    print(f"   ✓ SSE connected: {len(self.tools)} tool(s) loaded")
                    return self.tools
            
        except Exception as e:
            print(f"   ✗ SSE connection failed: {str(e)}")
            raise
    
    async def close(self):
        """Close SSE connection"""
        # SSE connections are managed by context manager
        self._is_connected = False
        print(f"   ✓ SSE connection closed")
