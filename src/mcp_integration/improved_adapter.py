"""
Improved MCP Tool to LangChain Adapter
Incorporates best practices from official langchain-mcp-adapters
while keeping support for internal Python tools
"""

from typing import Type, TypeVar, List, Optional, Dict, Any, Union
from functools import lru_cache
from pydantic import BaseModel, Field, create_model
from langchain_core.tools import StructuredTool, BaseTool
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='ImprovedMCPTool')


class ImprovedMCPTool:
    """
    Improved base class for MCP tools
    Incorporates best practices from langchain-mcp-adapters
    """

    def __init__(self):
        self._name = self.get_name()
        self._description = self.get_description()
        self._input_schema = self.get_input_schema()

    def get_name(self) -> str:
        """Return tool name - must be implemented by subclass"""
        raise NotImplementedError("Subclasses must implement get_name()")

    def get_description(self) -> str:
        """Return tool description - must be implemented by subclass"""
        raise NotImplementedError("Subclasses must implement get_description()")

    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for input parameters - must be implemented by subclass"""
        raise NotImplementedError("Subclasses must implement get_input_schema()")

    def execute(self, **kwargs) -> Any:
        """Execute the tool - must be implemented by subclass"""
        raise NotImplementedError("Subclasses must implement execute()")

    def to_langchain_tool(self, cache: bool = True) -> BaseTool:
        """
        Convert to LangChain StructuredTool with improvements

        Args:
            cache: Whether to cache the result (default True)

        Returns:
            LangChain StructuredTool
        """
        if cache:
            return self._to_langchain_tool_cached()
        else:
            return self._to_langchain_tool_uncached()

    @lru_cache(maxsize=128)
    def _to_langchain_tool_cached(self) -> BaseTool:
        """Cached version of tool conversion"""
        return self._to_langchain_tool_uncached()

    def _to_langchain_tool_uncached(self) -> BaseTool:
        """Uncached version of tool conversion"""
        # Validate schema first
        schema = self.get_input_schema()
        self._validate_schema(schema)

        # Create Pydantic model
        input_model = self._create_input_model(schema)

        # Create wrapper function with better error handling
        tool_func = self._create_tool_function()

        # Create StructuredTool
        tool = StructuredTool(
            name=self._name,
            description=self._description,
            func=tool_func,
            args_schema=input_model,
            return_direct=False,
            tags=["mcp", "internal"],
            metadata={"source": "internal_mcp", "tool_class": self.__class__.__name__}
        )

        # Validate created tool
        self._validate_tool(tool)

        logger.info(f"✅ Converted {self._name} to LangChain tool")
        return tool

    def _validate_schema(self, schema: Dict[str, Any]) -> None:
        """Validate the input schema"""
        if not isinstance(schema, dict):
            raise ValueError(f"Schema must be a dict, got {type(schema)}")

        if "type" not in schema:
            raise ValueError("Schema must have a 'type' field")

        if schema["type"] != "object":
            raise ValueError("Schema type must be 'object'")

        if "properties" not in schema:
            raise ValueError("Schema must have a 'properties' field")

        properties = schema["properties"]
        if not isinstance(properties, dict):
            raise ValueError("Schema properties must be a dict")

        logger.debug(f"Schema validation passed for {self._name}")

    def _create_input_model(self, schema: Dict[str, Any]) -> Type[BaseModel]:
        """Create Pydantic model from JSON schema"""
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        fields = {}
        for prop_name, prop_schema in properties.items():
            prop_type, prop_field = self._schema_field_to_pydantic(prop_name, prop_schema, prop_name in required_fields)
            fields[prop_name] = prop_field

        # Create model with descriptive name
        model_name = f"{self._name.capitalize()}Input"
        InputModel = create_model(model_name, **fields)

        return InputModel

    def _schema_field_to_pydantic(self, name: str, schema: Dict[str, Any], required: bool) -> tuple:
        """Convert JSON schema field to Pydantic field"""
        from typing import Optional, List

        json_type = schema.get("type", "string")
        description = schema.get("description", "")
        default = schema.get("default", self._get_default_for_type(json_type))

        # Map JSON types to Python types
        type_map = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "object": dict,
            "array": List[str],  # Default to List[str], can be overridden
        }

        prop_type = type_map.get(json_type, str)

        # Handle arrays specially
        if json_type == "array":
            items = schema.get("items", {})
            item_type = items.get("type", "string")
            item_type_map = {
                "string": str,
                "integer": int,
                "number": float,
                "boolean": bool,
            }
            prop_type = List[item_type_map.get(item_type, str)]

        # Handle enums - use string with validation in Field
        enum_values = schema.get("enum")
        if enum_values:
            # Keep as string, add enum constraint in Field
            if not required:
                default = default or enum_values[0]

        # Create field
        if required:
            field = Field(description=description, json_schema_extra={"enum": enum_values} if enum_values else None)
        else:
            field = Field(default=default, description=description, json_schema_extra={"enum": enum_values} if enum_values else None)

        return prop_type, field

    def _get_default_for_type(self, json_type: str) -> Any:
        """Get appropriate default value for JSON type"""
        defaults = {
            "string": "",
            "integer": 0,
            "number": 0.0,
            "boolean": False,
            "array": [],
            "object": {},
            "null": None,
        }
        return defaults.get(json_type, None)

    def _create_tool_function(self):
        """Create the tool function with error handling"""
        def tool_func(**kwargs) -> str:
            """Tool function with error handling"""
            try:
                result = self.execute(**kwargs)
                if result is None:
                    return '{"status": "success", "message": "Operation completed"}'
                return str(result)
            except Exception as e:
                import traceback
                error_info = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "tool": self._name,
                    "traceback": traceback.format_exc() if logger.isEnabledFor(logging.DEBUG) else None
                }

                import json
                return json.dumps(error_info, indent=2)

        return tool_func

    def _validate_tool(self, tool: BaseTool) -> None:
        """Validate the created tool"""
        if not hasattr(tool, 'name') or not tool.name:
            raise ValueError("Tool must have a name")

        if not hasattr(tool, 'description') or not tool.description:
            raise ValueError("Tool must have a description")

        if not callable(tool.func):
            raise ValueError("Tool must have a callable function")

        logger.debug(f"Tool validation passed for {tool.name}")


class MCPAdapter:
    """
    Factory for creating LangChain tools from MCP tools
    Incorporates best practices from langchain-mcp-adapters
    """

    @staticmethod
    def create_tool(tool_instance: ImprovedMCPTool, cache: bool = True) -> BaseTool:
        """
        Create a LangChain tool from an MCP tool instance

        Args:
            tool_instance: MCP tool instance
            cache: Whether to cache the result

        Returns:
            LangChain BaseTool
        """
        return tool_instance.to_langchain_tool(cache=cache)

    @staticmethod
    def create_tools(tool_instances: List[ImprovedMCPTool], cache: bool = True) -> List[BaseTool]:
        """
        Create multiple LangChain tools from MCP tool instances

        Args:
            tool_instances: List of MCP tool instances
            cache: Whether to cache the results

        Returns:
            List of LangChain BaseTools
        """
        tools = []
        for tool_instance in tool_instances:
            try:
                tool = MCPAdapter.create_tool(tool_instance, cache=cache)
                tools.append(tool)
                logger.info(f"✅ Created tool: {tool.name}")
            except Exception as e:
                logger.error(f"❌ Failed to create tool {tool_instance.get_name()}: {e}")
                raise

        return tools

    @staticmethod
    def from_class(tool_class: Type[ImprovedMCPTool], **kwargs) -> BaseTool:
        """
        Create a tool from a tool class

        Args:
            tool_class: MCPTool subclass
            **kwargs: Additional arguments for tool initialization

        Returns:
            LangChain BaseTool
        """
        instance = tool_class(**kwargs)
        return MCPAdapter.create_tool(instance)


# Example usage
if __name__ == "__main__":
    # Example tool class
    class DateTimeTool(ImprovedMCPTool):
        def get_name(self) -> str:
            return "datetime"

        def get_description(self) -> str:
            return "Get current date and time"

        def get_input_schema(self) -> Dict[str, Any]:
            return {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["now", "today", "timestamp"],
                        "description": "Operation to perform"
                    }
                },
                "required": ["operation"]
            }

        def execute(self, operation: str) -> str:
            from datetime import datetime
            if operation == "now":
                return datetime.now().isoformat()
            elif operation == "today":
                return datetime.now().date().isoformat()
            elif operation == "timestamp":
                return str(datetime.now().timestamp())
            return "Unknown operation"

    # Create tool
    tool = DateTimeTool()
    langchain_tool = tool.to_langchain_tool()

    print(f"Created tool: {langchain_tool.name}")
    print(f"Description: {langchain_tool.description}")
    print(f"Args schema: {langchain_tool.args_schema}")

    # Test execution
    result = langchain_tool.invoke({"operation": "now"})
    print(f"Result: {result}")
