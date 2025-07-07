"""Streamlit app configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Streamlit app settings."""

    # API Configuration
    API_BASE_URL: str = "http://localhost:8000"

    # UI Configuration
    PAGE_TITLE: str = "SecondBrain"
    PAGE_ICON: str = "🧠"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
