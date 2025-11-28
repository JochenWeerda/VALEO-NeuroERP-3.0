"""
DMS Adapter Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    ***REMOVED*** Service
    SERVICE_NAME: str = "dms-adapter"
    DEBUG: bool = False
    
    ***REMOVED*** Paperless-ngx
    PAPERLESS_URL: str = "http://paperless:8000"
    PAPERLESS_TOKEN: str = ""
    PAPERLESS_TIMEOUT: int = 30
    
    ***REMOVED*** Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/neuroerp"
    
    ***REMOVED*** Security
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    ***REMOVED*** Tag-Konventionen für Paperless
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

