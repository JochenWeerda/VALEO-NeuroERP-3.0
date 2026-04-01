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
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class SecretProvider(str, Enum):
    ENV = "env"
    MEMORY = "memory"
    KEYRING = "keyring"
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
_KEYRING_SERVICE_NAME = os.getenv("VALEO_SECRET_SERVICE_NAME", "VALEO-NeuroERP")
_KEYRING_INDEX_KEY = "__VALEO_SECRET_INDEX__"


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


def _load_settings() -> Any:
    from app.core.config import settings

    return settings


def _configured_default_provider() -> SecretProvider:
    provider_name = os.getenv("SECRET_PROVIDER")
    if not provider_name:
        provider_name = getattr(_load_settings(), "SECRET_PROVIDER", SecretProvider.ENV.value)
    try:
        return SecretProvider(str(provider_name).lower())
    except ValueError:
        logger.warning("Unbekannter SECRET_PROVIDER '%s', fallback auf env.", provider_name)
        return SecretProvider.ENV


def _is_production_environment() -> bool:
    settings = _load_settings()
    app_env = str(getattr(settings, "APP_ENV", "development") or "development").strip().lower()
    return app_env in {"prod", "production"}


def _external_secret_providers() -> set[SecretProvider]:
    return {
        SecretProvider.HASHICORP_VAULT,
        SecretProvider.AZURE_KEYVAULT,
        SecretProvider.AWS_SECRETS,
    }


def _hashicorp_secret_url(*, metadata: bool, key: str) -> str:
    settings = _load_settings()
    addr = (getattr(settings, "HASHICORP_VAULT_ADDR", None) or "").rstrip("/")
    mount = (getattr(settings, "HASHICORP_VAULT_MOUNT", "secret") or "secret").strip("/")
    prefix = (getattr(settings, "HASHICORP_VAULT_PATH_PREFIX", "valeo-neuroerp") or "valeo-neuroerp").strip("/")
    if not addr:
        raise RuntimeError("HASHICORP_VAULT_ADDR ist nicht konfiguriert.")
    if not getattr(settings, "HASHICORP_VAULT_TOKEN", None):
        raise RuntimeError("HASHICORP_VAULT_TOKEN ist nicht konfiguriert.")
    scope = "metadata" if metadata else "data"
    encoded_key = quote(key, safe="")
    return f"{addr}/v1/{mount}/{scope}/{prefix}/{encoded_key}"


def _hashicorp_headers() -> dict[str, str]:
    settings = _load_settings()
    token = getattr(settings, "HASHICORP_VAULT_TOKEN", None)
    if not token:
        raise RuntimeError("HASHICORP_VAULT_TOKEN ist nicht konfiguriert.")
    return {
        "X-Vault-Token": token,
        "Content-Type": "application/json",
    }


def _hashicorp_request(method: str, url: str, payload: Optional[dict[str, Any]] = None) -> tuple[int, str]:
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=_hashicorp_headers(), method=method)
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="ignore")
    except URLError as exc:
        raise RuntimeError(f"HashiCorp Vault nicht erreichbar: {exc.reason}") from exc


def _hashicorp_store_secret(key: str, value: str, metadata: SecretMetadata) -> None:
    url = _hashicorp_secret_url(metadata=False, key=key)
    status, body = _hashicorp_request(
        "POST",
        url,
        {
            "data": {
                "value": value,
                "metadata": metadata.to_dict(),
            }
        },
    )
    if status not in {200, 204}:
        raise RuntimeError(f"HashiCorp Vault write fehlgeschlagen ({status}): {body[:200]}")


def _hashicorp_get_secret(key: str) -> tuple[Optional[str], Optional[SecretMetadata]]:
    url = _hashicorp_secret_url(metadata=False, key=key)
    status, body = _hashicorp_request("GET", url)
    if status == 404:
        return None, None
    if status != 200:
        raise RuntimeError(f"HashiCorp Vault read fehlgeschlagen ({status}): {body[:200]}")
    payload = json.loads(body or "{}")
    data = payload.get("data", {}).get("data", {})
    value = data.get("value")
    metadata_payload = data.get("metadata") or {}
    metadata = _metadata_from_dict(metadata_payload) if metadata_payload else SecretMetadata(
        key=key,
        provider=SecretProvider.HASHICORP_VAULT,
    )
    metadata.key = key
    metadata.provider = SecretProvider.HASHICORP_VAULT
    return value, metadata


def _hashicorp_delete_secret(key: str) -> bool:
    url = _hashicorp_secret_url(metadata=True, key=key)
    status, body = _hashicorp_request("DELETE", url)
    if status == 404:
        return False
    if status not in {200, 204}:
        raise RuntimeError(f"HashiCorp Vault delete fehlgeschlagen ({status}): {body[:200]}")
    return True


def _get_keyring_module() -> Any | None:
    try:
        import keyring  # type: ignore
    except Exception:
        return None
    return keyring


