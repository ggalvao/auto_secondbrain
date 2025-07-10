"""Worker configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Worker settings."""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/secondbrain"

    # Storage
    VAULT_STORAGE_PATH: str = "./storage/vaults"
    MAX_VAULT_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Processing
    MAX_CONCURRENT_TASKS: int = 2
    TASK_TIMEOUT: int = 3600  # 1 hour

    # Logging
    LOG_LEVEL: str = "INFO"
    SQL_DEBUG: bool = False

    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Streamlit
    API_BASE_URL: str = "http://localhost:8000"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
