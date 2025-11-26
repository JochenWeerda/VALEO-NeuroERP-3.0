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
    
    # Event Bus (future use)
    EVENT_BUS_URL: str | None = Field(default=None)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()

