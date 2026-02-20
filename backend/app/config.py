"""Configuration settings for Learning Finnish API"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # API Configuration
    app_name: str = "Learning Finnish API"
    debug: bool = False
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8000",
        "https://ai-vaerksted.cloud",
    ]

    # Database Configuration
    database_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # Feature Flags
    enable_ai_practice: bool = False
    openai_api_key: Optional[str] = None

    # Optional API key for OpenClaw / external clients (Bearer token)
    finnish_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


# Load settings
settings = Settings()
