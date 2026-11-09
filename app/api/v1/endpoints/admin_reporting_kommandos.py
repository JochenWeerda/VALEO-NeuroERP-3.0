"""Report-Berechtigungen als Fachaktion fuer Maske, CLI und MCP (Studio-Liste ``admin/report-berechtigungen``).

Ersetzt die handgebaute Seite ``admin/report-berechtigungen-legacy`` (09.11.2026). Je Rolle und Auswertung genau
eine Berechtigung; Entfernen loescht wie bisher, jetzt mit Grund im Audit. Nur Administratoren.
"""
from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(prefix="/admin/report-permissions", tags=["admin", "reporting", "mask-actions"])

_NUR_ADMIN = [Depends(require_roles("admin"))]
_LEERE_FILTER = "{}"


def _blockiert(meldung: str, feld: str = "_entity") -> list[dict]:
    return [{"field": feld, "message": meldung, "severity": "blocking"}]


def _ja(wert: Any, standard: bool) -> bool:
    if wert in (None, ""):
        return standard
    return wert is True or str(wert).strip().lower() in {"true", "1", "ja", "yes"}


def _bereiche(wert: Any) -> list[str]:
    if isinstance(wert, list):
        return [str(w).strip() for w in wert if str(w).strip()]
    return [teil.strip() for teil in str(wert or "").split(",") if teil.strip()]


def _vorhanden(session: Session, tid: str, rolle: str, auswertung: str, ausser: str | None = None) -> bool:
    return bool(session.execute(text(
        "SELECT 1 FROM domain_shared.admin_report_permissions WHERE tenant_id = :t AND role_id = :r "
        "AND report_key = :k AND (CAST(:x AS text) IS NULL OR id::text <> :x)"),
        {"t": tid, "r": rolle, "k": auswertung, "x": ausser}).scalar())


def _felder_pruefen(session: Session, tid: str, payload: dict, ausser: str | None = None) -> list[dict]:
    rolle, auswertung = str(payload.get("role_id") or "").strip(), str(payload.get("report_key") or "").strip()
    if not rolle or len(rolle) > 64:
        return _blockiert("Rolle fehlt oder ist laenger als 64 Zeichen.", "role_id")
    if not auswertung or len(auswertung) > 120:
        return _blockiert("Auswertung fehlt oder ist laenger als 120 Zeichen.", "report_key")
    if _vorhanden(session, tid, rolle, auswertung, ausser):
        return _blockiert(f"Fuer {rolle} und {auswertung} gibt es schon eine Berechtigung.", "report_key")
    return []


def _werte(payload: dict) -> dict[str, Any]:
    return {"r": str(payload["role_id"]).strip(), "k": str(payload["report_key"]).strip(),
            "v": _ja(payload.get("can_view"), True), "e": _ja(payload.get("can_export"), False),
            "s": json.dumps(_bereiche(payload.get("allowed_scopes")))}


def _da(session: Session, tid: str, kennung: str) -> bool:
    return bool(session.execute(text("SELECT 1 FROM domain_shared.admin_report_permissions "
                                     "WHERE tenant_id = :t AND id::text = :i"), {"t": tid, "i": kennung}).scalar())


@router.post("/actions/anlegen", response_model=MaskActionResult, summary="Report-Berechtigung anlegen",
             dependencies=_NUR_ADMIN)
async def anlegen(body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                  tenant_id: str = Depends(get_tenant_id), nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        werte = _werte(payload)
        session.execute(text(
            "INSERT INTO domain_shared.admin_report_permissions (id, tenant_id, role_id, report_key, can_view, "
            "can_export, allowed_scopes, filters, active, created_at, updated_at) VALUES (:id, :t, :r, :k, :v, :e, "
            "CAST(:s AS jsonb), CAST(:f AS jsonb), true, NOW(), NOW())"),
            {"id": str(uuid4()), "t": tid, "f": _LEERE_FILTER, **werte})
        return f"Berechtigung {werte['r']} -> {werte['k']} angelegt."

    return await run_delegated_mask_action(
        db, action_key="anlegen", entity_type="report_permission", entity_id="neu", tenant_id=tenant_id, body=body,
        check_fn=lambda s, p, e, t: _felder_pruefen(s, t, p), delegate_fn=ausfuehren,
        outbox_event_type="admin.report_permission.created")


@router.post("/{entity_id}/actions/aendern", response_model=MaskActionResult, summary="Report-Berechtigung aendern",
             dependencies=_NUR_ADMIN)
async def aendern(entity_id: str, body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                  tenant_id: str = Depends(get_tenant_id), nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        return _felder_pruefen(session, tid, payload, eid) if _da(session, tid, eid) else _blockiert(
            "Berechtigung nicht gefunden.")

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        session.execute(text(
            "UPDATE domain_shared.admin_report_permissions SET role_id = :r, report_key = :k, can_view = :v, "
            "can_export = :e, allowed_scopes = CAST(:s AS jsonb), updated_at = NOW() "
            "WHERE tenant_id = :t AND id::text = :i"), {"t": tid, "i": eid, **_werte(payload)})
        return "Berechtigung geaendert."

    return await run_delegated_mask_action(
        db, action_key="aendern", entity_type="report_permission", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="admin.report_permission.updated")


@router.post("/{entity_id}/actions/entfernen", response_model=MaskActionResult, summary="Report-Berechtigung entfernen",
             dependencies=_NUR_ADMIN)
async def entfernen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                    tenant_id: str = Depends(get_tenant_id),
                    nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        session.execute(text("DELETE FROM domain_shared.admin_report_permissions WHERE tenant_id = :t "
                             "AND id::text = :i"), {"t": tid, "i": eid})
        return "Berechtigung entfernt."

    return await run_delegated_mask_action(
        db, action_key="entfernen", entity_type="report_permission", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=lambda s, p, e, t: [] if _da(s, t, e) else _blockiert("Berechtigung nicht gefunden."),
        delegate_fn=ausfuehren, outbox_event_type="admin.report_permission.deleted", require_audit_reason=True)
