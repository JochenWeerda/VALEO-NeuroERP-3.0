"""
Settings for CRM Service.
"""

from typing import Optional

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


def _default_database_url() -> str:
    return str(
        PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username="valeo_dev",
            host="localhost",
            port=5432,
            path="/valeo_neuro_erp",
        )
    )


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = Field(default_factory=_default_database_url)

    # Service
    SERVICE_NAME: str = Field(default="crm-service")
    DEBUG: bool = Field(default=False)

    # CORS
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    # Tenant
    DEFAULT_TENANT_ID: str = Field(default="00000000-0000-0000-0000-000000000001")

    # Event Bus (future use)
    EVENT_BUS_URL: Optional[str] = Field(default=None)

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()

