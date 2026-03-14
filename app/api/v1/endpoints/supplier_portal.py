from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid

router = APIRouter(prefix="/supplier-portal", tags=["supplier-portal"])

# --- Schemas ---

class SupplierLieferungView(BaseModel):
    """Gefilterte Lieferungsansicht für Lieferanten (Rolle: supplier)."""
    lieferung_id: str
    datum: str
    sorte: str
    menge_t: float
    qualitaet: str
    status: str
    abgerechnet: bool
    schema_version: int = 1

class SupplierKontraktView(BaseModel):
    lieferant_id: str
    kontrakt_id: str
    sorte: str
    menge_soll_t: float
    menge_geliefert_t: float
    offene_menge_t: float
    preis_eur_t: float
    status: str
    schema_version: int = 1

class SupplierPreisauskunft(BaseModel):
    sorte: str
    qualitaet: str
    stichtag: str
    preis_eur_t: Optional[float]
    verfuegbar: bool
    schema_version: int = 1

# --- Endpoints ---

@router.get("/lieferanten/{lieferant_id}/lieferungen", response_model=list[SupplierLieferungView])
def get_lieferant_lieferungen(
    lieferant_id: str,
    von: Optional[str] = Query(None),
    bis: Optional[str] = Query(None),
):
    """Liefert alle Lieferungen eines Lieferanten (gefilterte Sicht, Rolle: supplier)."""
    # Stub: In Wave 7 werden echte DB-Abfragen mit Tenant-Filter eingebaut
    return []

@router.get("/lieferanten/{lieferant_id}/kontrakte", response_model=list[SupplierKontraktView])
def get_lieferant_kontrakte(lieferant_id: str):
    """Liefert alle Kontrakte eines Lieferanten mit Erfüllungsstand."""
    return []

@router.get("/preisauskunft", response_model=SupplierPreisauskunft)
def get_preisauskunft(
    sorte: str = Query(...),
    qualitaet: str = Query(...),
    stichtag: str = Query(...),
):
    """Gibt Preisauskunft für Sorte/Qualität an einem Stichtag."""
    return SupplierPreisauskunft(
        sorte=sorte,
        qualitaet=qualitaet,
        stichtag=stichtag,
        preis_eur_t=None,
        verfuegbar=False,
    )

@router.get("/silo-bestaende")
def get_silo_bestaende(tenant_id: str = Query(...)):
    """Gibt aggregierte Silo-Bestände zurück (Lieferanten sehen nur eigene Ware)."""
    return {"tenant_id": tenant_id, "gesamtbestand_t": 0.0, "zellen": [], "schema_version": 1}
