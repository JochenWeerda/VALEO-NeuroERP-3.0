"""Nummernkreise als Fachaktion fuer Maske, CLI und MCP (Studio-Liste ``admin/nummernkreise``, 09.11.2026).

Ersetzt die handgebaute Seite ``admin/nummernkreise-legacy``. Die Regeln bleiben die des
``NumberRangeService``: Stellenanzahl darf nicht kleiner werden, der Startwert gilt nur, solange noch keine Nummer
vergeben ist. Neu: "Konfigurieren" nimmt einen stillgelegten Kreis wieder in Betrieb. Nur Administratoren.
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

router = APIRouter(prefix="/admin/number-ranges", tags=["admin", "number-ranges", "mask-actions"])

_NUR_ADMIN = [Depends(require_roles("admin"))]

KREISARTEN = [("debtor_account", "Debitorenkonto"), ("creditor_account", "Kreditorenkonto"),
              ("partner_number", "Partnernummer")]

_FORMAT_FELDER: list[dict[str, Any]] = [
    {"key": "prefix", "label": "Präfix", "type": "text"},
    {"key": "start_number", "label": "Startnummer", "type": "number", "required": True},
    {"key": "digit_count", "label": "Stellen", "type": "number", "required": True},
    {"key": "reserved_prefix_digits", "label": "Reservierte Präfixstellen", "type": "number"},
]
KONFIGURIEREN_FELDER: list[dict[str, Any]] = [
    {"key": "range_type", "label": "Nummernkreis", "type": "select", "required": True,
     "options": [{"value": w, "label": t} for w, t in KREISARTEN]},
    *_FORMAT_FELDER,
]
AENDERN_FELDER = _FORMAT_FELDER


def _blockiert(meldung: str, feld: str = "_entity") -> list[dict]:
    return [{"field": feld, "message": meldung, "severity": "blocking"}]


def _ganzzahl(wert: Any, standard: int | None = None) -> int | None:
    if wert in (None, ""):
        return standard
    try:
        return int(str(wert).strip())
    except ValueError:
        return None


def _format_pruefen(payload: dict, bestehend: Any | None) -> list[dict]:
    start, stellen = _ganzzahl(payload.get("start_number")), _ganzzahl(payload.get("digit_count"))
    reserviert = _ganzzahl(payload.get("reserved_prefix_digits"), 1)
    if start is None or start < 1:
        return _blockiert("Startnummer muss eine ganze Zahl ab 1 sein.", "start_number")
    if stellen is None or not 1 <= stellen <= 10:
        return _blockiert("Stellen muessen zwischen 1 und 10 liegen.", "digit_count")
    if reserviert is None or not 0 <= reserviert <= 3:
        return _blockiert("Reservierte Praefixstellen muessen zwischen 0 und 3 liegen.", "reserved_prefix_digits")
    if len(str(payload.get("prefix") or "")) > 20:
        return _blockiert("Praefix ist laenger als 20 Zeichen.", "prefix")
    if bestehend is not None and stellen < bestehend.digit_count:
        return _blockiert("Stellenanzahl darf nicht verkleinert werden.", "digit_count")
    return []


def _kreis(session: Session, tid: str, *, art: str | None = None, kennung: str | None = None):
    from app.services.number_range_service import NumberRangeService

    for kreis in NumberRangeService(session).list_ranges(tid):
        if (art and kreis.range_type == art) or (kennung and str(kreis.id) == kennung):
            return kreis
    return None


def _konfigurieren(session: Session, tid: str, art: str, payload: dict) -> str:
    from app.services.number_range_service import NumberRangeService

    kreis = NumberRangeService(session).configure(
        tenant_id=tid, range_type=art, prefix=str(payload.get("prefix") or ""),
        start_number=_ganzzahl(payload.get("start_number")), digit_count=_ganzzahl(payload.get("digit_count")),
        reserved_prefix_digits=_ganzzahl(payload.get("reserved_prefix_digits"), 1))
    kreis.is_active = True
    session.flush()
    return f"Nummernkreis {dict(KREISARTEN).get(art, art)} konfiguriert."


@router.post("/actions/konfigurieren", response_model=MaskActionResult, summary="Nummernkreis konfigurieren",
             dependencies=_NUR_ADMIN)
async def konfigurieren(body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                        tenant_id: str = Depends(get_tenant_id),
                        nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        art = payload.get("range_type")
        if art not in dict(KREISARTEN):
            return _blockiert("Unbekannter Nummernkreis.", "range_type")
        return _format_pruefen(payload, _kreis(session, tid, art=art))

    return await run_delegated_mask_action(
        db, action_key="konfigurieren", entity_type="number_range", entity_id="neu", tenant_id=tenant_id, body=body,
        check_fn=pruefen, delegate_fn=lambda s, p, e, t: _konfigurieren(s, t, p["range_type"], p),
        outbox_event_type="admin.number_range.configured")


@router.post("/{entity_id}/actions/aendern", response_model=MaskActionResult, summary="Nummernkreis aendern",
             dependencies=_NUR_ADMIN)
async def aendern(entity_id: str, body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                  tenant_id: str = Depends(get_tenant_id), nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        kreis = _kreis(session, tid, kennung=eid)
        return _blockiert("Nummernkreis nicht gefunden.") if kreis is None else _format_pruefen(payload, kreis)

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        return _konfigurieren(session, tid, _kreis(session, tid, kennung=eid).range_type, payload)

    return await run_delegated_mask_action(
        db, action_key="aendern", entity_type="number_range", entity_id=entity_id, tenant_id=tenant_id, body=body,
        check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="admin.number_range.configured")


@router.post("/{entity_id}/actions/stilllegen", response_model=MaskActionResult, summary="Nummernkreis stilllegen",
             dependencies=_NUR_ADMIN)
async def stilllegen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                     tenant_id: str = Depends(get_tenant_id),
                     nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        kreis = _kreis(session, tid, kennung=eid)
        if kreis is None:
            return _blockiert("Nummernkreis nicht gefunden.")
        return [] if kreis.is_active else _blockiert("Nummernkreis ist bereits stillgelegt.")

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        _kreis(session, tid, kennung=eid).is_active = False
        session.flush()
        return "Nummernkreis stillgelegt; neue Nummern vergibt er nicht mehr."

    return await run_delegated_mask_action(
        db, action_key="stilllegen", entity_type="number_range", entity_id=entity_id, tenant_id=tenant_id, body=body,
        check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="admin.number_range.deactivated",
        require_audit_reason=True)
