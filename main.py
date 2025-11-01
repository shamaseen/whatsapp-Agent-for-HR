"""
WhatsApp HR Assistant - Main Entry Point
"""
import warnings
import sys

# Suppress known harmless warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="asyncio")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*async_generator.*")
warnings.filterwarnings("ignore", message=".*cancel scope.*")

from src.api.app import create_app
from src.config import settings

# Create FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
