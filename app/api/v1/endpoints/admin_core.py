"""Core admin endpoints used by the settings/admin frontend.

Dünne Adapter-Schicht: Request-Parsing, Tenant-/DB-Dependencies und Response-
Modelle. Die gesamte Geschäftslogik liegt in :class:`AdminCoreService`
(``app/services/admin_core_service.py``). Fehler werden dort als
``DomainError``-Subklassen geworfen und global zu RFC-7807-Antworten gemappt.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.workflow_definitions import merge_workflow_variants
from app.core.tenant import get_tenant_id

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
from app.services.admin_core_service import AdminCoreService


router = APIRouter()


def _service(tenant_id: str, db: Session) -> AdminCoreService:
    return AdminCoreService(db, tenant_id)


def _load_tenant_settings(db: Session, tenant_id: str):
    """Compatibility hook for sandbox contract tests and adapter injection."""
    return _service(tenant_id, db)._load_tenant_settings()


# ── Users ────────────────────────────────────────────────────────────────────


@router.get("/benutzer", response_model=list[AdminUserOut], summary="Admin users auflisten")
async def list_admin_users(
    search: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).list_users(search)


@router.get("/benutzer/{user_id}", response_model=AdminUserOut, summary="Admin user abrufen")
async def get_admin_user(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).get_user(user_id)


@router.post("/benutzer", response_model=AdminUserOut, status_code=201, summary="Admin user anlegen")
async def create_admin_user(
    payload: AdminUserCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).create_user(payload)


@router.put("/benutzer/{user_id}", response_model=AdminUserOut, summary="Admin user aktualisieren")
async def update_admin_user(
    user_id: str,
    payload: AdminUserUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).update_user(user_id, payload)


@router.delete("/benutzer/{user_id}", status_code=204, response_class=Response, response_model=None, summary="Admin user löschen")
async def delete_admin_user(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _service(tenant_id, db).delete_user(user_id)


# ── Roles ────────────────────────────────────────────────────────────────────


@router.get("/rollen", response_model=list[AdminRoleOut], summary="Admin roles auflisten")
async def list_admin_roles(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).list_roles()


@router.post("/rollen", response_model=AdminRoleOut, status_code=201, summary="Admin role anlegen")
async def create_admin_role(
    payload: AdminRoleCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).create_role(payload)


@router.put("/rollen/{role_id}", response_model=AdminRoleOut, summary="Admin role aktualisieren")
async def update_admin_role(
    role_id: str,
    payload: AdminRoleUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).update_role(role_id, payload)


@router.delete("/rollen/{role_id}", status_code=204, response_class=Response, response_model=None, summary="Admin role löschen")
async def delete_admin_role(
    role_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _service(tenant_id, db).delete_role(role_id)


# ── Audit log ─────────────────────────────────────────────────────────────────


@router.get("/audit-log", response_model=list[AdminAuditOut], summary="Admin audit log auflisten")
async def list_admin_audit_log(
    search: str | None = Query(default=None),
    limit: int = Query(default=250, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).list_audit_log(search, limit)


# ── API keys ──────────────────────────────────────────────────────────────────


@router.get("/api-keys", response_model=list[AdminApiKeyOut], summary="Admin api keys auflisten")
async def list_admin_api_keys(
    include_revoked: bool = Query(default=False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).list_api_keys(include_revoked)


@router.get("/agent-manifest", response_model=AgentManifestOut, summary="Agent manifest abrufen")
async def get_agent_manifest() -> AgentManifestOut:
    """Maschinenlesbarer Einstiegspunkt fuer externe Agenten (Gap 048)."""
    return AdminCoreService.agent_manifest()


@router.post("/api-keys", response_model=AdminApiKeySecretOut, status_code=201, summary="Admin api key anlegen")
async def create_admin_api_key(
    payload: AdminApiKeyCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).create_api_key(payload)


@router.put("/api-keys/{key_id}", response_model=AdminApiKeyOut, summary="Admin api key aktualisieren")
async def update_admin_api_key(
    key_id: str,
    payload: AdminApiKeyUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).update_api_key(key_id, payload)


@router.post("/api-keys/{key_id}/rotate", response_model=AdminApiKeySecretOut, summary="Admin api key rotate")
async def rotate_admin_api_key(
    key_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).rotate_api_key(key_id)


@router.post("/api-keys/{key_id}/revoke", status_code=204, response_class=Response, response_model=None, summary="Admin api key revoke")
async def revoke_admin_api_key(
    key_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _service(tenant_id, db).revoke_api_key(key_id)


# ── Prozessvarianten (Gap 009) ────────────────────────────────────────────────


@router.get("/process-variants", response_model=ProcessVariantsOut, summary="Process variants abrufen")
async def get_process_variants(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).get_process_variants()


@router.put("/process-variants", response_model=ProcessVariantsOut, summary="Process variants put")
async def put_process_variants(
    payload: ProcessVariantsOut,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).put_process_variants(payload)


# ── Policy-Overrides (Gap 014) ────────────────────────────────────────────────


@router.get("/policy-overrides", response_model=PolicyOverridesOut, summary="Policy overrides abrufen")
async def get_policy_overrides(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).get_policy_overrides()


@router.put("/policy-overrides", response_model=PolicyOverridesOut, summary="Policy overrides put")
async def put_policy_overrides(
    payload: PolicyOverridesOut,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).put_policy_overrides(payload)


# ── Erntefenster (Gap 005) ────────────────────────────────────────────────────


@router.get("/erntefenster-templates", response_model=list[ErntefensterTemplateOut], summary="Erntefenster templates abrufen")
async def get_erntefenster_templates():
    return AdminCoreService.get_erntefenster_templates()


@router.get("/erntefenster-campaigns", response_model=list[ErntefensterCampaignOut], summary="Erntefenster campaigns abrufen")
async def get_erntefenster_campaigns(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).get_erntefenster_campaigns()


@router.post("/erntefenster-from-template", response_model=ErntefensterCampaignOut, status_code=201, summary="Erntefenster from template anlegen")
async def create_erntefenster_from_template(
    payload: ErntefensterFromTemplateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).create_erntefenster_from_template(payload)


# ── Workflow-Sandbox (Gap 012) ────────────────────────────────────────────────


@router.post("/workflow-sandbox/preview", response_model=WorkflowSandboxPreviewOut, summary="Workflow sandbox vorschauen")
async def preview_workflow_sandbox(
    payload: WorkflowSandboxPreviewIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(tenant_id, db).preview_workflow_sandbox(
        payload,
        settings_loader=lambda: _load_tenant_settings(db, tenant_id),
        variant_merger=merge_workflow_variants,
    )
