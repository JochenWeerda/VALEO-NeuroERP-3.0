"""WM-AGRI-LOT-LINK-001 endpoint: Annahme/Waage-Lot in Silozelle buchen."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.agri_lot_link_booking_service import AgriLotLinkBookingService


class AgriLotLinkOut(BaseSchema):
    model_config = ConfigDict(extra="allow")


class LotCellLinkIn(BaseModel):
    warehouse_id: str
    lot_id: str
    target_cell_id: str
    quantity_kg: Optional[Decimal] = None
    booked_by: Optional[str] = None
    reference: Optional[str] = None


router = APIRouter()


def _svc(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> AgriLotLinkBookingService:
    return AgriLotLinkBookingService(db, tenant_id)


@router.post(
    "/material-flow/lot-link",
    response_model=AgriLotLinkOut,
    status_code=status.HTTP_200_OK,
    summary="POST /material-flow/lot-link",
)
def book_lot_to_cell(
    payload: LotCellLinkIn,
    svc: AgriLotLinkBookingService = Depends(_svc),
) -> Any:
    """Bucht ein aktives Waage/WE-Lot transaktional in eine Silozelle."""
    try:
        return svc.book_lot_to_cell(
            lot_id=payload.lot_id,
            target_cell_id=payload.target_cell_id,
            warehouse_id=payload.warehouse_id,
            quantity_kg=payload.quantity_kg,
            booked_by=payload.booked_by or "system",
            reference=payload.reference,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
