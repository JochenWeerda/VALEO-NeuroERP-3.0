"""Application settings."""

from typing import Literal

from pydantic import Field, field_validator
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

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _parse_debug(cls, value: object) -> object:
        if isinstance(value, str) and value.lower() in {"release", "prod", "production"}:
            return False
        return value

    # CORS
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    # Tenant
    DEFAULT_TENANT_ID: str = Field(default="00000000-0000-0000-0000-000000000001")

    # Export
    EXPORT_STORAGE_PATH: str = Field(default="/tmp/gdpr-exports")
    EXPORT_RETENTION_DAYS: int = Field(default=30)
    SUPPORTED_EXPORT_FORMATS: list[str] = Field(default_factory=lambda: ["json", "csv", "pdf"])

    # CRM-Integration (Export / Loesch-Orchestrierung)
    CRM_CORE_BASE_URL: str = Field(default="http://127.0.0.1:5600/api/v1")
    CRM_SALES_BASE_URL: str = Field(default="http://127.0.0.1:5700/api/v1")
    CRM_CONSENT_BASE_URL: str = Field(default="http://127.0.0.1:5701/api/v1")
    CRM_MARKETING_BASE_URL: str = Field(default="http://127.0.0.1:5703/api/v1")
    CRM_INTEGRATION_TIMEOUT_SECONDS: float = Field(default=30.0)
    INTERNAL_SERVICE_TOKEN: str | None = Field(default=None)

    GDPR_PUBLIC_VERIFICATION_URL: str | None = Field(default=None)
    GDPR_VERIFICATION_EMAIL_SUBJECT: str = Field(default="Bestätigung Ihrer Datenschutz-Anfrage")

    # SMTP (Verifikations-Mail)
    SMTP_HOST: str | None = Field(default=None)
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str | None = Field(default=None)
    SMTP_PASSWORD: str | None = Field(default=None)
    SMTP_FROM: str | None = Field(default=None)
    SMTP_USE_TLS: bool = Field(default=True)
    SMTP_TIMEOUT_SECONDS: float = Field(default=30.0)

    ANONYMIZATION_PREFIX: str = Field(default="ANONYMIZED_")

    EVENT_BUS_URL: str | None = Field(default=None)

    # Privacy Erasure Decision API (ADR 2026-05-06 / Policy erasure-retention-audit)
    PRIVACY_POLICY_VERSION: str = Field(
        default="retention-policy-2026-05-dev-001",
        description="Versionierte Policy-Kennung für Evaluate/Audit",
    )
    PRIVACY_DECISION_TTL_SECONDS: int = Field(
        default=86_400,
        ge=60,
        description="Gültigkeit einer evaluate-Decision bis execute (Sekunden)",
    )
    #: Ohne ERP-/FiBu-Discovery liefert Evaluate standardmäßig insufficient_information (sicher).
    PRIVACY_ERASURE_LEGACY_CRM_EVALUATE: bool = Field(
        default=False,
        description=(
            "DEV/Übergang: True = für scope=crm_slice kann delete_allowed/anonymize_allowed "
            "mit Übergangsaktion legacy_http_crm_erasure_orchestration zurückgegeben werden"
        ),
    )
    #: Wenn True blockt POST /gdpr/requests/{id}/delete ohne vorheriges erfolgreiches execute.
    PRIVACY_GATE_GDPR_DELETE_BEHIND_DECISION: bool = Field(
        default=False,
        description="Produktionsnahe Absicherung: Lösch-Endpunkt nur nach erfolgreichem execute",
    )
    #: execute verweigert ohne actor_id wenn True
    PRIVACY_EXECUTE_REQUIRE_ACTOR_ID: bool = Field(
        default=False,
        description="Später mit IAM: actor_id bei execute Pflicht",
    )
    PRIVACY_ERASURE_PERSISTENCE: Literal["database", "memory"] = Field(
        default="database",
        description="database: Tabellen crm_privacy_*; memory: In-Memory-Singleton im Prozess",
    )

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
