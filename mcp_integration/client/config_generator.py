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
        Generate SSE connection config
        
        Args:
            url: Server URL
            headers: HTTP headers (optional)
            enabled: Whether server is enabled
        
        Returns:
            Configuration dictionary
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
    def generate_presets() -> Dict[str, Dict[str, Any]]:
        """
        Generate preset configurations for common MCP servers
        
        Returns:
            Dictionary of preset configurations
        """
        return {
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
            
            "gmail_sse": ConfigGenerator.sse_config(
                url="http://localhost:3000/gmail",
                headers={"Authorization": "Bearer ${GMAIL_TOKEN}"}
            ),
            
            "multi_example": ConfigGenerator.multi_server_config(
                servers=[
                    {
                        "name": "gmail",
                        "type": "stdio",
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-gmail"]
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


def generate_all_presets(output_dir: str = "mcp_servers"):
    """
    Generate all preset configuration files
    
    Args:
        output_dir: Directory to save configs
    """
    generator = ConfigGenerator()
    presets = generator.generate_presets()
    
    print(f"Generating preset configurations in {output_dir}/")
    print("=" * 60)
    
    for name, config in presets.items():
        file_path = generator.save_config(config, name, output_dir)
        print(f"✓ Created: {file_path}")
    
    print("=" * 60)
    print(f"Generated {len(presets)} preset configurations")
    print("\nNote: Replace ${VARIABLE} placeholders with actual values")


if __name__ == "__main__":
    # Generate all presets
    generate_all_presets()
    
    # Example: Create custom config
    custom_config = ConfigGenerator.stdio_config(
        command="python",
        args=["my_mcp_server.py"],
        env={"API_KEY": "secret"}
    )
    
    ConfigGenerator.save_config(custom_config, "custom_server")
    print("\n✓ Created custom_server.json")
