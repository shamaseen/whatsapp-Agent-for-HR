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
    
    @staticmethod
    def _get_python_type(json_type: str):
        """Map JSON schema types to Python types"""
        type_map = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        return type_map.get(json_type, str)
    
    @staticmethod
    def _get_default_value(json_type: str):
        """Get default value for a JSON type"""
        defaults = {
            "string": "",
            "integer": 0,
            "number": 0.0,
            "boolean": False,
            "array": [],
            "object": {}
        }
        return defaults.get(json_type)
