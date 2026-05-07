"""Privacy Erasure Decision API (evaluate / execute) — crm-gdpr."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.db.models import GDPRRequest, GDPRRequestStatus, GDPRRequestType
from app.db.session import get_db
from app.schemas.privacy_erasure import (
    ErasureEvaluateRequest,
    ErasureEvaluateResponse,
    ErasureExecuteRequest,
    ErasureExecuteResponse,
)
from app.services.privacy_erasure.repository_factory import build_privacy_erasure_repository
from app.services.privacy_erasure.service import PrivacyErasureError, PrivacyErasureService

router = APIRouter(
    prefix="/erasure-requests",
    tags=["privacy-erasure"],
)


def _map_error(exc: PrivacyErasureError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=str(exc))


async def _get_deletion_request_in_progress(
    db: AsyncSession,
    request_id: UUID,
) -> GDPRRequest:
    g = await db.get(GDPRRequest, request_id)
    if not g:
        raise HTTPException(status_code=404, detail="GDPR request not found")
    if g.request_type != GDPRRequestType.DELETION:
        raise HTTPException(status_code=400, detail="Request type must be deletion")
    if g.status != GDPRRequestStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400,
            detail="Request must be verified and in progress (same gate as legacy delete)",
        )
    return g


@router.post(
    "/{request_id}/evaluate",
    response_model=ErasureEvaluateResponse,
    summary="Policy-Evaluate für Löschantrag",
    description=(
        "Liefert `decision`, `allowed_actions` und `blocked_actions`. "
        "Default ohne `PRIVACY_ERASURE_LEGACY_CRM_EVALUATE`: konservativ "
        "`insufficient_information` (kein ERP-Discovery). Siehe ADR 2026-05-06."
    ),
)
async def evaluate_erasure(
    request_id: UUID,
    body: ErasureEvaluateRequest,
    db: AsyncSession = Depends(get_db),
    x_actor_id: str | None = Header(
        default=None,
        alias="X-Actor-ID",
        description="Sobald IAM angebunden: Pflicht empfohlen",
    ),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
) -> ErasureEvaluateResponse:
    gdpr_request = await _get_deletion_request_in_progress(db, request_id)
    if body.tenant_id != gdpr_request.tenant_id:
        raise HTTPException(status_code=403, detail="tenant_id mismatch")

    cid = (
        x_correlation_id.strip()
        if x_correlation_id and x_correlation_id.strip()
        else str(uuid4())
    )

    try:
        repo = build_privacy_erasure_repository(db)
        svc = PrivacyErasureService(repo)
        return await svc.evaluate(
            request_id=request_id,
            subject_id=gdpr_request.contact_id,
            body=body,
            correlation_id=cid,
            actor_id=x_actor_id,
        )
    except PrivacyErasureError as exc:
        raise _map_error(exc) from exc


@router.post(
    "/{request_id}/execute",
    response_model=ErasureExecuteResponse,
    summary="Ausführung unter gültiger Decision",
    description=(
        "`action` muss aus `evaluate.allowed_actions` stammen (z.B. Übergang "
        "`legacy_http_crm_erasure_orchestration`). Idempotenz über "
        "tenant_id + request_id + decision_id + action."
    ),
)
async def execute_erasure(
    request_id: UUID,
    body: ErasureExecuteRequest,
    db: AsyncSession = Depends(get_db),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
) -> ErasureExecuteResponse:
    gdpr_request = await _get_deletion_request_in_progress(db, request_id)
    if body.tenant_id != gdpr_request.tenant_id:
        raise HTTPException(status_code=403, detail="tenant_id mismatch")

    cid = (
        x_correlation_id.strip()
        if x_correlation_id and x_correlation_id.strip()
        else str(uuid4())
    )

    try:
        repo = build_privacy_erasure_repository(db)
        svc = PrivacyErasureService(repo)
        return await svc.execute(
            request_id=request_id,
            subject_id=gdpr_request.contact_id,
            body=body,
            correlation_id=cid,
        )
    except PrivacyErasureError as exc:
        raise _map_error(exc) from exc


@router.get(
    "/policy-hints",
    summary="Konfigurationshinweise (Lesen ohne Seiteneffekt)",
)
async def erasure_policy_hints():
    """Offenlegung relevanter Settings ohne Secrets."""
    return {
        "privacy_policy_version": settings.PRIVACY_POLICY_VERSION,
        "privacy_erasure_legacy_crm_evaluate": settings.PRIVACY_ERASURE_LEGACY_CRM_EVALUATE,
        "privacy_gate_gdpr_delete_behind_decision": settings.PRIVACY_GATE_GDPR_DELETE_BEHIND_DECISION,
        "privacy_decision_ttl_seconds": settings.PRIVACY_DECISION_TTL_SECONDS,
        "privacy_execute_require_actor_id": settings.PRIVACY_EXECUTE_REQUIRE_ACTOR_ID,
        "privacy_erasure_persistence": settings.PRIVACY_ERASURE_PERSISTENCE,
    }
