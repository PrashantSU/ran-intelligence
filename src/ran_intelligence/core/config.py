"""Central application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "RAN Intelligence Platform"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./ran_intelligence.db"

    model_device: str = "cpu"

    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
