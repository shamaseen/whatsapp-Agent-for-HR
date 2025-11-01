"""
Stdio MCP Client
Connects to MCP servers via stdio (standard input/output)

Uses RetryMixin for automatic retry on connection failures.
Stdio connections are prone to:
- Process spawning failures
- npm package download issues
- Subprocess communication errors
"""

from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.tools import load_mcp_tools

from .base import BaseMCPClient
from .retry import RetryMixin
from .tool_wrapper import wrap_tools_list


class StdioMCPClient(RetryMixin, BaseMCPClient):
    """MCP client using stdio connection with automatic retry support"""

    def __init__(self, server_name: str, config: Dict[str, Any]):
        # RetryMixin will extract retry config from config dict
        super().__init__(server_name, config)
        self._client_context = None
        self._session_context = None
        self._read = None
        self._write = None
    
    async def connect(self) -> List[StructuredTool]:
        """Connect to MCP server via stdio"""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.config["command"],
                args=self.config["args"],
                env=self.config.get("env")
            )

            # Connect to server using context manager
            self._client_context = stdio_client(server_params)
            self._read, self._write = await self._client_context.__aenter__()

            # Create session
            self._session_context = ClientSession(self._read, self._write)
            self.session = await self._session_context.__aenter__()

            # Initialize the connection
            await self.session.initialize()

            # Use LangChain's official adapter to load tools
            tools = await load_mcp_tools(self.session)

            # Wrap tools to support both sync and async invocation
            # This fixes the "StructuredTool does not support sync invocation" error
            self.tools = wrap_tools_list(tools, prefix=self.server_name)

            self._is_connected = True
            print(f"   ✓ Stdio connected: {len(self.tools)} tool(s) loaded")
            return self.tools

        except Exception as e:
            # Clean up on error
            await self._cleanup_internal()
            print(f"   ✗ Stdio connection failed: {str(e)}")
            raise

    async def _cleanup_internal(self):
        """Internal cleanup without closing session (for use during retries)"""
        if self._session_context:
            try:
                self._session_context = None
            except:
                pass

        if self._client_context:
            try:
                self._client_context = None
            except:
                pass

        self.session = None
        self._is_connected = False
    
    async def close(self):
        """Close stdio connection gracefully"""
        import warnings
        import asyncio

        # If already closed, just return
        if not self._is_connected and not self._session_context and not self._client_context:
            return

        # Close session first
        if self._session_context:
            try:
                await self._session_context.__aexit__(None, None, None)
            except Exception:
                pass  # Silently ignore all cleanup errors
            finally:
                self._session_context = None

        # Close client connection
        if self._client_context:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    await self._client_context.__aexit__(None, None, None)
            except Exception:
                pass  # Ignore all cleanup errors
            finally:
                self._client_context = None

        self._is_connected = False
        self.session = None