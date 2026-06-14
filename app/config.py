"""
Application Configuration
Loads all environment variables using Pydantic BaseSettings
Type-safe configuration management for the entire application
"""
import os
from pydantic_settings import BaseSettings

# Calculate the directory path of the project root (one level up from this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    """
    Application settings loaded from .env file
    All values have type hints and default fallbacks
    """
    # Database
    DATABASE_URL: str

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    APP_NAME: str = "E-Commerce Inventory API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Pydantic v2 configuration
    model_config = {
        "env_file": ENV_PATH,   # Points directly to the root folder .env file
        "case_sensitive": True  # Environment variables are case-sensitive
    }


# Create global settings instance - import this everywhere
settings = Settings()
