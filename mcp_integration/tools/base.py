"""
MCP Base Classes and Protocol
Implements Model Context Protocol for standardized tool interface

Supports dual-mode operation:
- Custom mode: Uses local Python implementations
- External mode: Connects to external MCP servers via HTTP/stdio
"""

from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, create_model
from langchain_core.tools import tool, StructuredTool
from config import settings


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

    def to_langchain_tool(self) -> StructuredTool:
        """
        Convert to LangChain StructuredTool with proper schema handling
        
        This creates a tool that:
        1. Has proper type validation via Pydantic
        2. Supports both sync and async invocation
        3. Preserves the input schema from get_input_schema()
        """
        schema = self.get_input_schema()
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Build Pydantic model fields from JSON schema
        fields = {}
        for prop_name, prop_schema in properties.items():
            json_type = prop_schema.get("type", "string")
            prop_description = prop_schema.get("description", "")
            enum_values = prop_schema.get("enum")
            
            # Handle array types specially - CRITICAL for Gemini
            if json_type == "array":
                items_schema = prop_schema.get("items", {})
                items_type = items_schema.get("type", "string")
                
                # Map item types to Python types
                from typing import List
                if items_type == "string":
                    prop_type = List[str]
                elif items_type == "integer":
                    prop_type = List[int]
                elif items_type == "number":
                    prop_type = List[float]
                elif items_type == "boolean":
                    prop_type = List[bool]
                elif items_type == "object":
                    prop_type = List[dict]
                else:
                    prop_type = List[str]  # Default to List[str]
                
                # Ensure the schema has items defined for Gemini
                if "items" not in prop_schema:
                    prop_schema["items"] = {"type": "string"}
            
            # Handle other types
            else:
                type_map = {
                    "string": str,
                    "integer": int,
                    "number": float,
                    "boolean": bool,
                    "object": dict
                }
                prop_type = type_map.get(json_type, str)
            
            # Handle required vs optional fields with enum constraints
            if prop_name in required:
                # Required field - no default value
                if enum_values:
                    # Use Field with enum constraint for validation
                    # The json_schema_extra passes enum info to the LLM
                    fields[prop_name] = (
                        prop_type, 
                        Field(
                            description=prop_description,
                            json_schema_extra={"enum": enum_values}
                        )
                    )
                else:
                    fields[prop_name] = (prop_type, Field(description=prop_description))
            else:
                # Optional field - provide sensible default
                default_val = self._get_default_value(json_type)
                if enum_values:
                    fields[prop_name] = (
                        Optional[prop_type], 
                        Field(
                            default=default_val, 
                            description=prop_description,
                            json_schema_extra={"enum": enum_values}
                        )
                    )
                else:
                    fields[prop_name] = (
                        Optional[prop_type], 
                        Field(default=default_val, description=prop_description)
                    )
        
        # If no properties defined, create a simple schema with one parameter
        if not fields:
            fields = {
                "input": (str, Field(default="", description="Tool input"))
            }
        
        # Create Pydantic model for input validation
        InputModel = create_model(
            f"{self.get_name()}Input",
            **fields
        )
        
        # Create wrapper function that ensures kwargs are passed correctly
        def tool_wrapper(**kwargs) -> str:
            """
            Wrapper that:
            1. Receives validated kwargs from Pydantic model
            2. Passes them to execute()
            3. Converts result to string
            """
            try:
                result = self.execute(**kwargs)
                return str(result) if result is not None else '{"status": "completed"}'
            except Exception as e:
                import json
                return json.dumps({
                    "error": str(e),
                    "type": type(e).__name__,
                    "tool": self.get_name()
                })
        
        # Create StructuredTool with proper metadata
        tool = StructuredTool(
            name=self.get_name(),
            description=self.get_description(),
            func=tool_wrapper,
            args_schema=InputModel,
            return_direct=False
        )
        
        return tool
    
    @staticmethod
    def _get_default_value(json_type: str) -> Any:
        """Get appropriate default value for a JSON schema type"""
        defaults = {
            "string": "",
            "integer": 0,
            "number": 0.0,
            "boolean": False,
            "array": [],
            "object": {}
        }
        return defaults.get(json_type, None)


class MCPToolRegistry:
    """Registry for managing MCP tools"""

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}

    def register(self, tool: MCPTool):
        """Register a tool"""
        self._tools[tool.name] = tool
        print(f"   ✓ Registered tool: {tool.name}")

    def unregister(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            print(f"   ✓ Unregistered tool: {tool_name}")

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

    def to_langchain_tools(self) -> List[StructuredTool]:
        """Convert all tools to LangChain format"""
        return [tool.to_langchain_tool() for tool in self._tools.values()]

    def get_tool_names(self) -> List[str]:
        """Get list of registered tool names"""
        return list(self._tools.keys())
    
    def get_tool_summary(self) -> Dict[str, Any]:
        """Get summary of registered tools"""
        return {
            "total_tools": len(self._tools),
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description[:100] + "..." if len(tool.description) > 100 else tool.description,
                    "parameters": list(tool.input_schema.get("properties", {}).keys())
                }
                for tool in self._tools.values()
            ]
        }


# Global registry instance
mcp_registry = MCPToolRegistry()


# MCP Protocol Tools - These allow LLM to discover and execute registered tools
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
def execute_tool(tool_name: str, kwargs: Optional[Dict[str, Any]] = None, **parameters) -> str:
    """
    Execute an MCP tool by name with given parameters.
    Must call list_tools first to verify tool availability.

    Args:
        tool_name: Name of the tool to execute
        kwargs: Dictionary of input parameters for the tool (alternative to **parameters)
        **parameters: Tool parameters can also be passed as keyword arguments

    Returns:
        Result from tool execution as string
        
    Examples:
        execute_tool(tool_name="datetime", kwargs={"operation": "get_current"})
        execute_tool(tool_name="datetime", operation="get_current")
    """
    import json
    try:
        # Handle both parameter styles:
        # 1. Nested kwargs: {"tool_name": "datetime", "kwargs": {"operation": "get_current"}}
        # 2. Direct parameters: {"tool_name": "datetime", "operation": "get_current"}
        
        if kwargs:
            # If kwargs dict is provided, use it
            params = kwargs
        elif parameters:
            # If direct parameters are provided, use them
            params = parameters
        else:
            # No parameters provided
            params = {}
        
        # Execute the tool with unpacked parameters
        result = mcp_registry.execute_tool(tool_name, **params)
        return str(result)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "tool_name": tool_name,
            "type": type(e).__name__,
            "hint": "Check that all required parameters are provided"
        })


# Convenience function for debugging
def print_registered_tools():
    """Print all registered tools for debugging"""
    import json
    summary = mcp_registry.get_tool_summary()
    print("\n" + "="*80)
    print(f"📋 Registered MCP Tools ({summary['total_tools']} total)")
    print("="*80)
    for tool_info in summary['tools']:
        print(f"\n🔧 {tool_info['name']}")
        print(f"   Description: {tool_info['description']}")
        print(f"   Parameters: {', '.join(tool_info['parameters']) if tool_info['parameters'] else 'None'}")
    print("="*80 + "\n")