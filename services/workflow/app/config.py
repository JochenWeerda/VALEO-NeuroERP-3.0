"""
Konfiguration für den Workflow-Service.
"""

from typing import List
from pydantic import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings


def _default_database_url() -> str:
    return str(
        PostgresDsn.build(
            scheme="postgresql",
            username="valeo_dev",
            host="postgres-events",
            port=5432,
            path="/valeo_events",
        )
    )


class Settings(BaseSettings):
    """Serviceweite Einstellungen."""

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 5100
    DEBUG: bool = True

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://backend:8000",
    ]

    # Telemetrie
    METRICS_ENABLED: bool = True

    # Datenbank
    DATABASE_URL: str = _default_database_url()

    # Eventbus (NATS)
    EVENT_BUS_ENABLED: bool = True
    EVENT_BUS_URL: str = "nats://nats:4222"
    EVENT_BUS_SUBJECT_PREFIX: str = "workflow"

    # Mandantenfähigkeit
    DEFAULT_TENANT: str = "default"

    # RAG Integration
    RAG_GATEWAY_URL: str = "http://ai-service:5000/api/v1/rag/query"
    RAG_ENABLED: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()



