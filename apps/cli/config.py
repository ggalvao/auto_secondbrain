from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """CLI settings."""

    # API Configuration
    API_BASE_URL: str = "http://localhost:8000"

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
