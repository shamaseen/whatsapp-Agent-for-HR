"""
Configuration Generator Utility
Helps create valid MCP server configurations
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class ConfigGenerator:
    """Generate MCP server configuration files"""
    
    @staticmethod
    def stdio_config(
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Generate stdio connection config
        
        Args:
            command: Command to run (e.g., 'npx', 'python', 'node')
            args: Command arguments
            env: Environment variables (optional)
            enabled: Whether server is enabled
        
        Returns:
            Configuration dictionary
        """
        config = {
            "enabled": enabled,
            "type": "stdio",
            "command": command,
            "args": args
        }
        
        if env:
            config["env"] = env
        
        return config
    
    @staticmethod
    def sse_config(
        url: str,
        headers: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Generate SSE connection config (DEPRECATED)
        
        Args:
            url: Server URL
            headers: HTTP headers (optional)
            enabled: Whether server is enabled
        
        Returns:
            Configuration dictionary
        
        Note:
            HTTP+SSE is deprecated. Use streamable_http_config() instead.
        """
        config = {
            "enabled": enabled,
            "type": "sse",
            "url": url
        }
        
        if headers:
            config["headers"] = headers
        
        return config
    
    @staticmethod
    def streamable_http_config(
        url: str,
        headers: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Generate Streamable HTTP connection config (RECOMMENDED for remote)
        
        Args:
            url: Server URL (should end with /mcp or /mcp/)
            headers: HTTP headers for authentication (optional)
            enabled: Whether server is enabled
        
        Returns:
            Configuration dictionary
        """
        config = {
            "enabled": enabled,
            "type": "streamable_http",
            "url": url
        }
        
        if headers:
            config["headers"] = headers
        
        return config
    
    @staticmethod
    def websocket_config(
        url: str,
        headers: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Generate WebSocket connection config (COMMUNITY PROPOSAL)
        
        Args:
            url: WebSocket URL (must start with ws:// or wss://)
            headers: HTTP headers for initial handshake (optional)
            enabled: Whether server is enabled
        
        Returns:
            Configuration dictionary
        """
        config = {
            "enabled": enabled,
            "type": "websocket",
            "url": url
        }
        
        if headers:
            config["headers"] = headers
        
        return config
    
    @staticmethod
    def multi_server_config(
        servers: List[Dict[str, Any]],
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Generate multi-server config
        
        Args:
            servers: List of server configurations
            enabled: Whether multi-server is enabled
        
        Returns:
            Configuration dictionary
        """
        return {
            "enabled": enabled,
            "type": "multi",
            "servers": servers
        }
    
    @staticmethod
    def save_config(
        config: Dict[str, Any],
        server_name: str,
        output_dir: str = "mcp_servers"
    ) -> Path:
        """
        Save configuration to file
        
        Args:
            config: Configuration dictionary
            server_name: Name of the server
            output_dir: Output directory path
        
        Returns:
            Path to saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        file_path = output_path / f"{server_name}.json"
        
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return file_path
    
    @staticmethod
    def validate_and_save(
        config: Dict[str, Any],
        server_name: str,
        output_dir: str = "mcp_servers"
    ) -> tuple[Path, bool, str]:
        """
        Validate and save configuration to file
        
        Args:
            config: Configuration dictionary
            server_name: Name of the server
            output_dir: Output directory path
        
        Returns:
            Tuple of (file_path, is_valid, error_message)
        """
        # Import validation function
        try:
            from .factory import validate_config
            
            # Validate config
            is_valid, error_msg = validate_config(config)
            if not is_valid:
                return None, False, error_msg
            
            # Save if valid
            file_path = ConfigGenerator.save_config(config, server_name, output_dir)
            return file_path, True, ""
            
        except ImportError:
            # If factory not available, just save without validation
            file_path = ConfigGenerator.save_config(config, server_name, output_dir)
            return file_path, True, "Validation skipped (factory not available)"
    
    @staticmethod
    def generate_presets() -> Dict[str, Dict[str, Any]]:
        """
        Generate preset configurations for common MCP servers
        
        Returns:
            Dictionary of preset configurations
        """
        return {
            # Stdio examples (local servers)
            "gmail_stdio": ConfigGenerator.stdio_config(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-gmail"],
                env={"GMAIL_API_KEY": "${GMAIL_API_KEY}"}
            ),
            
            "calendar_stdio": ConfigGenerator.stdio_config(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-calendar"],
                env={"CALENDAR_API_KEY": "${CALENDAR_API_KEY}"}
            ),
            
            "thinking_stdio": ConfigGenerator.stdio_config(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-sequential-thinking"]
            ),
            
            "sheets_stdio": ConfigGenerator.stdio_config(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-google-sheets"],
                env={"SHEETS_API_KEY": "${SHEETS_API_KEY}"}
            ),
            
            "datetime_stdio": ConfigGenerator.stdio_config(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-datetime"]
            ),
            
            "brave_search_stdio": ConfigGenerator.stdio_config(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-brave-search"],
                env={"BRAVE_API_KEY": "${BRAVE_API_KEY}"}
            ),
            
            "filesystem_stdio": ConfigGenerator.stdio_config(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"]
            ),
            
            # Streamable HTTP examples (modern remote servers - RECOMMENDED)
            "weather_streamable_http": ConfigGenerator.streamable_http_config(
                url="http://localhost:8000/mcp/",
                headers={"Authorization": "Bearer ${API_TOKEN}"}
            ),
            
            "stripe_streamable_http": ConfigGenerator.streamable_http_config(
                url="https://mcp.stripe.com/",
                headers={"Authorization": "Bearer ${STRIPE_SECRET_KEY}"}
            ),
            
            "custom_api_streamable_http": ConfigGenerator.streamable_http_config(
                url="https://api.example.com/mcp/",
                headers={
                    "Authorization": "Bearer ${API_TOKEN}",
                    "X-API-Version": "v1"
                }
            ),
            
            # SSE examples (deprecated - use streamable_http instead)
            "gmail_sse_deprecated": ConfigGenerator.sse_config(
                url="http://localhost:3000/gmail",
                headers={"Authorization": "Bearer ${GMAIL_TOKEN}"}
            ),
            
            # WebSocket examples (community proposal)
            "realtime_ws": ConfigGenerator.websocket_config(
                url="wss://realtime.example.com/mcp",
                headers={"Authorization": "Bearer ${WS_TOKEN}"}
            ),
            
            "local_ws": ConfigGenerator.websocket_config(
                url="ws://localhost:9000",
                headers={"X-Client-ID": "${CLIENT_ID}"}
            ),
            
            # Multi-server example
            "multi_example": ConfigGenerator.multi_server_config(
                servers=[
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
                        "name": "thinking",
                        "type": "stdio",
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
                    }
                ]
            )
        }


def generate_all_presets(output_dir: str = "mcp_servers", validate: bool = True):
    """
    Generate all preset configuration files
    
    Args:
        output_dir: Directory to save configs
        validate: Whether to validate configs before saving
    """
    generator = ConfigGenerator()
    presets = generator.generate_presets()
    
    print(f"Generating preset configurations in {output_dir}/")
    print("=" * 60)
    
    success_count = 0
    failed_count = 0
    
    for name, config in presets.items():
        try:
            if validate:
                file_path, is_valid, error_msg = generator.validate_and_save(
                    config, name, output_dir
                )
                if is_valid:
                    print(f"✓ Created: {file_path}")
                    success_count += 1
                else:
                    print(f"✗ Failed: {name} - {error_msg}")
                    failed_count += 1
            else:
                file_path = generator.save_config(config, name, output_dir)
                print(f"✓ Created: {file_path}")
                success_count += 1
                
        except Exception as e:
            print(f"✗ Error creating {name}: {e}")
            failed_count += 1
    
    print("=" * 60)
    print(f"Generated {success_count} configurations successfully")
    if failed_count > 0:
        print(f"Failed to generate {failed_count} configurations")
    print("\nNote: Replace ${VARIABLE} placeholders with actual values")
    print("\nTransport Recommendations:")
    print("  • stdio: For local servers (most common)")
    print("  • streamable_http: For remote servers (recommended)")
    print("  • sse: Deprecated, use streamable_http instead")
    print("  • websocket: Community proposal, limited support")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate MCP server configurations")
    parser.add_argument(
        "--output-dir",
        default="mcp_servers",
        help="Output directory for config files"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation before saving"
    )
    
    args = parser.parse_args()
    
    # Generate all presets
    generate_all_presets(
        output_dir=args.output_dir,
        validate=not args.no_validate
    )
    
    # Example: Create custom configs
    print("\n" + "=" * 60)
    print("Creating custom examples...")
    
    # Custom stdio config
    custom_stdio = ConfigGenerator.stdio_config(
        command="python",
        args=["my_mcp_server.py"],
        env={"API_KEY": "secret", "DEBUG": "true"}
    )
    
    # Custom streamable HTTP config
    custom_http = ConfigGenerator.streamable_http_config(
        url="https://api.myservice.com/mcp/",
        headers={
            "Authorization": "Bearer my-token",
            "X-Custom-Header": "value"
        }
    )
    
    try:
        file_path, is_valid, error_msg = ConfigGenerator().validate_and_save(
            custom_stdio,
            "custom_stdio_server",
            args.output_dir
        )
        if is_valid:
            print(f"✓ Created custom_stdio_server.json")
        else:
            print(f"✗ Validation failed: {error_msg}")
            
        file_path, is_valid, error_msg = ConfigGenerator().validate_and_save(
            custom_http,
            "custom_http_server",
            args.output_dir
        )
        if is_valid:
            print(f"✓ Created custom_http_server.json")
        else:
            print(f"✗ Validation failed: {error_msg}")
    except Exception as e:
        print(f"✗ Error: {e}")