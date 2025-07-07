"""Worker configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Worker settings."""

    # Environment
    ENVIRONMENT: str = "development"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/secondbrain"

    # Storage
    VAULT_STORAGE_PATH: str = "/app/storage/vaults"

    # Processing
    MAX_CONCURRENT_TASKS: int = 2
    TASK_TIMEOUT: int = 3600  # 1 hour

    # Logging
    LOG_LEVEL: str = "INFO"

    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
