"""
config.py — Application settings loaded from .env file.
Uses Pydantic BaseSettings for type-safe environment variable management.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    All values can be overridden via a .env file in the project root.
    """

    # GitHub API credentials
    GITHUB_USERNAME: str = Field(default="sajeerrr", description="GitHub username to fetch data for")
    GITHUB_TOKEN: str = Field(default="", description="GitHub Personal Access Token for API auth")

    # Cache configuration
    CACHE_TTL_SECONDS: int = Field(default=21600, description="Cache time-to-live in seconds (default: 6 hours)")

    # Server configuration
    PORT: int = Field(default=8000, description="Port to run the uvicorn server on")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton settings instance — import this wherever config is needed
settings = Settings()
