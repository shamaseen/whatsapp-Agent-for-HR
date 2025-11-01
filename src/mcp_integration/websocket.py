"""
WebSocket MCP Client
Connects to MCP servers via WebSocket transport

WebSocket transport is a community proposal, not officially part of the core MCP spec.
Useful for real-time, bidirectional communication with remote servers.
"""

from typing import List, Dict, Any
from mcp import ClientSession
from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.tools import load_mcp_tools

from .base import BaseMCPClient
from .retry import RetryMixin
from .tool_wrapper import wrap_tools_list


class WebSocketMCPClient(RetryMixin, BaseMCPClient):
    """MCP client using WebSocket transport with automatic retry support"""
    
    def __init__(self, server_name: str, config: Dict[str, Any]):
        # RetryMixin will extract retry config from config dict
        super().__init__(server_name, config)
        self.url = config.get("url")
        self.headers = config.get("headers", {})
        self._client_context = None
        self._session_context = None
        self._read = None
        self._write = None
    
    async def connect(self) -> List[StructuredTool]:
        """Connect to MCP server via WebSocket"""
        try:
            # Import WebSocket client
            try:
                from mcp.client.websocket import websocket_client
            except ImportError:
                raise ImportError(
                    "WebSocket client not available. "
                    "This is a community-contributed transport. "
                    "Install with: pip install mcp[websocket] or websockets"
                )
            
            if not self.url:
                raise ValueError("WebSocket client requires 'url' in config")
            
            # Validate WebSocket URL
            if not self.url.startswith(("ws://", "wss://")):
                raise ValueError(
                    f"WebSocket URL must start with ws:// or wss://, got: {self.url}"
                )
            
            # Connect via WebSocket using context manager
            self._client_context = websocket_client(
                self.url,
                headers=self.headers
            )
            self._read, self._write = await self._client_context.__aenter__()
            
            # Create session
            self._session_context = ClientSession(self._read, self._write)
            self.session = await self._session_context.__aenter__()
            
            # Initialize the connection
            await self.session.initialize()
            
            # Use LangChain's official adapter to load tools
            tools = await load_mcp_tools(self.session)

            # Wrap tools to support both sync and async invocation
            self.tools = wrap_tools_list(tools, prefix=self.server_name)
            
            self._is_connected = True
            print(f"   ✓ WebSocket connected: {len(self.tools)} tool(s) loaded")
            return self.tools
            
        except Exception as e:
            print(f"   ✗ WebSocket connection failed: {str(e)}")
            await self.close()  # Ensure cleanup on error
            raise
    
    async def close(self):
        """Close WebSocket connection"""
        if self._session_context:
            try:
                await self._session_context.__aexit__(None, None, None)
            except Exception as e:
                print(f"   ⚠️  Error closing session: {e}")
            finally:
                self._session_context = None
        
        if self._client_context:
            try:
                await self._client_context.__aexit__(None, None, None)
            except Exception as e:
                print(f"   ⚠️  Error closing client: {e}")
            finally:
                self._client_context = None
        
        self._is_connected = False
        self.session = None