"""
Settings for CRM Communication Service.
"""

import os
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://valeo_dev:valeo_dev@localhost:5432/valeo_neuro_erp"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/5"

    # Service
    SERVICE_NAME: str = "crm-communication"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Tenant
    DEFAULT_TENANT_ID: str = "00000000-0000-0000-0000-000000000001"

    # SMTP Configuration
    SMTP_SERVER: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: Optional[str] = "VALEO CRM"

    # IMAP Configuration (for inbound emails)
    IMAP_SERVER: Optional[str] = None
    IMAP_PORT: int = 993
    IMAP_USERNAME: Optional[str] = None
    IMAP_PASSWORD: Optional[str] = None
    IMAP_USE_SSL: bool = True

    # Email Processing
    EMAIL_BATCH_SIZE: int = 50
    EMAIL_POLL_INTERVAL: int = 300  # 5 minutes
    MAX_ATTACHMENT_SIZE: int = 10485760  # 10MB

    # CRM Service URLs (for context enrichment)
    CRM_CORE_BASE_URL: str = "http://localhost:5600"
    CRM_SALES_BASE_URL: str = "http://localhost:5700"
    CRM_SERVICE_BASE_URL: str = "http://localhost:5800"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()