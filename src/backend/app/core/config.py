"""アプリケーション設定"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_env_files() -> list[Path]:
    here = Path(__file__).resolve()
    backend_dir = here.parents[2]  # .../src/backend or /app (in Docker)

    candidates: list[Path] = []

    # Try to get repo root, but handle Docker environment where it doesn't exist
    try:
        repo_root = here.parents[4]  # .../ (repo root)
        for base in (repo_root, backend_dir):
            candidates.append(base / ".env.example")
            candidates.append(base / ".env")
            candidates.append(base / ".env.local")
    except IndexError:
        # Docker environment: only use backend_dir (which is /app)
        candidates.append(backend_dir / ".env.example")
        candidates.append(backend_dir / ".env")
        candidates.append(backend_dir / ".env.local")

    return candidates


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_default_env_files(),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = Field(default="development")
    debug: bool = Field(default=False)
    secret_key: str = Field(...)
    database_url: PostgresDsn = Field(...)
    redis_url: RedisDsn = Field(...)
    google_api_key: str = Field(...)
    wordpress_url: str = Field(...)
    wordpress_username: str = Field(...)
    wordpress_app_password: str = Field(...)
    google_credentials_json: str = Field(...)
    frontend_url: str = Field(default="http://localhost:3000")

    @property
    def async_database_url(self) -> str:
        return str(self.database_url).replace("postgresql://", "postgresql+asyncpg://")


@lru_cache
def get_settings() -> Settings:
    return Settings()