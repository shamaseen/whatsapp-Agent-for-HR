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
    WEBEX_REDIRECT_URI: Optional[str] = None
    
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

    # Tool Mode Configuration
    # - "mcp": Use internal MCP protocol tools (recommended for production)
    # - "mcp_client": Use external MCP servers via JSON configs (advanced)
    # - "direct": Use direct LangChain tools (legacy, not recommended)
    TOOL_MODE: str = "dynamic"

    # MCP Client Configuration (used when TOOL_MODE="mcp_client")
    # Server configurations are defined in: config/mcp_servers/*.json
    # Each JSON file specifies:
    #   - "transport": "stdio" (for NPM packages) or "sse" (for HTTP servers)
    #   - "command", "args", "env" for stdio
    #   - "url", "headers" for SSE
    # Example servers: gmail.json, calendar.json, datetime.json, thinking.json
    MCP_SERVER_URL: Optional[str] = None  # Optional: URL for single external MCP server

    # Agent Configuration
    # - "simple_react": Simple ReAct agent (LangChain)
    # - "complex_langgraph": Complex LangGraph agent with reflection
    # Note: Use "complex_langgraph" for production, "simple_react" for simple tasks
    AGENT_TYPE: str = "complex_langgraph"

    # Memory Configuration
    # - "buffer": Simple conversation buffer (LangChain)
    # - "summary": Conversation summary (LangChain)
    # - "postgres": PostgreSQL checkpointer (LangGraph)
    # - "sqlite": SQLite checkpointer (LangGraph)
    # - "memory": In-memory checkpointer (LangGraph)
    # - "openmemory": OpenMemory integration
    MEMORY_TYPE: str = "postgres"

    # OpenMemory Configuration (when MEMORY_TYPE="openmemory")
    OPENMEMORY_URL: Optional[str] = None
    OPENMEMORY_API_KEY: Optional[str] = None
    
    @field_validator('*', mode='before')
    @classmethod
    def strip_comments(cls, v):
        """Remove inline comments from .env values"""
        if v is not None and isinstance(v, str) and '#' in v:
            return v.split('#')[0].strip()
        return v
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()