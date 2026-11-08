"""Zeilenaktionen der CRM-Listen als Fachaktion fuer Maske, CLI und MCP (MASK-STUDIO-ROLLOUT, Welle 1).

Gewonnen und Verloren setzten in der handgebauten Liste per ``PUT`` je Zeile den Status, ohne Pruefung, ohne Grund
und ohne Audit, auch fuer bereits abgeschlossene Chancen. Hier ueber den Aenderungsweg ``update_opportunity`` (wie
``actions/bearbeiten`` der Objektmaske) mit Rahmenregeln von ``run_delegated_mask_action``.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(tags=["mask-actions"])

_ABGESCHLOSSEN = {"closed_won", "closed_lost", "won", "lost"}


async def _abschliessen(entity_id: str, body: dict[str, Any], db: Session, tenant_id: str, *,
                        ergebnis: str) -> MaskActionResult:
    from app.api.v1.endpoints.opportunities import _opportunity_im_mandanten, update_opportunity
    from app.api.v1.schemas.crm import OpportunityUpdate

    async def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        try:
            chance = await _opportunity_im_mandanten(session, eid, tid)
        except HTTPException as exc:
            if exc.status_code == 404:
                return [{"field": "_entity", "message": "Objekt nicht gefunden.", "severity": "blocking"}]
            raise
        stand = str(chance.get("stage") or chance.get("status") or "").lower()
        if stand in _ABGESCHLOSSEN:
            return [{"field": "_entity", "message": f"Chance ist bereits abgeschlossen ({stand}).",
                     "severity": "blocking"}]
        return []

    async def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        werte = OpportunityUpdate(status=ergebnis, stage=ergebnis, actual_close_date=datetime.now(timezone.utc))
        await update_opportunity(eid, werte, db=session, tenant_id=tid)
        return "Chance als gewonnen abgeschlossen." if ergebnis == "closed_won" else "Chance als verloren abgeschlossen."

    return await run_delegated_mask_action(
        db, action_key="gewonnen" if ergebnis == "closed_won" else "verloren", entity_type="opportunity",
        entity_id=entity_id, tenant_id=tenant_id, body=body, check_fn=pruefen, delegate_fn=ausfuehren,
        outbox_event_type=f"crm.opportunity.{ergebnis}", require_audit_reason=ergebnis == "closed_lost")


@router.post("/crm/opportunities/{entity_id}/actions/gewonnen", response_model=MaskActionResult,
             summary="Verkaufschance als gewonnen abschliessen", dependencies=SCHREIBEN["CRM"])
async def chance_gewonnen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                          db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _abschliessen(entity_id, body, db, tenant_id, ergebnis="closed_won")


@router.post("/crm/opportunities/{entity_id}/actions/verloren", response_model=MaskActionResult,
             summary="Verkaufschance mit Begruendung als verloren abschliessen", dependencies=SCHREIBEN["CRM"])
async def chance_verloren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                          db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _abschliessen(entity_id, body, db, tenant_id, ergebnis="closed_lost")
