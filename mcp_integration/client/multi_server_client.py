"""
Multi-Server MCP Client
Manages connections to multiple MCP servers simultaneously
"""

from typing import List, Dict, Any
from langchain_core.tools import StructuredTool

from .base import BaseMCPClient
from .factory import create_mcp_client


class MultiServerMCPClient(BaseMCPClient):
    """
    Client that manages multiple MCP server connections.
    Useful for connecting to several servers at once.
    """
    
    def __init__(self, server_name: str, config: Dict[str, Any]):
        super().__init__(server_name, config)
        self.sub_clients: Dict[str, BaseMCPClient] = {}
        self.servers = config.get("servers", [])
    
    async def connect(self) -> List[StructuredTool]:
        """Connect to all configured servers"""
        try:
            all_tools = []
            
            for server_config in self.servers:
                sub_server_name = server_config.get("name")
                if not sub_server_name:
                    print(f"   ⚠️  Skipping server without name")
                    continue
                
                try:
                    # Create client for each server
                    client = create_mcp_client(
                        server_name=sub_server_name,
                        config=server_config
                    )
                    
                    # Connect and get tools
                    tools = await client.connect()
                    self.sub_clients[sub_server_name] = client
                    all_tools.extend(tools)
                    
                    print(f"   ✓ {sub_server_name}: {len(tools)} tool(s)")
                    
                except Exception as e:
                    print(f"   ✗ {sub_server_name} failed: {e}")
                    continue
            
            self.tools = all_tools
            self._is_connected = len(self.sub_clients) > 0
            
            print(f"   ✓ Multi-server connected: {len(self.tools)} total tool(s) from {len(self.sub_clients)} server(s)")
            return self.tools
            
        except Exception as e:
            print(f"   ✗ Multi-server connection failed: {str(e)}")
            raise
    
    async def close(self):
        """Close all sub-client connections"""
        for server_name, client in list(self.sub_clients.items()):
            try:
                await client.close()
                print(f"   ✓ Closed {server_name}")
            except Exception as e:
                print(f"   ⚠️  Error closing {server_name}: {e}")
        
        self.sub_clients.clear()
        self._is_connected = False
