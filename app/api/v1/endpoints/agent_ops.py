"""NeuroASSIST Agent-Ops endpoints (stub — Persistence/Ops-Leitstand)."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/agents/neuroassist/ops", tags=["agents", "neuroassist", "ops"])

_EMPTY = {}


class _Open(BaseModel):
    model_config = {"extra": "allow"}


@router.get("/overview", response_model=dict)
def ops_overview(tenant_id: str = "default"):
    return {"tenant_id": tenant_id, "status": "ok", "open_tickets": 0, "budget_used": 0}


@router.get("/dashboard", response_model=dict)
def ops_dashboard(tenant_id: str = "default"):
    return {"tenant_id": tenant_id, "tickets": [], "revisions": [], "budgets": []}


@router.get("/interventions", response_model=list)
def ops_interventions(tenant_id: str = "default"):
    return []


@router.get("/templates/export", response_model=dict)
def ops_templates_export(tenant_id: str = "default", template_key: str = "default"):
    return {"tenant_id": tenant_id, "template_key": template_key, "templates": []}


@router.get("/skill-packs", response_model=list)
def ops_skill_packs(tenant_id: str = "default"):
    return []


@router.get("/mobile-overview", response_model=dict)
def ops_mobile_overview(tenant_id: str = "default"):
    return {"tenant_id": tenant_id, "active_sessions": 0, "pending_scans": 0}


@router.get("/plugin-boundary-review", response_model=dict)
def ops_plugin_boundary_review(tenant_id: str = "default"):
    return {"tenant_id": tenant_id, "violations": [], "ok": True}


@router.get("/control-center", response_model=dict)
def ops_control_center(tenant_id: str = "default"):
    return {"tenant_id": tenant_id, "mode": "auto", "alerts": [], "uptime_s": 0}


@router.get("/persistence", response_model=dict)
def ops_persistence(tenant_id: str = "default"):
    return {
        "tenant_id": tenant_id,
        "state_path": "runtime/agent-ops/state.json",
        "history_path": "runtime/agent-ops/history.jsonl",
        "persisted": False,
        "persisted_at": None,
        "history_count": 0,
        "recent_events": [],
        "snapshot_counts": {
            "budget_count": 0,
            "ticket_count": 0,
            "revision_count": 0,
            "intervention_count": 0,
        },
    }


@router.post("/tickets/{ticket_id}/interventions", response_model=dict, status_code=201)
def create_intervention(ticket_id: str, body: dict = None, tenant_id: str = "default"):  # type: ignore[assignment]
    return {"ok": True, "ticket_id": ticket_id}
