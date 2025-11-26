"""CRM Core service settings."""

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CRM_CORE_", case_sensitive=False)

    HOST: str = "0.0.0.0"
    PORT: int = 5600
    DEBUG: bool = True

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:4001",
        "http://localhost:5174",
    ]

    DATABASE_URL: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        username="valeo_dev",
        password="valeo_dev_2024!",
        host="postgres",
        port=5432,
        path="/valeo_neuro_erp",
    )
    DB_ECHO: bool = False

    DEFAULT_TENANT_ID: str = "00000000-0000-0000-0000-000000000001"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
