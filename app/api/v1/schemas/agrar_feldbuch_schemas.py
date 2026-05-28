"""Auto-generated domain schemas for agrar feldbuch."""
from __future__ import annotations
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class AgrarFeldbuchOut(BaseSchema):
    """Response schema for agrar feldbuch endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class SchlagCreate(BaseModel):
    customer_id: str
    name: str
    flik: Optional[str] = None
    flaeche: float
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: str = "aktiv"
    created_by: Optional[str] = None


class SchlagUpdate(BaseModel):
    name: Optional[str] = None
    flik: Optional[str] = None
    flaeche: Optional[float] = None
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: Optional[str] = None


class MassnahmeCreate(BaseModel):
    customer_id: str
    schlag_id: Optional[str] = None
    datum: datetime
    uhrzeit: Optional[str] = None
    typ: str
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    mittel_id: Optional[str] = None
    mittel_typ: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    quelle: str = "erp_service"
    lieferschein_id: Optional[str] = None
    auflagen: Optional[list[str]] = None
    wartezeit_tage: Optional[int] = None
    windgeschwindigkeit: Optional[float] = None
    temperatur: Optional[float] = None
    compliant: bool = True
    bemerkung: Optional[str] = None


class MassnahmeUpdate(BaseModel):
    schlag_id: Optional[str] = None
    datum: Optional[datetime] = None
    uhrzeit: Optional[str] = None
    typ: Optional[str] = None
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    auflagen: Optional[list[str]] = None
    wartezeit_tage: Optional[int] = None
    windgeschwindigkeit: Optional[float] = None
    temperatur: Optional[float] = None
    compliant: Optional[bool] = None
    bemerkung: Optional[str] = None


class FromLieferscheinCreate(BaseModel):
    lieferschein_id: str
    lieferschein_datum: datetime
    customer_id: str
    schlag_id: str
    artikel_name: str
    menge: float
    einheit: str
    flaeche: float
    anwender: str = "VALEO NeuroERP"


class MassnahmeBulkDeleteIn(BaseModel):
    ids: list[str] = Field(default_factory=list, min_length=1, max_length=100)


class MassnahmeBulkDeleteErrorOut(BaseModel):
    id: str
    detail: str


class MassnahmeBulkDeleteOut(BaseModel):
    requested: int
    deleted: int
    missing_ids: list[str] = Field(default_factory=list)
    errors: list[MassnahmeBulkDeleteErrorOut] = Field(default_factory=list)


class GeometryUpdate(BaseModel):
    geometry_geojson: str  # RFC 7946 GeoJSON Polygon/MultiPolygon als JSON-String

