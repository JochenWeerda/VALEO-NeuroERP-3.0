"""B2B webshop integration endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.webshop_integration_service import WebshopIntegrationService

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/webshop", tags=["webshop", "integration"])


class WebshopKonfiguration(BaseModel):
    id: Optional[str] = None
    shop_url: str
    api_key: str
    shop_system: str
    sync_interval_minutes: int = 15
    is_active: bool = True


class WebshopKonfigurationOut(BaseModel):
    id: str
    shop_url: str
    shop_system: str
    sync_interval_minutes: int
    is_active: bool


class ArtikelPosition(BaseModel):
    artikel_nr: str = Field(..., min_length=1)
    menge: float
    preis_brutto: float


class WebshopBestellung(BaseModel):
    externe_bestellnr: str
    shop_system: str
    kunde_email: str
    kunde_name: str
    artikel_positionen: list[ArtikelPosition]
    gesamtbetrag_brutto: float
    bestelldatum: str
    status: str = "NEU"


class WebshopSyncResult(BaseModel):
    sync_id: str
    shop_system: str
    neue_bestellungen: int
    fehler: int
    verarbeitete_ids: list[str]
    duplikate: list[str] = []
    blockierte_bestellungen: list[dict] = []
    sync_zeitpunkt: str


def _svc(db: Session, tenant_id: str) -> WebshopIntegrationService:
    return WebshopIntegrationService(db, tenant_id)


@router.get("/konfigurationen", response_model=list[WebshopKonfigurationOut], summary="Konfigurationen auflisten")
def list_konfigurationen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List shop configurations. API keys are never returned."""
    return _svc(db, tenant_id).list_configurations()


@router.post("/konfigurationen", response_model=WebshopKonfigurationOut, status_code=201, summary="Konfiguration anlegen")
def create_konfiguration(
    payload: WebshopKonfiguration,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Register a shop connection. API keys are write-only."""
    return _svc(db, tenant_id).create_configuration(payload.model_dump())


@router.delete("/konfigurationen/{id}", status_code=204, response_class=Response, response_model=None, summary="Konfiguration löschen")
def delete_konfiguration(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Remove a shop configuration."""
    _svc(db, tenant_id).delete_configuration(id)
    return Response(status_code=204)


@router.get("/bestellungen", response_model=list[WebshopBestellung], summary="Bestellungen auflisten")
def list_bestellungen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List imported shop orders."""
    return _svc(db, tenant_id).list_orders()


@router.get("/bestellungen/{external_order_no}", response_model=WebshopBestellung, summary="Bestellung abrufen")
def get_bestellung(
    external_order_no: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Read one imported shop order by external order number."""
    order = _svc(db, tenant_id).get_order(external_order_no)
    if not order:
        raise HTTPException(status_code=404, detail="Webshop-Bestellung nicht gefunden")
    return order


@router.post("/bestellungen/import", response_model=WebshopSyncResult, summary="Bestellungen importieren")
def import_bestellungen(
    bestellungen: list[WebshopBestellung],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Manual import trigger with idempotency and business blocker reporting."""
    return _svc(db, tenant_id).import_orders([b.model_dump() for b in bestellungen])


@router.post("/bestellungen/{id}/verarbeiten", summary="Verarbeiten",
    response_model=None
)
def verarbeiten(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Convert a clean shop order to an ERP-visible order reference."""
    return _svc(db, tenant_id).process_order(id)


@router.get("/sync-status", summary="Status synchronisieren",
    response_model=CompatFlexOut
)
def sync_status(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Connection and import health."""
    return _svc(db, tenant_id).sync_status()


@router.get("/orders", summary="Orders auflisten",
    response_model=CompatFlexOut
)
def list_orders(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List imported webshop orders (alias for /bestellungen, English path)."""
    return _svc(db, tenant_id).list_orders()


class ConvertOrderResult(BaseModel):
    auftrag_id: str
    auftrag_nr: str
    positionen_count: int


@router.post("/orders/{order_id}/convert", response_model=ConvertOrderResult, summary="Order umwandeln")
def convert_order(
    order_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Convert a webshop order to an ERP Auftrag.

    Returns ``auftrag_id``, ``auftrag_nr``, and ``positionen_count``.
    Raises 404 when the order does not exist, 422 when it has business blockers.
    """
    svc = _svc(db, tenant_id)
    order = svc.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Webshop-Bestellung nicht gefunden")
    blockers = order.get("blockers") or []
    if blockers:
        raise HTTPException(
            status_code=422,
            detail={"message": "Bestellung hat fachliche Blocker", "blockers": blockers},
        )
    result = svc.process_order(order_id)
    auftrag_nr = result.get("auftrag_nr") or ""
    return ConvertOrderResult(
        auftrag_id=str(order.get("id") or order_id),
        auftrag_nr=auftrag_nr,
        positionen_count=len(order.get("artikel_positionen") or []),
    )


@router.get("/sync-log", summary="Log synchronisieren",
    response_model=CompatFlexOut
)
def sync_log(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Return last 50 sync events from the webshop sync log."""
    return _svc(db, tenant_id).get_sync_log()
