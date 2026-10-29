"""Zeilenaktionen der Anfragen-Liste als Fachaktion fuer Maske, CLI und MCP (MASK-STUDIO-ROLLOUT, Welle 1).

Die handgebaute Liste rief ``/send`` ohne Lieferanten auf (die Massenfreigabe scheiterte deshalb immer mit 422) und
loeschte Anfragen in jedem Status. Hier delegiert jede Aktion an den bestehenden Fachweg, mit den Statusgrenzen der
alten Oberflaeche und den Rahmenregeln von ``statusaktion`` (Trockenlauf, Wiederholung, Audit, Savepoint).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult
from app.services.mask_commands import statusaktion

router = APIRouter(tags=["mask-actions"])

_STATUS = ("SELECT upper(coalesce(status, 'OFFEN')) AS status FROM einkauf_anfragen "
           "WHERE (id = :id OR anfrage_nummer = :id) AND tenant_id = :tid")


@router.post("/einkauf/anfragen/{entity_id}/actions/senden", response_model=MaskActionResult,
             summary="Anfrage an Lieferanten senden", dependencies=SCHREIBEN["EINKAUF"])
async def anfrage_senden(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                         db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                         nutzer: dict = Depends(get_current_user)) -> MaskActionResult:
    from app.services.rfq_service import RfqVersandFehler, versende_einkauf_anfrage

    lieferanten = [str(x) for x in (body.get("lieferanten") or []) if str(x).strip()]

    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        try:
            ergebnis = versende_einkauf_anfrage(session, tenant_id, entity_id, lieferanten, "email", nutzer)
        except RfqVersandFehler as exc:
            raise HTTPException(status_code=exc.http_status, detail=exc.detail) from exc
        return f"Anfrage an {ergebnis['count']} Lieferant(en) gesendet; Angebotsphase."

    return await statusaktion(
        db, action_key="senden", entity_type="anfrage", entity_id=entity_id, tenant_id=tenant_id, body=body,
        status_sql=_STATUS, erlaubt={"ENTWURF", "OFFEN", "FREIGEGEBEN"}, ausfuehren=ausfuehren,
        event_type="einkauf.anfrage.gesendet", begruendung_pflicht=False,
        zusatzpruefung=lambda zeile: None if lieferanten else "Keine Lieferanten gewaehlt.")


@router.post("/einkauf/anfragen/{entity_id}/actions/in_bestellung", response_model=MaskActionResult,
             summary="Anfrage in eine Bestellung ueberfuehren", dependencies=SCHREIBEN["EINKAUF"])
async def anfrage_in_bestellung(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                db: Session = Depends(get_db),
                                tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    from app.services.mask_action_runtime_service import run_delegated_mask_action
    from app.services.einkauf_compat_service import EinkaufCompatService

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        zeile = session.execute(text(_STATUS), {"id": eid, "tid": tid}).mappings().first()
        if zeile is None:
            return [{"field": "_entity", "message": "Objekt nicht gefunden.", "severity": "blocking"}]
        if zeile["status"] not in {"FREIGEGEBEN", "ANGEBOTSPHASE"}:
            return [{"field": "_entity", "message": f"Aktion im Status {zeile['status']} nicht moeglich.",
                     "severity": "blocking"}]
        return []

    async def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        ergebnis = await EinkaufCompatService(session, tid).convert_anfrage_to_order(eid)
        nummer = ergebnis.get("purchaseOrderNumber") or ergebnis.get("purchaseOrderId") or ""
        return f"Bestellung {nummer} aus der Anfrage erzeugt." if nummer else "Bestellung aus der Anfrage erzeugt."

    return await run_delegated_mask_action(
        db, action_key="in_bestellung", entity_type="anfrage", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="einkauf.anfrage.bestellt")


@router.post("/einkauf/anfragen/{entity_id}/actions/loeschen", response_model=MaskActionResult,
             summary="Anfrage im Entwurf loeschen", dependencies=SCHREIBEN["EINKAUF"])
async def anfrage_loeschen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                           db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        echt = session.execute(text("SELECT id FROM einkauf_anfragen WHERE (id = :id OR anfrage_nummer = :id) "
                                    "AND tenant_id = :tid"), {"id": entity_id, "tid": tenant_id}).scalar()
        session.execute(text("DELETE FROM einkauf_anfragen_positionen WHERE anfrage_id = :id"), {"id": echt})
        session.execute(text("DELETE FROM einkauf_anfragen WHERE id = :id AND tenant_id = :tid"),
                        {"id": echt, "tid": tenant_id})
        return "Anfrage geloescht."

    # Nur Entwuerfe: eine freigegebene oder bestellte Anfrage traegt Lieferantenverkehr bzw. eine Bestellung.
    return await statusaktion(
        db, action_key="loeschen", entity_type="anfrage", entity_id=entity_id, tenant_id=tenant_id, body=body,
        status_sql=_STATUS, erlaubt={"ENTWURF", "OFFEN"}, ausfuehren=ausfuehren,
        event_type="einkauf.anfrage.geloescht", begruendung_pflicht=True)
