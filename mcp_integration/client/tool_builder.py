"""
Tool Builder Utility
Creates LangChain tools from MCP tool definitions
"""

import asyncio
from typing import Any, List
from pydantic import create_model, Field
from langchain_core.tools import StructuredTool


def build_langchain_tool(mcp_tool: Any, server_name: str, session: Any) -> StructuredTool:
    """
    Build a LangChain StructuredTool from MCP tool definition
    
    Args:
        mcp_tool: MCP tool object from server
        server_name: Name of the MCP server
        session: MCP session for tool execution
    
    Returns:
        LangChain StructuredTool with sync/async support
    """
    
    # Build input schema
    input_model = _build_input_model(mcp_tool)
    
    # Create async execution function
    async def tool_func_async(**kwargs):
        """Async version - directly calls MCP tool"""
        try:
            result = await session.call_tool(mcp_tool.name, kwargs)
            
            if result.content:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return content.text
                return str(content)
            
            return "No content returned"
            
        except Exception as e:
            return f"Error executing tool: {str(e)}"
    
    # Create sync wrapper
    def tool_func_sync(**kwargs):
        """Sync wrapper - creates new event loop if needed"""
        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot run sync tool from async context. "
                "Use ainvoke() instead or let LangChain handle it."
            )
        except RuntimeError as e:
            if "Cannot run" in str(e):
                raise
            # No running loop - safe to create one
            return asyncio.run(tool_func_async(**kwargs))
    
    # Create StructuredTool
    tool = StructuredTool(
        name=f"{server_name}_{mcp_tool.name}",
        description=mcp_tool.description or f"Tool: {mcp_tool.name}",
        func=tool_func_sync,
        coroutine=tool_func_async,
        args_schema=input_model
    )
    
    return tool


def _build_input_model(mcp_tool: Any):
    """Build Pydantic input model from MCP tool schema"""
    
    if mcp_tool.inputSchema and "properties" in mcp_tool.inputSchema:
        properties = mcp_tool.inputSchema.get("properties", {})
        required = mcp_tool.inputSchema.get("required", [])
        
        fields = {}
        for prop_name, prop_schema in properties.items():
            json_type = prop_schema.get("type", "string")
            prop_description = prop_schema.get("description", "")
            
            # Handle array types specially for Gemini compatibility
            if json_type == "array":
                prop_type = _get_array_type(prop_schema)
            else:
                prop_type = _get_python_type(json_type)
            
            # Handle required vs optional
            if prop_name in required:
                fields[prop_name] = (prop_type, Field(description=prop_description))
            else:
                default_val = _get_default_value(json_type)
                fields[prop_name] = (
                    prop_type, 
                    Field(default=default_val, description=prop_description)
                )
        
        return create_model(f"{mcp_tool.name}Input", **fields)
    
    # Fallback schema
    return create_model(
        f"{mcp_tool.name}Input",
        query=(str, Field(default="", description="Tool input"))
    )


def _get_array_type(prop_schema: dict):
    """Get Python type for array properties"""
    items_schema = prop_schema.get("items", {})
    items_type = items_schema.get("type", "string")
    
    type_map = {
        "string": List[str],
        "integer": List[int],
        "number": List[float],
        "boolean": List[bool],
        "object": List[dict]
    }
    
    return type_map.get(items_type, List[str])


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
