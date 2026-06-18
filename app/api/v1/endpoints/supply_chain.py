"""Supply-Chain-Traceability (DOM-SUPPLY-004).

Durchgängige, prüfbare Kette Wiegung → Annahme → Lager → Abrechnung je Lieferung
(Rückgrat: weighing_ticket). Read-only; macht Rückverfolgbarkeit, Mengen-Konsistenz
(Schwund) und Lücken (fehlende Folgeobjekte) sichtbar.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.supply_chain_event_service import SupplyChainEventService
from app.services.supply_chain_lot_service import LotActionError, SupplyChainLotService
from app.services.supply_chain_trace_service import SupplyChainTraceService

router = APIRouter(prefix="/supply-chain", tags=["supply-chain", "agrar", "lager"])


@router.get("/traceability/tickets", response_model=dict[str, Any], summary="Wiegescheine mit Ketten-Vollständigkeit (Übersicht/Picker)")
def list_tickets(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": SupplyChainTraceService(db, tenant_id).list_tickets(limit=limit)}


@router.get("/traceability", response_model=dict[str, Any], summary="Durchgängige Kette je Lieferung (Rückverfolgbarkeit)")
def traceability(
    ticket: Optional[str] = Query(None, description="Wiegeschein-Nr oder -ID"),
    acceptance: Optional[str] = Query(None, description="Annahme-Nr oder -ID"),
    lot: Optional[str] = Query(None, description="Silo-Lot-Nr oder -ID"),
    settlement: Optional[str] = Query(None, description="Abrechnungs-Nr oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return SupplyChainTraceService(db, tenant_id).trace(
        ticket=ticket, acceptance=acceptance, lot=lot, settlement=settlement
    )


class ChainEventIn(BaseModel):
    ticketId: str                 # Wiegeschein-Nr oder -ID (Rückgrat)
    stage: str = "kette"          # wiegung|annahme|lager|abrechnung|kette
    eventType: str = "notiz"      # erfasst|freigegeben|eingelagert|abgerechnet|abweichung|korrektur|storniert|notiz
    refLabel: Optional[str] = None
    statusFrom: Optional[str] = None
    statusTo: Optional[str] = None
    mengeKg: Optional[float] = None
    abweichungGrund: Optional[str] = None
    bediener: Optional[str] = None


@router.post("/traceability/sync", response_model=dict[str, Any], summary="Ereignis-Log aus Ist-Zustand befüllen (Backfill, idempotent)")
def sync_events(
    ticket: str = Query(..., description="Wiegeschein-Nr oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return SupplyChainEventService(db, tenant_id).sync_from_state(ticket)


@router.post("/events", response_model=dict[str, Any], summary="Ketten-Ereignis erfassen (Korrektur/Abweichung/Notiz/Storno)")
def add_event(
    body: ChainEventIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    # Eingabe-Ticket auf das Wiegeschein-Rückgrat auflösen.
    svc = SupplyChainTraceService(db, tenant_id)
    ticket_id = svc._resolve_ticket_id(ticket=body.ticketId, acceptance=body.ticketId,
                                       lot=body.ticketId, settlement=body.ticketId)
    if not ticket_id:
        return {"ok": False, "detail": "Ticket nicht auflösbar."}
    event = SupplyChainEventService(db, tenant_id).record(
        ticket_id=ticket_id,
        stage=body.stage,
        event_type=body.eventType,
        ref_label=body.refLabel,
        status_from=body.statusFrom,
        status_to=body.statusTo,
        menge_kg=body.mengeKg,
        abweichung_grund=body.abweichungGrund,
        bediener=body.bediener or "KIM",
        source="manual",
    )
    return {"ok": True, "event": event}


# ── Lager-Lot-Folgeaktionen (Sperre / QS-Freigabe / Schwund) ────────────────────
class LotReasonIn(BaseModel):
    grund: str
    bediener: Optional[str] = None


class LotShrinkageIn(BaseModel):
    mengeKg: float
    grund: str
    bediener: Optional[str] = None


@router.post("/lots/{lot_id}/block", response_model=dict[str, Any], summary="Silo-Lot sperren (Sperrbestand)")
def block_lot(
    lot_id: str,
    body: LotReasonIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return SupplyChainLotService(db, tenant_id).block(lot_id, body.grund, body.bediener or "KIM")
    except LotActionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/lots/{lot_id}/release", response_model=dict[str, Any], summary="Silo-Lot QS-freigeben")
def release_lot(
    lot_id: str,
    body: LotReasonIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return SupplyChainLotService(db, tenant_id).release(lot_id, body.grund, body.bediener or "KIM")
    except LotActionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/lots/{lot_id}/shrinkage", response_model=dict[str, Any], summary="Schwund auf Silo-Lot buchen")
def shrinkage_lot(
    lot_id: str,
    body: LotShrinkageIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return SupplyChainLotService(db, tenant_id).shrinkage(lot_id, body.mengeKg, body.grund, body.bediener or "KIM")
    except LotActionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/traceability/cancel", response_model=dict[str, Any], summary="Lieferkette stornieren (durchgängig)")
def cancel_chain(
    ticket: str = Query(..., description="Wiegeschein-Nr oder -ID"),
    body: LotReasonIn = ...,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return SupplyChainLotService(db, tenant_id).cancel_chain(ticket, body.grund, body.bediener or "KIM")
    except LotActionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
