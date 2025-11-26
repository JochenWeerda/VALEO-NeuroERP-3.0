"""
Settings for CRM Multi-Channel Integration Service.
"""

import os
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://valeo_dev:valeo_dev_2024!@postgres:5432/valeo_neuro_erp"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/9"

    # Service
    SERVICE_NAME: str = "crm-multichannel"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Tenant
    DEFAULT_TENANT_ID: str = "00000000-0000-0000-0000-000000000001"

    # CRM Service URLs (for integration)
    CRM_CORE_BASE_URL: str = "http://localhost:5600"
    CRM_SALES_BASE_URL: str = "http://localhost:5700"
    CRM_SERVICE_BASE_URL: str = "http://localhost:5800"
    CRM_COMMUNICATION_BASE_URL: str = "http://localhost:6100"

    # Social Media API Keys (configure in environment)
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_ACCESS_TOKEN: Optional[str] = None

    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None

    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None

    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None

    # Webhook Configuration
    WEBHOOK_SECRET: str = "dev-webhook-secret"
    WEBHOOK_TIMEOUT: int = 30

    # External System Integrations
    SHOPIFY_API_KEY: Optional[str] = None
    SHOPIFY_PASSWORD: Optional[str] = None
    SHOPIFY_STORE_DOMAIN: Optional[str] = None

    WOOCOMMERCE_CONSUMER_KEY: Optional[str] = None
    WOOCOMMERCE_CONSUMER_SECRET: Optional[str] = None
    WOOCOMMERCE_STORE_URL: Optional[str] = None

    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Message Processing
    MAX_MESSAGE_LENGTH: int = 4096
    MESSAGE_BATCH_SIZE: int = 100
    CONVERSATION_TIMEOUT_HOURS: int = 24

    # Form Configuration
    MAX_FORM_FIELDS: int = 50
    FORM_SUBMISSION_TIMEOUT: int = 300  # 5 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()