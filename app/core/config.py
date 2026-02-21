from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "dev"
    api_v1_prefix: str = "/api/v1"
    klug_api_key: str | None = None
    klug_api_auth_mode: Literal["disabled", "write", "all"] = "write"
    klug_session_password: str | None = None
    klug_session_secret: str | None = None
    klug_session_ttl_seconds: int = 60 * 60 * 24 * 30
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/klug_media"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
