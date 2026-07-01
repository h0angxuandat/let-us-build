"""Runtime settings, loaded from environment (prefix ``LUB_``) or a .env file."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core configuration. Secrets come from env only (never committed)."""

    model_config = SettingsConfigDict(env_prefix="LUB_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8300
    web_port: int = 8301
    database_url: str = "postgresql+asyncpg://lub:lub@127.0.0.1:5432/letusbuild"
    default_provider: str = "anthropic"
    default_model: str = "claude-opus-4-8"
    seed_on_startup: bool = True
    cors_origins: list[str] = ["http://localhost:8301", "http://127.0.0.1:8301"]


def get_settings() -> Settings:
    return Settings()
