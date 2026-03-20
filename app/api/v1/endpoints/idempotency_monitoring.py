from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.action_idempotency import get_action_idempotency_store

router = APIRouter(prefix="/process/idempotency", tags=["process-kernel", "idempotency", "monitoring"])


@router.get("/summary", summary="Idempotency Summary")
def get_idempotency_summary() -> dict:
    store = get_action_idempotency_store()
    return store.summary()


@router.get("/audit", summary="Idempotency Audit Feed")
def get_idempotency_audit(
    tenant_id: str | None = Query(default=None, description="Optional tenant filter"),
    command_name: str | None = Query(default=None, description="Optional command filter"),
    aggregate_type: str | None = Query(default=None, description="Optional aggregate filter"),
    limit: int = Query(default=100, ge=1, le=1000),
) -> dict:
    store = get_action_idempotency_store()
    trail = store.audit_feed(
        tenant_id=tenant_id,
        command_name=command_name,
        aggregate_type=aggregate_type,
        limit=limit,
    )
    return trail.as_dict()
