"""
MCP Base Classes and Protocol
Implements Model Context Protocol for standardized tool interface
"""

from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from langchain_core.tools import tool


class MCPToolSchema(BaseModel):
    """Schema for MCP tool metadata"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None


class MCPTool(ABC):
    """Base class for MCP-compatible tools"""

    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.input_schema = self.get_input_schema()

    @abstractmethod
    def get_name(self) -> str:
        """Return tool name"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return tool description"""
        pass

    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for input parameters"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        pass

    def to_schema(self) -> MCPToolSchema:
        """Convert to MCP schema"""
        return MCPToolSchema(
            name=self.name,
            description=self.description,
            input_schema=self.input_schema
        )

    def to_langchain_tool(self):
        """Convert to LangChain tool"""
        tool_name = self.name
        tool_description = self.description
        tool_execute = self.execute

        @tool(tool_name)
        def langchain_wrapper(**kwargs) -> str:
            f"""{tool_description}"""
            return str(tool_execute(**kwargs))

        # Update the wrapper's metadata
        langchain_wrapper.name = tool_name
        langchain_wrapper.description = tool_description

        return langchain_wrapper


class MCPToolRegistry:
    """Registry for managing MCP tools"""

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}

    def register(self, tool: MCPTool):
        """Register a tool"""
        self._tools[tool.name] = tool

    def unregister(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in self._tools:
            del self._tools[tool_name]

    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[MCPToolSchema]:
        """List all registered tools"""
        return [tool.to_schema() for tool in self._tools.values()]

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        return tool.execute(**kwargs)

    def to_langchain_tools(self) -> List:
        """Convert all tools to LangChain format"""
        return [tool.to_langchain_tool() for tool in self._tools.values()]

    def get_tool_names(self) -> List[str]:
        """Get list of registered tool names"""
        return list(self._tools.keys())


# Global registry instance
mcp_registry = MCPToolRegistry()


# MCP Protocol Tools
@tool
def list_tools() -> str:
    """
    List all available MCP tools with their descriptions and schemas.
    Always call this FIRST before using any other tool to verify availability.

    Returns:
        JSON string containing list of available tools
    """
    import json
    tools = mcp_registry.list_tools()
    return json.dumps([{
        "name": t.name,
        "description": t.description,
        "input_schema": t.input_schema
    } for t in tools], indent=2)


@tool
def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> str:
    """
    Execute an MCP tool by name with given parameters.
    Must call list_tools first to verify tool availability.

    Args:
        tool_name: Name of the tool to execute
        parameters: Dictionary of input parameters for the tool

    Returns:
        Result from tool execution as string
    """
    try:
        result = mcp_registry.execute_tool(tool_name, **parameters)
        return str(result)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
