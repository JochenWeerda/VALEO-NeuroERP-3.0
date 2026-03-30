"""
Secrets Vault Service — NC-15
Abstraktionsschicht fuer sichere Verwaltung von Geheimnissen.
Unterstuetzt: Umgebungsvariablen, verschluesselte In-Memory-Speicherung,
und als Erweiterungspunkt: HashiCorp Vault, Azure Key Vault, AWS Secrets Manager.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class SecretProvider(str, Enum):
    ENV = "env"
    MEMORY = "memory"
    HASHICORP_VAULT = "hashicorp_vault"
    AZURE_KEYVAULT = "azure_keyvault"
    AWS_SECRETS = "aws_secrets"


class SecretType(str, Enum):
    API_KEY = "api_key"
    DATABASE_CREDENTIAL = "database_credential"
    OIDC_SECRET = "oidc_secret"
    ENCRYPTION_KEY = "encryption_key"
    WEBHOOK_SECRET = "webhook_secret"
    SMTP_CREDENTIAL = "smtp_credential"
    EXTERNAL_SERVICE = "external_service"


@dataclass
class SecretMetadata:
    secret_id: str = field(default_factory=lambda: str(uuid4()))
    key: str = ""
    secret_type: SecretType = SecretType.API_KEY
    provider: SecretProvider = SecretProvider.ENV
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    rotated_at: Optional[str] = None
    expires_at: Optional[str] = None
    access_count: int = 0
    last_accessed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "secret_id": self.secret_id,
            "key": self.key,
            "secret_type": self.secret_type.value,
            "provider": self.provider.value,
            "description": self.description,
            "created_at": self.created_at,
            "rotated_at": self.rotated_at,
            "expires_at": self.expires_at,
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at,
        }


_OBFUSCATION_KEY = os.getenv("VAULT_OBFUSCATION_KEY", "valeo-neuro-erp-default-key")


def _obfuscate(value: str) -> str:
    """XOR-basierte Obfuskation (NICHT Verschluesselung — fuer Produktionsbetrieb Vault nutzen)."""
    key_bytes = hashlib.sha256(_OBFUSCATION_KEY.encode()).digest()
    val_bytes = value.encode()
    result = bytes(v ^ key_bytes[i % len(key_bytes)] for i, v in enumerate(val_bytes))
    return base64.b64encode(result).decode()


def _deobfuscate(encoded: str) -> str:
    key_bytes = hashlib.sha256(_OBFUSCATION_KEY.encode()).digest()
    val_bytes = base64.b64decode(encoded)
    result = bytes(v ^ key_bytes[i % len(key_bytes)] for i, v in enumerate(val_bytes))
    return result.decode()


_VAULT_STORE: dict[str, tuple[SecretMetadata, str]] = {}
_ACCESS_LOG: list[dict[str, Any]] = []


def store_secret(
    key: str,
    value: str,
    secret_type: SecretType = SecretType.API_KEY,
    description: str = "",
    provider: SecretProvider = SecretProvider.MEMORY,
) -> SecretMetadata:
    metadata = SecretMetadata(
        key=key,
        secret_type=secret_type,
        provider=provider,
        description=description,
    )
    obfuscated = _obfuscate(value)
    _VAULT_STORE[key] = (metadata, obfuscated)
    logger.info("Secret '%s' gespeichert (Typ: %s, Provider: %s)", key, secret_type.value, provider.value)
    return metadata


def get_secret(key: str, accessor: str = "system") -> Optional[str]:
    if key in _VAULT_STORE:
        metadata, obfuscated = _VAULT_STORE[key]
        metadata.access_count += 1
        metadata.last_accessed_at = datetime.now(timezone.utc).isoformat()
        _record_access(key, accessor, "read")
        return _deobfuscate(obfuscated)

    env_value = os.getenv(key)
    if env_value:
        _record_access(key, accessor, "env_read")
        return env_value

    return None


def get_secret_metadata(key: str) -> Optional[SecretMetadata]:
    if key in _VAULT_STORE:
        return _VAULT_STORE[key][0]
    return None


def rotate_secret(key: str, new_value: str, rotated_by: str = "system") -> Optional[SecretMetadata]:
    if key not in _VAULT_STORE:
        return None
    metadata, _ = _VAULT_STORE[key]
    obfuscated = _obfuscate(new_value)
    metadata.rotated_at = datetime.now(timezone.utc).isoformat()
    _VAULT_STORE[key] = (metadata, obfuscated)
    _record_access(key, rotated_by, "rotate")
    logger.info("Secret '%s' rotiert von %s", key, rotated_by)
    return metadata


def delete_secret(key: str, deleted_by: str = "system") -> bool:
    if key in _VAULT_STORE:
        del _VAULT_STORE[key]
        _record_access(key, deleted_by, "delete")
        return True
    return False


def list_secrets() -> list[SecretMetadata]:
    return [metadata for metadata, _ in _VAULT_STORE.values()]


def get_access_log(limit: int = 50) -> list[dict[str, Any]]:
    return _ACCESS_LOG[-limit:]


def _record_access(key: str, accessor: str, operation: str) -> None:
    _ACCESS_LOG.append({
        "key": key,
        "accessor": accessor,
        "operation": operation,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    if len(_ACCESS_LOG) > 1000:
        _ACCESS_LOG[:] = _ACCESS_LOG[-500:]


def check_health() -> dict[str, Any]:
    total = len(_VAULT_STORE)
    now = datetime.now(timezone.utc)
    expired = 0
    for metadata, _ in _VAULT_STORE.values():
        if metadata.expires_at:
            try:
                if datetime.fromisoformat(metadata.expires_at) < now:
                    expired += 1
            except ValueError:
                pass

    return {
        "status": "healthy" if expired == 0 else "warning",
        "total_secrets": total,
        "expired_secrets": expired,
        "provider_counts": _provider_counts(),
    }


def _provider_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for metadata, _ in _VAULT_STORE.values():
        p = metadata.provider.value
        counts[p] = counts.get(p, 0) + 1
    return counts
