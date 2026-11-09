"""CSV-Import von Angeboten in DocFlow (BELEG-052, 09.11.2026; vorher ``/sales/offers/actions/import-csv``).

Je Zeile ein Angebotsentwurf (``app/services/sales_offer_import.py``); nur Menschen, idempotent je Schluessel,
alles oder nichts.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/belege/sales_offer", tags=["belege", "import"])


class SalesOfferImportCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    csv_content: str = Field(min_length=1)
    idempotency_key: str = Field(alias="_idempotencyKey", min_length=1, max_length=200)
    audit_reason: Optional[str] = Field(default=None, alias="_auditReason", max_length=1000)
    mode: Optional[str] = Field(default=None, alias="_mode")


class SalesOfferImportOut(BaseModel):
    """Ergebnis von ``sales_offer_import.import_offers``; ``replayed`` bei wiederholtem Idempotenzschluessel."""
    success: bool
    count: int
    offer_ids: list[str]
    auditEntryId: Optional[str] = None
    replayed: bool = False


@router.post("/actions/import-csv", response_model=SalesOfferImportOut, summary="Angebote aus CSV als DocFlow-Entwuerfe",
             dependencies=SCHREIBEN["VERKAUF"])
async def import_sales_offers(payload: SalesOfferImportCommand, tenant_id: str = Depends(get_tenant_id),
                              db: Session = Depends(get_db)):
    from app.services.sales_offer_import import import_offers

    if payload.mode not in (None, "execute"):
        raise HTTPException(422, "Unsupported import mode")
    return import_offers(db, tenant_id, payload.csv_content, payload.idempotency_key, payload.audit_reason)
