"""
Base MCP Client Interface
Defines common interface for all MCP client implementations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain_core.tools import StructuredTool


class BaseMCPClient(ABC):
    """Abstract base class for MCP clients"""
    
    def __init__(self, server_name: str, config: Dict[str, Any]):
        self.server_name = server_name
        self.config = config
        self.session = None
        self.tools: List[StructuredTool] = []
        self._is_connected = False
    
    @abstractmethod
    async def connect(self) -> List[StructuredTool]:
        """
        Connect to MCP server and retrieve tools
        
        Returns:
            List of LangChain StructuredTool instances
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Close connection to MCP server"""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._is_connected
    
    def get_tools(self) -> List[StructuredTool]:
        """Get loaded tools"""
        return self.tools