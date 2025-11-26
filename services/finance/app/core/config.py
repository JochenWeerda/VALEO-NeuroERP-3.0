"""Zentrale Konfiguration für den Finance-Service."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic Settings für Infrastruktur & Business Defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FINANCE_",
        case_sensitive=False,
        extra="ignore",
    )

    HOST: str = "0.0.0.0"
    PORT: int = 8003
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./finance.db"
    DEFAULT_TENANT: str = "default"
    DEFAULT_CURRENCY: str = "EUR"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        AnyHttpUrl("http://localhost:3000"),
        AnyHttpUrl("http://frontend:3000"),
    ]

    PROMETHEUS_NAMESPACE: str = "finance_service"
    LOG_LEVEL: str = Field(default="INFO", alias="FINANCE_LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

