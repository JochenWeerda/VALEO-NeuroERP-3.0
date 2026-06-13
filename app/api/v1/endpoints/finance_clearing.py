"""Zahlungseingang / OP-Auszifferung (DOM-FIN-004.3)."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.finance_clearing_service import ClearingError, FinanceClearingService
from app.documents.router_helpers import get_repository, get_from_store, save_to_store

router = APIRouter(prefix="/finance", tags=["finance", "fibu", "op"])


@router.get("/zahlungseingang/clearings", summary="Auszifferungen je OP")
def clearings(
    rechnungsnr: str = Query(..., description="Rechnungsnummer des OP"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": FinanceClearingService(db, tenant_id).clearings(rechnungsnr)}


class PaymentIn(BaseModel):
    rechnungsnr: str
    betrag: float
    skontoBetrag: Optional[float] = 0.0
    zahlungsdatum: Optional[str] = None      # ISO; Default heute
    zahlungsart: Optional[str] = None
    bediener: Optional[str] = None


@router.post("/zahlungseingang", summary="Zahlungseingang erfassen (OP ausziffern)")
def record_payment(
    body: PaymentIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    zd: Optional[date] = None
    if body.zahlungsdatum:
        try:
            zd = date.fromisoformat(body.zahlungsdatum[:10])
        except ValueError:
            raise HTTPException(status_code=422, detail="Ungültiges Datum (erwartet ISO YYYY-MM-DD).")
    try:
        result = FinanceClearingService(db, tenant_id).record_payment(
            rechnungsnr=body.rechnungsnr, betrag=body.betrag, skonto_betrag=body.skontoBetrag or 0.0,
            zahlungsdatum=zd, zahlungsart=body.zahlungsart or "ueberweisung", bediener=body.bediener or "KIM",
        )
    except ClearingError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Belegbruch schließen: Rechnung auf BEZAHLT setzen wenn vollständig ausgeziffert
    if result.get("voll_ausgeziffert"):
        try:
            repo = get_repository(db)
            inv = get_from_store("sales_invoice", body.rechnungsnr, repo)
            if inv and inv.get("status") not in ("BEZAHLT", "STORNIERT"):
                inv["status"] = "BEZAHLT"
                save_to_store("sales_invoice", body.rechnungsnr, inv, repo)
        except Exception:  # noqa: BLE001 — invoice status update is non-blocking
            pass

    return result
