"""Application settings."""

import os

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://valeo_dev@localhost:5432/valeo_neuro_erp"
    )
    
    # Service
    SERVICE_NAME: str = Field(default="crm-marketing")
    DEBUG: bool = Field(default=False)
    
    # CORS
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])
    
    # Tenant
    DEFAULT_TENANT_ID: str = Field(default="00000000-0000-0000-0000-000000000001")
    
    # Segment Calculation
    SEGMENT_CALCULATION_BATCH_SIZE: int = Field(default=1000)  # Process contacts in batches
    SEGMENT_CALCULATION_TIMEOUT: int = Field(default=300)  # 5 minutes timeout
    
    # Performance Tracking
    PERFORMANCE_AGGREGATION_INTERVAL: str = Field(default="daily")  # daily, weekly, monthly
    
    # E-Mail (Versand Kampagnen / Transaktional; M-07)
    SMTP_HOST: str | None = Field(default=None)
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str | None = Field(default=None)
    SMTP_PASSWORD: str | None = Field(default=None)
    SMTP_FROM: str | None = Field(default=None)
    SMTP_USE_TLS: bool = Field(default=True)
    SMTP_TIMEOUT_SECONDS: float = Field(default=30.0)

    # Auth (M-06): Bearer JWT (HS256 oder OIDC/JWKS); optional X-User-Id
    API_DEV_TOKEN: str | None = Field(default=None, description="Echo-Token fuer Tests/CI")
    JWT_HS256_SECRET: str | None = Field(
        default=None,
        validation_alias=AliasChoices("JWT_HS256_SECRET", "JWT_SECRET"),
    )
    OIDC_JWKS_URL: str | None = Field(default=None)
    OIDC_ISSUER_URL: str | None = Field(default=None)
    OIDC_CLIENT_ID: str | None = Field(default=None)
    KEYCLOAK_URL: str | None = Field(default=None)
    KEYCLOAK_REALM: str | None = Field(default=None)
    KEYCLOAK_CLIENT_ID: str | None = Field(default=None)
    CRM_ACTOR_ALLOW_SYSTEM_FALLBACK: bool = Field(
        default=True,
        description="Wenn false: ohne gueltiges Bearer oder X-User-Id -> 401",
    )

    # Event Bus (future use)
    EVENT_BUS_URL: str | None = Field(default=None)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }

    def effective_jwt_hs256_secret(self) -> str | None:
        return (self.JWT_HS256_SECRET or os.environ.get("JWT_SECRET") or "").strip() or None


settings = Settings()


