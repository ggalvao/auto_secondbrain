"""CLI configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """CLI settings."""

    # API Configuration
    API_BASE_URL: str = "http://localhost:8000"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Storage (not used by CLI but needed for .env compatibility)
    MAX_VAULT_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Logging
    SQL_DEBUG: bool = False

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
