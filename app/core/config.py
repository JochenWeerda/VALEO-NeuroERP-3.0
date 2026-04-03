"""
VALEO-NeuroERP Configuration
Centralized configuration management using Pydantic settings
"""

import json
import secrets
from typing import Any, List, Optional, Union
from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """

    # API Configuration
    API_V1_STR: str = "/api/v1"
    # SC-SECRETS-001: SECRET_KEY MUSS aus Umgebungsvariable geladen werden.
    # Kein hardcoded Default — Startup schlägt fehl wenn nicht gesetzt (außer DEBUG).
    # In Produktion: openssl rand -hex 32 > .env (SECRET_KEY=<value>)
    SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    APP_ENV: str = "development"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_flag(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            normalized = v.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return bool(v)

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Vite dev server (Fallback)
        "http://localhost:8080",  # Vue dev server
        "http://localhost:5173",  # Vite dev server (Primary)
        "/api/v1/channels/slack/events",
        "/api/v1/channels/teams/events",
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
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "testserver"]

    # Database Configuration
    # HINWEIS: In Docker-Umgebung muss host="postgres" sein (Service-Name aus docker-compose.yml)
    # In lokalen Umgebung ohne Docker kann 127.0.0.1 verwendet werden
    DATABASE_URL: str = Field(
        default="postgresql://CHANGE_ME_USER:CHANGE_ME_PASSWORD@postgres:5432/CHANGE_ME_DB"
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
    # SC-SECRETS-001: ENCRYPTION_KEY MUSS aus Umgebungsvariable geladen werden.
    ENCRYPTION_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    SECRET_PROVIDER: str = "env"
    REQUIRE_EXTERNAL_SECRETS_IN_PRODUCTION: bool = True
    HASHICORP_VAULT_ADDR: Optional[str] = None
    HASHICORP_VAULT_TOKEN: Optional[str] = None
    HASHICORP_VAULT_MOUNT: str = "secret"
    HASHICORP_VAULT_PATH_PREFIX: str = "valeo-neuroerp"
    OUTBOUND_HTTP_ALLOWED_HOSTS: List[str] = []
    OUTBOUND_HTTP_ALLOWED_DOMAINS: List[str] = []
    SUPERGLUE_ENABLED: bool = False
    SUPERGLUE_BASE_URL: Optional[str] = None
    SUPERGLUE_GRAPHQL_URL: Optional[str] = None
    SUPERGLUE_REST_URL: Optional[str] = None
    SUPERGLUE_DASHBOARD_URL: Optional[str] = None
    SUPERGLUE_AUTH_TOKEN: Optional[str] = None
    SUPERGLUE_TIMEOUT_SECONDS: float = 10.0
    SUPERGLUE_PROVIDER_KEY: str = "superglue"
    SUPERGLUE_ALLOWED_HOSTS: List[str] = []
    SUPERGLUE_ALLOWED_DOMAINS: List[str] = []
    SUPERGLUE_SYNC_ENABLED: bool = False
    SUPERGLUE_EXECUTION_ENABLED: bool = False
    SECURITY_EVENT_PERSISTENCE_ENABLED: bool = True
    SECURITY_EVENT_LOG_PATH: str = "runtime/security-events/security-events.jsonl"

    # Feature Flags
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False
    ENABLE_CACHE: bool = True

    # OpenTelemetry (Gap 039) — OTLP-HTTP-Endpoint, z.B. http://localhost:4318/v1/traces
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    OTEL_SERVICE_NAME: str = "valeo-neuroerp-api"

    # Event Bus / Outbox
    EVENT_BUS_ENABLED: bool = False
    EVENT_BUS_PROVIDER: str = "memory"  # memory | nats
    EVENT_BUS_NATS_URL: str = "nats://localhost:4222"
    OUTBOX_WORKER_ENABLED: bool = True
    OUTBOX_WORKER_INTERVAL_SECONDS: int = 5

    # Downstream CRM services
    CRM_CORE_BASE_URL: str = "http://localhost:5600"
    CRM_CORE_HTTP_TIMEOUT_SECONDS: float = 5.0
    CRM_SALES_BASE_URL: str = "http://localhost:5700"
    CRM_SALES_HTTP_TIMEOUT_SECONDS: float = 5.0
    CRM_SERVICE_BASE_URL: str = "http://localhost:5800"
    CRM_SERVICE_HTTP_TIMEOUT_SECONDS: float = 5.0

    # Multi-tenancy defaults
    DEFAULT_TENANT_ID: str = "00000000-0000-0000-0000-000000000001"
    DEFAULT_BANK_ACCOUNT_ID: str = "1000"  # Kontonummer für OP-Ausgleich (Zahlungseingang)
    DEFAULT_VAT_RATE: float = 0.19  # MwSt-Satz (19 %) für Portal-Shop
    INSTALLED_MODULES: List[str] = ["core", "agrar"]
    TENANT_MODULE_FLAGS: dict[str, list[str]] = {}

    @field_validator("INSTALLED_MODULES", mode="before")
    @classmethod
    def assemble_installed_modules(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("TENANT_MODULE_FLAGS", mode="before")
    @classmethod
    def assemble_tenant_module_flags(
        cls, v: Any
    ) -> dict[str, list[str]]:
        if v is None or v == "":
            return {}
        if isinstance(v, dict):
            return {
                str(tenant_id): [str(module).strip() for module in modules if str(module).strip()]
                for tenant_id, modules in v.items()
                if isinstance(modules, list)
            }
        if isinstance(v, str):
            parsed = json.loads(v)
            if not isinstance(parsed, dict):
                raise ValueError("TENANT_MODULE_FLAGS must be an object")
            return {
                str(tenant_id): [str(module).strip() for module in modules if str(module).strip()]
                for tenant_id, modules in parsed.items()
                if isinstance(modules, list)
            }
        raise ValueError("TENANT_MODULE_FLAGS must be dict or JSON object string")

    @field_validator(
        "OUTBOUND_HTTP_ALLOWED_HOSTS",
        "OUTBOUND_HTTP_ALLOWED_DOMAINS",
        "SUPERGLUE_ALLOWED_HOSTS",
        "SUPERGLUE_ALLOWED_DOMAINS",
        mode="before",
    )
    @classmethod
    def assemble_outbound_allowlists(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if v is None or v == "":
            return []
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        if isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # External Services
    EMAIL_SMTP_SERVER: Optional[str] = None
    EMAIL_SMTP_PORT: Optional[int] = None
    EMAIL_USERNAME: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None

    # VIES (EU USt-ID-Prüfung) – bei True ruft der Compliance-Worker den VIES-Service auf
    ENABLE_VIES_CHECK: bool = False

    # Agrar Feature-Flags
    AGRAR_ZONEN_FROM_API: bool = False  # True = Zonen via WFS/PostGIS statt Seed-Daten

    # Rationsoptimierung Microservice
    RATIONS_OPTIMIZATION_URL: Optional[str] = None  # z.B. http://rations-optimization:8000
    RATIONS_OPTIMIZATION_API_KEY: str = "dev-api-key-change-in-production"

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000

    # API Authentication
    # SC-AUTH-002: In Produktion MUSS API_DEV_TOKEN=None sein (Startup-Guard in main.py).
    # In Entwicklung: API_DEV_TOKEN=dev-token in .env setzen.
    API_DEV_TOKEN: Optional[str] = None
    CHANNEL_SLACK_SIGNING_SECRET: Optional[str] = None
    CHANNEL_SLACK_BOT_TOKEN: Optional[str] = None
    CHANNEL_TEAMS_WEBHOOK_SECRET: Optional[str] = None
    CHANNEL_INGRESS_MAX_AGE_SECONDS: int = 300
    API_AUTH_EXEMPT_PATHS: List[str] = [
        "/api/v1/health",
        "/api/v1/health/ready",
        "/api/v1/health/live",
        "/api/v1/health/database",
        "/api/v1/channels/slack/events",
        "/api/v1/channels/teams/events",
        "/api/v1/gap/pipeline/status",  # GAP Pipeline Status (für Admin-UI)
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
