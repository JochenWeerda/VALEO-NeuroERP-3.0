"""Geo-Endpoints für den Außendienst-Kartenviewer.

Liefert Betriebe als GeoJSON-FeatureCollection mit Koordinaten und den
verknüpften Potenzialen (GAP-Fläche/Prämien, Milchleistung, Partner-Score).
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.geo_pipeline import get_map_points

router = APIRouter(prefix="/geo", tags=["geo", "prospecting"])


class GeoPointProperties(BaseModel):
    name: str
    plz: Optional[str] = None
    ort: Optional[str] = None
    gap_area_ha: float = 0.0
    gap_potential_eur: int = 0
    has_dairy: bool = False
    dairy_milch_kg: Optional[float] = None
    dairy_fe_kg: Optional[float] = None
    herd_size_group: Optional[str] = None
    trend: Optional[str] = None
    trend_rel_pct: Optional[float] = None
    is_customer: bool = False
    kunden_nr: Optional[str] = None
    score: int = 0
    segment: str = "C"


class GeoFeature(BaseModel):
    type: str = "Feature"
    geometry: dict[str, Any]
    properties: GeoPointProperties


class GeoFeatureCollectionOut(BaseModel):
    type: str = "FeatureCollection"
    features: list[GeoFeature] = Field(default_factory=list)


@router.get("/map-points", response_model=GeoFeatureCollectionOut, summary="Betriebe als GeoJSON mit Potenzialen")
async def map_points(
    only_geocoded: bool = Query(True, description="Nur bereits geocodierte Punkte zurückgeben"),
    db: Session = Depends(get_db),
):
    """Liefert alle Karten-Betriebe als GeoJSON inkl. GAP-/Milch-Potenzial und Partner-Score."""
    return get_map_points(db, only_geocoded=only_geocoded)
