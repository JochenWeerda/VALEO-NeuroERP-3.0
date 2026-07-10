"""
DMS Adapter Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from functools import lru_cache


def _default_database_url() -> str:
    return str(
        PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username="postgres",
            host="postgres",
            port=5432,
            path="/neuroerp",
        )
    )


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "dms-adapter"
    DEBUG: bool = False
    
    # Paperless-ngx
    PAPERLESS_URL: str = "http://paperless:8000"
    PAPERLESS_TOKEN: str = ""
    PAPERLESS_TIMEOUT: int = 30
    
    # Database
    DATABASE_URL: str = _default_database_url()
    
    # Security
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Tag-Konventionen für Paperless
    TAG_PREFIX_TENANT: str = "TENANT"
    TAG_PREFIX_OBJECT_TYPE: str = "OBJ"
    TAG_PREFIX_OBJECT_ID: str = "OBJID"
    TAG_PREFIX_DOCTYPE: str = "DOCTYPE"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