def _metadata_from_dict(payload: dict[str, Any]) -> SecretMetadata:
    return SecretMetadata(
        secret_id=payload.get("secret_id", str(uuid4())),
        key=payload.get("key", ""),
        secret_type=SecretType(payload.get("secret_type", SecretType.API_KEY.value)),
        provider=SecretProvider(payload.get("provider", SecretProvider.MEMORY.value)),
        description=payload.get("description", ""),
        created_at=payload.get("created_at", datetime.now(timezone.utc).isoformat()),
        rotated_at=payload.get("rotated_at"),
        expires_at=payload.get("expires_at"),
        access_count=payload.get("access_count", 0),
        last_accessed_at=payload.get("last_accessed_at"),
    )


def _load_keyring_index(keyring_module: Any) -> dict[str, SecretMetadata]:
    raw = keyring_module.get_password(_KEYRING_SERVICE_NAME, _KEYRING_INDEX_KEY)
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Keyring metadata index ist unlesbar und wird ignoriert.")
        return {}
    return {key: _metadata_from_dict(value) for key, value in payload.items()}


def _save_keyring_index(keyring_module: Any, index: dict[str, SecretMetadata]) -> None:
    serialized = json.dumps({key: metadata.to_dict() for key, metadata in index.items()})
    keyring_module.set_password(_KEYRING_SERVICE_NAME, _KEYRING_INDEX_KEY, serialized)


def _touch_metadata(metadata: SecretMetadata, accessor: str, operation: str) -> None:
    metadata.access_count += 1
    metadata.last_accessed_at = datetime.now(timezone.utc).isoformat()
    _record_access(metadata.key, accessor, operation)


def store_secret(
    key: str,
    value: str,
    secret_type: SecretType = SecretType.API_KEY,
    description: str = "",
    provider: Optional[SecretProvider] = None,
) -> SecretMetadata:
    provider = provider or _configured_default_provider()
    metadata = SecretMetadata(
        key=key,
        secret_type=secret_type,
        provider=provider,
        description=description,
    )
    if provider == SecretProvider.KEYRING:
        keyring_module = _get_keyring_module()
        if keyring_module is None:
            raise RuntimeError("Python-Paket 'keyring' ist nicht verfuegbar.")
        keyring_module.set_password(_KEYRING_SERVICE_NAME, key, value)
        index = _load_keyring_index(keyring_module)
        index[key] = metadata
        _save_keyring_index(keyring_module, index)
        _VAULT_STORE[key] = (metadata, "")
    elif provider == SecretProvider.HASHICORP_VAULT:
        _hashicorp_store_secret(key, value, metadata)
        _VAULT_STORE[key] = (metadata, "")
    else:
        obfuscated = _obfuscate(value)
        _VAULT_STORE[key] = (metadata, obfuscated)
    logger.info("Secret '%s' gespeichert (Typ: %s, Provider: %s)", key, secret_type.value, provider.value)
    return metadata


def get_secret(key: str, accessor: str = "system") -> Optional[str]:
    if key in _VAULT_STORE:
        metadata, obfuscated = _VAULT_STORE[key]
        if metadata.provider == SecretProvider.KEYRING:
            keyring_module = _get_keyring_module()
            if keyring_module is None:
                return None
            value = keyring_module.get_password(_KEYRING_SERVICE_NAME, key)
            if value is not None:
                _touch_metadata(metadata, accessor, "keyring_read")
            return value
        if metadata.provider == SecretProvider.HASHICORP_VAULT:
            value, remote_metadata = _hashicorp_get_secret(key)
            if value is not None:
                metadata = remote_metadata or metadata
                _touch_metadata(metadata, accessor, "hashicorp_read")
                _VAULT_STORE[key] = (metadata, "")
            return value
        _touch_metadata(metadata, accessor, "read")
        return _deobfuscate(obfuscated)

    keyring_module = _get_keyring_module()
    if keyring_module is not None:
        value = keyring_module.get_password(_KEYRING_SERVICE_NAME, key)
        if value is not None:
            index = _load_keyring_index(keyring_module)
            metadata = index.get(
                key,
                SecretMetadata(key=key, provider=SecretProvider.KEYRING),
            )
            _touch_metadata(metadata, accessor, "keyring_read")
            index[key] = metadata
            _save_keyring_index(keyring_module, index)
            _VAULT_STORE[key] = (metadata, "")
            return value

    provider = _configured_default_provider()
    if provider == SecretProvider.HASHICORP_VAULT:
        value, metadata = _hashicorp_get_secret(key)
        if value is not None:
            resolved_metadata = metadata or SecretMetadata(key=key, provider=SecretProvider.HASHICORP_VAULT)
            _touch_metadata(resolved_metadata, accessor, "hashicorp_read")
            _VAULT_STORE[key] = (resolved_metadata, "")
            return value

    env_value = os.getenv(key)
    if env_value:
        _record_access(key, accessor, "env_read")
        return env_value

    return None


def get_secret_metadata(key: str) -> Optional[SecretMetadata]:
    if key in _VAULT_STORE:
        return _VAULT_STORE[key][0]
    keyring_module = _get_keyring_module()
    if keyring_module is not None:
        return _load_keyring_index(keyring_module).get(key)
    if _configured_default_provider() == SecretProvider.HASHICORP_VAULT:
        _, metadata = _hashicorp_get_secret(key)
        return metadata
    return None


