from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: str = "./service-account.json"

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

    # Agent Settings
    TEMPERATURE: float = 0.7
    MODEL_NAME: str = "gemini-1.5-pro"
    MAX_MESSAGES_PER_SESSION: int = 5000

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()
