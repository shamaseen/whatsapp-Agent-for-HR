"""
Dynamic Tool Loader
Loads tools based on flexible YAML configuration with auto-discovery
Supports mixing internal MCP tools, external MCP clients, and direct tools
"""

import yaml
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
import logging

from .registry import ToolRegistry, get_registry

logger = logging.getLogger(__name__)


class ToolLoader:
    """Dynamic tool loader with auto-discovery support"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize tool loader

        Args:
            config_path: Path to YAML config file (default: config/tools.yaml)
        """
        if config_path is None:
            # Look for config at project root/config/tools.yaml
            # __file__ is at src/tools/loader.py, so go up 3 levels to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "tools.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.loaded_tools: List[BaseTool] = []
        self.mcp_clients: Dict[str, Any] = {}  # Store clients for cleanup

        # Get global tool registry
        self.registry = get_registry()

    def _load_config(self) -> dict:
        """Load and parse YAML configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Replace environment variables in config
            config = self._replace_env_vars(config)
            return config
        except Exception as e:
            logger.error(f"Failed to load tool config: {e}")
            return {"tools": {}, "global_mcp_settings": {}}

    def _replace_env_vars(self, obj: Any) -> Any:
        """Recursively replace ${VAR} with environment variables"""
        if isinstance(obj, dict):
            return {k: self._replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # Replace ${VAR} patterns
            import re
            pattern = r'\$\{([^}]+)\}'

            def replacer(match):
                var_name = match.group(1)
                return os.getenv(var_name, match.group(0))

            return re.sub(pattern, replacer, obj)
        else:
            return obj

    def get_tools(self) -> List[BaseTool]:
        """
        Get all configured tools using auto-discovery

        Returns:
            List of loaded LangChain tools
        """
        # Optional dry-run to avoid external connections during tests/notebooks
        # BUT still load the tools for testing - just skip actual API calls
        skip_connect = os.getenv("TOOL_LOADER_SKIP_CONNECT") == "1"
        dry_run = os.getenv("TOOL_LOADER_DRY_RUN") == "1"

        if skip_connect or dry_run:
            # Load tools but mark them as dry run
            if not self.loaded_tools:
                self._load_tools_dry_run()
            return self.loaded_tools

        if self.loaded_tools:
            return self.loaded_tools

        # Suppress all async generator cleanup warnings
        import warnings
        import sys

        # Save stderr
        original_stderr = sys.stderr

        # Try to get running event loop
        try:
            loop = asyncio.get_running_loop()
            # If there's a running loop, we need to handle async differently
            import nest_asyncio
            nest_asyncio.apply()

            # Set up custom exception handler to suppress anyio cleanup warnings
            def handle_exception(loop, context):
                """Suppress anyio cancel scope errors"""
                exception = context.get('exception')
                if exception:
                    exc_str = str(exception)
                    # Suppress known harmless errors
                    if 'cancel scope' in exc_str or 'async_generator' in exc_str:
                        return
                # For other exceptions, use default handler
                if loop.get_exception_handler():
                    loop.default_exception_handler(context)

            # Store original handler and set custom one
            original_handler = loop.get_exception_handler()
            loop.set_exception_handler(handle_exception)

            try:
                # Suppress stderr during tool loading to hide async generator warnings
                import io
                sys.stderr = io.StringIO()
                self.loaded_tools = loop.run_until_complete(self._load_tools_async())
            finally:
                # Restore stderr and handler
                sys.stderr = original_stderr
                loop.set_exception_handler(original_handler)

        except RuntimeError:
            # No event loop running, create one
            try:
                # Suppress stderr during tool loading
                import io
                sys.stderr = io.StringIO()
                self.loaded_tools = asyncio.run(self._load_tools_async())
            finally:
                sys.stderr = original_stderr

        return self.loaded_tools

    async def _load_tools_async(self) -> List[BaseTool]:
        """Load all tools asynchronously using registry"""
        tools = []
        tool_configs = self.config.get("tools", {})

        logger.info(f"🔧 Loading tools from configuration...")
        logger.info(f"   Found {len(tool_configs)} tool configurations")

        for tool_name, tool_config in tool_configs.items():
            if not tool_config.get("enabled", True):
                logger.info(f"   ⏭️  Skipping disabled tool: {tool_name}")
                continue

            # Get provider (mode is legacy, provider is new name)
            provider = tool_config.get("provider", tool_config.get("mode", "auto"))

            try:
                # Auto-select provider if set to "auto"
                if provider == "auto":
                    provider = self._select_provider(tool_name)
                    logger.info(f"   🤖 Auto-selected provider for {tool_name}: {provider}")

                if provider == "internal_mcp":
                    tool = await self._load_internal_mcp_tool(tool_name, tool_config)
                    if tool:
                        if isinstance(tool, list):
                            tools.extend(tool)
                        else:
                            tools.append(tool)

                elif provider == "mcp_client":
                    client_tools = await self._load_mcp_client_tool(tool_name, tool_config)
                    if client_tools:
                        tools.extend(client_tools)

                elif provider == "direct":
                    tool = await self._load_direct_tool(tool_name, tool_config)
                    if tool:
                        tools.append(tool)

                else:
                    logger.warning(f"   ⚠️  Unknown provider '{provider}' for tool: {tool_name}")

            except Exception as e:
                logger.error(f"   ❌ Failed to load {tool_name}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                continue

        # Load multi-server configurations
        multi_configs = self.config.get("multi_servers", {}) or {}
        for suite_name, suite_config in multi_configs.items():
            if not suite_config.get("enabled", False):
                continue

            try:
                suite_tools = await self._load_multi_server(suite_name, suite_config)
                tools.extend(suite_tools)
            except Exception as e:
                logger.error(f"   ❌ Failed to load multi-server {suite_name}: {e}")

        logger.info(f"\n✅ Successfully loaded {len(tools)} tools")
        return tools

    def _load_tools_dry_run(self):
        """
        Load tools for testing without making external connections
        Loads tool definitions but skips actual API calls
        """
        tools = []
        tool_configs = self.config.get("tools", {})

        logger.info(f"🔧 Loading tools in DRY RUN mode...")
        logger.info(f"   Found {len(tool_configs)} tool configurations")

        for tool_name, tool_config in tool_configs.items():
            if not tool_config.get("enabled", True):
                logger.info(f"   ⏭️  Skipping disabled tool: {tool_name}")
                continue

            try:
                # Get the tool from registry
                tool_info = self.registry.get_tool_info(tool_name)
                if not tool_info:
                    logger.warning(f"   ⚠️  Tool {tool_name} not found in registry")
                    continue

                # Instantiate the tool from class_path
                internal_info = tool_info.get("internal")
                if not internal_info:
                    logger.warning(f"   ⚠️  Tool {tool_name} has no internal implementation")
                    continue

                class_path = internal_info.get("class_path")
                class_name = internal_info.get("class_name")

                if not class_path:
                    logger.warning(f"   ⚠️  Tool {tool_name} has no class_path")
                    continue

                # Dynamically import and instantiate
                module_path, cls_name = class_path.rsplit(".", 1)
                module = __import__(module_path, fromlist=[cls_name])
                tool_class = getattr(module, cls_name)
                tool_instance = tool_class()

                # Convert MCPTool to LangChain tool
                langchain_tool = tool_instance.to_langchain_tool()
                tools.append(langchain_tool)

                logger.info(f"   ✅ Loaded (dry run): {tool_name}")

            except Exception as e:
                logger.error(f"   ❌ Failed to load {tool_name}: {e}")
                import traceback
                logger.debug(traceback.format_exc())

        self.loaded_tools = tools
        logger.info(f"\n✅ Successfully loaded {len(tools)} tools in dry run mode")

    def _select_provider(self, tool_name: str) -> str:
        """
        Auto-select best provider for a tool
        Prefers internal_mcp over mcp_client

        Args:
            tool_name: Name of the tool

        Returns:
            Selected provider name
        """
        tool_info = self.registry.get_tool_info(tool_name)

        if not tool_info:
            logger.warning(f"   ⚠️  Tool '{tool_name}' not found in registry")
            return "internal_mcp"  # Default fallback

        providers = tool_info.get("providers", [])

        # Prefer internal over external
        if "internal_mcp" in providers:
            return "internal_mcp"
        elif "mcp_client" in providers:
            return "mcp_client"
        else:
            logger.warning(f"   ⚠️  No providers found for '{tool_name}'")
            return "internal_mcp"  # Default fallback

    async def _load_internal_mcp_tool(self, tool_name: str, config: dict) -> Optional[BaseTool]:
        """Load internal MCP protocol tool using registry"""
        logger.info(f"   📦 Loading internal MCP tool: {tool_name}")

        # Get tool info from registry
        internal_tools = self.registry.get_internal_tools()
        tool_info = internal_tools.get(tool_name)

        if not tool_info:
            logger.warning(f"   ⚠️  Internal tool '{tool_name}' not found in registry")
            logger.info(f"   💡 Available internal tools: {', '.join(internal_tools.keys())}")
            return None

        # Handle multi-tool case (e.g., cv_processing)
        if "tools" in tool_info:
            tools = []
            for sub_tool in tool_info["tools"]:
                tool = self._import_and_instantiate(sub_tool["class_path"])
                if tool:
                    tools.append(tool.to_langchain_tool())
            logger.info(f"   ✓ Loaded {len(tools)} tools for {tool_name}")
            return tools
        else:
            # Single tool
            tool = self._import_and_instantiate(tool_info["class_path"])
            if tool:
                logger.info(f"   ✓ Loaded {tool_name} from {tool_info['file_path']}")
                return tool.to_langchain_tool()

        return None

    async def _load_mcp_client_tool(self, tool_name: str, config: dict) -> List[BaseTool]:
        """Load external MCP client tool using registry"""
        logger.info(f"   🌐 Loading MCP client tool: {tool_name}")

        # Check for config override first
        tool_overrides = self.config.get("tool_overrides", {}) or {}
        override_config = tool_overrides.get(tool_name, {}) if tool_overrides else {}

        # Check if config references a config file
        mcp_config_file = config.get("mcp_config_file") or override_config.get("mcp_config_file")

        if mcp_config_file:
            # Load from servers directory using registry
            external_servers = self.registry.get_external_servers()
            server_info = external_servers.get(mcp_config_file)

            if not server_info:
                logger.error(f"   ❌ External server '{mcp_config_file}' not found in registry")
                logger.info(f"   💡 Available servers: {', '.join(external_servers.keys())}")
                return []

            # Load the actual config file
            import json
            config_path = Path(server_info["config_path"])

            with open(config_path, 'r') as f:
                mcp_config = json.load(f)

            logger.info(f"   📄 Using MCP config file: {mcp_config_file}.json")
        else:
            # Use inline config
            mcp_config = override_config.get("mcp_config") or config.get("mcp_config", {})
            if not mcp_config:
                logger.error(f"   ❌ No mcp_config or mcp_config_file provided for {tool_name}")
                return []

        # Add global settings
        global_settings = self.config.get("global_mcp_settings", {})
        for key, value in global_settings.items():
            if key not in mcp_config:
                mcp_config[key] = value

        # Import client factory
        from src.mcp_integration.factory import create_mcp_client, validate_config

        # Validate configuration
        is_valid, error = validate_config(mcp_config)
        if not is_valid:
            logger.error(f"   ❌ Invalid MCP config for {tool_name}: {error}")
            return []

        try:
            # Create client
            client = create_mcp_client(tool_name, mcp_config)

            # Connect with retry
            if hasattr(client, 'connect_with_retry'):
                tools = await client.connect_with_retry()
            else:
                tools = await client.connect()

            # Store client for later cleanup
            self.mcp_clients[tool_name] = client

            logger.info(f"   ✓ Loaded {len(tools)} tools from {tool_name} MCP server")
            return tools

        except Exception as e:
            logger.error(f"   ❌ Failed to connect to {tool_name} MCP server: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []

    async def _load_direct_tool(self, tool_name: str, config: dict) -> Optional[BaseTool]:
        """Load direct LangChain tool (legacy)"""
        logger.info(f"   🔧 Loading direct tool: {tool_name}")
        logger.warning(f"   ⚠️  Direct tools not implemented yet")
        return None

    async def _load_multi_server(self, suite_name: str, config: dict) -> List[BaseTool]:
        """Load multi-server configuration"""
        logger.info(f"   🔗 Loading multi-server suite: {suite_name}")

        from src.mcp_integration.factory import create_mcp_client

        multi_config = {
            "type": "multi",
            "servers": []
        }

        # Convert tool list to multi-server format
        for server_config in config.get("servers", []):
            multi_config["servers"].append(server_config)

        try:
            client = create_mcp_client(suite_name, multi_config)
            tools = await client.connect()

            self.mcp_clients[suite_name] = client

            logger.info(f"   ✓ Loaded {len(tools)} tools from {suite_name} suite")
            return tools

        except Exception as e:
            logger.error(f"   ❌ Failed to load {suite_name} suite: {e}")
            return []

    def _import_and_instantiate(self, class_path: str) -> Any:
        """Import and instantiate a class from module path"""
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            tool_class = getattr(module, class_name)
            return tool_class()
        except Exception as e:
            logger.error(f"   ❌ Failed to import {class_path}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    async def cleanup(self):
        """Close all MCP client connections"""
        logger.info("🧹 Cleaning up MCP client connections...")

        for name, client in self.mcp_clients.items():
            try:
                await client.close()
                logger.info(f"   ✓ Closed {name}")
            except Exception as e:
                logger.error(f"   ⚠️  Error closing {name}: {e}")

        self.mcp_clients.clear()
        logger.info("✅ Cleanup complete")

    def get_tool_summary(self) -> Dict[str, Any]:
        """Get summary of loaded tools"""
        return {
            "total_tools": len(self.loaded_tools),
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
                }
                for tool in self.loaded_tools
            ],
            "active_clients": list(self.mcp_clients.keys()),
            "config_file": str(self.config_path)
        }

    def list_available_tools(self) -> Dict[str, Any]:
        """
        List all available tools from registry

        Returns:
            Dictionary with available tools and their providers
        """
        all_tools = self.registry.get_all_tools()
        configured_tools = self.config.get("tools", {})

        def safe_get_enabled(cfg):
            """Safely get enabled status from config, handling non-dict values"""
            if isinstance(cfg, dict):
                return cfg.get("enabled", False)
            return False

        return {
            "available_tools": {
                name: {
                    "providers": info["providers"],
                    "configured": name in configured_tools,
                    "enabled": safe_get_enabled(configured_tools.get(name, {})) if name in configured_tools else False
                }
                for name, info in all_tools.items()
            },
            "summary": {
                "total_available": len(all_tools),
                "total_configured": len(configured_tools),
                "total_enabled": sum(1 for cfg in configured_tools.values() if isinstance(cfg, dict) and cfg.get("enabled", True))
            }
        }


# Convenience function
def get_dynamic_tools(config_path: Optional[str] = None) -> List[BaseTool]:
    """
    Get tools dynamically from YAML configuration

    Args:
        config_path: Optional path to config file

    Returns:
        List of loaded tools
    """
    loader = ToolLoader(config_path)
    return loader.get_tools()


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'
        )

        loader = ToolLoader()

        # Show available tools
        print("\n" + "="*80)
        print("AVAILABLE TOOLS")
        print("="*80)
        available = loader.list_available_tools()
        print(f"\nTotal available: {available['summary']['total_available']}")
        print(f"Total configured: {available['summary']['total_configured']}")
        print(f"Total enabled: {available['summary']['total_enabled']}")

        print("\n" + "-"*80)
        for name, info in sorted(available['available_tools'].items()):
            status = "✓ enabled" if info['enabled'] else "✗ disabled" if info['configured'] else "○ not configured"
            providers = ", ".join(info['providers'])
            print(f"{status:20} {name:20} ({providers})")

        # Load tools
        print("\n" + "="*80)
        print("LOADING TOOLS")
        print("="*80)
        tools = loader.get_tools()

        print("\n" + "="*80)
        print("LOADED TOOLS")
        print("="*80)

        summary = loader.get_tool_summary()
        print(f"\nTotal: {summary['total_tools']} tools")
        print(f"Active MCP Clients: {', '.join(summary['active_clients']) if summary['active_clients'] else 'None'}")
        print(f"\nTools:")
        for tool_info in summary['tools']:
            print(f"  • {tool_info['name']}: {tool_info['description']}")

        # Cleanup
        await loader.cleanup()

    asyncio.run(main())
