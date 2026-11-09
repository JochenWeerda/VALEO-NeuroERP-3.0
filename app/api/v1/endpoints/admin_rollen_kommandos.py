"""Rollen als Fachaktion fuer Maske, CLI und MCP (Studio-Liste ``admin/rollen-verwaltung``, 09.11.2026).

Ersetzt die handgebaute Seite ``admin/rollen-verwaltung-legacy`` (sie zeigte nur die Liste und sprang fuer
"Neue Rolle" auf sich selbst). Die Regeln bleiben die des ``AdminCoreService``: Systemrollen sind nur lesbar, eine
Rolle mit Benutzern laesst sich nicht entfernen. Rechte je Rolle pflegt die Berechtigungsmatrix. Nur Administratoren.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(prefix="/admin/rollen", tags=["admin", "rollen", "mask-actions"])

_NUR_ADMIN = [Depends(require_roles("admin"))]


def _blockiert(meldung: str, feld: str = "_entity") -> list[dict]:
    return [{"field": feld, "message": meldung, "severity": "blocking"}]


def _dienst(session: Session, tid: str):
    from app.services.admin_core_service import AdminCoreService

    return AdminCoreService(session, tid)


def _rollen(session: Session, tid: str) -> dict[str, Any]:
    return {r.id: r for r in _dienst(session, tid).list_roles()}


def _rechte(wert: Any) -> list[str]:
    if isinstance(wert, list):
        return [str(w).strip() for w in wert if str(w).strip()]
    return [teil.strip() for teil in str(wert or "").split(",") if teil.strip()]


@router.post("/actions/anlegen", response_model=MaskActionResult, summary="Rolle anlegen", dependencies=_NUR_ADMIN)
async def anlegen(body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                  tenant_id: str = Depends(get_tenant_id), nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        name = str(payload.get("name") or "").strip()
        if not name or len(name) > 64:
            return _blockiert("Name fehlt oder ist laenger als 64 Zeichen.", "name")
        if any(r.name.lower() == name.lower() for r in _rollen(session, tid).values()):
            return _blockiert(f"Eine Rolle {name} gibt es schon.", "name")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        from app.api.v1.schemas.admin_core_schemas import AdminRoleCreate

        rolle = _dienst(session, tid).create_role(AdminRoleCreate(
            name=str(payload["name"]).strip(), beschreibung=str(payload.get("beschreibung") or "").strip(),
            rechte_liste=_rechte(payload.get("rechte_liste"))))
        return f"Rolle {rolle.name} angelegt ({rolle.id})."

    return await run_delegated_mask_action(
        db, action_key="anlegen", entity_type="admin_role", entity_id="neu", tenant_id=tenant_id, body=body,
        check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="admin.role.created")


@router.post("/{entity_id}/actions/aendern", response_model=MaskActionResult, summary="Rolle aendern",
             dependencies=_NUR_ADMIN)
async def aendern(entity_id: str, body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                  tenant_id: str = Depends(get_tenant_id), nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        if eid not in _rollen(session, tid):
            return _blockiert("Rolle nicht gefunden.")
        if not str(payload.get("name") or "").strip():
            return _blockiert("Name fehlt.", "name")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        from app.api.v1.schemas.admin_core_schemas import AdminRoleUpdate

        _dienst(session, tid).update_role(eid, AdminRoleUpdate(
            name=str(payload["name"]).strip(), beschreibung=str(payload.get("beschreibung") or "").strip()))
        return "Rolle geaendert."

    return await run_delegated_mask_action(
        db, action_key="aendern", entity_type="admin_role", entity_id=entity_id, tenant_id=tenant_id, body=body,
        check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="admin.role.updated")


@router.post("/{entity_id}/actions/entfernen", response_model=MaskActionResult, summary="Rolle entfernen",
             dependencies=_NUR_ADMIN)
async def entfernen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                    tenant_id: str = Depends(get_tenant_id),
                    nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        rolle = _rollen(session, tid).get(eid)
        if rolle is None:
            return _blockiert("Rolle nicht gefunden.")
        if rolle.benutzer:
            return _blockiert(f"Rolle hat {rolle.benutzer} Benutzer und laesst sich nicht entfernen.")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        _dienst(session, tid).delete_role(eid)
        return "Rolle entfernt."

    return await run_delegated_mask_action(
        db, action_key="entfernen", entity_type="admin_role", entity_id=entity_id, tenant_id=tenant_id, body=body,
        check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="admin.role.deleted", require_audit_reason=True)
