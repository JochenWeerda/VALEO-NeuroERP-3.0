"""Cross-Sell-Auswertung Milchvieh (Hygiene-Bedarf + Kraftfutter-Potenzial).

Read-only Endpoints über ``MilchviehCrossSellService`` für die gleichnamige Maske.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.services.milchvieh_crosssell_service import MilchviehCrossSellService

router = APIRouter(prefix="/agrar/milchvieh-crosssell", tags=["agrar", "crosssell"])


class MilchviehCrossSellItem(BaseSchema):
    kunden_nr: str
    name: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    herd_size_kuehe: int = 0
    herd_size_group: Optional[str] = None
    milch_kg: Optional[int] = None
    ecm_kg: Optional[int] = None
    fett_pct: Optional[float] = None
    eiw_pct: Optional[float] = None
    milchmenge_l_jahr: int = 0
    zellzahl_tsd_ml: Optional[int] = None
    zellzahl_quelle: Optional[str] = None
    hygiene_bedarf: str = "niedrig"
    hygiene_dipp_l_jahr: int = 0
    kraftfutter_t_jahr_min: float = 0
    kraftfutter_t_jahr_max: float = 0
    crosssell_ziel_eur: int = 0
    crosssell_adressierbar_eur_min: int = 0
    crosssell_adressierbar_eur_max: int = 0
    crosssell_gewinnbar_eur_min: int = 0
    crosssell_gewinnbar_eur_max: int = 0
    produktgruppen: list[dict[str, Any]] = []


@router.get("", response_model=list[MilchviehCrossSellItem], summary="Milchvieh Cross-Sell-Liste")
def list_crosssell(
    hygiene_bedarf: Optional[str] = Query(None, description="Filter: niedrig|mittel|hoch"),
    min_kuehe: Optional[int] = Query(None, ge=0, description="Mindest-Herdengröße"),
    sort: str = Query("kraftfutter", description="kraftfutter|hygiene|umsatz"),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return MilchviehCrossSellService(db).list_items(
        hygiene_bedarf=hygiene_bedarf, min_kuehe=min_kuehe, sort=sort
    )


@router.get("/summary", summary="Cross-Sell-Summen (Potenziale gesamt)")
def crosssell_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    return MilchviehCrossSellService(db).summary()


@router.get("/map", summary="Betriebe als GeoJSON (Karte + Kennzahlen-Flyover)")
def crosssell_map(
    hygiene_bedarf: Optional[str] = Query(None),
    min_kuehe: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return MilchviehCrossSellService(db).map_features(hygiene_bedarf=hygiene_bedarf, min_kuehe=min_kuehe)
