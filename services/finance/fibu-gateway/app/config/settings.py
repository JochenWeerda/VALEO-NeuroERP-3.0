"""Pydantic Settings für den FiBu-Gateway."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Konfiguration für das Gateway."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FIBUGW_",
        case_sensitive=True,
        extra="ignore",
    )

    HOST: str = "0.0.0.0"
    PORT: int = 8600
    DEBUG: bool = False

    DEFAULT_TENANT: str = "default"
    DEFAULT_CURRENCY: str = "EUR"
    JOURNAL_APPROVAL_THRESHOLD_EUR: float = 1000.0

    # Während Phase 0 bündeln alle FiBu-Endpunkte der neue Python-Service
    FIBU_CORE_URL: AnyHttpUrl = "http://finance-service:8003"
    FIBU_MASTER_DATA_URL: AnyHttpUrl = "http://finance-service:8003"
    FIBU_OP_URL: AnyHttpUrl = "http://finance-service:8003"

    HTTP_TIMEOUT_SECONDS: float = 10.0

    EVENT_BUS_ENABLED: bool = True
    EVENT_BUS_URL: str = "nats://nats:4222"
    EVENT_BUS_SUBJECT_BOOKING_CREATED: str = "fibu.booking.created"

    APPROVAL_RULES_DB_PATH: str = "./data/approval_rules.db"

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://frontend:3000",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

