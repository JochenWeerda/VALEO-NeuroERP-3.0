"""Core admin endpoints used by the settings/admin frontend."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.scopes import ROLE_SCOPES
from app.core.database import get_db
from app.core.tenant import get_tenant_id

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
