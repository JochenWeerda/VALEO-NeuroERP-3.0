"""Bestellvorschlag als Fachaktion fuer Maske, CLI und MCP (Familie ``bestellvorschlag``, 09.11.2026).

* ``berechnung/<art>/actions/speichern``: rechnet den Vorschlag der Art (Lager, Verkauf, Rohware, Bedarf) auf dem
  Server neu und speichert ihn; die Maske schickt keine Zeilen, also kann keine veraltete Ansicht gespeichert werden.
* ``{entity_id}/actions/zu_bestellung``: legt aus einem gespeicherten Vorschlag je Lieferant einen
  DocFlow-Bestellentwurf an (BELEG-052).
"""
from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import get_current_user
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(tags=["einkauf", "bestellvorschlag", "mask-actions"])

ARTEN = {"lager": "Lager", "verkauf": "Verkauf", "rohware": "Rohware", "bedarf": "Bedarf"}


def _rechne(session: Session, tid: str, art: str) -> list[dict]:
    from app.services.procurement_service import ProcurementService

    dienst = ProcurementService(session, tid)
    if art == "lager":
        return dienst.compute_vorschlag_lager(None, None, None, None, True)
    if art == "verkauf":
        return dienst.compute_vorschlag_verkauf(None, None, None, None)
    if art == "rohware":
        return dienst.compute_vorschlag_rohware(None, None)
    return dienst.compute_vorschlag_bedarf(horizont="monatlich", stichtag=None, niederlassung_id=None,
                                           artikelgruppe=None, artikel_nr=None, warehouse_id=None,
                                           lagerkosten_satz=None, frachtkosten_fix=None, nur_mit_bedarf=True)


def _speichern_fuer(art: str) -> Callable:
    async def speichern(body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                        tenant_id: str = Depends(get_tenant_id),
                        nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
        gepruefter_akteur(nutzer)

        def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
            zeilen = [z for z in _rechne(session, tid, art) if float(z.get("vorschlag_menge") or 0) > 0]
            if not zeilen:
                return [{"field": "_entity", "message": "Kein Bedarf - nichts zu speichern.", "severity": "blocking"}]
            return []

        def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
            from app.services.procurement_service import ProcurementService

            zeilen = [z for z in _rechne(session, tid, art) if float(z.get("vorschlag_menge") or 0) > 0]
            bezeichnung = str(payload.get("bezeichnung") or "").strip() or f"Bestellvorschlag {ARTEN[art]}"
            ergebnis = ProcurementService(session, tid).create_vorschlag(art, zeilen, None, None, bezeichnung)
            return f"{bezeichnung} mit {len(zeilen)} Positionen gespeichert ({ergebnis.get('id')})."

        return await run_delegated_mask_action(
            db, action_key="speichern", entity_type="bestellvorschlag_berechnung", entity_id=art,
            tenant_id=tenant_id, body=body, check_fn=pruefen, delegate_fn=ausfuehren,
            outbox_event_type=f"einkauf.bestellvorschlag.{art}_gespeichert")

    return speichern


for _art, _label in ARTEN.items():
    router.add_api_route(f"/einkauf/bestellvorschlaege/berechnung/{_art}/actions/speichern", _speichern_fuer(_art),
                         methods=["POST"], response_model=MaskActionResult,
                         summary=f"Bestellvorschlag {_label} berechnen und speichern",
                         dependencies=SCHREIBEN["EINKAUF"], name=f"bestellvorschlag_{_art}_speichern")


@router.post("/einkauf/bestellvorschlaege/{entity_id}/actions/zu_bestellung", response_model=MaskActionResult,
             summary="Aus dem Bestellvorschlag je Lieferant einen Bestellentwurf (DocFlow) anlegen",
             dependencies=SCHREIBEN["EINKAUF"])
async def zu_bestellung(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                        db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                        nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    akteur = gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        status = session.execute(text(
            "SELECT status FROM domain_einkauf.bestellvorschlaege WHERE tenant_id = :t AND id::text = :id"),
            {"t": tid, "id": eid}).scalar()
        if status is None:
            return [{"field": "_entity", "message": "Bestellvorschlag nicht gefunden.", "severity": "blocking"}]
        if status == "in_bestellung":
            return [{"field": "_entity", "message": "Bestellvorschlag ist bereits bestellt.", "severity": "blocking"}]
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        from app.services.procurement_service import ProcurementService

        ergebnis = ProcurementService(session, tid).freigebe_vorschlag(eid, freigegeben_von=akteur)
        return f"{ergebnis['anzahl']} Bestellentwurf/-entwuerfe in DocFlow angelegt."

    return await run_delegated_mask_action(
        db, action_key="zu_bestellung", entity_type="bestellvorschlag", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="einkauf.bestellvorschlag.bestellt",
        require_audit_reason=False)
