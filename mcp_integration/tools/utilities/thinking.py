"""
Sequential Thinking Tool
Uses existing MCPToolManager to connect to the Sequential Thinking MCP server
"""

from typing import List
from langchain_core.tools import BaseTool
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp_integration.client.stdio import stdio_client
from typing import Annotated, TypedDict, Literal, Any
from langgraph.prebuilt import ToolNode
import json
from pydantic import BaseModel, Field, create_model
from langchain_core.tools import StructuredTool
class MCPToolManager:
    """Manages MCP connection with detailed schema debugging"""
    
    def __init__(self, server_config: dict = None):
        self.session = None
        self.read = None
        self.write = None
        self.tools = []
        self._client_context = None
        self._session_context = None
        self.server_config = server_config or {
            "command": "npx",
            "args": ["@modelcontextprotocol/server-sequential-thinking"]
        }
    
    async def connect(self):
        """Connect to MCP server and create tools"""
        server_params = StdioServerParameters(
            command=self.server_config["command"],
            args=self.server_config["args"],
            env=self.server_config.get("env")
        )
        
        self._client_context = stdio_client(server_params)
        self.read, self.write = await self._client_context.__aenter__()
        
        self._session_context = ClientSession(self.read, self.write)
        self.session = await self._session_context.__aenter__()
        await self.session.initialize()
        
        tool_list = await self.session.list_tools()
        server_name = ' '.join(self.server_config['args'])
        
        print(f"\n{'='*80}")
        print(f"Connected to: {self.server_config['command']} {server_name}")
        print(f"{'='*80}")
        
        for mcp_tool in tool_list.tools:
            print(f"\n📦 Tool: {mcp_tool.name}")
            print(f"   Description: {mcp_tool.description}")
            
            if mcp_tool.inputSchema:
                print(f"   Input Schema:")
                print(f"   {json.dumps(mcp_tool.inputSchema, indent=6)}")
            else:
                print(f"   ⚠️  No input schema provided")
            
            langchain_tool = self._create_tool(mcp_tool)
            self.tools.append(langchain_tool)
            print(f"   ✓ Created LangChain tool")
        
        print(f"\n{'='*80}\n")
        return self.tools
    
    def _create_tool(self, mcp_tool):
        """Create a LangChain tool with proper parameter handling"""
        
        if mcp_tool.inputSchema and "properties" in mcp_tool.inputSchema:
            properties = mcp_tool.inputSchema.get("properties", {})
            required = mcp_tool.inputSchema.get("required", [])
            
            print(f"   📋 Parameters detected:")
            for prop_name in properties.keys():
                req_status = "required" if prop_name in required else "optional"
                print(f"      - {prop_name} ({req_status})")
            
            fields = {}
            for prop_name, prop_schema in properties.items():
                json_type = prop_schema.get("type", "string")
                prop_description = prop_schema.get("description", "")
                
                # Handle array types specially for Gemini compatibility
                if json_type == "array":
                    # Check if items schema exists
                    items_schema = prop_schema.get("items", {})
                    items_type = items_schema.get("type", "string")
                    
                    # For Gemini, we need to be more specific about array item types
                    if items_type == "string":
                        from typing import List
                        prop_type = List[str]
                    elif items_type == "integer":
                        from typing import List
                        prop_type = List[int]
                    elif items_type == "object":
                        from typing import List
                        prop_type = List[dict]
                    else:
                        from typing import List
                        prop_type = List[str]  # Default to List[str]
                else:
                    prop_type = self._get_python_type(json_type)
                
                # Handle required vs optional
                if prop_name in required:
                    fields[prop_name] = (prop_type, Field(description=prop_description))
                else:
                    if json_type == "array":
                        default_val = []
                    elif prop_type == str:
                        default_val = ""
                    elif prop_type in [int, float]:
                        default_val = 0
                    elif prop_type == bool:
                        default_val = False
                    elif prop_type == dict:
                        default_val = {}
                    else:
                        default_val = None
                    
                    fields[prop_name] = (prop_type, Field(default=default_val, description=prop_description))
            
            input_model = create_model(
                f"{mcp_tool.name}Input",
                **fields
            )
        else:
            print(f"   ⚠️  Using fallback schema (query parameter)")
            input_model = create_model(
                f"{mcp_tool.name}Input",
                query=(str, Field(default="", description="Tool input"))
            )
        
        def make_tool_func(tool_name: str, session_ref: Any):
            async def tool_func(**kwargs):
                try:
                    print(f"\n   🔧 Calling {tool_name} with args: {kwargs}")
                    result = await session_ref.call_tool(tool_name, kwargs)
                    
                    if result.content:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            response = content.text
                        else:
                            response = str(content)
                        
                        print(f"   ✓ Tool returned: {response[:100]}...")
                        return response
                    
                    print(f"   ⚠️  Tool returned no content")
                    return "No content returned"
                    
                except Exception as e:
                    error_msg = f"Error executing tool: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    return error_msg
            
            return tool_func
        
        tool = StructuredTool(
            name=mcp_tool.name,
            description=mcp_tool.description or f"Tool: {mcp_tool.name}",
            coroutine=make_tool_func(mcp_tool.name, self.session),
            args_schema=input_model
        )
        
        return tool
    
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
    
    async def close(self):
        """Close MCP connection"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._client_context:
            await self._client_context.__aexit__(None, None, None)


class SequentialThinkingTool:
    """
    Wrapper for Sequential Thinking MCP server using MCPToolManager.
    Provides easy access to sequential thinking capabilities.
    """

    def __init__(self, use_simple_manager: bool = False):
        """
        Initialize Sequential Thinking Tool
        
        Args:
            use_simple_manager: If True, use SimpleMCPToolManager, else use MCPToolManager
        """
        self.manager = None
        self.tools = []
        self._initialized = False
        self.use_simple_manager = use_simple_manager
        
        # Sequential Thinking server configuration
        self.server_config = {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
        }

    async def initialize_async(self):
        """Initialize the MCP connection and load tools (async)"""
        if self._initialized:
            return
        
        # Import here to avoid circular dependencies

            
        self.manager = MCPToolManager(self.server_config)
        
        # Connect and get tools
        self.tools = await self.manager.connect()
        self._initialized = True
        
        print(f"\n✅ Sequential Thinking initialized with {len(self.tools)} tool(s)")

    def initialize(self):
        """Initialize the MCP connection and load tools (sync wrapper)"""
        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot initialize in running event loop. Use 'await initialize_async()' instead"
            )
        except RuntimeError:
            # No event loop - safe to create one
            asyncio.run(self.initialize_async())

    def get_tools(self) -> List[BaseTool]:
        """
        Get all loaded LangChain tools
        
        Returns:
            List of LangChain BaseTool instances ready to use with agents
        """
        if not self._initialized:
            raise RuntimeError("Tool not initialized. Call 'initialize()' or 'await initialize_async()' first")
        
        return self.tools

    def get_tool_by_name(self, name: str = "sequential_thinking") -> BaseTool:
        """
        Get a specific tool by name
        
        Args:
            name: Tool name (default: "sequential_thinking")
            
        Returns:
            LangChain BaseTool instance
        """
        if not self._initialized:
            raise RuntimeError("Tool not initialized. Call 'initialize()' or 'await initialize_async()' first")
        
        for tool in self.tools:
            if tool.name == name:
                return tool
        
        raise ValueError(f"Tool '{name}' not found. Available: {[t.name for t in self.tools]}")

    async def close_async(self):
        """Close MCP connection (async)"""
        if self.manager:
            await self.manager.close()
            self.manager = None
            self.tools = []
            self._initialized = False

    def close(self):
        """Close MCP connection (sync wrapper)"""
        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot close in running event loop. Use 'await close_async()' instead"
            )
        except RuntimeError:
            asyncio.run(self.close_async())


# Quick helper function
async def get_sequential_thinking_tools(use_simple: bool = False) -> List[BaseTool]:
    """
    Quick helper to get Sequential Thinking tools
    
    Args:
        use_simple: If True, use SimpleMCPToolManager
    
    Returns:
        List of LangChain BaseTool instances ready to use
        
    Example:
        tools = await get_sequential_thinking_tools()
        agent = create_tool_calling_agent(llm, tools, prompt)
    """
    tool_wrapper = SequentialThinkingTool(use_simple_manager=use_simple)
    await tool_wrapper.initialize_async()
    return tool_wrapper.get_tools()
