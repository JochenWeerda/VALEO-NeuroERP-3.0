"""Studio-Parity-Listen und -Overview der Admin Suite (Godfile-Auslagerung).

Dieselben URL-Pfade wie zuvor unter ``admin_suite.router``; Human/CI/MCP unveraendert.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from app.auth.deps import require_roles
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.connector_config import save_connectors
from app.api.v1.endpoints import admin_suite as suite

router = APIRouter(prefix="/admin-suite", tags=["admin-suite", "readiness", "parity"])
@router.get("/readiness/evidence", summary="Admin Suite readiness Evidenzliste")
async def list_admin_suite_readiness_evidence() -> list[dict[str, Any]]:
    """Flache Evidenzliste fuer Studio-Cockpit-Tabelle (wie Legacy-Karten)."""
    readiness = suite.build_admin_suite_readiness()
    rows: list[dict[str, Any]] = []
    for item in readiness.evidence:
        rows.append(
            {
                "id": item.key,
                "key": item.key,
                "label": item.label,
                "status": item.status,
                "source": item.source,
                "evidence": item.evidence,
                "details": "; ".join(item.details) if item.details else "",
                "checked_at": item.checked_at.isoformat(),
            }
        )
    return rows


@router.get("/setup/steps", summary="Admin Suite Setup-Schritte auflisten")
async def list_setup_steps(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Flache Setup-Schritte fuer NativeList (Human/CI/MCP)."""
    settings = suite._load_tenant_settings(db, tenant_id)
    session = suite._build_setup_session(tenant_id, settings.get("admin_suite_setup"))
    return [
        {
            "id": step.key,
            "key": step.key,
            "label": step.label,
            "status": step.status,
            "target_path": step.target_path,
            "evidence": step.evidence,
            "responsible": step.responsible,
            "updated_at": step.updated_at.isoformat() if step.updated_at else None,
        }
        for step in session.steps
    ]


@router.get("/migration/profiles", summary="Migration-Profile auflisten")
async def list_migration_profiles() -> list[dict[str, Any]]:
    """Flache Profile-Liste fuer Studio-Cockpit-Tabelle."""
    return [
        {
            "id": profile["key"],
            "key": profile["key"],
            "label": profile["label"],
            "status": profile["status"],
            "adapter": profile.get("adapter"),
            "notes": profile["notes"],
        }
        for profile in suite.MIGRATION_PROFILES
    ]


