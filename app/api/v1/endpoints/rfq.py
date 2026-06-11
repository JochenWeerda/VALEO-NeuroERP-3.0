"""
Einkauf — RFQ (Request for Quotation) — Anfrageprozess

Endpoints:
  GET/POST /einkauf/rfq                        → Anfragen liste/erstellen
  GET      /einkauf/rfq/{id}                   → Detail mit Angeboten
  POST     /einkauf/rfq/{id}/send              → An Lieferanten versenden
  POST     /einkauf/rfq/{id}/quotes            → Angebot erfassen
  GET      /einkauf/rfq/{id}/comparison        → Angebotsvergleich (nach Preis)
  POST     /einkauf/rfq/{id}/accept/{quote_id} → Zuschlag erteilen → Bestellung
"""

from __future__ import annotations

from datetime import date
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.rfq_service import RfqService

router = APIRouter(prefix="/einkauf/rfq", tags=["einkauf", "rfq"])


class RfqOut(BaseSchema):
    model_config = ConfigDict(extra="allow")


class RfqCreate(BaseModel):
    article_id: str
    quantity: float
    needed_by_date: Optional[date] = None
    notes: Optional[str] = None


class QuoteCreate(BaseModel):
    supplier_id: str
    unit_price: float
    delivery_days: Optional[int] = None
    notes: Optional[str] = None


class SendRequest(BaseModel):
    supplier_ids: Optional[List[str]] = None


def _service(db: Session, tenant_id: str) -> RfqService:
    return RfqService(db, tenant_id)


@router.get("", summary="Rfq auflisten", response_model=list[RfqOut])
def list_rfq(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    try:
        return _service(db, tenant_id).list_requests()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc


@router.post("", summary="Rfq anlegen", response_model=RfqOut, status_code=201)
def create_rfq(
    body: RfqCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _service(db, tenant_id).create_request(
            article_id=body.article_id,
            quantity=body.quantity,
            needed_by_date=body.needed_by_date,
            notes=body.notes,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc


@router.get("/{rfq_id}", summary="Rfq abrufen", response_model=RfqOut)
def get_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        rfq = _service(db, tenant_id).get_request(rfq_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc
    if not rfq:
        raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")
    return rfq


@router.post("/{rfq_id}/send", summary="Rfq senden", response_model=RfqOut)
def send_rfq(
    rfq_id: int,
    body: SendRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _service(db, tenant_id).send_request(rfq_id, body.supplier_ids)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc


@router.post("/{rfq_id}/quotes", summary="Quote hinzufügen", response_model=RfqOut, status_code=201)
def add_quote(
    rfq_id: int,
    body: QuoteCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _service(db, tenant_id).add_quote(
            rfq_id,
            supplier_id=body.supplier_id,
            unit_price=body.unit_price,
            delivery_days=body.delivery_days,
            notes=body.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc


@router.get("/{rfq_id}/comparison", summary="Quotes compare", response_model=RfqOut)
def compare_quotes(
    rfq_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _service(db, tenant_id).compare_quotes(rfq_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc


@router.post("/{rfq_id}/accept/{quote_id}", summary="Quote akzeptieren", response_model=RfqOut)
def accept_quote(
    rfq_id: int,
    quote_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _service(db, tenant_id).accept_quote(rfq_id, quote_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc
