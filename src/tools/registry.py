"""
Tool Registry - Auto-discovers and catalogs available tools
Scans for:
- Internal tools from src/tools/**/*_mcp.py and *_tools.py
- External MCP servers from config/mcp_servers/*.json

Tools are organized by category:
- src/tools/google/ - Gmail, Calendar, CV tools
- src/tools/communication/ - Webex, messaging tools
- src/tools/utilities/ - DateTime, helpers
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util
import inspect

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Discovers and catalogs all available tools
    - Internal tools from src/tools/**/*_mcp.py and *_tools.py (organized by category)
    - External MCP servers from config/mcp_servers/*.json
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize tool registry

        Args:
            base_path: Base path to project (default: auto-detect)
        """
        if base_path is None:
            # Auto-detect: go up from this file to project root
            # We're in src/tools/registry.py, so go up 2 levels to project root
            base_path = Path(__file__).parent.parent.parent

        self.base_path = Path(base_path)
        # New flat structure: tools are right here in src/tools/
        self.tools_dir = self.base_path / "src" / "tools"
        self.servers_dir = self.base_path / "config" / "mcp_servers"

        self._internal_tools: Dict[str, Any] = {}
        self._external_servers: Dict[str, Any] = {}
        self._discovered = False

    def discover(self) -> None:
        """Discover all available tools"""
        if self._discovered:
            return

        logger.info("🔍 Discovering available tools...")
        self._discover_internal_tools()
        self._discover_external_servers()
        self._discovered = True

        logger.info(f"✅ Discovery complete: {len(self._internal_tools)} internal, "
                   f"{len(self._external_servers)} external")

    def _discover_internal_tools(self) -> None:
        """Discover internal tools from Python files in category subdirectories"""
        if not self.tools_dir.exists():
            logger.warning(f"Tools directory not found: {self.tools_dir}")
            return

        logger.info(f"   📦 Scanning for internal tools in {self.tools_dir}")

        # Find all *_mcp.py and *_tools.py files in subdirectories
        mcp_files = list(self.tools_dir.rglob("*_mcp.py"))
        tools_files = list(self.tools_dir.rglob("*_tools.py"))
        all_tool_files = mcp_files + tools_files

        logger.info(f"   Found {len(all_tool_files)} tool files ({len(mcp_files)} MCP, {len(tools_files)} LangChain)")

        for file_path in all_tool_files:
            try:
                self._register_internal_tool(file_path)
            except Exception as e:
                logger.error(f"   ❌ Error processing {file_path.name}: {e}")
                import traceback
                logger.debug(traceback.format_exc())

    def _register_internal_tool(self, file_path: Path) -> None:
        """Register an internal tool from a Python file"""
        # Convert file path to module path
        rel_path = file_path.relative_to(self.base_path)
        module_path = str(rel_path.with_suffix('')).replace('/', '.')

        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(module_path, file_path)
            if spec is None or spec.loader is None:
                return

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find all MCPTool subclasses
            from src.mcp_integration.protocol import MCPTool

            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Skip the base class itself
                if obj is MCPTool:
                    continue

                # Check if it's a subclass of MCPTool
                if issubclass(obj, MCPTool) and obj.__module__ == module_path:
                    # Get tool metadata
                    try:
                        instance = obj()
                        tool_name = instance.get_name()

                        # Register the tool
                        if tool_name not in self._internal_tools:
                            self._internal_tools[tool_name] = {
                                "class_path": f"{module_path}.{name}",
                                "class_name": name,
                                "file_path": str(file_path),
                                "description": instance.get_description(),
                                "category": self._get_category(file_path)
                            }
                            logger.info(f"   ✓ Registered internal tool: {tool_name} ({name})")
                        else:
                            # Handle multiple tools with same name (e.g., cv_processing)
                            # Store as list
                            existing = self._internal_tools[tool_name]
                            if isinstance(existing, dict) and "class_path" in existing:
                                # Convert to list
                                self._internal_tools[tool_name] = {
                                    "tools": [existing, {
                                        "class_path": f"{module_path}.{name}",
                                        "class_name": name,
                                        "file_path": str(file_path),
                                        "description": instance.get_description(),
                                        "category": self._get_category(file_path)
                                    }],
                                    "category": existing["category"]
                                }
                            elif "tools" in existing:
                                # Add to existing list
                                existing["tools"].append({
                                    "class_path": f"{module_path}.{name}",
                                    "class_name": name,
                                    "file_path": str(file_path),
                                    "description": instance.get_description(),
                                    "category": self._get_category(file_path)
                                })
                            logger.info(f"   ✓ Added to multi-tool: {tool_name} ({name})")

                    except Exception as e:
                        logger.debug(f"   Could not instantiate {name}: {e}")

        except Exception as e:
            logger.debug(f"   Could not load module {module_path}: {e}")

    def _get_category(self, file_path: Path) -> str:
        """Extract category from file path"""
        # Get parent directory relative to tools dir
        try:
            rel_path = file_path.parent.relative_to(self.tools_dir)
            return str(rel_path.parts[0]) if rel_path.parts else "utilities"
        except ValueError:
            return "utilities"

    def _discover_external_servers(self) -> None:
        """Discover external MCP server configurations"""
        if not self.servers_dir.exists():
            logger.warning(f"Servers directory not found: {self.servers_dir}")
            return

        logger.info(f"   🌐 Scanning for external MCP servers in {self.servers_dir}")

        # Find all .json files
        json_files = list(self.servers_dir.glob("*.json"))
        logger.info(f"   Found {len(json_files)} server config files")

        for file_path in json_files:
            try:
                self._register_external_server(file_path)
            except Exception as e:
                logger.error(f"   ❌ Error processing {file_path.name}: {e}")

    def _register_external_server(self, file_path: Path) -> None:
        """Register an external MCP server from JSON config"""
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)

            # Get server name from file name (without .json)
            server_name = file_path.stem

            # Check if enabled (default to true if not specified)
            if not config.get("enabled", True):
                logger.info(f"   ⏭️  Skipping disabled server: {server_name}")
                return

            # Register the server
            self._external_servers[server_name] = {
                "config_file": file_path.name,
                "config_path": str(file_path),
                "transport": config.get("transport", config.get("type", "unknown")),
                "command": config.get("command", ""),
                "description": config.get("description", f"External MCP server: {server_name}"),
                "enabled": config.get("enabled", True)
            }

            logger.info(f"   ✓ Registered external server: {server_name} "
                       f"({self._external_servers[server_name]['transport']})")

        except json.JSONDecodeError as e:
            logger.error(f"   ❌ Invalid JSON in {file_path.name}: {e}")
        except Exception as e:
            logger.error(f"   ❌ Error loading {file_path.name}: {e}")

    def get_internal_tools(self) -> Dict[str, Any]:
        """Get all discovered internal tools"""
        if not self._discovered:
            self.discover()
        return self._internal_tools.copy()

    def get_external_servers(self) -> Dict[str, Any]:
        """Get all discovered external servers"""
        if not self._discovered:
            self.discover()
        return self._external_servers.copy()

    def get_all_tools(self) -> Dict[str, Any]:
        """Get all tools with their available providers"""
        if not self._discovered:
            self.discover()

        all_tools = {}

        # Add internal tools
        for name, info in self._internal_tools.items():
            all_tools[name] = {
                "name": name,
                "providers": ["internal_mcp"],
                "internal": info,
                "external": None
            }

        # Add external servers
        for name, info in self._external_servers.items():
            if name in all_tools:
                # Tool available via both internal and external
                all_tools[name]["providers"].append("mcp_client")
                all_tools[name]["external"] = info
            else:
                # Only available via external
                all_tools[name] = {
                    "name": name,
                    "providers": ["mcp_client"],
                    "internal": None,
                    "external": info
                }

        return all_tools

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        all_tools = self.get_all_tools()
        return all_tools.get(tool_name)

    def is_tool_available(self, tool_name: str, provider: str = None) -> bool:
        """
        Check if a tool is available

        Args:
            tool_name: Name of the tool
            provider: Optional provider type ("internal_mcp" or "mcp_client")

        Returns:
            True if tool is available
        """
        tool_info = self.get_tool_info(tool_name)
        if not tool_info:
            return False

        if provider is None:
            return True

        return provider in tool_info["providers"]

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of discovered tools"""
        if not self._discovered:
            self.discover()

        all_tools = self.get_all_tools()

        # Count by provider availability
        internal_only = sum(1 for t in all_tools.values() if t["providers"] == ["internal_mcp"])
        external_only = sum(1 for t in all_tools.values() if t["providers"] == ["mcp_client"])
        both = sum(1 for t in all_tools.values() if len(t["providers"]) > 1)

        # Group internal tools by category
        categories = {}
        for name, info in self._internal_tools.items():
            if isinstance(info, dict) and "category" in info:
                category = info["category"]
            else:
                category = "utilities"

            if category not in categories:
                categories[category] = []
            categories[category].append(name)

        return {
            "total_tools": len(all_tools),
            "internal_tools": len(self._internal_tools),
            "external_servers": len(self._external_servers),
            "availability": {
                "internal_only": internal_only,
                "external_only": external_only,
                "both_providers": both
            },
            "categories": categories,
            "tools": all_tools
        }

    def print_summary(self) -> None:
        """Print a human-readable summary"""
        summary = self.get_summary()

        print("\n" + "="*80)
        print("TOOL REGISTRY SUMMARY")
        print("="*80)
        print(f"\nTotal Tools: {summary['total_tools']}")
        print(f"  • Internal implementations: {summary['internal_tools']}")
        print(f"  • External MCP servers: {summary['external_servers']}")
        print(f"\nAvailability:")
        print(f"  • Internal only: {summary['availability']['internal_only']}")
        print(f"  • External only: {summary['availability']['external_only']}")
        print(f"  • Both providers: {summary['availability']['both_providers']}")

        print(f"\nCategories:")
        for category, tools in summary['categories'].items():
            print(f"  • {category}: {len(tools)} tool(s)")
            for tool in sorted(tools):
                print(f"    - {tool}")

        print(f"\nAll Available Tools:")
        for name, info in sorted(summary['tools'].items()):
            providers = ", ".join(info['providers'])
            print(f"  • {name} ({providers})")

        print("\n" + "="*80)


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get global tool registry instance"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
        _registry.discover()
    return _registry


# Convenience functions
def get_internal_tools() -> Dict[str, Any]:
    """Get all internal tools"""
    return get_registry().get_internal_tools()


def get_external_servers() -> Dict[str, Any]:
    """Get all external servers"""
    return get_registry().get_external_servers()


def get_all_tools() -> Dict[str, Any]:
    """Get all tools"""
    return get_registry().get_all_tools()


def is_tool_available(tool_name: str, provider: str = None) -> bool:
    """Check if tool is available"""
    return get_registry().is_tool_available(tool_name, provider)


# CLI usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    registry = ToolRegistry()
    registry.discover()
    registry.print_summary()
