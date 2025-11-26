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
    SERVICE_NAME: str = Field(default="crm-gdpr")
    DEBUG: bool = Field(default=False)
    
    # CORS
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])
    
    # Tenant
    DEFAULT_TENANT_ID: str = Field(default="00000000-0000-0000-0000-000000000001")
    
    # Export Settings
    EXPORT_STORAGE_PATH: str = Field(default="/tmp/gdpr-exports")
    EXPORT_RETENTION_DAYS: int = Field(default=30)  # Export files kept for 30 days
    
    # Export Formats
    SUPPORTED_EXPORT_FORMATS: list[str] = Field(default_factory=lambda: ["json", "csv", "pdf"])
    
    # Anonymization
    ANONYMIZATION_PREFIX: str = Field(default="ANONYMIZED_")
    
    # Event Bus (future use)
    EVENT_BUS_URL: str | None = Field(default=None)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()

