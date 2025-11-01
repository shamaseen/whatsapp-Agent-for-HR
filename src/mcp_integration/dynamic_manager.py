"""
Dynamic MCP Manager

A comprehensive, generic MCP manager that can:
- Auto-discover MCP servers
- Dynamically load tools from any server
- Support any configuration
- Handle multiple servers simultaneously
- Provide unified tool interface

This makes the MCP integration truly reusable and generic.
"""

import os
import json
import yaml
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from langchain_core.tools import BaseTool

from .factory import create_mcp_client, validate_config
from .retry import RetryConfig
from .tool_wrapper import wrap_tools_list


class DynamicMCPManager:
    """
    A dynamic MCP manager that can handle any MCP server configuration.

    Features:
    - Auto-discovery of MCP servers from directories
    - Dynamic loading of tools
    - Support for multiple transports
    - Unified tool interface
    - Configurable retry and error handling
    - Generic and reusable
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        auto_discover: bool = True,
        servers_dir: Optional[Path] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize DynamicMCPManager.

        Args:
            config: Optional configuration dict
            auto_discover: Whether to auto-discover servers on init
            servers_dir: Directory to search for server configs
            retry_config: Optional retry configuration
        """
        self.config = config or {}
        self.servers: Dict[str, Any] = {}
        self.clients: Dict[str, Any] = {}
        self.loaded_tools: List[BaseTool] = []
        self.retry_config = retry_config or RetryConfig()
        self.auto_discover = auto_discover

        # Default servers directory
        self.servers_dir = servers_dir or Path("config/mcp_servers")

        # Track discovered servers
        self.discovered_servers: List[str] = []

        if self.auto_discover:
            asyncio.create_task(self.discover_servers())

    @staticmethod
    def _validate_server_config(config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate a server configuration.

        Args:
            config: Server configuration dict

        Returns:
            Tuple of (is_valid, error_message)
        """
        from .factory import validate_config
        return validate_config(config)

    async def discover_servers(
        self,
        servers_dir: Optional[Path] = None,
        pattern: str = "*.json",
    ) -> List[str]:
        """
        Auto-discover MCP servers from directory.

        Args:
            servers_dir: Directory to search
            pattern: File pattern to match

        Returns:
            List of discovered server names
        """
        search_dir = servers_dir or self.servers_dir

        if not search_dir.exists():
            self.servers_dir = search_dir
            self.discovered_servers = []
            return []

        discovered = []

        # Find all JSON config files
        config_files = list(search_dir.glob(pattern))

        for config_file in config_files:
            try:
                with open(config_file, 'r') as f:
                    server_config = json.load(f)

                # Validate config
                is_valid, error = validate_config(server_config)
                if not is_valid:
                    print(f"⚠️  Invalid server config {config_file.name}: {error}")
                    continue

                server_name = server_config.get('name', config_file.stem)

                # Check if enabled
                if not server_config.get('enabled', True):
                    print(f"⏭️  Server '{server_name}' is disabled")
                    continue

                # Store server config
                self.servers[server_name] = server_config
                discovered.append(server_name)

                print(f"✅ Discovered MCP server: {server_name}")

            except Exception as e:
                print(f"❌ Failed to load {config_file.name}: {e}")

        self.discovered_servers = discovered
        return discovered

    async def load_server(
        self,
        server_name: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> List[BaseTool]:
        """
        Load tools from a specific MCP server.

        Args:
            server_name: Name of the server
            config: Optional override config

        Returns:
            List of loaded tools
        """
        # Get server config
        if server_name not in self.servers:
            if server_name not in self.discovered_servers:
                raise ValueError(f"Server '{server_name}' not found or not discovered")

        server_config = config or self.servers[server_name]

        try:
            # Create client
            client = create_mcp_client(server_name, server_config)

            # Set retry config if provided
            if hasattr(client, 'retry_config'):
                client.retry_config = self.retry_config

            # Connect and load tools
            if hasattr(client, 'connect_with_retry'):
                tools = await client.connect_with_retry()
            else:
                tools = await client.connect()

            # Wrap tools with prefix
            wrapped_tools = wrap_tools_list(tools, prefix=server_name)

            # Store client and tools
            self.clients[server_name] = client
            self.loaded_tools.extend(wrapped_tools)

            print(f"✅ Loaded {len(wrapped_tools)} tools from '{server_name}'")
            return wrapped_tools

        except Exception as e:
            print(f"❌ Failed to load server '{server_name}': {e}")
            raise

    async def load_all_tools(
        self,
        server_names: Optional[List[str]] = None,
        exclude_disabled: bool = True,
    ) -> List[BaseTool]:
        """
        Load tools from all discovered servers.

        Args:
            server_names: Optional list of server names to load
            exclude_disabled: Whether to exclude disabled servers

        Returns:
            List of all loaded tools
        """
        # Get servers to load
        if server_names:
            servers_to_load = server_names
        else:
            servers_to_load = self.discovered_servers

        # Load tools from each server
        all_tools = []

        for server_name in servers_to_load:
            try:
                tools = await self.load_server(server_name)
                all_tools.extend(tools)
            except Exception as e:
                print(f"⚠️  Skipping server '{server_name}': {e}")
                continue

        return all_tools

    async def load_tools_from_config(
        self,
        config: Dict[str, Any],
    ) -> List[BaseTool]:
        """
        Load tools from a complete tools configuration.

        Expected config format:
        {
            "tools": {
                "tool_name": {
                    "enabled": true,
                    "provider": "mcp_client",
                    "mcp_config_file": "server_name",
                    # or
                    "mcp_config": {...}
                }
            }
        }

        Args:
            config: Tools configuration dict

        Returns:
            List of loaded tools
        """
        tools_config = config.get('tools', {})
        loaded_tools = []

        # Load tools according to config
        for tool_name, tool_config in tools_config.items():
            # Check if enabled
            if not tool_config.get('enabled', True):
                continue

            # Get provider
            provider = tool_config.get('provider', 'auto')

            # Skip non-mcp_client providers for now
            if provider != 'mcp_client':
                continue

            # Get server config
            server_name = tool_config.get('mcp_config_file')

            if not server_name:
                # Try inline config
                inline_config = tool_config.get('mcp_config')
                if inline_config:
                    # Use inline config
                    try:
                        tools = await self.load_server(
                            server_name or tool_name,
                            config=inline_config
                        )
                        loaded_tools.extend(tools)
                    except Exception as e:
                        print(f"⚠️  Failed to load tool '{tool_name}': {e}")
                        continue
            else:
                # Load from discovered server
                try:
                    tools = await self.load_server(server_name)
                    loaded_tools.extend(tools)
                except Exception as e:
                    print(f"⚠️  Failed to load tool '{tool_name}': {e}")
                    continue

        return loaded_tools

    async def load_from_yaml(
        self,
        yaml_path: Union[str, Path],
    ) -> List[BaseTool]:
        """
        Load tools from YAML configuration file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            List of loaded tools
        """
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)

        return await self.load_tools_from_config(config)

    def get_loaded_tools(self) -> List[BaseTool]:
        """
        Get all currently loaded tools.

        Returns:
            List of loaded tools
        """
        return self.loaded_tools

    def get_server_info(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a server.

        Args:
            server_name: Name of the server

        Returns:
            Server configuration dict or None
        """
        return self.servers.get(server_name)

    def list_discovered_servers(self) -> List[str]:
        """
        List all discovered server names.

        Returns:
            List of server names
        """
        return self.discovered_servers

    async def reload_server(
        self,
        server_name: str,
    ) -> List[BaseTool]:
        """
        Reload a specific server.

        Args:
            server_name: Name of the server

        Returns:
            List of loaded tools
        """
        # Remove from loaded tools
        self.loaded_tools = [
            tool for tool in self.loaded_tools
            if not tool.name.startswith(f"{server_name}_")
        ]

        # Remove client
        if server_name in self.clients:
            try:
                await self.clients[server_name].close()
            except:
                pass
            del self.clients[server_name]

        # Reload
        return await self.load_server(server_name)

    async def close_all(self):
        """Close all client connections."""
        for client in self.clients.values():
            try:
                await client.close()
            except:
                pass

        self.clients.clear()
        self.loaded_tools.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the manager.

        Returns:
            Statistics dict
        """
        return {
            'discovered_servers': len(self.discovered_servers),
            'loaded_servers': len(self.clients),
            'loaded_tools': len(self.loaded_tools),
            'servers_dir': str(self.servers_dir),
        }

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (
            f"DynamicMCPManager("
            f"discovered={stats['discovered_servers']}, "
            f"loaded={stats['loaded_servers']}, "
            f"tools={stats['loaded_tools']})"
        )


# Convenience function
async def load_tools_from_yaml(yaml_path: Union[str, Path]) -> List[BaseTool]:
    """
    Convenience function to load tools from YAML config.

    Args:
        yaml_path: Path to YAML configuration file

    Returns:
        List of loaded tools
    """
    manager = DynamicMCPManager()
    return await manager.load_from_yaml(yaml_path)


# Example usage
EXAMPLE_CONFIG = """
# Example YAML configuration for DynamicMCPManager

tools:
  # Using discovered server
  gmail:
    enabled: true
    provider: "mcp_client"
    mcp_config_file: "gmail"

  # Using inline config
  custom_tool:
    enabled: true
    provider: "mcp_client"
    mcp_config:
      type: "stdio"
      command: "npx"
      args: ["-y", "@some/mcp-server"]
      env:
        API_KEY: "your-api-key"

  # Disabled server
  thinking:
    enabled: false
    provider: "mcp_client"
    mcp_config_file: "thinking"

global_mcp_settings:
  retry_attempts: 3
  retry_delay: 1.0
  retry_max_delay: 60.0
"""

if __name__ == "__main__":
    # Example usage
    async def example():
        # Create manager
        manager = DynamicMCPManager()

        # Discover servers
        servers = await manager.discover_servers()
        print(f"Discovered {len(servers)} servers: {servers}")

        # Load tools
        tools = await manager.load_all_tools()
        print(f"Loaded {len(tools)} tools")

        # Show stats
        print(manager.get_stats())

        # Close all
        await manager.close_all()

    # Run example
    asyncio.run(example())
