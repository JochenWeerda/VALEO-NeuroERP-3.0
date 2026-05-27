"""
Schaeden (Damage Reports) API
Schadenmeldung und Versicherungsverwaltung
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.uuid7 import uuid7

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schaeden", tags=["schaeden", "versicherung"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class Versicherung(BaseModel):
    id: str
    bezeichnung: str
    vertragsnummer: str
    typ: str  # hagel, haftpflicht, feuer, kasko, inhalt
    versicherer: str
    gueltig_bis: Optional[str] = None


class SchadenMeldungCreate(BaseModel):
    art: str = Field(..., description="Schadenart: hagel, frost, feuer, unfall, diebstahl")
    datum: str = Field(..., description="Schadendatum (YYYY-MM-DD)")
    ort: Optional[str] = Field(None, description="Schadenort z.B. Schlag S-001")
    beschreibung: str = Field(..., min_length=1, description="Schadenhergang")
    schadenhoehe: float = Field(0, ge=0, description="Geschätzte Schadenhöhe in EUR")
    versicherung_id: Optional[str] = Field(None, description="ID der zuständigen Versicherung")
    zeuge: Optional[str] = Field(None, description="Name(n) der Zeugen")


class SchadenMeldungResponse(BaseModel):
    id: str
    meldungsnummer: str
    art: str
    datum: str
    ort: Optional[str]
    beschreibung: str
    schadenhoehe: float
    versicherung_id: Optional[str]
    versicherung_bezeichnung: Optional[str]
    zeuge: Optional[str]
    status: str  # entwurf, gemeldet, in_bearbeitung, reguliert, abgelehnt
    erstellt_am: str
    aktualisiert_am: str


# ── Versicherungen ────────────────────────────────────────────────────────────

@router.get("/versicherungen", response_model=List[Versicherung], summary="Versicherungen auflisten")
async def list_versicherungen(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Alle Versicherungsverträge des Mandanten."""
    # Demo data — in production this would query domain_erp.versicherungen
    return [
        Versicherung(
            id="vers-001",
            bezeichnung="Vereinigte Hagel",
            vertragsnummer="VH-2024-5678",
            typ="hagel",
            versicherer="Vereinigte Hagelversicherung VVaG",
            gueltig_bis="2026-12-31",
        ),
        Versicherung(
            id="vers-002",
            bezeichnung="R+V Haftpflicht",
            vertragsnummer="RV-2024-1234",
            typ="haftpflicht",
            versicherer="R+V Versicherung AG",
            gueltig_bis="2026-12-31",
        ),
        Versicherung(
            id="vers-003",
            bezeichnung="LVM Feuerversicherung",
            vertragsnummer="LVM-2024-9012",
            typ="feuer",
            versicherer="LVM Versicherung",
            gueltig_bis="2027-06-30",
        ),
        Versicherung(
            id="vers-004",
            bezeichnung="Allianz Kfz-Kasko",
            vertragsnummer="ALZ-2024-3456",
            typ="kasko",
            versicherer="Allianz Versicherungs-AG",
            gueltig_bis="2026-12-31",
        ),
    ]


# ── Schadenmeldungen ──────────────────────────────────────────────────────────

@router.post("/meldungen", response_model=SchadenMeldungResponse, status_code=201, summary="Schadenmeldung anlegen")
async def create_schadenmeldung(
    data: SchadenMeldungCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neue Schadenmeldung anlegen."""
    meldung_id = str(uuid7())
    now = datetime.utcnow().isoformat()
    nr = f"SM-{datetime.utcnow().strftime('%Y%m%d')}-{meldung_id[:6].upper()}"

    # In production: INSERT INTO domain_erp.schaden_meldungen ...
    logger.info(
        "Schadenmeldung %s erstellt: art=%s, ort=%s, hoehe=%.2f, tenant=%s",
        nr, data.art, data.ort, data.schadenhoehe, tenant_id,
    )

    # Lookup versicherung label
    versicherung_bezeichnung = None
    if data.versicherung_id:
        lookup = {
            "vers-001": "Vereinigte Hagel (VH-2024-5678)",
            "vers-002": "R+V Haftpflicht (RV-2024-1234)",
            "vers-003": "LVM Feuerversicherung (LVM-2024-9012)",
            "vers-004": "Allianz Kfz-Kasko (ALZ-2024-3456)",
        }
        versicherung_bezeichnung = lookup.get(data.versicherung_id, data.versicherung_id)

    return SchadenMeldungResponse(
        id=meldung_id,
        meldungsnummer=nr,
        art=data.art,
        datum=data.datum,
        ort=data.ort,
        beschreibung=data.beschreibung,
        schadenhoehe=data.schadenhoehe,
        versicherung_id=data.versicherung_id,
        versicherung_bezeichnung=versicherung_bezeichnung,
        zeuge=data.zeuge,
        status="gemeldet",
        erstellt_am=now,
        aktualisiert_am=now,
    )


@router.get("/meldungen", response_model=List[SchadenMeldungResponse], summary="Schadenmeldungen auflisten")
async def list_schadenmeldungen(
    status: Optional[str] = Query(None, description="Filter nach Status"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Alle Schadenmeldungen des Mandanten."""
    # Demo data — in production this would query the DB
    return [
        SchadenMeldungResponse(
            id="sm-demo-001",
            meldungsnummer="SM-20260315-A1B2C3",
            art="hagel",
            datum="2026-03-15",
            ort="Schlag S-042",
            beschreibung="Hagelschaden am Winterweizen, ca. 30% Bestandsverlust",
            schadenhoehe=12500.0,
            versicherung_id="vers-001",
            versicherung_bezeichnung="Vereinigte Hagel (VH-2024-5678)",
            zeuge="Hans Müller",
            status="in_bearbeitung",
            erstellt_am="2026-03-15T14:30:00",
            aktualisiert_am="2026-03-16T09:00:00",
        ),
    ]
