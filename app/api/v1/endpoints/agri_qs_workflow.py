"""WM-AGRI-QS-003 endpoints fuer Silo-Lot-QS-Workflow."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.agri_qs_workflow_service import AgriQsWorkflowError, AgriQsWorkflowService


class AgriQsOut(BaseSchema):
    model_config = ConfigDict(extra="allow")


class LotQsTransitionIn(BaseModel):
    targetStatus: str
    reason: str
    operator: str
    sampleId: Optional[str] = None
    analysisId: Optional[str] = None
    labDocumentId: Optional[str] = None
    gmpEvidenceId: Optional[str] = None
    vlogEvidenceId: Optional[str] = None
    productionReleaseRef: Optional[str] = None


router = APIRouter(prefix="/supply-chain", tags=["supply-chain", "agrar", "qs", "lager"])


def _svc(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> AgriQsWorkflowService:
    return AgriQsWorkflowService(db, tenant_id)


@router.post("/lots/{lot_id}/qs-transition", response_model=AgriQsOut, summary="Silo-Lot QS-Status wechseln")
def change_lot_qs_status(
    lot_id: str,
    body: LotQsTransitionIn,
    svc: AgriQsWorkflowService = Depends(_svc),
) -> Any:
    try:
        return svc.change_lot_qs_status(
            lot_id=lot_id,
            target_status=body.targetStatus,
            reason=body.reason,
            operator=body.operator,
            sample_id=body.sampleId,
            analysis_id=body.analysisId,
            lab_document_id=body.labDocumentId,
            gmp_evidence_id=body.gmpEvidenceId,
            vlog_evidence_id=body.vlogEvidenceId,
            production_release_ref=body.productionReleaseRef,
        )
    except AgriQsWorkflowError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
