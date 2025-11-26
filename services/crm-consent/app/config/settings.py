"""Application settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://valeo_dev:valeo_dev@localhost:5432/valeo_neuro_erp"
    )
    
    # Service
    SERVICE_NAME: str = Field(default="crm-consent")
    DEBUG: bool = Field(default=False)
    
    # CORS
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])
    
    # Tenant
    DEFAULT_TENANT_ID: str = Field(default="00000000-0000-0000-0000-000000000001")
    
    # Email Service (for double opt-in)
    EMAIL_SERVICE_URL: str = Field(default="http://localhost:5000/api/v1/emails")
    
    # Double Opt-In
    DOUBLE_OPT_IN_TOKEN_EXPIRY_HOURS: int = Field(default=48)
    
    # Event Bus (future use)
    EVENT_BUS_URL: str | None = Field(default=None)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()

