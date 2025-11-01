"""
MCP Client Factory
Creates appropriate MCP client based on configuration
"""

from typing import Dict, Any
from .base import BaseMCPClient

# Note: streamable_http and multi_server not in new structure
# Add them if needed


def create_mcp_client(server_name: str, config: Dict[str, Any]) -> BaseMCPClient:
    """
    Factory function to create appropriate MCP client based on config type
    
    Args:
        server_name: Name of the MCP server
        config: Configuration dictionary with 'type' field
    
    Returns:
        Appropriate BaseMCPClient implementation
    
    Raises:
        ValueError: If config type is unknown or invalid
    
    Supported types:
        - stdio: Local subprocess communication (most common)
        - streamable_http: Modern HTTP transport (recommended for remote)
        - sse: HTTP+SSE (deprecated, use streamable_http)
        - websocket: WebSocket transport (community proposal)
        - multi: Multiple servers simultaneously
    """
    client_type = config.get("type", "stdio").lower()
    
    if client_type == "stdio":
        from .stdio import StdioMCPClient
        return StdioMCPClient(server_name, config)
    
    elif client_type == "sse":
        # Legacy HTTP+SSE transport (deprecated)
        print(f"   ⚠️  Warning: HTTP+SSE transport is deprecated. Consider using 'streamable_http' instead.")
        from .sse import SSEMCPClient
        return SSEMCPClient(server_name, config)
    
    elif client_type in ["streamable_http", "http", "streamable-http"]:
        from .streamable_http_client import StreamableHTTPMCPClient
        return StreamableHTTPMCPClient(server_name, config)
    
    elif client_type in ["websocket", "ws", "wss"]:
        from .websocket import WebSocketMCPClient
        return WebSocketMCPClient(server_name, config)
    
    elif client_type == "multi":
        from .multi_server_client import MultiServerMCPClient
        return MultiServerMCPClient(server_name, config)
    
    else:
        raise ValueError(
            f"Unknown MCP client type: '{client_type}'. "
            f"Supported types: stdio, streamable_http (recommended), sse (deprecated), websocket, multi"
        )


def validate_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate MCP server configuration
    
    Args:
        config: Configuration dictionary to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    client_type = config.get("type", "stdio").lower()
    
    # Check if type is supported
    supported_types = ["stdio", "sse", "streamable_http", "streamable-http", "http", "websocket", "ws", "wss", "multi"]
    if client_type not in supported_types:
        return False, f"Unsupported type: '{client_type}'. Supported: {', '.join(set(['stdio', 'streamable_http', 'sse', 'websocket', 'multi']))}"
    
    # Validate stdio config
    if client_type == "stdio":
        if "command" not in config:
            return False, "stdio config requires 'command' field"
        if "args" not in config:
            return False, "stdio config requires 'args' field"
        if not isinstance(config["args"], list):
            return False, "'args' must be a list"
    
    # Validate SSE config
    elif client_type == "sse":
        if "url" not in config:
            return False, "sse config requires 'url' field"
        if not config["url"].startswith(("http://", "https://")):
            return False, "'url' must start with http:// or https://"
    
    # Validate Streamable HTTP config
    elif client_type in ["streamable_http", "streamable-http", "http"]:
        if "url" not in config:
            return False, "streamable_http config requires 'url' field"
        if not config["url"].startswith(("http://", "https://")):
            return False, "'url' must start with http:// or https://"
    
    # Validate WebSocket config
    elif client_type in ["websocket", "ws", "wss"]:
        if "url" not in config:
            return False, "websocket config requires 'url' field"
        if not config["url"].startswith(("ws://", "wss://")):
            return False, "'url' must start with ws:// or wss://"
    
    # Validate multi-server config
    elif client_type == "multi":
        if "servers" not in config:
            return False, "multi config requires 'servers' field"
        if not isinstance(config["servers"], list):
            return False, "'servers' must be a list"
        if len(config["servers"]) == 0:
            return False, "'servers' list cannot be empty"
        
        # Validate each sub-server config
        for i, server_config in enumerate(config["servers"]):
            if "name" not in server_config:
                return False, f"Server {i} missing 'name' field"
            
            # Recursively validate sub-server config
            is_valid, error = validate_config(server_config)
            if not is_valid:
                return False, f"Server '{server_config.get('name', i)}': {error}"
    
    return True, ""


# Configuration examples for documentation
EXAMPLE_CONFIGS = {
    "stdio_npx": {
        "enabled": True,
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-gmail"],
        "env": {"GMAIL_API_KEY": "your-api-key"}
    },
    
    "stdio_python": {
        "enabled": True,
        "type": "stdio",
        "command": "python",
        "args": ["path/to/server.py"],
        "env": {"DEBUG": "true"}
    },
    
    "streamable_http": {
        "enabled": True,
        "type": "streamable_http",
        "url": "https://api.example.com/mcp/",
        "headers": {
            "Authorization": "Bearer your-token",
            "Content-Type": "application/json"
        }
    },
    
    "sse_http_deprecated": {
        "enabled": True,
        "type": "sse",
        "url": "http://localhost:3000/mcp",
        "headers": {
            "Authorization": "Bearer your-token",
            "Content-Type": "application/json"
        }
    },
    
    "websocket": {
        "enabled": True,
        "type": "websocket",
        "url": "wss://realtime.example.com/mcp",
        "headers": {
            "Authorization": "Bearer your-token"
        }
    },
    
    "multi_server": {
        "enabled": True,
        "type": "multi",
        "servers": [
            {
                "name": "gmail",
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-gmail"]
            },
            {
                "name": "weather",
                "type": "streamable_http",
                "url": "http://localhost:8000/mcp/"
            },
            {
                "name": "realtime",
                "type": "websocket",
                "url": "ws://localhost:9000"
            }
        ]
    }
}