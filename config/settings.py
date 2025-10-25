from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import field_validator

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: str = "./client_secret.json"
    
    # Chatwoot API (Optional - for Chatwoot integration)
    CHATWOOT_API_URL: Optional[str] = None
    CHATWOOT_API_KEY: Optional[str] = None
    
    # Evolution API (Optional - for direct Evolution API integration)
    EVOLUTION_API_URL: Optional[str] = None
    EVOLUTION_API_KEY: Optional[str] = None
    EVOLUTION_INSTANCE_NAME: Optional[str] = None
    
    # Database
    DATABASE_URL: str
    
    # Google Drive
    CV_FOLDER_ID: str
    SHEETS_FOLDER_ID: str
    
    # Webex (using Client ID and Secret instead of Access Token)
    WEBEX_CLIENT_ID: Optional[str] = None
    WEBEX_CLIENT_SECRET: Optional[str] = None
    WEBEX_ACCESS_TOKEN: Optional[str] = None
    
    # App Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Agent Settings
    TEMPERATURE: float = 0.7
    MODEL_NAME: str = "gemini-1.5-pro"
    MAX_REVISIONS: int = 2
    CONTEXT_WINDOW: int = 1
    MAX_MESSAGES_PER_SESSION: int = 5000

    # Tool Mode: "mcp", "mcp_client", or "direct"
    # - "mcp": Use MCP protocol with execute_tool wrapper (recommended)
    # - "mcp_client": Use MCP client for external MCP servers (advanced)
    # - "direct": Use traditional LangChain tools directly (legacy)
    TOOL_MODE: str = "mcp"

    # MCP Client Configuration (only used when TOOL_MODE="mcp_client")
    MCP_SERVER_URL: Optional[str] = None
    MCP_SERVER_TRANSPORT: str = "stdio"  # "stdio" or "sse"

    # Legacy Tool/MCP Mode Configuration (deprecated, use TOOL_MODE instead)
    GMAIL_MODE: str = "tool"
    CALENDAR_MODE: str = "tool"
    SHEETS_MODE: str = "tool"
    DATETIME_MODE: str = "tool"
    THINKING_MODE: str = "mcp"
    WEBEX_MODE: str = "tool"
    CV_MODE: str = "tool"
    
    # MCP Server URLs
    MCP_GMAIL_SERVER_URL: Optional[str] = None
    MCP_CALENDAR_SERVER_URL: Optional[str] = None
    MCP_SHEETS_SERVER_URL: Optional[str] = None
    MCP_DATETIME_SERVER_URL: Optional[str] = None
    
    @field_validator('*', mode='before')
    @classmethod
    def strip_comments(cls, v):
        """Remove inline comments from .env values"""
        if isinstance(v, str) and '#' in v:
            return v.split('#')[0].strip()
        return v
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()