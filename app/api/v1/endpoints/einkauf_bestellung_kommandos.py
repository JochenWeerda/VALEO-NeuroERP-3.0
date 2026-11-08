"""Zeilenaktionen der Bestell-Liste als Fachaktion fuer Maske, CLI und MCP (MASK-STUDIO-ROLLOUT, Welle 1).

Freigeben, Versenden und Stornieren delegieren an den Einkaufsdienst (``ProcurementService``), der die Statusregeln,
die Obligo-Buchung und den Versand fuehrt. Hier kommen nur die Rahmenregeln von ``run_delegated_mask_action`` dazu:
Trockenlauf, Wiederholungsschutz, Audit, Ereignis, Savepoint. Die Liste liest dieselbe Quelle wie die Objektmaske
``einkauf/purchase-order`` (``domain_einkauf.bestellungen``).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult
from app.services.mask_commands import statusaktion

router = APIRouter(tags=["mask-actions"])

_STATUS = ("SELECT lower(coalesce(status, 'entwurf')) AS status FROM domain_einkauf.bestellungen "
           "WHERE (CAST(id AS text) = :id OR bestellnummer = :id) AND tenant_id = :tid")
_ID = ("SELECT CAST(id AS text) FROM domain_einkauf.bestellungen "
       "WHERE (CAST(id AS text) = :id OR bestellnummer = :id) AND tenant_id = :tid")


def _kennung(session: Session, entity_id: str, tenant_id: str) -> str:
    return session.execute(text(_ID), {"id": entity_id, "tid": tenant_id}).scalar() or entity_id


@router.post("/einkauf/bestellungen/{entity_id}/actions/freigeben", response_model=MaskActionResult,
             summary="Bestellentwurf freigeben (Obligo)", dependencies=SCHREIBEN["EINKAUF"])
async def bestellung_freigeben(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                               db: Session = Depends(get_db),
                               tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    from app.services.procurement_service import ProcurementService

    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        ergebnis = ProcurementService(session, tenant_id).freigebe_bestellung(_kennung(session, entity_id, tenant_id))
        return f"Bestellung {ergebnis['bestellnummer']} freigegeben."

    return await statusaktion(
        db, action_key="freigeben", entity_type="bestellung", entity_id=entity_id, tenant_id=tenant_id, body=body,
        status_sql=_STATUS, erlaubt={"entwurf", "draft"}, ausfuehren=ausfuehren,
        event_type="einkauf.bestellung.freigegeben", begruendung_pflicht=False)


@router.post("/einkauf/bestellungen/{entity_id}/actions/versenden", response_model=MaskActionResult,
             summary="Bestellung an den Lieferanten senden", dependencies=SCHREIBEN["EINKAUF"])
async def bestellung_versenden(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                               db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                               nutzer: dict = Depends(get_current_user)) -> MaskActionResult:
    from app.services.procurement_service import ProcurementService

    versand_art = str(body.get("versand_art") or "email")

    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        # VersandNichtMoeglich (kein Postfach, kein Empfaenger, Server lehnt ab) wird zur Ablehnung der Aktion.
        ergebnis = ProcurementService(session, tenant_id).versende_bestellung_svc(
            _kennung(session, entity_id, tenant_id), versand_art, None, nutzer=nutzer)
        return f"Bestellung {ergebnis['bestellnummer']} versendet ({ergebnis['versand'].get('status')})."

    return await statusaktion(
        db, action_key="versenden", entity_type="bestellung", entity_id=entity_id, tenant_id=tenant_id, body=body,
        status_sql=_STATUS, erlaubt=None, ausfuehren=ausfuehren, event_type="einkauf.bestellung.versendet",
        begruendung_pflicht=False,
        zusatzpruefung=lambda zeile: f"Bestellung ist {zeile['status']}." if zeile["status"] in {
            "storniert", "abgeschlossen"} else None)


@router.post("/einkauf/bestellungen/{entity_id}/actions/stornieren", response_model=MaskActionResult,
             summary="Bestellung mit Begruendung stornieren", dependencies=SCHREIBEN["EINKAUF"])
async def bestellung_stornieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                db: Session = Depends(get_db),
                                tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    from app.services.mask_commands import begruendung
    from app.services.procurement_service import ProcurementService

    grund = begruendung(body)

    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        ergebnis = ProcurementService(session, tenant_id).storniere_bestellung(
            _kennung(session, entity_id, tenant_id), grund)
        return f"Bestellung {ergebnis['bestellnummer']} storniert."

    return await statusaktion(
        db, action_key="stornieren", entity_type="bestellung", entity_id=entity_id, tenant_id=tenant_id, body=body,
        status_sql=_STATUS, erlaubt=None, ausfuehren=ausfuehren, event_type="einkauf.bestellung.storniert",
        begruendung_pflicht=True,
        zusatzpruefung=lambda zeile: f"Bestellung ist {zeile['status']}." if zeile["status"] in {
            "storniert", "abgeschlossen"} else None)
