"""
AI Service Configuration
"""

from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AI Service settings"""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    DEBUG: bool = True
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://backend:8000",
    ]
    
    # Database (read-only access to main ERP DB)
    DATABASE_URL: str = "postgresql://valeo_dev:valeo_dev_2024!@postgres:5432/valeo_neuro_erp"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Vector Store Configuration
    CHROMA_PERSIST_DIR: str = "/app/data/chroma"
    CHROMA_COLLECTION_NAME: str = "valeo_erp_knowledge"
    
    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379/1"
    REDIS_CACHE_TTL: int = 3600
    
    # MCP Configuration
    MCP_SERVER_PORT: int = 5001
    MCP_SERVER_HOST: str = "0.0.0.0"
    
    # Backend API Configuration
    BACKEND_API_URL: str = "http://backend:8000/api/v1"
    API_DEV_TOKEN: str = "dev-token"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

