"""
Konfiguration für den Workflow-Service.
"""

from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Serviceweite Einstellungen."""

    ***REMOVED*** Server
    HOST: str = "0.0.0.0"
    PORT: int = 5100
    DEBUG: bool = True

    ***REMOVED*** CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://backend:8000",
    ]

    ***REMOVED*** Telemetrie
    METRICS_ENABLED: bool = True

    ***REMOVED*** Datenbank
    DATABASE_URL: str = "postgresql://valeo_dev:REDACTED_PASSWORD@postgres-events:5432/valeo_events"

    ***REMOVED*** Eventbus (NATS)
    EVENT_BUS_ENABLED: bool = True
    EVENT_BUS_URL: str = "nats://nats:4222"
    EVENT_BUS_SUBJECT_PREFIX: str = "workflow"

    ***REMOVED*** Mandantenfähigkeit
    DEFAULT_TENANT: str = "default"

    ***REMOVED*** RAG Integration
    RAG_GATEWAY_URL: str = "http://ai-service:5000/api/v1/rag/query"
    RAG_ENABLED: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()


