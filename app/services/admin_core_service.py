"""Service layer for the core admin domain.

Bündelt die Geschäftslogik der Admin-/Settings-Endpunkte (Benutzer, Rollen,
Audit-Log, API-Keys, Prozessvarianten, Policy-Overrides, Erntefenster-Kampagnen
und Workflow-Sandbox). Die Endpunkte in ``admin_core.py`` sind dünne Adapter,
die ausschließlich an diesen Service delegieren.

Fehler werden als ``DomainError``-Subklassen geworfen und vom globalen
Exception-Handler (siehe ``app/core/exceptions.py``) in RFC-7807-Antworten
übersetzt.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import date, datetime
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.scopes import ROLE_SCOPES
from app.core.exceptions import BadRequestError, ConflictError, EntityNotFoundError
from app.core.process_config import DEFAULT_ERNTEFENSTER_TEMPLATES, DEFAULT_PROCESS_VARIANTS
from app.core.workflow_definitions import merge_workflow_variants

from app.api.v1.schemas.admin_core_schemas import (
    AdminApiKeyCreate,
    AdminApiKeyOut,
    AdminApiKeySecretOut,
    AdminApiKeyUpdate,
    AdminAuditOut,
    AdminRoleCreate,
    AdminRoleOut,
    AdminRoleUpdate,
    AdminUserCreate,
    AdminUserOut,
    AdminUserUpdate,
    AgentManifestExampleOut,
    AgentManifestLinkOut,
    AgentManifestOut,
    ErntefensterCampaignOut,
    ErntefensterFromTemplateIn,
    ErntefensterTemplateOut,
    PolicyOverridesOut,
    ProcessVariantsOut,
    WorkflowSandboxCampaignMatchOut,
    WorkflowSandboxPreviewIn,
    WorkflowSandboxPreviewOut,
)


ROLE_DESCRIPTIONS: dict[str, str] = {
    "admin": "Vollzugriff auf System- und Fachfunktionen",
    "manager": "Freigaben, Steuerung und Auswertungen",
    "controller": "Controlling- und Abschlussfunktionen",
    "operator": "Operative Bearbeitung der Kernprozesse",
}


# ── Pure helpers ─────────────────────────────────────────────────────────────


def _parse_roles(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [str(role).strip() for role in raw if str(role).strip()]
    if raw is None:
        return []
    if isinstance(raw, str):
        value = raw.strip()
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(role).strip() for role in parsed if str(role).strip()]
        except Exception:  # noqa: BLE001 — JSON parse failed, fallback to comma-split
            pass
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def _to_iso(ts: datetime | None) -> str:
    return (ts or datetime.utcnow()).isoformat()


def _split_name(first_name: str | None, last_name: str | None, name: str | None) -> tuple[str, str]:
    if first_name or last_name:
        return (first_name or "").strip(), (last_name or "").strip()
    if not name:
        return "", ""
    parts = [part for part in name.strip().split(" ") if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]


def _role_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9_\-]", "-", value.lower().strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or f"role-{uuid4().hex[:8]}"


def _hash_api_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _new_api_token() -> str:
    return f"vak_{secrets.token_urlsafe(32)}"


def _to_api_key_out(row: dict[str, Any]) -> AdminApiKeyOut:
    scopes = row.get("scopes")
    allowlist = row.get("ip_allowlist")
    return AdminApiKeyOut(
        id=str(row["id"]),
        name=str(row["name"]),
        key_prefix=str(row["key_prefix"]),
        scopes=[str(item) for item in (scopes or []) if str(item).strip()],
        ip_allowlist=[str(item) for item in (allowlist or []) if str(item).strip()],
        rate_limit_per_minute=row.get("rate_limit_per_minute"),
        expires_at=_to_iso(row["expires_at"]) if row.get("expires_at") else None,
        last_used_at=_to_iso(row["last_used_at"]) if row.get("last_used_at") else None,
        status=str(row["status"]),
        created_at=_to_iso(row["created_at"]),
    )


class AdminCoreService:
    """Tenant-scoped service for the admin/settings surface."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Tenant settings (JSON blob in domain_shared.tenants.settings) ────────

    def load_tenant_settings(self) -> dict[str, Any]:
        """Public accessor for the tenant settings blob (used cross-domain)."""
        return self._load_tenant_settings()

    def _load_tenant_settings(self) -> dict[str, Any]:
        row = self.db.execute(
            text("SELECT settings FROM domain_shared.tenants WHERE id = :tenant_id"),
            {"tenant_id": self.tenant_id},
        ).first()
        if not row:
            raise EntityNotFoundError("Tenant", self.tenant_id)
        raw = row[0]
        if not raw:
            return {}
        if isinstance(raw, dict):
            return raw
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:  # noqa: BLE001 — corrupt settings JSON degrades to empty config
            return {}

    def _save_tenant_settings(self, settings: dict[str, Any]) -> None:
        self.db.execute(
            text("UPDATE domain_shared.tenants SET settings = :settings, updated_at = NOW() WHERE id = :tenant_id"),
            {"tenant_id": self.tenant_id, "settings": json.dumps(settings)},
        )

    # ── Role definitions (system roles + tenant custom roles) ────────────────

    def _load_role_definitions(self) -> dict[str, dict[str, Any]]:
        roles: dict[str, dict[str, Any]] = {
            role_id: {
                "id": role_id,
                "name": role_id,
                "beschreibung": ROLE_DESCRIPTIONS.get(role_id, "Systemrolle"),
                "rechte_liste": sorted(set(scope_list)),
                "is_system": True,
            }
            for role_id, scope_list in ROLE_SCOPES.items()
        }

        settings = self._load_tenant_settings()
        custom_entries = settings.get("admin_roles") if isinstance(settings, dict) else None
        if isinstance(custom_entries, dict):
            for role_id, payload in custom_entries.items():
                if not isinstance(payload, dict):
                    continue
                rights = payload.get("rechte_liste")
                roles[role_id] = {
                    "id": role_id,
                    "name": str(payload.get("name") or role_id),
                    "beschreibung": str(payload.get("beschreibung") or ""),
                    "rechte_liste": [str(item) for item in (rights or []) if str(item).strip()],
                    "is_system": bool(payload.get("is_system", role_id in ROLE_SCOPES)),
                }
        return roles

    def _persist_custom_role(self, role_id: str, role_payload: dict[str, Any]) -> None:
        settings = self._load_tenant_settings()
        roles = settings.get("admin_roles") if isinstance(settings.get("admin_roles"), dict) else {}
        roles[role_id] = role_payload
        settings["admin_roles"] = roles
        self._save_tenant_settings(settings)

    def _delete_custom_role(self, role_id: str) -> bool:
        settings = self._load_tenant_settings()
        roles = settings.get("admin_roles")
        if not isinstance(roles, dict) or role_id not in roles:
            return False
        del roles[role_id]
        settings["admin_roles"] = roles
        self._save_tenant_settings(settings)
        return True

    # ── Audit log ────────────────────────────────────────────────────────────

    def _audit_log_exists(self) -> bool:
        return (
            self.db.execute(
                text(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'infrastructure' AND table_name = 'audit_log'
                    LIMIT 1
                    """
                )
            ).first()
            is not None
        )

    def _write_admin_audit(self, user_id: str, action: str, resource_type: str, resource_id: str) -> None:
        if not self._audit_log_exists():
            return
        try:
            resource_uuid = str(UUID(str(resource_id)))
        except (ValueError, TypeError):
            # audit_log.resource_id is UUID in this schema; derive stable UUID for non-UUID resource keys.
            resource_uuid = str(uuid5(NAMESPACE_URL, f"{resource_type}:{resource_id}"))

        self.db.execute(
            text(
                """
                INSERT INTO infrastructure.audit_log
                  (id, user_id, action, resource_type, resource_id, old_values, new_values, ip_address, user_agent, timestamp)
                VALUES
                  (:id, :user_id, :action, :resource_type, :resource_id, '{}'::jsonb, '{}'::jsonb, NULL, NULL, NOW())
                """
            ),
            {
                "id": str(uuid4()),
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_uuid,
            },
        )

    def _resolve_actor_user_id(self) -> str | None:
        row = self.db.execute(
            text(
                """
                SELECT id
                FROM domain_shared.users
                WHERE tenant_id = :tenant_id
                ORDER BY created_at ASC
                LIMIT 1
                """
            ),
            {"tenant_id": self.tenant_id},
        ).first()
        return str(row[0]) if row else None

    # ── Users ────────────────────────────────────────────────────────────────

    def list_users(self, search: str | None) -> list[AdminUserOut]:
        params: dict[str, Any] = {"tenant_id": self.tenant_id}
        where = "WHERE tenant_id = :tenant_id"
        if search and search.strip():
            params["needle"] = f"%{search.strip()}%"
            where += """
                AND (
                    username ILIKE :needle
                    OR email ILIKE :needle
                    OR first_name ILIKE :needle
                    OR last_name ILIKE :needle
                )
            """

        items = self.db.execute(
            text(
                f"""
                SELECT id, username, email, first_name, last_name, is_active, roles, created_at, updated_at
                FROM domain_shared.users
                {where}
                ORDER BY last_name ASC, first_name ASC
                """
            ),
            params,
        ).mappings().all()
        return [self._user_row_to_out(row) for row in items]

    def get_user(self, user_id: str) -> AdminUserOut:
        row = self.db.execute(
            text(
                """
                SELECT id, username, email, first_name, last_name, is_active, roles, created_at, updated_at
                FROM domain_shared.users
                WHERE id = :user_id AND tenant_id = :tenant_id
                """
            ),
            {"user_id": user_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not row:
            raise EntityNotFoundError("User", user_id)
        return self._user_row_to_out(row)

    @staticmethod
    def _user_row_to_out(row: Any) -> AdminUserOut:
        roles = _parse_roles(row["roles"])
        display_name = f"{(row['first_name'] or '').strip()} {(row['last_name'] or '').strip()}".strip()
        return AdminUserOut(
            id=str(row["id"]),
            name=display_name or row["username"] or str(row["id"]),
            email=row["email"],
            rolle=roles[0] if roles else "ohne",
            status="aktiv" if bool(row["is_active"]) else "inaktiv",
            letzteAnmeldung=_to_iso(row["updated_at"] or row["created_at"]),
        )

    def create_user(self, payload: AdminUserCreate) -> AdminUserOut:
        available_roles = self._load_role_definitions()
        if payload.rolle not in available_roles:
            raise BadRequestError(f"Unknown role: {payload.rolle}")

        existing = self.db.execute(
            text(
                """
                SELECT id
                FROM domain_shared.users
                WHERE username = :username OR email = :email
                LIMIT 1
                """
            ),
            {"username": payload.username, "email": payload.email},
        ).first()
        if existing:
            raise ConflictError("Username or email already exists")

        first_name, last_name = _split_name(payload.first_name, payload.last_name, payload.name)
        user_id = str(uuid4())
        self.db.execute(
            text(
                """
                INSERT INTO domain_shared.users
                  (id, keycloak_id, username, email, first_name, last_name, is_active, roles, tenant_id, preferences, created_at, updated_at)
                VALUES
                  (:id, :keycloak_id, :username, :email, :first_name, :last_name, :is_active, :roles, :tenant_id, '{}'::jsonb, NOW(), NOW())
                """
            ),
            {
                "id": user_id,
                "keycloak_id": f"local-{user_id}",
                "username": payload.username,
                "email": payload.email,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": payload.status == "aktiv",
                "roles": [payload.rolle],
                "tenant_id": self.tenant_id,
            },
        )
        self._write_admin_audit(user_id, "admin.user.created", "user", user_id)
        self.db.commit()
        return self.get_user(user_id)

    def update_user(self, user_id: str, payload: AdminUserUpdate) -> AdminUserOut:
        current = self.db.execute(
            text(
                """
                SELECT id, username, email, first_name, last_name, is_active, roles
                FROM domain_shared.users
                WHERE id = :user_id AND tenant_id = :tenant_id
                """
            ),
            {"user_id": user_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not current:
            raise EntityNotFoundError("User", user_id)

        if payload.rolle is not None:
            available_roles = self._load_role_definitions()
            if payload.rolle not in available_roles:
                raise BadRequestError(f"Unknown role: {payload.rolle}")

        if payload.email and payload.email != current["email"]:
            conflict = self.db.execute(
                text("SELECT id FROM domain_shared.users WHERE email = :email AND id <> :id LIMIT 1"),
                {"email": payload.email, "id": user_id},
            ).first()
            if conflict:
                raise ConflictError("Email already exists")

        first_name = current["first_name"]
        last_name = current["last_name"]
        if payload.first_name is not None or payload.last_name is not None or payload.name is not None:
            first_name, last_name = _split_name(payload.first_name, payload.last_name, payload.name)

        roles = _parse_roles(current["roles"])
        if payload.rolle is not None:
            roles = [payload.rolle]

        is_active = bool(current["is_active"])
        if payload.status is not None:
            is_active = payload.status == "aktiv"

        self.db.execute(
            text(
                """
                UPDATE domain_shared.users
                SET email = :email,
                    first_name = :first_name,
                    last_name = :last_name,
                    roles = :roles,
                    is_active = :is_active,
                    updated_at = NOW()
                WHERE id = :user_id AND tenant_id = :tenant_id
                """
            ),
            {
                "user_id": user_id,
                "tenant_id": self.tenant_id,
                "email": payload.email if payload.email is not None else current["email"],
                "first_name": first_name,
                "last_name": last_name,
                "roles": roles,
                "is_active": is_active,
            },
        )
        self._write_admin_audit(user_id, "admin.user.updated", "user", user_id)
        self.db.commit()
        return self.get_user(user_id)

    def delete_user(self, user_id: str) -> None:
        row = self.db.execute(
            text("SELECT id FROM domain_shared.users WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": user_id, "tenant_id": self.tenant_id},
        ).first()
        if not row:
            raise EntityNotFoundError("User", user_id)

        self.db.execute(
            text(
                """
                UPDATE domain_shared.users
                SET is_active = false,
                    updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {"id": user_id, "tenant_id": self.tenant_id},
        )
        self._write_admin_audit(user_id, "admin.user.deactivated", "user", user_id)
        self.db.commit()

    # ── Roles ────────────────────────────────────────────────────────────────

    def list_roles(self) -> list[AdminRoleOut]:
        users = self.db.execute(
            text(
                """
                SELECT id, roles
                FROM domain_shared.users
                WHERE tenant_id = :tenant_id
                """
            ),
            {"tenant_id": self.tenant_id},
        ).mappings().all()

        users_per_role: dict[str, int] = {}
        for user in users:
            for role in _parse_roles(user["roles"]):
                users_per_role[role] = users_per_role.get(role, 0) + 1

        all_roles = self._load_role_definitions()
        rows: list[AdminRoleOut] = []
        for role_id in sorted(all_roles.keys()):
            role = all_roles[role_id]
            rows.append(
                AdminRoleOut(
                    id=role_id,
                    name=str(role.get("name") or role_id),
                    beschreibung=str(role.get("beschreibung") or ""),
                    benutzer=users_per_role.get(role_id, 0),
                    rechte=len({str(item) for item in (role.get("rechte_liste") or []) if str(item).strip()}),
                )
            )
        return rows

    def _role_out(self, role_id: str, action: str) -> AdminRoleOut:
        for row in self.list_roles():
            if row.id == role_id:
                return row
        raise EntityNotFoundError("Role", role_id)

    def create_role(self, payload: AdminRoleCreate) -> AdminRoleOut:
        role_id = payload.id.strip() if payload.id else _role_slug(payload.name)
        roles = self._load_role_definitions()
        if role_id in roles:
            raise ConflictError(f"Role already exists: {role_id}")

        self._persist_custom_role(
            role_id,
            {
                "name": payload.name,
                "beschreibung": payload.beschreibung or "",
                "rechte_liste": [str(item).strip() for item in payload.rechte_liste if str(item).strip()],
                "is_system": False,
            },
        )
        actor_user_id = self._resolve_actor_user_id()
        if actor_user_id:
            self._write_admin_audit(actor_user_id, "admin.role.created", "role", role_id)
        self.db.commit()
        return self._role_out(role_id, "created")

    def update_role(self, role_id: str, payload: AdminRoleUpdate) -> AdminRoleOut:
        roles = self._load_role_definitions()
        current = roles.get(role_id)
        if not current:
            raise EntityNotFoundError("Role", role_id)
        if bool(current.get("is_system", role_id in ROLE_SCOPES)):
            raise BadRequestError("System roles are read-only")

        role_payload = {
            "name": payload.name if payload.name is not None else str(current.get("name") or role_id),
            "beschreibung": payload.beschreibung if payload.beschreibung is not None else str(current.get("beschreibung") or ""),
            "rechte_liste": (
                [str(item).strip() for item in payload.rechte_liste if str(item).strip()]
                if payload.rechte_liste is not None
                else [str(item) for item in (current.get("rechte_liste") or []) if str(item).strip()]
            ),
            "is_system": bool(current.get("is_system", role_id in ROLE_SCOPES)),
        }
        self._persist_custom_role(role_id, role_payload)
        actor_user_id = self._resolve_actor_user_id()
        if actor_user_id:
            self._write_admin_audit(actor_user_id, "admin.role.updated", "role", role_id)
        self.db.commit()
        return self._role_out(role_id, "updated")

    def delete_role(self, role_id: str) -> None:
        users = self.db.execute(
            text(
                """
                SELECT id, roles
                FROM domain_shared.users
                WHERE tenant_id = :tenant_id
                """
            ),
            {"tenant_id": self.tenant_id},
        ).mappings().all()
        assigned_users = [row["id"] for row in users if role_id in _parse_roles(row["roles"])]
        if assigned_users:
            raise ConflictError("Role is assigned to users and cannot be deleted")

        if not self._delete_custom_role(role_id):
            raise BadRequestError("System roles cannot be deleted directly")

        actor_user_id = self._resolve_actor_user_id()
        if actor_user_id:
            self._write_admin_audit(actor_user_id, "admin.role.deleted", "role", role_id)
        self.db.commit()

    # ── Audit log query ──────────────────────────────────────────────────────

    def list_audit_log(self, search: str | None, limit: int) -> list[AdminAuditOut]:
        if not self._audit_log_exists():
            return []

        params: dict[str, Any] = {"limit": limit}
        where = ""
        if search and search.strip():
            params["needle"] = f"%{search.strip()}%"
            where = """
                WHERE (
                    action ILIKE :needle
                    OR resource_type ILIKE :needle
                    OR resource_id::text ILIKE :needle
                    OR user_id::text ILIKE :needle
                )
            """

        rows = self.db.execute(
            text(
                f"""
                SELECT id, user_id, action, resource_type, resource_id, timestamp
                FROM infrastructure.audit_log
                {where}
                ORDER BY timestamp DESC
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()
        result: list[AdminAuditOut] = []
        for row in rows:
            action_text = (row["action"] or "").lower()
            failed = any(token in action_text for token in ("fail", "error", "denied", "blocked"))
            result.append(
                AdminAuditOut(
                    id=str(row["id"]),
                    zeitstempel=_to_iso(row["timestamp"]),
                    benutzer=str(row["user_id"]),
                    aktion=row["action"],
                    objekt=f"{row['resource_type']}:{row['resource_id']}",
                    status="fehler" if failed else "erfolg",
                )
            )
        return result

    # ── API keys ─────────────────────────────────────────────────────────────

    def list_api_keys(self, include_revoked: bool) -> list[AdminApiKeyOut]:
        where = "WHERE tenant_id = :tenant_id"
        if not include_revoked:
            where += " AND status = 'active'"
        rows = self.db.execute(
            text(
                f"""
                SELECT id, name, key_prefix, scopes, ip_allowlist, rate_limit_per_minute, expires_at, last_used_at, status, created_at
                FROM domain_shared.api_keys
                {where}
                ORDER BY created_at DESC
                """
            ),
            {"tenant_id": self.tenant_id},
        ).mappings().all()
        return [_to_api_key_out(dict(row)) for row in rows]

    def create_api_key(self, payload: AdminApiKeyCreate) -> AdminApiKeySecretOut:
        duplicate = self.db.execute(
            text(
                """
                SELECT id
                FROM domain_shared.api_keys
                WHERE tenant_id = :tenant_id AND lower(name) = lower(:name) AND status = 'active'
                LIMIT 1
                """
            ),
            {"tenant_id": self.tenant_id, "name": payload.name.strip()},
        ).first()
        if duplicate:
            raise ConflictError("API key name already exists")

        token = _new_api_token()
        key_prefix = token[:16]
        key_id = str(uuid4())
        actor_user_id = self._resolve_actor_user_id()
        self.db.execute(
            text(
                """
                INSERT INTO domain_shared.api_keys
                  (id, tenant_id, name, key_prefix, key_hash, scopes, ip_allowlist, rate_limit_per_minute, expires_at,
                   status, created_by, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :name, :key_prefix, :key_hash, CAST(:scopes AS jsonb), CAST(:ip_allowlist AS jsonb), :rate_limit,
                   :expires_at, 'active', :created_by, NOW(), NOW())
                """
            ),
            {
                "id": key_id,
                "tenant_id": self.tenant_id,
                "name": payload.name.strip(),
                "key_prefix": key_prefix,
                "key_hash": _hash_api_token(token),
                "scopes": json.dumps([str(item).strip() for item in payload.scopes if str(item).strip()]),
                "ip_allowlist": json.dumps([str(item).strip() for item in payload.ip_allowlist if str(item).strip()]),
                "rate_limit": payload.rate_limit_per_minute,
                "expires_at": payload.expires_at,
                "created_by": actor_user_id,
            },
        )
        if actor_user_id:
            self._write_admin_audit(actor_user_id, "admin.api_key.created", "api_key", key_id)
        self.db.commit()
        return AdminApiKeySecretOut(
            id=key_id,
            name=payload.name.strip(),
            key_prefix=key_prefix,
            token=token,
            created_at=_to_iso(datetime.utcnow()),
        )

    def update_api_key(self, key_id: str, payload: AdminApiKeyUpdate) -> AdminApiKeyOut:
        current = self.db.execute(
            text(
                """
                SELECT id, name, key_prefix, scopes, ip_allowlist, rate_limit_per_minute, expires_at, last_used_at, status, created_at
                FROM domain_shared.api_keys
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {"id": key_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not current:
            raise EntityNotFoundError("API key", key_id)
        if current["status"] != "active":
            raise BadRequestError("Only active API keys can be updated")

        new_name = payload.name.strip() if payload.name is not None else current["name"]
        if payload.name is not None and new_name.lower() != str(current["name"]).lower():
            conflict = self.db.execute(
                text(
                    """
                    SELECT id
                    FROM domain_shared.api_keys
                    WHERE tenant_id = :tenant_id AND lower(name) = lower(:name) AND id <> :id AND status = 'active'
                    LIMIT 1
                    """
                ),
                {"tenant_id": self.tenant_id, "name": new_name, "id": key_id},
            ).first()
            if conflict:
                raise ConflictError("API key name already exists")

        scopes = payload.scopes if payload.scopes is not None else (current.get("scopes") or [])
        allowlist = payload.ip_allowlist if payload.ip_allowlist is not None else (current.get("ip_allowlist") or [])
        rate_limit = payload.rate_limit_per_minute if payload.rate_limit_per_minute is not None else current["rate_limit_per_minute"]
        expires_at = payload.expires_at if payload.expires_at is not None else current["expires_at"]

        self.db.execute(
            text(
                """
                UPDATE domain_shared.api_keys
                SET name = :name,
                    scopes = CAST(:scopes AS jsonb),
                    ip_allowlist = CAST(:ip_allowlist AS jsonb),
                    rate_limit_per_minute = :rate_limit,
                    expires_at = :expires_at,
                    updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {
                "id": key_id,
                "tenant_id": self.tenant_id,
                "name": new_name,
                "scopes": json.dumps([str(item).strip() for item in scopes if str(item).strip()]),
                "ip_allowlist": json.dumps([str(item).strip() for item in allowlist if str(item).strip()]),
                "rate_limit": rate_limit,
                "expires_at": expires_at,
            },
        )
        actor_user_id = self._resolve_actor_user_id()
        if actor_user_id:
            self._write_admin_audit(actor_user_id, "admin.api_key.updated", "api_key", key_id)
        self.db.commit()

        row = self.db.execute(
            text(
                """
                SELECT id, name, key_prefix, scopes, ip_allowlist, rate_limit_per_minute, expires_at, last_used_at, status, created_at
                FROM domain_shared.api_keys
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {"id": key_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        return _to_api_key_out(dict(row))

    def rotate_api_key(self, key_id: str) -> AdminApiKeySecretOut:
        current = self.db.execute(
            text(
                """
                SELECT id, name, status
                FROM domain_shared.api_keys
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {"id": key_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not current:
            raise EntityNotFoundError("API key", key_id)
        if current["status"] != "active":
            raise BadRequestError("Only active API keys can be rotated")

        token = _new_api_token()
        key_prefix = token[:16]
        self.db.execute(
            text(
                """
                UPDATE domain_shared.api_keys
                SET key_prefix = :key_prefix,
                    key_hash = :key_hash,
                    updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {
                "id": key_id,
                "tenant_id": self.tenant_id,
                "key_prefix": key_prefix,
                "key_hash": _hash_api_token(token),
            },
        )
        actor_user_id = self._resolve_actor_user_id()
        if actor_user_id:
            self._write_admin_audit(actor_user_id, "admin.api_key.rotated", "api_key", key_id)
        self.db.commit()
        return AdminApiKeySecretOut(
            id=str(current["id"]),
            name=str(current["name"]),
            key_prefix=key_prefix,
            token=token,
            created_at=_to_iso(datetime.utcnow()),
        )

    def revoke_api_key(self, key_id: str) -> None:
        row = self.db.execute(
            text(
                """
                SELECT id, status
                FROM domain_shared.api_keys
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {"id": key_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not row:
            raise EntityNotFoundError("API key", key_id)
        if row["status"] == "revoked":
            return

        self.db.execute(
            text(
                """
                UPDATE domain_shared.api_keys
                SET status = 'revoked',
                    revoked_at = NOW(),
                    updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {"id": key_id, "tenant_id": self.tenant_id},
        )
        actor_user_id = self._resolve_actor_user_id()
        if actor_user_id:
            self._write_admin_audit(actor_user_id, "admin.api_key.revoked", "api_key", key_id)
        self.db.commit()

    # ── Process variants (Gap 009) ───────────────────────────────────────────

    def get_process_variants(self) -> ProcessVariantsOut:
        settings = self._load_tenant_settings()
        custom = settings.get("process_variants")
        if isinstance(custom, dict):
            merged = dict(DEFAULT_PROCESS_VARIANTS)
            for k, v in custom.items():
                if isinstance(v, dict):
                    merged[k] = {**merged.get(k, {}), **v}
            return ProcessVariantsOut(variants=merged)
        return ProcessVariantsOut(variants=DEFAULT_PROCESS_VARIANTS)

    def put_process_variants(self, payload: ProcessVariantsOut) -> ProcessVariantsOut:
        settings = self._load_tenant_settings()
        existing = settings.get("process_variants")
        if not isinstance(existing, dict):
            existing = {}
        updated = {**existing, **payload.variants}
        settings["process_variants"] = updated
        self._save_tenant_settings(settings)
        self.db.commit()
        return ProcessVariantsOut(variants={**DEFAULT_PROCESS_VARIANTS, **updated})

    # ── Policy overrides (Gap 014) ───────────────────────────────────────────

    def get_policy_overrides(self) -> PolicyOverridesOut:
        settings = self._load_tenant_settings()
        overrides = settings.get("policy_overrides")
        if isinstance(overrides, dict):
            return PolicyOverridesOut(overrides=overrides)
        return PolicyOverridesOut(overrides={})

    def put_policy_overrides(self, payload: PolicyOverridesOut) -> PolicyOverridesOut:
        for rule_id, ov in (payload.overrides or {}).items():
            if isinstance(ov, dict) and not ov.get("reason"):
                raise BadRequestError(
                    f"policy_overrides.{rule_id}: 'reason' ist Pflichtfeld (Gap 014)"
                )
        settings = self._load_tenant_settings()
        settings["policy_overrides"] = payload.overrides or {}
        self._save_tenant_settings(settings)
        self.db.commit()
        return PolicyOverridesOut(overrides=settings.get("policy_overrides", {}))

    # ── Erntefenster (Gap 005) ───────────────────────────────────────────────

    @staticmethod
    def get_erntefenster_templates() -> list[ErntefensterTemplateOut]:
        return [
            ErntefensterTemplateOut(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                process_key=t["process_key"],
                default_start_mmdd=t["default_start_mmdd"],
                default_end_mmdd=t["default_end_mmdd"],
                product_groups=t.get("product_groups", []),
            )
            for t in DEFAULT_ERNTEFENSTER_TEMPLATES
        ]

    def get_erntefenster_campaigns(self) -> list[ErntefensterCampaignOut]:
        settings = self._load_tenant_settings()
        campaigns = settings.get("erntefenster_campaigns")
        if not isinstance(campaigns, list):
            return []
        return [ErntefensterCampaignOut(**c) for c in campaigns if isinstance(c, dict)]

    def create_erntefenster_from_template(self, payload: ErntefensterFromTemplateIn) -> ErntefensterCampaignOut:
        template = next((t for t in DEFAULT_ERNTEFENSTER_TEMPLATES if t["id"] == payload.template_id), None)
        if not template:
            raise EntityNotFoundError("Vorlage", payload.template_id)

        start_mmdd = payload.start_mmdd or template["default_start_mmdd"]
        end_mmdd = payload.end_mmdd or template["default_end_mmdd"]
        campaign = {
            "id": str(uuid4()),
            "template_id": payload.template_id,
            "name": payload.name,
            "start_date": f"{payload.year}-{start_mmdd}",
            "end_date": f"{payload.year}-{end_mmdd}",
            "process_key": template["process_key"],
            "product_groups": template.get("product_groups", []),
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        settings = self._load_tenant_settings()
        campaigns = settings.get("erntefenster_campaigns")
        if not isinstance(campaigns, list):
            campaigns = []
        campaigns.append(campaign)
        settings["erntefenster_campaigns"] = campaigns
        self._save_tenant_settings(settings)
        self.db.commit()
        return ErntefensterCampaignOut(**campaign)

    # ── Workflow sandbox (Gap 012) ───────────────────────────────────────────

    @staticmethod
    def _campaign_matches_preview(
        campaign: dict[str, Any],
        *,
        simulation_date: date,
        process_key: str,
        campaign_id: str | None,
        product_group: str | None,
    ) -> WorkflowSandboxCampaignMatchOut | None:
        if campaign_id and str(campaign.get("id")) != campaign_id:
            return None
        if str(campaign.get("process_key")) != process_key:
            return None

        try:
            start_date = date.fromisoformat(str(campaign.get("start_date")))
            end_date = date.fromisoformat(str(campaign.get("end_date")))
        except Exception:  # noqa: BLE001 — malformed campaign dates are skipped, not fatal
            return None

        normalized_product_group = (product_group or "").strip().lower()
        campaign_product_groups = [str(group) for group in campaign.get("product_groups") or []]
        product_group_match = not normalized_product_group or normalized_product_group in {
            group.lower() for group in campaign_product_groups
        }

        return WorkflowSandboxCampaignMatchOut(
            id=str(campaign.get("id")),
            name=str(campaign.get("name") or ""),
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            process_key=process_key,
            product_groups=campaign_product_groups,
            in_window=start_date <= simulation_date <= end_date,
            product_group_match=product_group_match,
        )

    def preview_workflow_sandbox(self, payload: WorkflowSandboxPreviewIn) -> WorkflowSandboxPreviewOut:
        settings = self._load_tenant_settings()
        variants = settings.get("process_variants")
        merged_variants = merge_workflow_variants(
            DEFAULT_PROCESS_VARIANTS,
            variants,
            tenant_id=self.tenant_id,
        )

        process_variant = merged_variants.get(payload.process_key)
        if process_variant is None:
            raise EntityNotFoundError("Prozess", payload.process_key)

        simulation_date = payload.simulation_date or date.today()
        campaigns = settings.get("erntefenster_campaigns")
        matches: list[WorkflowSandboxCampaignMatchOut] = []
        if isinstance(campaigns, list):
            for campaign in campaigns:
                if not isinstance(campaign, dict):
                    continue
                preview_match = self._campaign_matches_preview(
                    campaign,
                    simulation_date=simulation_date,
                    process_key=payload.process_key,
                    campaign_id=payload.campaign_id,
                    product_group=payload.product_group,
                )
                if preview_match is not None:
                    matches.append(preview_match)

        warnings: list[str] = []
        if payload.campaign_id and not matches:
            warnings.append("Die ausgewaehlte Kampagne passt nicht zum gewaehlten Prozess oder existiert nicht mehr.")
        if matches and not any(match.in_window for match in matches):
            warnings.append("Es gibt eine passende Kampagne, aber das Simulationsdatum liegt ausserhalb des Erntefensters.")
        if payload.product_group and matches and not any(match.product_group_match for match in matches):
            warnings.append("Keine passende Kampagne deckt die gewaehlte Produktgruppe ab.")
        if not matches:
            warnings.append("Keine saisonale Kampagne aktiv. Die Vorschau basiert nur auf der Prozessvariante.")

        import dataclasses as _dc
        if isinstance(process_variant, dict):
            definition_dump = process_variant
        elif hasattr(process_variant, "model_dump"):
            definition_dump = process_variant.model_dump()
        elif _dc.is_dataclass(process_variant):
            definition_dump = _dc.asdict(process_variant)
        else:
            definition_dump = {}
        steps = definition_dump.get("steps")
        required_roles = definition_dump.get("required_roles")
        step_sla = definition_dump.get("step_sla")

        return WorkflowSandboxPreviewOut(
            process_key=payload.process_key,
            simulation_date=simulation_date.isoformat(),
            definition_version=definition_dump.get("version", 1),
            definition_origin=definition_dump.get("origin", "default"),
            definition_status=definition_dump.get("status", "active"),
            steps=[str(step) for step in steps] if isinstance(steps, list) else [],
            required_roles={
                str(step): [str(role) for role in roles]
                for step, roles in (required_roles or {}).items()
                if isinstance(roles, list)
            }
            if isinstance(required_roles, dict)
            else {},
            step_sla={
                str(step): value
                for step, value in (step_sla or {}).items()
                if isinstance(value, dict)
            }
            if isinstance(step_sla, dict)
            else {},
            description=str(definition_dump.get("description") or "") or None,
            matched_campaigns=matches,
            warnings=warnings,
        )

    # ── Agent manifest (Gap 048, static) ─────────────────────────────────────

    @staticmethod
    def agent_manifest() -> AgentManifestOut:
        return AgentManifestOut(
            version="2026-03-08",
            generated_at=datetime.utcnow().isoformat() + "Z",
            auth={
                "scheme": "bearer",
                "oidc": True,
                "tenant_header": "X-Tenant-ID",
                "dev_token_supported": True,
                "api_keys": "planned_in_mainline",
            },
            headers=[
                "Authorization: Bearer <access_token>",
                "X-Tenant-ID: <tenant-uuid>",
                "Content-Type: application/json",
            ],
            links=[
                AgentManifestLinkOut(
                    rel="openapi",
                    href="/api/v1/openapi.json",
                    description="OpenAPI JSON fuer Codegen und Agent-Tools",
                ),
                AgentManifestLinkOut(
                    rel="swagger",
                    href="/docs",
                    description="Interaktive Swagger-UI",
                ),
                AgentManifestLinkOut(
                    rel="redoc",
                    href="/redoc",
                    description="Alternative API-Dokumentation",
                ),
                AgentManifestLinkOut(
                    rel="agent-docs",
                    href="/docs/AGENT-INTEGRATION.md",
                    description="Projektinterne Integrationsanleitung",
                ),
            ],
            examples=[
                AgentManifestExampleOut(
                    name="benchmark",
                    description="Branchenbenchmark je Genossenschaft",
                    method="GET",
                    path="/api/v1/analytics/benchmark",
                    required_headers=["Authorization", "X-Tenant-ID"],
                ),
                AgentManifestExampleOut(
                    name="esg_report",
                    description="ESG-Report fuer Nachhaltigkeitsauswertungen",
                    method="GET",
                    path="/api/v1/sustainability/esg-report?year=2025",
                    required_headers=["Authorization", "X-Tenant-ID"],
                ),
                AgentManifestExampleOut(
                    name="data_quality_validate",
                    description="Datenqualitaetsregeln gegen eine Entity pruefen",
                    method="POST",
                    path="/api/v1/admin/data-quality/validate",
                    required_headers=["Authorization", "X-Tenant-ID", "Content-Type"],
                ),
                AgentManifestExampleOut(
                    name="mcp_analytics_kpis",
                    description="MCP-BFF fuer Copilot-/Agenten-Queries",
                    method="POST",
                    path="/api/mcp/analytics/kpis",
                    required_headers=["Authorization", "X-Tenant-ID", "Content-Type"],
                ),
            ],
            notes=[
                "Jede Anfrage muss tenant-isoliert ueber X-Tenant-ID erfolgen.",
                "Dedizierte Agent-API-Keys und produktives Rate-Limiting liegen im Hauptstrang.",
                "OpenAPI ist die bevorzugte Quelle fuer Codegen; MCP ergaenzt interaktive Copilot-Pfade.",
            ],
        )
