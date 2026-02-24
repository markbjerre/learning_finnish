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
    port: int = 8001

    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:8001",
        "https://ai-vaerksted.cloud",
    ]

    # Database Configuration
    database_url: Optional[str] = None
    finnish_db_password: Optional[str] = None
    finnish_db_host: str = "dobbybrain"
    use_sqlite: bool = False  # When True, force SQLite (ignores database_url)
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
_settings = Settings()
# When FINNISH_DB_PASSWORD is set, use homelab URL (overrides database_url unless use_sqlite)
if _settings.use_sqlite:
    _settings.database_url = None
elif _settings.finnish_db_password:
    _settings.database_url = f"postgresql+asyncpg://learning_finnish:{_settings.finnish_db_password}@{_settings.finnish_db_host}:5433/learning_finnish"
settings = _settings
