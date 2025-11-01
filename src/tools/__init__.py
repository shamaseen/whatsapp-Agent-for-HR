from .loader import ToolLoader
from .registry import ToolRegistry, get_registry

# Backwards-compatibility aliases for legacy notebook imports
ToolDiscovery = ToolRegistry
ToolInspector = ToolRegistry


