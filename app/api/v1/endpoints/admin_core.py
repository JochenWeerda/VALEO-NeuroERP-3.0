"""Core admin endpoints used by the settings/admin frontend."""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import date, datetime
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.scopes import ROLE_SCOPES
from app.core.database import get_db
from app.core.process_config import DEFAULT_ERNTEFENSTER_TEMPLATES, DEFAULT_PROCESS_VARIANTS
from app.core.tenant import get_tenant_id
from app.core.workflow_definitions import merge_workflow_variants

router = APIRouter()


class AdminUserOut(BaseModel):
    id: str
    name: str
    email: str
    rolle: str
    status: str
    letzteAnmeldung: str


class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=3, max_length=100)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    name: str | None = Field(default=None, max_length=120)
    rolle: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="aktiv", pattern="^(aktiv|inaktiv)$")


class AdminUserUpdate(BaseModel):
    email: str | None = Field(default=None, min_length=3, max_length=100)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    name: str | None = Field(default=None, max_length=120)
    rolle: str | None = Field(default=None, min_length=1, max_length=50)
    status: str | None = Field(default=None, pattern="^(aktiv|inaktiv)$")


class AdminRoleOut(BaseModel):
    id: str
    name: str
    beschreibung: str
    benutzer: int
    rechte: int


class AdminRoleCreate(BaseModel):
    id: str | None = Field(default=None, max_length=64)
    name: str = Field(..., min_length=1, max_length=64)
    beschreibung: str | None = Field(default="", max_length=255)
    rechte_liste: list[str] = Field(default_factory=list)


class AdminRoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    beschreibung: str | None = Field(default=None, max_length=255)
    rechte_liste: list[str] | None = None


class AdminAuditOut(BaseModel):
    id: str
    zeitstempel: str
    benutzer: str
    aktion: str
    objekt: str
    status: str


class AdminApiKeyOut(BaseModel):
    id: str
    name: str
    key_prefix: str
    scopes: list[str]
    ip_allowlist: list[str]
    rate_limit_per_minute: int | None
    expires_at: str | None
    last_used_at: str | None
    status: str
    created_at: str


class AdminApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    scopes: list[str] = Field(default_factory=list)
    ip_allowlist: list[str] = Field(default_factory=list)
    rate_limit_per_minute: int | None = Field(default=None, ge=1, le=20000)
    expires_at: datetime | None = None


class AdminApiKeyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    scopes: list[str] | None = None
    ip_allowlist: list[str] | None = None
    rate_limit_per_minute: int | None = Field(default=None, ge=1, le=20000)
    expires_at: datetime | None = None


class AdminApiKeySecretOut(BaseModel):
    id: str
    name: str
    key_prefix: str
    token: str
    created_at: str


class AgentManifestLinkOut(BaseModel):
    rel: str
    href: str
    method: str = "GET"
    description: str


class AgentManifestExampleOut(BaseModel):
    name: str
    description: str
    method: str
    path: str
    required_headers: list[str] = Field(default_factory=list)


class AgentManifestOut(BaseModel):
    version: str
    generated_at: str
    auth: dict[str, Any]
    headers: list[str] = Field(default_factory=list)
    links: list[AgentManifestLinkOut] = Field(default_factory=list)
    examples: list[AgentManifestExampleOut] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


ROLE_DESCRIPTIONS: dict[str, str] = {
    "admin": "Vollzugriff auf System- und Fachfunktionen",
    "manager": "Freigaben, Steuerung und Auswertungen",
    "controller": "Controlling- und Abschlussfunktionen",
    "operator": "Operative Bearbeitung der Kernprozesse",
}


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
        except Exception:
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


