"""Application settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    ***REMOVED*** Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://valeo_dev:valeo_dev@localhost:5432/valeo_neuro_erp"
    )
    
    ***REMOVED*** Service
    SERVICE_NAME: str = Field(default="crm-marketing")
    DEBUG: bool = Field(default=False)
    
    ***REMOVED*** CORS
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])
    
    ***REMOVED*** Tenant
    DEFAULT_TENANT_ID: str = Field(default="00000000-0000-0000-0000-000000000001")
    
    ***REMOVED*** Segment Calculation
    SEGMENT_CALCULATION_BATCH_SIZE: int = Field(default=1000)  ***REMOVED*** Process contacts in batches
    SEGMENT_CALCULATION_TIMEOUT: int = Field(default=300)  ***REMOVED*** 5 minutes timeout
    
    ***REMOVED*** Performance Tracking
    PERFORMANCE_AGGREGATION_INTERVAL: str = Field(default="daily")  ***REMOVED*** daily, weekly, monthly
    
    ***REMOVED*** Event Bus (future use)
    EVENT_BUS_URL: str | None = Field(default=None)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()

