"""
Settings for CRM Sales service.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://valeo_dev:valeo_dev@localhost:5432/valeo_neuro_erp"
    )

    # Service
    SERVICE_NAME: str = Field(default="crm-sales")
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