def _load_tenant_settings(db: Session, tenant_id: str) -> dict[str, Any]:
    row = db.execute(
        text("SELECT settings FROM domain_shared.tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id},
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Tenant not found: {tenant_id}")
    raw = row[0]
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _save_tenant_settings(db: Session, tenant_id: str, settings: dict[str, Any]) -> None:
    db.execute(
        text("UPDATE domain_shared.tenants SET settings = :settings, updated_at = NOW() WHERE id = :tenant_id"),
        {"tenant_id": tenant_id, "settings": json.dumps(settings)},
    )


def _load_role_definitions(db: Session, tenant_id: str) -> dict[str, dict[str, Any]]:
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

    settings = _load_tenant_settings(db, tenant_id)
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


def _persist_custom_role(db: Session, tenant_id: str, role_id: str, role_payload: dict[str, Any]) -> None:
    settings = _load_tenant_settings(db, tenant_id)
    roles = settings.get("admin_roles") if isinstance(settings.get("admin_roles"), dict) else {}
    roles[role_id] = role_payload
    settings["admin_roles"] = roles
    _save_tenant_settings(db, tenant_id, settings)


def _delete_custom_role(db: Session, tenant_id: str, role_id: str) -> bool:
    settings = _load_tenant_settings(db, tenant_id)
    roles = settings.get("admin_roles")
    if not isinstance(roles, dict) or role_id not in roles:
        return False
    del roles[role_id]
    settings["admin_roles"] = roles
    _save_tenant_settings(db, tenant_id, settings)
    return True


def _write_admin_audit(db: Session, user_id: str, action: str, resource_type: str, resource_id: str) -> None:
    has_audit_log = db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'infrastructure' AND table_name = 'audit_log'
            LIMIT 1
            """
        )
    ).first()
    if not has_audit_log:
        return
    try:
        resource_uuid = str(UUID(str(resource_id)))
    except (ValueError, TypeError):
        # audit_log.resource_id is UUID in this schema; derive stable UUID for non-UUID resource keys.
        resource_uuid = str(uuid5(NAMESPACE_URL, f"{resource_type}:{resource_id}"))

    db.execute(
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


def _resolve_actor_user_id(db: Session, tenant_id: str) -> str | None:
    row = db.execute(
        text(
            """
            SELECT id
            FROM domain_shared.users
            WHERE tenant_id = :tenant_id
            ORDER BY created_at ASC
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id},
    ).first()
    return str(row[0]) if row else None


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


