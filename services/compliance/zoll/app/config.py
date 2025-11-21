"""Konfiguration für den Zoll-/Exportkontroll-Service."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Serviceweite Einstellungen."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ZOLL_", case_sensitive=True)

    HOST: str = "0.0.0.0"
    PORT: int = 5300
    DEBUG: bool = False

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://backend:8000",
    ]

    DATABASE_URL: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        username="valeo_compliance",
        password="valeo_dev_2024!",
        host="postgres-events",
        port="5432",
        path="/valeo_compliance",
    )
    DB_ECHO: bool = False

    EVENT_BUS_ENABLED: bool = True
    EVENT_BUS_URL: str = "nats://nats:4222"
    EVENT_BUS_SUBJECT_PREFIX: str = "compliance.zoll"

    SANCTIONS_DATA_PATH: str = "data/reference/compliance/sanctions.csv"
    CUSTOMS_DUTY_TABLE: str = "data/reference/compliance/duty_rates.csv"
    PREFERENCE_RULES_PATH: str = "data/reference/compliance/preference_rules.yaml"

    WORKFLOW_SERVICE_URL: str = "http://workflow-service:5100"
    WORKFLOW_TENANT: str = "zoll"

    SCREENING_THRESHOLD_BLOCK: float = 0.8
    SCREENING_THRESHOLD_REVIEW: float = 0.4

    SANCTIONS_REFRESH_URL: str = "http://sanctions-service:5200/refresh"
    SANCTIONS_REFRESH_INTERVAL_MINUTES: int = 60
    SANCTIONS_REFRESH_BACKOFF_MINUTES: int = 15
    SANCTIONS_REFRESH_MAX_BACKOFF_MINUTES: int = 720
    WORKFLOW_REGISTRATION_TIMEOUT: float = 300

    OFAC_API_URL: str = "https://api.treasury.gov/ofac/sanctions/list.csv"
    OFAC_API_KEY: str | None = None
    EU_API_URL: str = "https://webgate.ec.europa.eu/api/eu-sanctions"
    EU_API_KEY: str | None = None

    API_URL: AnyHttpUrl = AnyHttpUrl.build(scheme="http", host="localhost", port=8000)
    API_KEY: str = "your_api_key"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