@router.get("/migration/batches", summary="Migration-Batches auflisten")
async def list_migration_batches(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Flache Batch-Liste fuer Studio-Cockpit-Tabelle (Human/CI/MCP)."""
    settings = suite._load_tenant_settings(db, tenant_id)
    store = suite._migration_store(settings)
    rows: list[dict[str, Any]] = []
    for batch in store.get("batches", []):
        if not isinstance(batch, dict):
            continue
        recon = batch.get("reconciliation") if isinstance(batch.get("reconciliation"), dict) else {}
        rows.append(
            {
                "id": batch.get("id"),
                "tenant_id": batch.get("tenant_id"),
                "source_profile": batch.get("source_profile"),
                "source_ref": batch.get("source_ref"),
                "source_hash": batch.get("source_hash"),
                "mapping_version": batch.get("mapping_version"),
                "dry_run": batch.get("dry_run"),
                "status": batch.get("status"),
                "reconciliation_ok": all(bool(v) for v in recon.values()) if recon else False,
                "created_at": batch.get("created_at"),
                "updated_at": batch.get("updated_at"),
            }
        )
    return rows


@router.get("/migration/overview", summary="Migration Cockpit KPI-Ueberblick")
async def get_migration_overview(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Flache KPIs fuer Studio-Cockpit-Summary."""
    settings = suite._load_tenant_settings(db, tenant_id)
    cockpit = suite._migration_cockpit(tenant_id, suite._migration_store(settings))
    available = sum(1 for p in cockpit.profiles if p.status == "available")
    blocked = sum(1 for p in cockpit.profiles if p.status == "blocked")
    approved = sum(1 for b in cockpit.batches if b.status == "approved")
    return {
        "profile_count": len(cockpit.profiles),
        "available_profiles": available,
        "blocked_profiles": blocked,
        "batch_count": len(cockpit.batches),
        "approved_batches": approved,
        "execute_locked": True,
    }


@router.get("/security/overview", summary="Security Governance KPI-Ueberblick")
async def get_security_overview() -> dict[str, Any]:
    """Flache KPIs fuer Studio-Cockpit-Summary."""
    humans = suite._security_roles()
    agents = suite._agent_roles()
    return {
        "human_role_count": len(humans),
        "agent_role_count": len(agents),
        "role_count": len(humans) + len(agents),
        "sod_simulation_only": True,
        "agent_admin_blocked": True,
    }


def _security_role_row(role: suite.SecurityRoleOut) -> dict[str, Any]:
    return {
        "id": role.key,
        "key": role.key,
        "actor_type": role.actor_type,
        "notes": role.notes or "",
        "permissions_text": ", ".join(role.permissions),
        "permission_count": len(role.permissions),
    }


@router.get("/security/roles", summary="Menschenrollen auflisten")
async def list_security_roles() -> list[dict[str, Any]]:
    """Flache Menschenrollen fuer Studio-Cockpit-Tabelle."""
    return [_security_role_row(role) for role in suite._security_roles()]


@router.get("/security/agent-roles", summary="Agentenrollen auflisten")
async def list_security_agent_roles() -> list[dict[str, Any]]:
    """Flache Agentenrollen fuer Studio-Cockpit-Tabelle."""
    return [_security_role_row(role) for role in suite._agent_roles()]


@router.get("/capture-connectors/overview", summary="Capture-Connector KPI-Ueberblick")
async def get_capture_connectors_overview(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Flache STT-/IMAP-Statusfelder fuer Studio-Cockpit (ohne Secrets)."""
    out = suite._connectors_out(db, tenant_id)
    return {
        "stt_enabled": out.stt.enabled,
        "stt_configured": out.stt.configured,
        "stt_base_url": out.stt.base_url,
        "stt_model": out.stt.model,
        "stt_language": out.stt.language,
        "stt_api_key_set": out.stt.api_key_set,
        "imap_enabled": out.imap.enabled,
        "imap_configured": out.imap.configured,
        "imap_host": out.imap.host,
        "imap_port": out.imap.port,
        "imap_ssl": out.imap.ssl,
        "imap_user": out.imap.user,
        "imap_inbox": out.imap.inbox,
        "imap_sent": out.imap.sent,
        "imap_own_addresses": out.imap.own_addresses,
        "imap_poll_seconds": out.imap.poll_seconds,
        "imap_password_set": out.imap.password_set,
    }


@router.put("/capture-connectors/stt", response_model=suite.ConnectorsConfigOut, summary="STT-Konfiguration speichern", dependencies=[Depends(require_roles("admin"))])
async def update_connector_stt(
    payload: suite.ConnectorSttUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> suite.ConnectorsConfigOut:
    """Flaches STT-Update fuer Studio-Aktionen (Human/CI/MCP gleiche Endpunkte)."""
    save_connectors(db, tenant_id, stt=payload.model_dump(exclude_none=True), imap=None)
    return suite._connectors_out(db, tenant_id)


@router.put("/capture-connectors/imap", response_model=suite.ConnectorsConfigOut, summary="IMAP-Konfiguration speichern", dependencies=[Depends(require_roles("admin"))])
async def update_connector_imap(
    payload: suite.ConnectorImapUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> suite.ConnectorsConfigOut:
    """Flaches IMAP-Update fuer Studio-Aktionen (Human/CI/MCP gleiche Endpunkte)."""
    save_connectors(db, tenant_id, stt=None, imap=payload.model_dump(exclude_none=True))
    return suite._connectors_out(db, tenant_id)


