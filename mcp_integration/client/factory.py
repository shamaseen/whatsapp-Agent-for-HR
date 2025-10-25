"""
Changes to services/tool_factory.py

REPLACE the imports section:
"""

# OLD imports to remove:
# from mcp import ClientSession, StdioServerParameters
# from mcp_integration.client.stdio import stdio_client
# from pydantic import create_model, Field
# from langchain_core.tools import StructuredTool

# NEW imports to add:
from mcp_integration.client import BaseMCPClient
from mcp_integration.client.stdio_client import StdioMCPClient
from mcp_integration.client.sse_client import SSEMCPClient


"""
REPLACE the entire MCPServerClient class with:
"""

# DELETE: class MCPServerClient (entire class)

# This class is now replaced by mcp_clients module
# The new architecture uses:
# - mcp_clients.stdio_client.StdioMCPClient
# - mcp_clients.sse_client.SSEMCPClient  
# - mcp_clients.multi_server_client.MultiServerMCPClient
# - Factory function: create_mcp_client()


"""
UPDATE ToolFactory class - MODIFY these attributes:
"""

class ToolFactory:
    """Factory to create tools based on MODE configuration"""

    def __init__(self):
        self.tools = []
        self._initialized = False
        self.mcp_servers_dir = Path(__file__).parent.parent / "mcp_servers"
        
        # CHANGED: Use BaseMCPClient type instead of MCPServerClient
        self.mcp_clients: Dict[str, BaseMCPClient] = {}


"""
UPDATE _load_mcp_server method - REPLACE entire method:
"""

async def _load_mcp_server(self, server_name: str):
    """
    Load external MCP server based on JSON config
    
    Supports multiple connection types:
    - stdio: Standard input/output (default)
    - sse: Server-Sent Events (HTTP)
    - multi: Multiple servers simultaneously
    
    Args:
        server_name: Name of server (gmail, calendar, datetime, thinking, etc.)
    
    Returns:
        List of tools from the MCP server
    """
    try:
        # Load config
        config_file = self.mcp_servers_dir / f"{server_name}.json"
        if not config_file.exists():
            print(f"   ⚠️  Config not found: {config_file}")
            return await self._fallback_to_custom(server_name)

        with open(config_file) as f:
            config = json.load(f)

        if not config.get("enabled", False) and server_name != "thinking":
            print(f"   ⚠️  Server disabled in config")
            return await self._fallback_to_custom(server_name)

        # Validate configuration
        is_valid, error_msg = validate_config(config)
        if not is_valid:
            print(f"   ⚠️  Invalid config: {error_msg}")
            return await self._fallback_to_custom(server_name)

        # Create appropriate client using factory
        client = create_mcp_client(server_name, config)
        
        # Connect to MCP server
        tools = await client.connect()
        
        # Store client for cleanup
        self.mcp_clients[server_name] = client
        
        return tools

    except Exception as e:
        print(f"   ⚠️  MCP server failed: {e}")
        return await self._fallback_to_custom(server_name)


"""
UPDATE get_tool_summary method - ADD connection type info:
"""

def get_tool_summary(self) -> dict:
    """Get summary of loaded tools"""
    
    # Build MCP server info
    mcp_info = {}
    for name, client in self.mcp_clients.items():
        mcp_info[name] = {
            "connected": client.is_connected,
            "type": client.__class__.__name__,
            "tools_count": len(client.tools)
        }
    
    return {
        "total_tools": len(self.tools),
        "tool_names": [t.name for t in self.tools],
        "mcp_servers_active": list(self.mcp_clients.keys()),
        "mcp_servers_info": mcp_info,  # NEW: Detailed connection info
        "configuration": {
            "gmail": settings.GMAIL_MODE,
            "calendar": settings.CALENDAR_MODE,
            "sheets": settings.SHEETS_MODE,
            "datetime": settings.DATETIME_MODE,
            "thinking": settings.THINKING_MODE,
            "webex": settings.WEBEX_MODE,
            "cv": settings.CV_MODE
        }
    }
