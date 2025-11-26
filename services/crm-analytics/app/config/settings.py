"""
Settings for CRM Analytics Service.
"""

import os
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://valeo_dev:valeo_dev@localhost:5432/valeo_neuro_erp"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/3"

    # Service
    SERVICE_NAME: str = "crm-analytics"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Tenant
    DEFAULT_TENANT_ID: str = "00000000-0000-0000-0000-000000000001"

    # CRM Service URLs (for data aggregation)
    CRM_CORE_BASE_URL: str = "http://localhost:5600"
    CRM_SALES_BASE_URL: str = "http://localhost:5700"
    CRM_SERVICE_BASE_URL: str = "http://localhost:5800"
    CRM_WORKFLOW_BASE_URL: str = "http://localhost:5900"

    # Analytics settings
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    MAX_REPORT_ROWS: int = 10000
    PREDICTIVE_MODEL_UPDATE_INTERVAL: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()