def rotate_secret(key: str, new_value: str, rotated_by: str = "system") -> Optional[SecretMetadata]:
    metadata = get_secret_metadata(key)
    if metadata is None:
        return None
    metadata.rotated_at = datetime.now(timezone.utc).isoformat()
    if metadata.provider == SecretProvider.KEYRING:
        keyring_module = _get_keyring_module()
        if keyring_module is None:
            return None
        keyring_module.set_password(_KEYRING_SERVICE_NAME, key, new_value)
        index = _load_keyring_index(keyring_module)
        index[key] = metadata
        _save_keyring_index(keyring_module, index)
        _VAULT_STORE[key] = (metadata, "")
    elif metadata.provider == SecretProvider.HASHICORP_VAULT:
        _hashicorp_store_secret(key, new_value, metadata)
        _VAULT_STORE[key] = (metadata, "")
    else:
        obfuscated = _obfuscate(new_value)
        _VAULT_STORE[key] = (metadata, obfuscated)
    _record_access(key, rotated_by, "rotate")
    logger.info("Secret '%s' rotiert von %s", key, rotated_by)
    return metadata


def delete_secret(key: str, deleted_by: str = "system") -> bool:
    if key in _VAULT_STORE:
        metadata, _ = _VAULT_STORE[key]
        if metadata.provider == SecretProvider.KEYRING:
            keyring_module = _get_keyring_module()
            if keyring_module is not None:
                try:
                    keyring_module.delete_password(_KEYRING_SERVICE_NAME, key)
                except Exception:
                    pass
                index = _load_keyring_index(keyring_module)
                index.pop(key, None)
                _save_keyring_index(keyring_module, index)
        del _VAULT_STORE[key]
        _record_access(key, deleted_by, "delete")
        return True
    keyring_module = _get_keyring_module()
    if keyring_module is not None:
        value = keyring_module.get_password(_KEYRING_SERVICE_NAME, key)
        if value is not None:
            try:
                keyring_module.delete_password(_KEYRING_SERVICE_NAME, key)
            except Exception:
                pass
            index = _load_keyring_index(keyring_module)
            index.pop(key, None)
            _save_keyring_index(keyring_module, index)
            _record_access(key, deleted_by, "delete")
            return True
    if _configured_default_provider() == SecretProvider.HASHICORP_VAULT:
        deleted = _hashicorp_delete_secret(key)
        if deleted:
            _record_access(key, deleted_by, "delete")
        return deleted
    return False


def list_secrets() -> list[SecretMetadata]:
    combined: dict[str, SecretMetadata] = {metadata.key: metadata for metadata, _ in _VAULT_STORE.values()}
    keyring_module = _get_keyring_module()
    if keyring_module is not None:
        combined.update(_load_keyring_index(keyring_module))
    return list(combined.values())


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

    provider = _configured_default_provider()
    external_vault = {
        "configured_provider": provider.value,
        "healthy": True,
        "detail": None,
    }
    if provider == SecretProvider.HASHICORP_VAULT:
        try:
            url = _hashicorp_secret_url(metadata=False, key="__healthcheck__")
            status, _ = _hashicorp_request("GET", url)
            external_vault["healthy"] = status in {200, 404}
            if not external_vault["healthy"]:
                external_vault["detail"] = f"unexpected_status:{status}"
        except Exception as exc:
            external_vault["healthy"] = False
            external_vault["detail"] = str(exc)

    return {
        "status": "healthy" if expired == 0 and external_vault["healthy"] else "warning",
        "total_secrets": total,
        "expired_secrets": expired,
        "provider_counts": _provider_counts(),
        "external_vault": external_vault,
    }


def _provider_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for metadata, _ in _VAULT_STORE.values():
        p = metadata.provider.value
        counts[p] = counts.get(p, 0) + 1
    return counts


def validate_startup_secrets() -> None:
    settings = _load_settings()
    provider = _configured_default_provider()
    is_production = _is_production_environment()

    if is_production and settings.API_DEV_TOKEN:
        raise RuntimeError("API_DEV_TOKEN darf in Produktion nicht gesetzt sein.")

    if is_production and settings.REQUIRE_EXTERNAL_SECRETS_IN_PRODUCTION and provider not in _external_secret_providers():
        raise RuntimeError(
            "Produktion erfordert einen externen Secret-Provider "
            f"({', '.join(sorted(item.value for item in _external_secret_providers()))}); "
            f"konfiguriert ist '{provider.value}'."
        )

    for secret_key in ("SECRET_KEY", "ENCRYPTION_KEY"):
        current_value = getattr(settings, secret_key, None)
        resolved = current_value or get_secret(secret_key, accessor="startup_guard")
        if is_production and not resolved:
            raise RuntimeError(f"{secret_key} konnte zum Startup nicht aus Secret-Provider oder Environment geladen werden.")
        if resolved and not current_value:
            setattr(settings, secret_key, resolved)
