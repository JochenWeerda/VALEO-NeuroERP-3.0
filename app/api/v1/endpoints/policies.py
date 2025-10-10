"""
Policy Manager API Endpoints
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

from app.services.policy_service import (
    PolicyStore,
    PolicyEngine,
    Rule,
    Alert,
    Decision
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/policy", tags=["policy"])

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


class RestoreRequest(BaseModel):
    """Restore-Request"""
    json: str


# Endpoints

@router.get("/list")
async def list_policies() -> Dict[str, Any]:
    """
    Listet alle Policies auf

    Returns:
        Dict mit ok=True und data=List[Rule]
    """
    try:
        rules = policy_store.list()
        return {"ok": True, "data": [r.dict() for r in rules]}
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upsert")
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


@router.post("/create")
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


@router.post("/update")
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


@router.post("/delete")
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


@router.post("/test", response_model=TestResponse)
async def test_policy(request: TestRequest) -> TestResponse:
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
        logger.info(f"Policy test: {request.alert.kpiId} -> {decision.type}")
        return TestResponse(ok=True, decision=decision)
    except Exception as e:
        logger.error(f"Failed to test policy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export")
async def export_policies():
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


@router.post("/restore")
async def restore_policies(request: RestoreRequest) -> Dict[str, Any]:
    """
    Importiert Policies aus JSON (ACHTUNG: ersetzt alle!)

    Args:
        request: RestoreRequest mit json

    Returns:
        Dict mit ok=True
    """
    try:
        policy_store.restore_json(request.json)
        logger.warning("Policies restored from JSON - all previous policies replaced")
        return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to restore policies: {e}")
        raise HTTPException(status_code=400, detail=str(e))

