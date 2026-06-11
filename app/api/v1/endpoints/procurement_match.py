"""Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004).

Bestellung ↔ Wareneingang (Basis; Rechnungs-Stufe folgt). Read-only: Mengen-/
Wertabweichung und Lücken je Bestellung sichtbar machen.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.procurement_match_service import ProcurementMatchService

router = APIRouter(prefix="/procurement", tags=["procurement", "einkauf"])


class FollowUpIn(BaseModel):
    bestellnummer: str = Field(..., min_length=1)
    action_type: str = Field(..., description="nachforderung | reklamation | eskalation | freigabe")
    grund: str = Field(..., min_length=3)
    ausnahme_code: Optional[str] = None
    created_by: Optional[str] = None


class ErsCreditIn(BaseModel):
    bestellnummer: str = Field(..., min_length=1)
    grund: Optional[str] = None
    created_by: Optional[str] = None


@router.get("/match/orders", summary="Bestellungen mit Match-Übersicht (Picker)")
def list_orders(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": ProcurementMatchService(db, tenant_id).list_orders(limit=limit)}


@router.get("/match", summary="3-Wege-Match je Bestellung (Bestellung ↔ Wareneingang)")
def match(
    bestellung: str = Query(..., description="Bestellnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).match(bestellung)


@router.get("/match/three-way", summary="3-Wege-Match inkl. Eingangsrechnung")
def match_three_way(
    bestellung: str = Query(..., description="Bestellnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).match_three_way(bestellung)


@router.get("/match/follow-up", summary="Folgeaktionen je Bestellung (append-only)")
def list_follow_ups(
    bestellung: str = Query(..., description="Bestellnummer"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {
        "items": ProcurementMatchService(db, tenant_id).list_follow_ups(bestellung),
    }


@router.post("/match/follow-up", summary="Folgeaktion erfassen (append-only)", status_code=201)
def create_follow_up(
    body: FollowUpIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    service = ProcurementMatchService(db, tenant_id)
    try:
        return service.create_follow_up(
            bestellnummer=body.bestellnummer,
            action_type=body.action_type,
            grund=body.grund,
            ausnahme_code=body.ausnahme_code,
            created_by=body.created_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Folgeaktion konnte nicht gespeichert werden: {exc}") from exc


@router.get("/match/ers/preview", summary="ERS-Gutschrift-Vorschau je Bestellung")
def preview_ers(
    bestellung: str = Query(..., description="Bestellnummer"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).preview_ers(bestellung)


@router.get("/match/ers", summary="Erfasste ERS-Gutschriften je Bestellung")
def list_ers_credits(
    bestellung: str = Query(..., description="Bestellnummer"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {
        "items": ProcurementMatchService(db, tenant_id).list_ers_credits(bestellung),
    }


@router.post("/match/ers", summary="ERS-Gutschrift aus Match-Abweichung erzeugen", status_code=201)
def create_ers_credit(
    body: ErsCreditIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    service = ProcurementMatchService(db, tenant_id)
    try:
        return service.create_ers_credit(
            bestellnummer=body.bestellnummer,
            grund=body.grund,
            created_by=body.created_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"ERS-Gutschrift konnte nicht erzeugt werden: {exc}") from exc
