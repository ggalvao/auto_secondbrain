"""Streamlit app configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Streamlit app settings."""

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }

    # API Configuration
    API_BASE_URL: str = "http://localhost:8000"

    # UI Configuration
    PAGE_TITLE: str = "SecondBrain"
    PAGE_ICON: str = "🧠"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Storage
    MAX_VAULT_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Logging
    SQL_DEBUG: bool = False


settings = Settings()
