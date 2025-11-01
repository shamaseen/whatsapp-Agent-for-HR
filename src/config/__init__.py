"""
Configuration package
"""
from .settings import Settings

# Create global settings instance
settings = Settings()

__all__ = ['settings', 'Settings']
