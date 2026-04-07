"""
Etiketten (Label Printing) API
Druckerverwaltung und Druckaufträge
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.uuid7 import uuid7

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/etiketten", tags=["etiketten", "druck"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class Drucker(BaseModel):
    id: str
    name: str
    standort: str
    typ: str  # zebra, cab, sato, brother
    modell: str
    status: str  # online, offline, fehler, wartung
    ip: Optional[str] = None


class DruckauftragCreate(BaseModel):
    chargen_id: str = Field(..., description="Chargen-ID")
    artikel: Optional[str] = Field(None, description="Artikelbezeichnung")
    menge: Optional[float] = Field(None, ge=0, description="Menge in t")
    lieferant: Optional[str] = Field(None, description="Lieferant")
    eingang: Optional[str] = Field(None, description="Eingangsdatum (YYYY-MM-DD)")
    anzahl_etiketten: int = Field(1, ge=1, description="Anzahl Etiketten")
    drucker_id: str = Field(..., description="Ziel-Drucker ID")


class DruckauftragResponse(BaseModel):
    id: str
    auftrags_nr: str
    chargen_id: str
    artikel: Optional[str]
    menge: Optional[float]
    lieferant: Optional[str]
    eingang: Optional[str]
    anzahl_etiketten: int
    drucker_id: str
    drucker_name: str
    status: str  # erstellt, druckt, fertig, fehler
    erstellt_am: str


# ── Drucker ────────────────────────────────────────────────────────────────────

@router.get("/drucker", response_model=List[Drucker])
async def list_drucker(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Alle verfügbaren Etikettendrucker."""
    # Demo data — in production this would come from device management
    return [
        Drucker(
            id="drk-001",
            name="Zebra ZT230 (Annahme)",
            standort="Annahme Halle 1",
            typ="zebra",
            modell="ZT230",
            status="online",
            ip="192.168.10.51",
        ),
        Drucker(
            id="drk-002",
            name="Zebra ZT410 (Lager)",
            standort="Lager Halle 2",
            typ="zebra",
            modell="ZT410",
            status="online",
            ip="192.168.10.52",
        ),
        Drucker(
            id="drk-003",
            name="CAB SQUIX 4 (Versand)",
            standort="Versand",
            typ="cab",
            modell="SQUIX 4",
            status="offline",
            ip="192.168.10.53",
        ),
    ]


# ── Druckaufträge ─────────────────────────────────────────────────────────────

@router.post("/druckauftrag", response_model=DruckauftragResponse, status_code=201)
async def create_druckauftrag(
    data: DruckauftragCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Druckauftrag für Etiketten erstellen und an Drucker senden."""
    auftrag_id = str(uuid7())
    now = datetime.utcnow().isoformat()
    nr = f"ETK-{datetime.utcnow().strftime('%Y%m%d')}-{auftrag_id[:6].upper()}"

    # Lookup printer name
    drucker_lookup = {
        "drk-001": "Zebra ZT230 (Annahme)",
        "drk-002": "Zebra ZT410 (Lager)",
        "drk-003": "CAB SQUIX 4 (Versand)",
    }
    drucker_name = drucker_lookup.get(data.drucker_id, data.drucker_id)

    logger.info(
        "Druckauftrag %s: %d Etiketten für Charge %s an %s, tenant=%s",
        nr, data.anzahl_etiketten, data.chargen_id, drucker_name, tenant_id,
    )

    # In production: INSERT INTO domain_erp.druckauftraege + send to print spooler
    return DruckauftragResponse(
        id=auftrag_id,
        auftrags_nr=nr,
        chargen_id=data.chargen_id,
        artikel=data.artikel,
        menge=data.menge,
        lieferant=data.lieferant,
        eingang=data.eingang,
        anzahl_etiketten=data.anzahl_etiketten,
        drucker_id=data.drucker_id,
        drucker_name=drucker_name,
        status="erstellt",
        erstellt_am=now,
    )