@router.get("/benutzer", response_model=list[AdminUserOut])
async def list_admin_users(
    search: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
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

    items = db.execute(
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
    result: list[AdminUserOut] = []
    for row in items:
        roles = _parse_roles(row.roles)
        primary_role = roles[0] if roles else "ohne"
        display_name = f"{(row.first_name or '').strip()} {(row.last_name or '').strip()}".strip()
        result.append(
            AdminUserOut(
                id=str(row.id),
                name=display_name or row.username or str(row.id),
                email=row.email,
                rolle=primary_role,
                status="aktiv" if bool(row.is_active) else "inaktiv",
                letzteAnmeldung=_to_iso(row.updated_at or row.created_at),
            )
        )
    return result


@router.get("/benutzer/{user_id}", response_model=AdminUserOut)
async def get_admin_user(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            """
            SELECT id, username, email, first_name, last_name, is_active, roles, created_at, updated_at
            FROM domain_shared.users
            WHERE id = :user_id AND tenant_id = :tenant_id
            """
        ),
        {"user_id": user_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    roles = _parse_roles(row.roles)
    display_name = f"{(row.first_name or '').strip()} {(row.last_name or '').strip()}".strip()
    return AdminUserOut(
        id=str(row.id),
        name=display_name or row.username or str(row.id),
        email=row.email,
        rolle=roles[0] if roles else "ohne",
        status="aktiv" if bool(row.is_active) else "inaktiv",
        letzteAnmeldung=_to_iso(row.updated_at or row.created_at),
    )


@router.post("/benutzer", response_model=AdminUserOut, status_code=201)
async def create_admin_user(
    payload: AdminUserCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    # Validate target role exists.
    available_roles = _load_role_definitions(db, tenant_id)
    if payload.rolle not in available_roles:
        raise HTTPException(status_code=400, detail=f"Unknown role: {payload.rolle}")

    existing = db.execute(
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
        raise HTTPException(status_code=409, detail="Username or email already exists")

    first_name, last_name = _split_name(payload.first_name, payload.last_name, payload.name)
    user_id = str(uuid4())
    db.execute(
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
            "tenant_id": tenant_id,
        },
    )
    _write_admin_audit(db, user_id, "admin.user.created", "user", user_id)
    db.commit()
    return await get_admin_user(user_id=user_id, tenant_id=tenant_id, db=db)


@router.put("/benutzer/{user_id}", response_model=AdminUserOut)
async def update_admin_user(
    user_id: str,
    payload: AdminUserUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    current = db.execute(
        text(
            """
            SELECT id, username, email, first_name, last_name, is_active, roles
            FROM domain_shared.users
            WHERE id = :user_id AND tenant_id = :tenant_id
            """
        ),
        {"user_id": user_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not current:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.rolle is not None:
        available_roles = _load_role_definitions(db, tenant_id)
        if payload.rolle not in available_roles:
            raise HTTPException(status_code=400, detail=f"Unknown role: {payload.rolle}")

    if payload.email and payload.email != current["email"]:
        conflict = db.execute(
            text("SELECT id FROM domain_shared.users WHERE email = :email AND id <> :id LIMIT 1"),
            {"email": payload.email, "id": user_id},
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail="Email already exists")

    first_name = current["first_name"]
    last_name = current["last_name"]
    if payload.first_name is not None or payload.last_name is not None or payload.name is not None:
        split_first, split_last = _split_name(payload.first_name, payload.last_name, payload.name)
        first_name = split_first
        last_name = split_last

    roles = _parse_roles(current["roles"])
    if payload.rolle is not None:
        roles = [payload.rolle]

    is_active = bool(current["is_active"])
    if payload.status is not None:
        is_active = payload.status == "aktiv"

    db.execute(
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
            "tenant_id": tenant_id,
            "email": payload.email if payload.email is not None else current["email"],
            "first_name": first_name,
            "last_name": last_name,
            "roles": roles,
            "is_active": is_active,
        },
    )
    _write_admin_audit(db, user_id, "admin.user.updated", "user", user_id)
    db.commit()
    return await get_admin_user(user_id=user_id, tenant_id=tenant_id, db=db)


@router.delete("/benutzer/{user_id}", status_code=204)
async def delete_admin_user(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("SELECT id FROM domain_shared.users WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": user_id, "tenant_id": tenant_id},
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    db.execute(
        text(
            """
            UPDATE domain_shared.users
            SET is_active = false,
                updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
            """
        ),
        {"id": user_id, "tenant_id": tenant_id},
    )
    _write_admin_audit(db, user_id, "admin.user.deactivated", "user", user_id)
    db.commit()


@router.get("/rollen", response_model=list[AdminRoleOut])
async def list_admin_roles(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    users = db.execute(
        text(
            """
            SELECT id, roles
            FROM domain_shared.users
            WHERE tenant_id = :tenant_id
            """
        ),
        {"tenant_id": tenant_id},
    ).mappings().all()

    users_per_role: dict[str, int] = {}
    for user in users:
        for role in _parse_roles(user["roles"]):
            users_per_role[role] = users_per_role.get(role, 0) + 1

    all_roles = _load_role_definitions(db, tenant_id)
    rows: list[AdminRoleOut] = []
    for role_id in sorted(all_roles.keys()):
        role = all_roles[role_id]
        rows.append(
            AdminRoleOut(
                id=role_id,
                name=str(role.get("name") or role_id),
                beschreibung=str(role.get("beschreibung") or ""),
                benutzer=users_per_role.get(role_id, 0),
                rechte=len(set([str(item) for item in (role.get("rechte_liste") or []) if str(item).strip()])),
            )
        )
    return rows


@router.post("/rollen", response_model=AdminRoleOut, status_code=201)
async def create_admin_role(
    payload: AdminRoleCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    role_id = payload.id.strip() if payload.id else _role_slug(payload.name)
    roles = _load_role_definitions(db, tenant_id)
    if role_id in roles:
        raise HTTPException(status_code=409, detail=f"Role already exists: {role_id}")

    _persist_custom_role(
        db,
        tenant_id,
        role_id,
        {
            "name": payload.name,
            "beschreibung": payload.beschreibung or "",
            "rechte_liste": [str(item).strip() for item in payload.rechte_liste if str(item).strip()],
            "is_system": False,
        },
    )
    actor_user_id = _resolve_actor_user_id(db, tenant_id)
    if actor_user_id:
        _write_admin_audit(db, actor_user_id, "admin.role.created", "role", role_id)
    db.commit()

    rows = await list_admin_roles(tenant_id=tenant_id, db=db)
    for row in rows:
        if row.id == role_id:
            return row
    raise HTTPException(status_code=500, detail="Role created but not retrievable")


@router.put("/rollen/{role_id}", response_model=AdminRoleOut)
async def update_admin_role(
    role_id: str,
    payload: AdminRoleUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    roles = _load_role_definitions(db, tenant_id)
    current = roles.get(role_id)
    if not current:
        raise HTTPException(status_code=404, detail="Role not found")
    if bool(current.get("is_system", role_id in ROLE_SCOPES)):
        raise HTTPException(status_code=400, detail="System roles are read-only")

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
    _persist_custom_role(db, tenant_id, role_id, role_payload)
    actor_user_id = _resolve_actor_user_id(db, tenant_id)
    if actor_user_id:
        _write_admin_audit(db, actor_user_id, "admin.role.updated", "role", role_id)
    db.commit()

    rows = await list_admin_roles(tenant_id=tenant_id, db=db)
    for row in rows:
        if row.id == role_id:
            return row
    raise HTTPException(status_code=500, detail="Role updated but not retrievable")


@router.delete("/rollen/{role_id}", status_code=204)
async def delete_admin_role(
    role_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    users = db.execute(
        text(
            """
            SELECT id, roles
            FROM domain_shared.users
            WHERE tenant_id = :tenant_id
            """
        ),
        {"tenant_id": tenant_id},
    ).mappings().all()
    assigned_users = [row["id"] for row in users if role_id in _parse_roles(row["roles"])]
    if assigned_users:
        raise HTTPException(status_code=409, detail="Role is assigned to users and cannot be deleted")

    deleted = _delete_custom_role(db, tenant_id, role_id)
    if not deleted:
        raise HTTPException(status_code=400, detail="System roles cannot be deleted directly")

    actor_user_id = _resolve_actor_user_id(db, tenant_id)
    if actor_user_id:
        _write_admin_audit(db, actor_user_id, "admin.role.deleted", "role", role_id)
    db.commit()


@router.get("/audit-log", response_model=list[AdminAuditOut])
async def list_admin_audit_log(
    search: str | None = Query(default=None),
    limit: int = Query(default=250, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _ = tenant_id  # reserved for future tenant-aware audit storage
    has_audit_log = db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'infrastructure' AND table_name = 'audit_log'
            LIMIT 1
            """
        )
    ).first()
    if not has_audit_log:
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

    rows = db.execute(
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


@router.get("/api-keys", response_model=list[AdminApiKeyOut])
async def list_admin_api_keys(
    include_revoked: bool = Query(default=False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = "WHERE tenant_id = :tenant_id"
    if not include_revoked:
        where += " AND status = 'active'"
    rows = db.execute(
        text(
            f"""
            SELECT id, name, key_prefix, scopes, ip_allowlist, rate_limit_per_minute, expires_at, last_used_at, status, created_at
            FROM domain_shared.api_keys
            {where}
            ORDER BY created_at DESC
            """
        ),
        {"tenant_id": tenant_id},
    ).mappings().all()
    return [_to_api_key_out(dict(row)) for row in rows]


@router.get("/agent-manifest", response_model=AgentManifestOut)
async def get_agent_manifest() -> AgentManifestOut:
    """
    Maschinenlesbarer Einstiegspunkt fuer externe Agenten (Gap 048).
    Beschreibt Auth, zentrale Links und Beispiel-Endpunkte fuer OpenAPI-/REST-/MCP-Nutzung.
    """
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


@router.post("/api-keys", response_model=AdminApiKeySecretOut, status_code=201)
async def create_admin_api_key(
    payload: AdminApiKeyCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    duplicate = db.execute(
        text(
            """
            SELECT id
            FROM domain_shared.api_keys
            WHERE tenant_id = :tenant_id AND lower(name) = lower(:name) AND status = 'active'
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id, "name": payload.name.strip()},
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="API key name already exists")

    token = _new_api_token()
    key_prefix = token[:16]
    key_id = str(uuid4())
    actor_user_id = _resolve_actor_user_id(db, tenant_id)
    db.execute(
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
            "tenant_id": tenant_id,
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
        _write_admin_audit(db, actor_user_id, "admin.api_key.created", "api_key", key_id)
    db.commit()
    return AdminApiKeySecretOut(
        id=key_id,
        name=payload.name.strip(),
        key_prefix=key_prefix,
        token=token,
        created_at=_to_iso(datetime.utcnow()),
    )


@router.put("/api-keys/{key_id}", response_model=AdminApiKeyOut)
async def update_admin_api_key(
    key_id: str,
    payload: AdminApiKeyUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    current = db.execute(
        text(
            """
            SELECT id, name, key_prefix, scopes, ip_allowlist, rate_limit_per_minute, expires_at, last_used_at, status, created_at
            FROM domain_shared.api_keys
            WHERE id = :id AND tenant_id = :tenant_id
            """
        ),
        {"id": key_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not current:
        raise HTTPException(status_code=404, detail="API key not found")
    if current["status"] != "active":
        raise HTTPException(status_code=400, detail="Only active API keys can be updated")

    new_name = payload.name.strip() if payload.name is not None else current["name"]
    if payload.name is not None and new_name.lower() != str(current["name"]).lower():
        conflict = db.execute(
            text(
                """
                SELECT id
                FROM domain_shared.api_keys
                WHERE tenant_id = :tenant_id AND lower(name) = lower(:name) AND id <> :id AND status = 'active'
                LIMIT 1
                """
            ),
            {"tenant_id": tenant_id, "name": new_name, "id": key_id},
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail="API key name already exists")

    scopes = payload.scopes if payload.scopes is not None else (current.get("scopes") or [])
    allowlist = payload.ip_allowlist if payload.ip_allowlist is not None else (current.get("ip_allowlist") or [])
    rate_limit = payload.rate_limit_per_minute if payload.rate_limit_per_minute is not None else current["rate_limit_per_minute"]
    expires_at = payload.expires_at if payload.expires_at is not None else current["expires_at"]

    db.execute(
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
            "tenant_id": tenant_id,
            "name": new_name,
            "scopes": json.dumps([str(item).strip() for item in scopes if str(item).strip()]),
            "ip_allowlist": json.dumps([str(item).strip() for item in allowlist if str(item).strip()]),
            "rate_limit": rate_limit,
            "expires_at": expires_at,
        },
    )
    actor_user_id = _resolve_actor_user_id(db, tenant_id)
    if actor_user_id:
        _write_admin_audit(db, actor_user_id, "admin.api_key.updated", "api_key", key_id)
    db.commit()

    row = db.execute(
        text(
            """
            SELECT id, name, key_prefix, scopes, ip_allowlist, rate_limit_per_minute, expires_at, last_used_at, status, created_at
            FROM domain_shared.api_keys
            WHERE id = :id AND tenant_id = :tenant_id
            """
        ),
        {"id": key_id, "tenant_id": tenant_id},
    ).mappings().first()
    return _to_api_key_out(dict(row))


@router.post("/api-keys/{key_id}/rotate", response_model=AdminApiKeySecretOut)
async def rotate_admin_api_key(
    key_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    current = db.execute(
        text(
            """
            SELECT id, name, status
            FROM domain_shared.api_keys
            WHERE id = :id AND tenant_id = :tenant_id
            """
        ),
        {"id": key_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not current:
        raise HTTPException(status_code=404, detail="API key not found")
    if current["status"] != "active":
        raise HTTPException(status_code=400, detail="Only active API keys can be rotated")

    token = _new_api_token()
    key_prefix = token[:16]
    db.execute(
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
            "tenant_id": tenant_id,
            "key_prefix": key_prefix,
            "key_hash": _hash_api_token(token),
        },
    )
    actor_user_id = _resolve_actor_user_id(db, tenant_id)
    if actor_user_id:
        _write_admin_audit(db, actor_user_id, "admin.api_key.rotated", "api_key", key_id)
    db.commit()

    return AdminApiKeySecretOut(
        id=str(current["id"]),
        name=str(current["name"]),
        key_prefix=key_prefix,
        token=token,
        created_at=_to_iso(datetime.utcnow()),
    )


@router.post("/api-keys/{key_id}/revoke", status_code=204)
async def revoke_admin_api_key(
    key_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            """
            SELECT id, status
            FROM domain_shared.api_keys
            WHERE id = :id AND tenant_id = :tenant_id
            """
        ),
        {"id": key_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="API key not found")
    if row["status"] == "revoked":
        return

    db.execute(
        text(
            """
            UPDATE domain_shared.api_keys
            SET status = 'revoked',
                revoked_at = NOW(),
                updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
            """
        ),
        {"id": key_id, "tenant_id": tenant_id},
    )
    actor_user_id = _resolve_actor_user_id(db, tenant_id)
    if actor_user_id:
        _write_admin_audit(db, actor_user_id, "admin.api_key.revoked", "api_key", key_id)
    db.commit()


# ---------------------------------------------------------------------------
# Prozessvarianten (Gap 009: Rollenbasierte Prozessvarianten je Genossenschaft)
# ---------------------------------------------------------------------------


class ProcessVariantsOut(BaseModel):
    """Prozessvarianten-Konfiguration pro Tenant (Gap 009)."""

    variants: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="SchlÃ¼ssel = Prozess-Code (z.B. annahme, settlement), Wert = { steps, required_roles?, description? }",
    )


@router.get("/process-variants", response_model=ProcessVariantsOut)
async def get_process_variants(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Prozessvarianten fÃ¼r den Tenant abrufen (Gap 009).
    Liefert Tenant-Overrides oder Defaults. Keine Hardcoded-Schritte in der Logik â€“
    Prozessschritte kommen aus dieser Konfiguration.
    """
    settings = _load_tenant_settings(db, tenant_id)
    custom = settings.get("process_variants")
    if isinstance(custom, dict):
        # Merge mit Defaults: Tenant-Overrides ersetzen Defaults
        merged = dict(DEFAULT_PROCESS_VARIANTS)
        for k, v in custom.items():
            if isinstance(v, dict):
                merged[k] = {**merged.get(k, {}), **v}
        return ProcessVariantsOut(variants=merged)
    return ProcessVariantsOut(variants=DEFAULT_PROCESS_VARIANTS)


@router.put("/process-variants", response_model=ProcessVariantsOut)
async def put_process_variants(
    payload: ProcessVariantsOut,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Prozessvarianten fÃ¼r den Tenant speichern (Gap 009).
    Ãœberschreibt nur die Ã¼bergebenen Prozesse; andere bleiben unverÃ¤ndert.
    """
    settings = _load_tenant_settings(db, tenant_id)
    existing = settings.get("process_variants")
    if not isinstance(existing, dict):
        existing = {}
    updated = {**existing, **payload.variants}
    settings["process_variants"] = updated
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return ProcessVariantsOut(variants={**DEFAULT_PROCESS_VARIANTS, **updated})


# ---------------------------------------------------------------------------
# Policy-Overrides (Gap 014: Policy-as-Code mit Tenant Overrides)
# ---------------------------------------------------------------------------

class PolicyOverridesOut(BaseModel):
    """Policy-Overrides pro Tenant (Gap 014). Ausnahmen regelbasiert dokumentiert."""

    overrides: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="SchlÃ¼ssel = rule_id, Wert = { enabled?, reason, valid_until?, params_override? }",
    )


@router.get("/policy-overrides", response_model=PolicyOverridesOut)
async def get_policy_overrides(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Policy-Overrides fÃ¼r den Tenant abrufen (Gap 014).
    Dokumentiert Ausnahmen zu Standard-Policies (reason, valid_until).
    """
    settings = _load_tenant_settings(db, tenant_id)
    overrides = settings.get("policy_overrides")
    if isinstance(overrides, dict):
        return PolicyOverridesOut(overrides=overrides)
    return PolicyOverridesOut(overrides={})


@router.put("/policy-overrides", response_model=PolicyOverridesOut)
async def put_policy_overrides(
    payload: PolicyOverridesOut,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Policy-Overrides fÃ¼r den Tenant speichern (Gap 014).
    Jede Ausnahme muss reason enthalten (regelbasiert dokumentiert).
    """
    for rule_id, ov in (payload.overrides or {}).items():
        if isinstance(ov, dict) and not ov.get("reason"):
            raise HTTPException(
                status_code=400,
                detail=f"policy_overrides.{rule_id}: 'reason' ist Pflichtfeld (Gap 014)",
            )
    settings = _load_tenant_settings(db, tenant_id)
    settings["policy_overrides"] = payload.overrides or {}
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()
    return PolicyOverridesOut(overrides=settings.get("policy_overrides", {}))


# ---------------------------------------------------------------------------
# Erntefenster (Gap 005: Saisonale Kampagnenprozesse als Vorlagen)
# ---------------------------------------------------------------------------


class ErntefensterTemplateOut(BaseModel):
    """Eine Erntefenster-Vorlage (Raps, Weizen, Mais, etc.)."""

    id: str
    name: str
    description: str
    process_key: str
    default_start_mmdd: str
    default_end_mmdd: str
    product_groups: list[str]


class ErntefensterCampaignOut(BaseModel):
    """Eine aus Vorlage erstellte Erntefenster-Kampagne."""

    id: str
    template_id: str
    name: str
    start_date: str
    end_date: str
    process_key: str
    product_groups: list[str]
    created_at: str


class ErntefensterFromTemplateIn(BaseModel):
    """Payload zum Erstellen einer Kampagne aus Vorlage."""

    template_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=120)
    year: int = Field(..., ge=2020, le=2030)
    start_mmdd: str | None = Field(default=None, pattern=r"^\d{2}-\d{2}$")
    end_mmdd: str | None = Field(default=None, pattern=r"^\d{2}-\d{2}$")


class WorkflowSandboxPreviewIn(BaseModel):
    """Preview eines effektiven Prozessablaufs fuer Simulation/Sandbox (Gap 012)."""

    process_key: str = Field(..., min_length=1)
    simulation_date: date | None = None
    campaign_id: str | None = None
    product_group: str | None = Field(default=None, max_length=80)


class WorkflowSandboxCampaignMatchOut(BaseModel):
    id: str
    name: str
    start_date: str
    end_date: str
    process_key: str
    product_groups: list[str]
    in_window: bool
    product_group_match: bool


class WorkflowSandboxPreviewOut(BaseModel):
    process_key: str
    simulation_date: str
    definition_version: int = 1
    definition_origin: str = "default"
    definition_status: str = "active"
    steps: list[str]
    required_roles: dict[str, list[str]] = Field(default_factory=dict)
    step_sla: dict[str, dict[str, Any]] = Field(default_factory=dict)
    description: str | None = None
    matched_campaigns: list[WorkflowSandboxCampaignMatchOut] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


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
    except Exception:
        return None

    normalized_product_group = (product_group or "").strip().lower()
    campaign_product_groups = [str(group) for group in campaign.get("product_groups") or []]
    product_group_match = not normalized_product_group or normalized_product_group in {
        group.lower() for group in campaign_product_groups
    }

    in_window = start_date <= simulation_date <= end_date
    return WorkflowSandboxCampaignMatchOut(
        id=str(campaign.get("id")),
        name=str(campaign.get("name") or ""),
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        process_key=process_key,
        product_groups=campaign_product_groups,
        in_window=in_window,
        product_group_match=product_group_match,
    )


@router.get("/erntefenster-templates", response_model=list[ErntefensterTemplateOut])
async def get_erntefenster_templates():
    """
    Erntefenster-Vorlagen abrufen (Gap 005).
    Liefert die vordefinierten Vorlagen (Raps, Weizen, Gerste, Mais, ZuckerrÃ¼be).
    """
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


@router.get("/erntefenster-campaigns", response_model=list[ErntefensterCampaignOut])
async def get_erntefenster_campaigns(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Vom Tenant erstellte Erntefenster-Kampagnen abrufen."""
    settings = _load_tenant_settings(db, tenant_id)
    campaigns = settings.get("erntefenster_campaigns")
    if not isinstance(campaigns, list):
        return []
    return [ErntefensterCampaignOut(**c) for c in campaigns if isinstance(c, dict)]


@router.post("/erntefenster-from-template", response_model=ErntefensterCampaignOut, status_code=201)
async def create_erntefenster_from_template(
    payload: ErntefensterFromTemplateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Neue Erntefenster-Kampagne aus Vorlage erstellen (Gap 005).
    Setup-Zeit <30 min: Vorlage wÃ¤hlen, Zeitfenster anpassen, speichern.
    """
    template = next((t for t in DEFAULT_ERNTEFENSTER_TEMPLATES if t["id"] == payload.template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail=f"Vorlage '{payload.template_id}' nicht gefunden")

    start_mmdd = payload.start_mmdd or template["default_start_mmdd"]
    end_mmdd = payload.end_mmdd or template["default_end_mmdd"]
    start_date = f"{payload.year}-{start_mmdd}"
    end_date = f"{payload.year}-{end_mmdd}"

    campaign = {
        "id": str(uuid4()),
        "template_id": payload.template_id,
        "name": payload.name,
        "start_date": start_date,
        "end_date": end_date,
        "process_key": template["process_key"],
        "product_groups": template.get("product_groups", []),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    settings = _load_tenant_settings(db, tenant_id)
    campaigns = settings.get("erntefenster_campaigns")
    if not isinstance(campaigns, list):
        campaigns = []
    campaigns.append(campaign)
    settings["erntefenster_campaigns"] = campaigns
    _save_tenant_settings(db, tenant_id, settings)
    db.commit()

    return ErntefensterCampaignOut(**campaign)


@router.post("/workflow-sandbox/preview", response_model=WorkflowSandboxPreviewOut)
async def preview_workflow_sandbox(
    payload: WorkflowSandboxPreviewIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Effektiven Prozessablauf fuer einen Stichtag simulieren (Gap 012).
    Nutzt Tenant-Prozessvarianten und saisonale Kampagnen als Sandbox-Preview,
    ohne produktive Workflows auszufuehren.
    """
    settings = _load_tenant_settings(db, tenant_id)
    variants = settings.get("process_variants")
    merged_variants = merge_workflow_variants(
        DEFAULT_PROCESS_VARIANTS,
        variants,
        tenant_id=tenant_id,
    )

    process_variant = merged_variants.get(payload.process_key)
    if process_variant is None:
        raise HTTPException(status_code=404, detail=f"Prozess '{payload.process_key}' nicht gefunden")

    simulation_date = payload.simulation_date or date.today()
    campaigns = settings.get("erntefenster_campaigns")
    matches: list[WorkflowSandboxCampaignMatchOut] = []
    if isinstance(campaigns, list):
        for campaign in campaigns:
            if not isinstance(campaign, dict):
                continue
            preview_match = _campaign_matches_preview(
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

    definition_dump = process_variant.model_dump()
    steps = definition_dump.get("steps")
    required_roles = definition_dump.get("required_roles")
    step_sla = definition_dump.get("step_sla")

    return WorkflowSandboxPreviewOut(
        process_key=payload.process_key,
        simulation_date=simulation_date.isoformat(),
        definition_version=process_variant.version,
        definition_origin=process_variant.origin,
        definition_status=process_variant.status,
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

