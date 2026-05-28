"""Report and print endpoints for traceability, weighing PDFs and labels."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.report_print_service import ReportPrintService

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/report-print", tags=["report-print", "agrar", "waage"])


class ReportPrintLabelRequest(BaseModel):
    partie_ref: str = Field(..., min_length=1)
    charge_ref: str = Field(..., min_length=1)
    article_ref: str = Field(..., min_length=1)
    gtin: str = Field(..., min_length=8)
    sscc: str = Field(..., min_length=8)
    quantity_kg: float = Field(..., gt=0)
    label_type: str = "GS1_LOGISTICS_LABEL"


def _svc(db: Session, tenant_id: str) -> ReportPrintService:
    return ReportPrintService(db, tenant_id)


@router.get("/readiness", summary="Report print readiness abrufen",
    response_model=CompatFlexOut
)
def get_report_print_readiness(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Return repo-side readiness for report/print contracts."""
    return _svc(db, tenant_id).build_readiness()


@router.get("/parties/{partie_ref}/genealogy", summary="Partie genealogy abrufen",
    response_model=CompatFlexOut
)
def get_partie_genealogy(
    partie_ref: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Return traceability graph for one agrar partie."""
    return _svc(db, tenant_id).build_partie_genealogy(partie_ref)


@router.get("/weighing-tickets/{ticket_ref}/pdf-preview", summary="Weighing ticket pdf preview abrufen",
    response_model=CompatFlexOut
)
def get_weighing_ticket_pdf_preview(
    ticket_ref: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Return deterministic PDF preview metadata for one weighing ticket."""
    return _svc(db, tenant_id).build_weighing_pdf_preview(ticket_ref)


@router.post("/labels", status_code=201, summary="Label payload anlegen",
    response_model=CompatFlexOut
)
def create_label_payload(
    payload: ReportPrintLabelRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Return print-ready GS1 label data for a partie/charge."""
    return _svc(db, tenant_id).build_label_payload(payload.model_dump())
