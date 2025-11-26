"""
VALEO-NeuroERP Configuration
Centralized configuration management using Pydantic settings
"""

import secrets
from typing import List, Optional, Union
from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Vite dev server (Fallback)
        "http://localhost:8080",  # Vue dev server
        "http://localhost:5173",  # Vite dev server (Primary)
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Trusted Hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp",
        env="DATABASE_URL"
    )
    DATABASE_CONNECT_ARGS: dict = {}

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # Keycloak Configuration
    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "valeo-neuro-erp"
    KEYCLOAK_CLIENT_ID: str = "valeo-neuro-erp-backend"
    KEYCLOAK_CLIENT_SECRET: Optional[str] = None
    OIDC_CLIENT_ID: Optional[str] = None
    OIDC_ISSUER_URL: Optional[str] = None
    OIDC_JWKS_URL: Optional[str] = None

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Security Configuration
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"

    # Feature Flags
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False
    ENABLE_CACHE: bool = True

    # Downstream CRM services
    CRM_CORE_BASE_URL: str = "http://localhost:5600"
    CRM_CORE_HTTP_TIMEOUT_SECONDS: float = 5.0
    CRM_SALES_BASE_URL: str = "http://localhost:5700"
    CRM_SALES_HTTP_TIMEOUT_SECONDS: float = 5.0
    CRM_SERVICE_BASE_URL: str = "http://localhost:5800"
    CRM_SERVICE_HTTP_TIMEOUT_SECONDS: float = 5.0

    # Multi-tenancy defaults
    DEFAULT_TENANT_ID: str = "00000000-0000-0000-0000-000000000001"

    # External Services
    EMAIL_SMTP_SERVER: Optional[str] = None
    EMAIL_SMTP_PORT: Optional[int] = None
    EMAIL_USERNAME: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000

    # API Authentication
    API_DEV_TOKEN: Optional[str] = "dev-token"
    API_AUTH_EXEMPT_PATHS: List[str] = [
        "/api/v1/health",
        "/api/v1/health/ready",
        "/api/v1/health/live",
        "/api/v1/health/database",
        "/api/v1/gap/pipeline/status",  # GAP Pipeline Status (für Admin-UI)
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields from environment


# Global settings instance
settings = Settings()
