"""WM-SILO-RULE-ENGINE-001 — Zielzellen-Vorschlag API."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.silo_rule_engine_service import SiloRuleEngineService

router = APIRouter(prefix="/silo", tags=["silo", "rule-engine"])


def _svc(
    db: Session = Depends(get_db),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> SiloRuleEngineService:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID fehlt")
    return SiloRuleEngineService(db=db, tenant_id=x_tenant_id)


@router.get("/zielzellen-vorschlag", response_model=dict[str, Any], summary="Zielzellen-Vorschlag fuer Einlagerung")
def zielzellen_vorschlag(
    artikel_id: str = Query(..., description="Artikel-ID / Material-Nr"),
    menge_kg: float = Query(..., gt=0, description="Einzulagernde Menge in kg"),
    ernte_jahr: int | None = Query(None, description="Erntejahr (optional, verbessert Segregation)"),
    qualitaetsklasse: str | None = Query(None),
    warehouse_id: str | None = Query(None, description="Auf bestimmtes Lager einschraenken"),
    max_vorschlaege: int = Query(5, ge=1, le=20),
    svc: SiloRuleEngineService = Depends(_svc),
) -> dict[str, Any]:
    vorschlaege = svc.vorschlag(
        artikel_id=artikel_id,
        menge_kg=menge_kg,
        ernte_jahr=ernte_jahr,
        qualitaetsklasse=qualitaetsklasse,
        warehouse_id=warehouse_id,
        max_vorschlaege=max_vorschlaege,
    )
    return {
        "artikel_id": artikel_id,
        "angefragte_menge_kg": menge_kg,
        "ernte_jahr": ernte_jahr,
        "warehouse_id": warehouse_id,
        "vorschlaege": vorschlaege,
        "anzahl_vorschlaege": len(vorschlaege),
    }


@router.get(
    "/zielzellen-vorschlag/lot/{lot_id}",
    response_model=dict[str, Any],
    summary="Zielzellen-Vorschlag direkt aus Lot",
)
def zielzellen_vorschlag_lot(
    lot_id: str,
    menge_kg: float | None = Query(None, gt=0),
    warehouse_id: str | None = Query(None),
    max_vorschlaege: int = Query(5, ge=1, le=20),
    svc: SiloRuleEngineService = Depends(_svc),
) -> dict[str, Any]:
    result = svc.vorschlag_fuer_lot(
        lot_id=lot_id,
        menge_kg=menge_kg,
        warehouse_id=warehouse_id,
        max_vorschlaege=max_vorschlaege,
    )
    if "fehler" in result:
        raise HTTPException(status_code=404, detail=result["fehler"])
    return result
