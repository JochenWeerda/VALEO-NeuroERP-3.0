"""Konfiguration für den InfraStat-Service."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Serviceweite Einstellungen."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="INFRASTAT_", case_sensitive=True)

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 5200
    DEBUG: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://backend:8000",
    ]

    # Datenbank
    DATABASE_URL: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        username="valeo_compliance",
        password="valeo_dev_2024!",
        host="postgres-events",
        port="5432",
        path="/valeo_compliance",
    )
    DB_ECHO: bool = False

    # Eventbus
    EVENT_BUS_ENABLED: bool = True
    EVENT_BUS_URL: str = "nats://nats:4222"
    EVENT_BUS_SUBJECT_PREFIX: str = "compliance.infrastat"

    # Mandantenfähigkeit
    DEFAULT_TENANT: str = "default"

    # Scheduler
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_CRON: str = "0 6 10 * *"  # 10. des Monats 06:00 UTC

    # Referenzdaten
    TARIC_DATA_PATH: str = "data/reference/intrastat/taric.csv"
    COUNTRY_CODES_PATH: str = "data/reference/common/country_codes.csv"

    # Workflow-Service
    WORKFLOW_SERVICE_URL: str = "http://workflow-service:5100"
    WORKFLOW_REGISTRATION_TIMEOUT: float = 10.0

    # Submission
    SUBMISSION_ENABLED: bool = False
    SUBMISSION_BASE_URL: str = "https://www-idev.destatis.de/idev"
    SUBMISSION_USERNAME: str | None = None
    SUBMISSION_PASSWORD: str | None = None
    SUBMISSION_CLIENT_CERT: str | None = None
    SUBMISSION_CLIENT_KEY: str | None = None
    SUBMISSION_VERIFY_SSL: bool = True
    SUBMISSION_RETRY_ATTEMPTS: int = 3
    SUBMISSION_RETRY_DELAY_SECONDS: int = 10


@lru_cache
def get_settings() -> Settings:
    """Singleton für Settings."""

    return Settings()


settings = get_settings()

