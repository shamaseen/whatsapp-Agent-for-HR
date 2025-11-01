"""
Streamable HTTP MCP Client
Connects to MCP servers via modern Streamable HTTP transport

This is the recommended transport for remote MCP servers.
Uses a single POST /mcp endpoint (vs HTTP+SSE which needed two endpoints).
"""

from typing import List, Dict, Any
from mcp import ClientSession
from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.tools import load_mcp_tools

from .base import BaseMCPClient
from .retry import RetryMixin
from .tool_wrapper import wrap_tools_list


class StreamableHTTPMCPClient(RetryMixin, BaseMCPClient):
    """MCP client using Streamable HTTP transport with automatic retry support"""
    
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
        """Connect to MCP server via Streamable HTTP"""
        try:
            # Import streamable HTTP client
            try:
                from mcp.client.streamable_http import streamablehttp_client
            except ImportError:
                raise ImportError(
                    "Streamable HTTP client not available. "
                    "Install with: pip install mcp[streamable-http]"
                )
            
            if not self.url:
                raise ValueError("Streamable HTTP client requires 'url' in config")
            
            # Ensure URL ends with /mcp/ or /mcp
            if not self.url.rstrip('/').endswith('/mcp'):
                if not self.url.endswith('/'):
                    self.url += '/'
                self.url += 'mcp/'
            
            # Connect via Streamable HTTP using context manager
            # streamablehttp_client returns (read, write, session_info)
            self._client_context = streamablehttp_client(
                self.url, 
                headers=self.headers
            )
            client_result = await self._client_context.__aenter__()
            
            # Unpack the tuple - streamablehttp returns 3 items
            self._read, self._write = client_result[0], client_result[1]
            
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
            print(f"   ✓ Streamable HTTP connected: {len(self.tools)} tool(s) loaded")
            return self.tools
            
        except Exception as e:
            print(f"   ✗ Streamable HTTP connection failed: {str(e)}")
            await self.close()  # Ensure cleanup on error
            raise
    
    async def close(self):
        """Close Streamable HTTP connection"""
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