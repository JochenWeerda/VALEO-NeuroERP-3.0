"""Settings für Inventory Service mit Betriebsprofile-Support."""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Dict, List

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class OperationMode(str, Enum):
    TEST = "test"
    REAL = "real"


class Settings(BaseSettings):
    """Zentrale Konfiguration für den Inventory-Service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="INVENTORY_",
        case_sensitive=True,
        extra="ignore",
    )

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 5400
    DEBUG: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://backend:8000",
    ]

    # Betriebsprofile
    GLOBAL_OPERATION_MODE: OperationMode = OperationMode.TEST
    MODULE_MODE_OVERRIDES: Dict[str, OperationMode] = Field(default_factory=dict)

    # Datenbank
    DATABASE_URL: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        username="valeo_inventory",
        password="valeo_inventory_2024!",
        host="postgres-inventory",
        port=5432,
        path="/valeo_inventory",
    )
    DB_ECHO: bool = False

    # EventBus
    EVENT_BUS_ENABLED: bool | None = None
    EVENT_BUS_URL: str = "nats://nats:4222"
    EVENT_BUS_SUBJECT_PREFIX: str = "inventory"

    DEFAULT_TENANT: str = "default"

    # Workflow-Service
    WORKFLOW_SERVICE_URL: AnyHttpUrl = "http://workflow:8000"
    WORKFLOW_REGISTRATION_TIMEOUT: float = 10.0

    # Ops Notifications (optional)
    TEAMS_WEBHOOK_URL: str | None = None
    ESCALATION_EMAIL: str | None = None

    # Schutz & Resilienz
    RATE_LIMIT_PER_MINUTE: int = 600
    NATS_FAILURE_THRESHOLD: int = 5
    NATS_CIRCUIT_BREAKER_OPEN_SECONDS: int = 60

    # DSGVO / Retention für EPCIS
    EPCIS_RETENTION_DAYS: int = 365
    EPCIS_ANONYMIZE_KEYS: List[str] = Field(
        default_factory=lambda: ["userName", "email", "phone", "address", "personalId"]
    )

    @field_validator("MODULE_MODE_OVERRIDES", mode="before")
    @classmethod
    def _parse_module_modes(cls, value: object) -> Dict[str, OperationMode]:
        if value in (None, "", {}):
            return {}
        if isinstance(value, dict):
            parsed: Dict[str, OperationMode] = {}
            for key, mode_value in value.items():
                if key is None or mode_value is None:
                    continue
                parsed[str(key).lower()] = OperationMode(str(mode_value).lower())
            return parsed
        if isinstance(value, str):
            parsed: Dict[str, OperationMode] = {}
            for token in value.split(","):
                item = token.strip()
                if not item:
                    continue
                module, sep, mode = item.partition("=")
                if not sep:
                    raise ValueError(f"Ungültiger Eintrag in MODULE_MODE_OVERRIDES: '{item}' (Format modul=modus).")
                module_key = module.strip().lower()
                mode_value = mode.strip().lower()
                if not module_key or not mode_value:
                    raise ValueError(f"Ungültiger Eintrag in MODULE_MODE_OVERRIDES: '{item}' (fehlender Wert).")
                parsed[module_key] = OperationMode(mode_value)
            return parsed
        raise ValueError("MODULE_MODE_OVERRIDES erwartet ein Dict oder einen String.")

    @model_validator(mode="after")
    def _apply_mode_defaults(self) -> "Settings":
        if self.EVENT_BUS_ENABLED is None:
            self.EVENT_BUS_ENABLED = self.is_real_mode("event_bus")
        return self

    def get_module_mode(self, module: str, default: OperationMode | None = None) -> OperationMode:
        module_key = module.lower()
        if module_key in self.MODULE_MODE_OVERRIDES:
            return self.MODULE_MODE_OVERRIDES[module_key]
        return default or self.GLOBAL_OPERATION_MODE

    def is_real_mode(self, module: str) -> bool:
        return self.get_module_mode(module) == OperationMode.REAL


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
