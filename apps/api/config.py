"""Configuration settings for the API application."""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/secondbrain"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    VAULT_STORAGE_PATH: str = "./storage/vaults"
    MAX_VAULT_SIZE: int = 100 * 1024 * 1024  # 100MB

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8000",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    SQL_DEBUG: bool = False

    # API Keys (optional)
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Streamlit
    API_BASE_URL: str = "http://localhost:8000"

    class Config:
        """Pydantic configuration for settings."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
