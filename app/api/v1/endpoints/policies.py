"""
Policy Manager API Endpoints
"""

from fastapi import APIRouter, HTTPException, Request, Query, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.middleware.rate_limit import limiter
from app.core.database import get_db
from app.core.explainability import ExplainabilityView, build_policy_explainability_view
from app.core.policy_decisions import PolicyOverrideResolution
from app.services.policy_service import (
    PolicyStore,
    PolicyEngine,
    Rule,
    Alert,
    Decision
)

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema, StatusResponse


router = APIRouter(tags=["policy"])

# Global Policy Store Instance
policy_store = PolicyStore()


# Request/Response Models
class UpsertRequest(BaseModel):
    """Upsert-Request (einzeln oder bulk)"""
    rules: List[Rule]


class DeleteRequest(BaseModel):
    """Delete-Request"""
    id: str


class TestRequest(BaseModel):
    """Test-Request (Simulator)"""
    alert: Alert
    roles: List[str]


class TestResponse(BaseModel):
    """Test-Response"""
    ok: bool
    decision: Decision
    override_resolution: PolicyOverrideResolution
    explainability: ExplainabilityView


class RestoreRequest(BaseModel):
    """Restore-Request (JSON-String der wiederherzustellenden Policies)."""
    json_payload: str = Field(..., alias="json", description="JSON-String der Policy-Daten")


def resolve_tenant_policy_override(
    db,
    tenant_id: str,
    rule_id: str | None,
    base_params: dict[str, Any] | None = None,
) -> PolicyOverrideResolution:
    resolved_rule_id = str(rule_id or "policy.default")
    return PolicyOverrideResolution(
        rule_id=resolved_rule_id,
        effective_scope="global",
        effective_scope_key="policy-engine",
        effective_enabled=True,
        effective_params=dict(base_params or {}),
        applied_reason="policy default",
        applied_source="policy-engine",
    )


# Endpoints

@router.get("/policy/list", summary="Policies auflisten",
    response_model=StatusResponse
)
async def list_policies() -> Dict[str, Any]:
    """
    Listet alle Policies auf

    Returns:
        Dict mit success=True und data=List[Rule]
    """
    try:
        rules = policy_store.list()
        return {"success": True, "data": [r.dict() for r in rules]}
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policy/upsert", summary="Policies upsert",
    response_model=StatusResponse
)
async def upsert_policies(request: UpsertRequest) -> Dict[str, Any]:
    """
    Erstellt oder aktualisiert Policies (bulk)

    Args:
        request: UpsertRequest mit rules[]

    Returns:
        Dict mit ok=True und count=Anzahl
    """
    try:
        policy_store.bulk_upsert(request.rules)
        logger.info(f"Upserted {len(request.rules)} policies")
        return {"ok": True, "count": len(request.rules)}
    except Exception as e:
        logger.error(f"Failed to upsert policies: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/policy/create", summary="Policy anlegen",
    response_model=StatusResponse
)
async def create_policy(rule: Rule) -> Dict[str, Any]:
    """
    Erstellt oder aktualisiert eine einzelne Policy

    Args:
        rule: Rule-Objekt

    Returns:
        Dict mit ok=True
    """
    try:
        policy_store.upsert(rule)
        logger.info(f"Created/updated policy: {rule.id}")
        return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to create policy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/policy/update", summary="Policy aktualisieren",
    response_model=StatusResponse
)
async def update_policy(rule: Rule) -> Dict[str, Any]:
    """
    Aktualisiert eine existierende Policy

    Args:
        rule: Rule-Objekt

    Returns:
        Dict mit ok=True
    """
    try:
        existing = policy_store.get(rule.id)
        if not existing:
            raise HTTPException(status_code=404, detail="Policy not found")

        policy_store.upsert(rule)
        logger.info(f"Updated policy: {rule.id}")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update policy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/policy/delete", summary="Policy löschen",
    response_model=StatusResponse
)
async def delete_policy(request: DeleteRequest) -> Dict[str, Any]:
    """
    Löscht eine Policy

    Args:
        request: DeleteRequest mit id

    Returns:
        Dict mit ok=True
    """
    try:
        existing = policy_store.get(request.id)
        if not existing:
            raise HTTPException(status_code=404, detail="Policy not found")

        policy_store.delete(request.id)
        logger.info(f"Deleted policy: {request.id}")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policy/test", response_model=TestResponse, summary="Policy testen")
async def test_policy(
    request: TestRequest,
    tenant_id: str = Query("system", description="Tenant ID"),
    db=Depends(get_db),
) -> TestResponse:
    """
    Test-Simulator - testet Policy-Entscheidung gegen Alert

    Args:
        request: TestRequest mit alert und roles

    Returns:
        TestResponse mit Decision
    """
    try:
        rules = policy_store.list()
        decision = PolicyEngine.decide(request.roles, request.alert, rules)
        resolution = resolve_tenant_policy_override(
            db,
            tenant_id,
            decision.ruleId,
            base_params=decision.resolvedParams or {},
        )
        effective_enabled = resolution.effective_enabled
        blocked = effective_enabled is False or decision.type == "deny"
        needs_approval = bool(decision.needsApproval) and not blocked
        effective_decision = decision.model_copy(
            update={
                "type": "deny" if blocked else decision.type,
                "resolvedParams": dict(resolution.effective_params or decision.resolvedParams or {}),
            }
        )
        explainability = build_policy_explainability_view(
            resolution,
            blocked=blocked,
            needs_approval=needs_approval,
        )
        logger.info(f"Policy test: {request.alert.kpiId} -> {decision.type}")
        return TestResponse(
            ok=True,
            decision=effective_decision,
            override_resolution=resolution,
            explainability=explainability,
        )
    except Exception as e:
        logger.error(f"Failed to test policy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/policy/export", summary="Policies exportieren",
    response_model=StatusResponse
)
@limiter.limit("10/minute")
async def export_policies(request: Request):
    """
    Exportiert alle Policies als JSON-Download

    Returns:
        StreamingResponse mit JSON-Datei
    """
    try:
        json_str = policy_store.export_json()

        def iter_json():
            yield json_str.encode()

        return StreamingResponse(
            iter_json(),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=policies-backup.json"}
        )
    except Exception as e:
        logger.error(f"Failed to export policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policy/restore", summary="Policies wiederherstellen",
    response_model=StatusResponse
)
@limiter.limit("5/minute")
async def restore_policies(request: Request, request_body: RestoreRequest) -> Dict[str, Any]:
    """
    Importiert Policies aus JSON (ACHTUNG: ersetzt alle!)

    Args:
        request: RestoreRequest mit json

    Returns:
        Dict mit ok=True
    """
    try:
        policy_store.restore_json(request_body.json_payload)
        logger.warning("Policies restored from JSON - all previous policies replaced")
        return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to restore policies: {e}")
        raise HTTPException(status_code=400, detail=str(e))

