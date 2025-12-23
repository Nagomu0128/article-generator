"""アプリケーション設定"""
from functools import lru_cache
from typing import Optional
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_env: str = Field(default="development")
    debug: bool = Field(default=False)
    secret_key: str = Field(...)
    database_url: PostgresDsn = Field(...)
    redis_url: RedisDsn = Field(...)
    anthropic_api_key: str = Field(...)
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