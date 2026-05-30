"""
AI Agents API
Endpoints for triggering and managing agent workflows
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ....core.logging import set_correlation_id

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class AgentOut(BaseSchema):
    """Typed response schema for AgentOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


router = APIRouter()


class CapabilityResponse(BaseModel):
    capability_key: str
    title: str
    kind: str
    domain: str
    role_key: str
    orchestration_pattern: str
    default_stage_sequence: list[str]
    readiness: str
    workflow_module: str
    workflow_builder: str
    workflow_entrypoint: str
    description: str
    process_scopes: list[str]


class NeuroAssistRunRequest(BaseModel):
    capability_key: str
    tenant_id: str = "system"
    parameters: dict = Field(default_factory=dict)


class NeuroAssistRunResponse(BaseModel):
    run_id: str
    correlation_id: str
    capability_key: str
    status: str
    started_at: str
    runtime: dict
    result: dict = Field(default_factory=dict)


class NeuroAssistGateActionRequest(BaseModel):
    gate_type: str
    decision: str
    rejection_reason: str | None = None


class NeuroAssistGateActionResponse(BaseModel):
    run_id: str
    correlation_id: str
    capability_key: str
    started_at: str
    status: str
    runtime: dict
    result: dict = Field(default_factory=dict)


class AgentBudgetUpdateRequest(BaseModel):
    tenant_id: str = "system"
    monthly_budget_cents: int = Field(ge=0)
    changed_by: str = "admin-ui"


class AgentOpsOverviewResponse(BaseModel):
    tenant_id: str
    schema_version: int
    budget_total_cents: int
    spent_total_cents: int
    remaining_total_cents: int
    blocked_budget_count: int
    monthly_run_count: int
    budget_summaries: list[dict] = Field(default_factory=list)
    cost_ledger: list[dict] = Field(default_factory=list)
    heartbeats: list[dict] = Field(default_factory=list)
    roles: list[dict] = Field(default_factory=list)
    profiles: list[dict] = Field(default_factory=list)
    goals: list[dict] = Field(default_factory=list)
    open_tickets: list[dict] = Field(default_factory=list)


class AgentTicketResponse(BaseModel):
    tenant_id: str
    ticket_id: str
    run_id: str
    capability_key: str
    role_key: str
    goal_key: str
    status: str
    opened_at: str
    updated_at: str
    latest_stage_key: str
    latest_summary: str
    work_item_type: str = "agent_case"
    work_item_id: str | None = None
    work_item_title: str | None = None
    owner_role: str | None = None
    escalation_role: str | None = None
    allowed_actions: list[str] = Field(default_factory=list)
    blocker_reasons: list[str] = Field(default_factory=list)
    requires_review: bool = False
    is_stale: bool = False
    review_due_at: str | None = None
    age_minutes: int = 0


class AgentInterventionRequest(BaseModel):
    tenant_id: str = "system"
    action: str
    requested_by: str = "admin-ui"
    note: str | None = None


class AgentTemplateImportRequest(BaseModel):
    tenant_id: str = "system"
    template: dict


class AgentHeartbeatUpdateRequest(BaseModel):
    tenant_id: str = "system"
    cadence: str | None = None
    enabled: bool | None = None
    stale_after_hours: int | None = Field(default=None, ge=1)
    changed_by: str = "admin-ui"


class AgentProfileUpdateRequest(BaseModel):
    tenant_id: str = "system"
    owner_role: str | None = None
    escalation_role: str | None = None
    review_sla_hours: int | None = Field(default=None, ge=1)
    stale_after_hours: int | None = Field(default=None, ge=1)
    allowed_actions: list[str] | None = None
    changed_by: str = "admin-ui"


class AgentSkillPackUpdateRequest(BaseModel):
    tenant_id: str = "system"
    skills: list[str] | None = None
    prompt_contracts: list[str] | None = None
    changed_by: str = "admin-ui"


class LowStockSimulateRequest(BaseModel):
    tenant_id: str = "default"
    artikel_id: str
    artikel_name: str
    bestand: float = Field(ge=0)
    mindestbestand: float = Field(gt=0)
    einheit: str = "Stk"
    lieferant_id: str | None = None
    durchschnittlicher_verbrauch_pro_tag: float | None = Field(default=None, ge=0)


class AgentPersistenceStatusResponse(BaseModel):
    tenant_id: str
    state_path: str
    history_path: str
    persisted: bool
    persisted_at: str | None = None
    history_count: int
    recent_events: list[dict] = Field(default_factory=list)
    snapshot_counts: dict = Field(default_factory=dict)
    schema_version: int = 1


class ControlCenterPlanItemRequest(BaseModel):
    tenant_id: str = "system"
    plan_id: str
    title: str
    kind: str
    owner: str
    scheduled_for: str
    status: str
    notes: str | None = None


class ControlCenterIncidentActionRequest(BaseModel):
    tenant_id: str = "system"
    action: str
    requested_by: str = "admin-ui"
    note: str | None = None


def _get_neuroassist_service():
    try:
        from ....agents import get_neuroassist_service
    except ModuleNotFoundError as exc:
        logger.error("NeuroASSIST dependencies are not available: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="NeuroASSIST runtime dependencies are not installed on this backend",
        ) from exc
    return get_neuroassist_service()


class _NeuroAssistServiceProxy:
    """
    Modul-globaler Proxy zum NeuroASSIST-Service.
    Ermöglicht monkeypatch in Tests: monkeypatch.setattr(agents.neuroassist_service, "run_capability", ...)
    Leitet alle Attributzugriffe an den echten Service weiter.
    """
    def __getattr__(self, name: str):
        return getattr(_get_neuroassist_service(), name)


neuroassist_service = _NeuroAssistServiceProxy()


def _get_agent_ops_service():
    try:
        from ....agents import get_agent_ops_service
    except ModuleNotFoundError as exc:
        logger.error("Agent Ops dependencies are not available: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Agent Ops runtime dependencies are not installed on this backend",
        ) from exc
    return get_agent_ops_service()


def _get_agent_ops_template_model():
    from ....agents import AgentTemplateExport

    return AgentTemplateExport


def _get_control_center_helpers():
    from ....agents import (
        apply_control_center_incident_action,
        build_control_center_incidents,
        build_control_center_planning,
        upsert_control_center_plan_item,
    )

    return {
        "build_planning": build_control_center_planning,
        "build_incidents": build_control_center_incidents,
        "upsert_plan_item": upsert_control_center_plan_item,
        "apply_incident_action": apply_control_center_incident_action,
    }


def _list_capability_responses(productive_only: bool) -> list[CapabilityResponse]:
    neuroassist_service = _get_neuroassist_service()
    capabilities = neuroassist_service.list_capabilities(productive_only=productive_only)
    return [
        CapabilityResponse(
            capability_key=cap.capability_key,
            title=cap.title,
            kind=cap.kind,
            domain=cap.domain,
            role_key=cap.role_key,
            orchestration_pattern=cap.orchestration_pattern,
            default_stage_sequence=list(cap.default_stage_sequence),
            readiness=cap.readiness,
            workflow_module=cap.workflow_module,
            workflow_builder=cap.workflow_builder,
            workflow_entrypoint=cap.workflow_entrypoint,
            description=cap.description,
            process_scopes=list(cap.process_scopes),
        )
        for cap in capabilities
    ]


@router.get("/neuroassist/capabilities", response_model=list[CapabilityResponse], summary="Neuroassist capabilities auflisten")
async def list_neuroassist_capabilities(productive_only: bool = True):
    return _list_capability_responses(productive_only)


@router.get("/neuroassist/runs", response_model=list[NeuroAssistRunResponse], summary="Neuroassist runs auflisten")
async def list_neuroassist_runs(status: str | None = None, limit: int = 50):
    try:
        runs = await neuroassist_service.list_runs(status=status, limit=limit)
        return [NeuroAssistRunResponse(**r) for r in runs]
    except AttributeError:
        # Service may not implement list_runs — return empty list gracefully
        return []
    except Exception as exc:
        logger.error("NeuroASSIST list runs failed: %s", exc, exc_info=True)
        return []


@router.post("/neuroassist/runs", response_model=NeuroAssistRunResponse, summary="Neuroassist capability ausführen")
async def run_neuroassist_capability(request: NeuroAssistRunRequest):
    logger.info(
        "Running NeuroASSIST capability '%s' (tenant: %s)",
        request.capability_key,
        request.tenant_id,
    )

    try:
        result = await neuroassist_service.run_capability(
            request.capability_key,
            tenant_id=request.tenant_id,
            parameters=request.parameters,
        )
        set_correlation_id(result["correlation_id"])
        return NeuroAssistRunResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST capability run failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST run failed: {str(exc)}")


@router.get("/neuroassist/runs/{run_id}", response_model=NeuroAssistRunResponse, summary="Neuroassist run status abrufen")
async def get_neuroassist_run_status(run_id: str):
    try:
        return NeuroAssistRunResponse(**(await neuroassist_service.get_run_status(run_id)))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST run status lookup failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST status lookup failed: {str(exc)}")


@router.post("/neuroassist/runs/{run_id}/gates", response_model=NeuroAssistGateActionResponse, summary="Neuroassist gate action apply")
async def apply_neuroassist_gate_action(run_id: str, request: NeuroAssistGateActionRequest):
    try:
        return NeuroAssistGateActionResponse(
            **(
                await neuroassist_service.apply_gate_action(
                    run_id,
                    gate_type=request.gate_type,
                    decision=request.decision,
                    rejection_reason=request.rejection_reason,
                )
            )
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST gate action failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST gate action failed: {str(exc)}")


@router.get("/neuroassist/ops/overview", response_model=AgentOpsOverviewResponse, summary="Neuroassist ops overview abrufen")
async def get_neuroassist_ops_overview(tenant_id: str = "system"):
    try:
        return AgentOpsOverviewResponse(**_get_agent_ops_service().build_overview(tenant_id).model_dump(mode="json"))
    except Exception as exc:
        logger.error("NeuroASSIST ops overview failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST ops overview failed: {str(exc)}")


@router.get("/neuroassist/ops/tickets", response_model=list[AgentTicketResponse], summary="Neuroassist ops tickets auflisten")
async def list_neuroassist_ops_tickets(tenant_id: str = "system", include_closed: bool = False):
    try:
        tickets = _get_agent_ops_service().list_tickets(tenant_id, include_closed=include_closed)
        return [AgentTicketResponse(**ticket.model_dump(mode="json")) for ticket in tickets]
    except Exception as exc:
        logger.error("NeuroASSIST ops tickets failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST ops tickets failed: {str(exc)}")


@router.post("/neuroassist/ops/budgets/{capability_key}", response_model=AgentOut, summary="Neuroassist budget aktualisieren")
async def update_neuroassist_budget(capability_key: str, request: AgentBudgetUpdateRequest):
    try:
        budget = _get_agent_ops_service().set_budget(
            request.tenant_id,
            capability_key,
            request.monthly_budget_cents,
            changed_by=request.changed_by,
        )
        return budget.model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST budget update failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST budget update failed: {str(exc)}")


@router.get("/neuroassist/ops/dashboard", response_model=AgentOut, summary="Neuroassist ops dashboard abrufen")
async def get_neuroassist_ops_dashboard(tenant_id: str = "system"):
    try:
        return _get_agent_ops_service().build_dashboard(tenant_id).model_dump(mode="json")
    except Exception as exc:
        logger.error("NeuroASSIST ops dashboard failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST ops dashboard failed: {str(exc)}")


@router.get("/neuroassist/ops/control-center", response_model=AgentOut, summary="Neuroassist control center abrufen")
async def get_neuroassist_control_center(tenant_id: str = "system"):
    try:
        return _get_agent_ops_service().build_control_center(tenant_id).model_dump(mode="json")
    except Exception as exc:
        logger.error("NeuroASSIST control center failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST control center failed: {str(exc)}")


@router.get("/neuroassist/ops/mobile-overview", response_model=AgentOut, summary="Neuroassist mobile ops overview abrufen")
async def get_neuroassist_mobile_ops_overview(tenant_id: str = "system"):
    try:
        return _get_agent_ops_service().build_mobile_overview(tenant_id).model_dump(mode="json")
    except Exception as exc:
        logger.error("NeuroASSIST mobile ops overview failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST mobile ops overview failed: {str(exc)}")


@router.get("/neuroassist/ops/interventions", response_model=list[AgentOut], summary="Neuroassist interventions auflisten")
async def list_neuroassist_interventions(tenant_id: str = "system"):
    try:
        return [item.model_dump(mode="json") for item in _get_agent_ops_service().list_interventions(tenant_id)]
    except Exception as exc:
        logger.error("NeuroASSIST interventions failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST interventions failed: {str(exc)}")


@router.get("/neuroassist/ops/config-revisions", response_model=list[AgentOut], summary="Neuroassist config revisions auflisten")
async def list_neuroassist_config_revisions(tenant_id: str = "system"):
    try:
        return [item.model_dump(mode="json") for item in _get_agent_ops_service().list_config_revisions(tenant_id)]
    except Exception as exc:
        logger.error("NeuroASSIST config revisions failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST config revisions failed: {str(exc)}")


@router.get("/neuroassist/ops/persistence", response_model=AgentPersistenceStatusResponse, summary="Neuroassist persistence status abrufen")
async def get_neuroassist_persistence_status(tenant_id: str = "system"):
    try:
        return AgentPersistenceStatusResponse(**_get_agent_ops_service().build_persistence_status(tenant_id))
    except Exception as exc:
        logger.error("NeuroASSIST persistence status failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST persistence status failed: {str(exc)}")


@router.get("/neuroassist/ops/planning", response_model=AgentOut, summary="Neuroassist control center planning abrufen")
async def get_neuroassist_control_center_planning(tenant_id: str = "system"):
    try:
        return _get_control_center_helpers()["build_planning"](tenant_id)
    except Exception as exc:
        logger.error("NeuroASSIST control-center planning failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST control-center planning failed: {str(exc)}")


@router.post("/neuroassist/ops/planning/items", response_model=AgentOut, summary="Neuroassist control center plan item upsert")
async def upsert_neuroassist_control_center_plan_item(request: ControlCenterPlanItemRequest):
    try:
        return _get_control_center_helpers()["upsert_plan_item"](
            request.tenant_id,
            plan_id=request.plan_id,
            title=request.title,
            kind=request.kind,
            owner=request.owner,
            scheduled_for=request.scheduled_for,
            status=request.status,
            notes=request.notes,
        )
    except Exception as exc:
        logger.error("NeuroASSIST control-center plan update failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST control-center plan update failed: {str(exc)}")


@router.get("/neuroassist/ops/incidents", response_model=AgentOut, summary="Neuroassist control center incidents abrufen")
async def get_neuroassist_control_center_incidents(tenant_id: str = "system"):
    try:
        return _get_control_center_helpers()["build_incidents"](tenant_id)
    except Exception as exc:
        logger.error("NeuroASSIST control-center incidents failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST control-center incidents failed: {str(exc)}")


@router.post("/neuroassist/ops/incidents/{incident_id}/actions", response_model=AgentOut, summary="Neuroassist control center incident action apply")
async def apply_neuroassist_control_center_incident_action(incident_id: str, request: ControlCenterIncidentActionRequest):
    try:
        return _get_control_center_helpers()["apply_incident_action"](
            request.tenant_id,
            incident_id,
            action=request.action,
            requested_by=request.requested_by,
            note=request.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST control-center incident action failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST control-center incident action failed: {str(exc)}")


@router.post("/neuroassist/ops/tickets/{ticket_id}/interventions", response_model=AgentOut, summary="Neuroassist intervention apply")
async def apply_neuroassist_intervention(ticket_id: str, request: AgentInterventionRequest):
    try:
        return _get_agent_ops_service().apply_intervention(
            request.tenant_id,
            ticket_id,
            action=request.action,
            requested_by=request.requested_by,
            note=request.note,
        ).model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST intervention failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST intervention failed: {str(exc)}")


@router.get("/neuroassist/ops/templates/export", response_model=AgentOut, summary="Neuroassist template exportieren")
async def export_neuroassist_template(tenant_id: str = "system", template_key: str = "default"):
    try:
        return _get_agent_ops_service().export_template(tenant_id, template_key=template_key).model_dump(mode="json")
    except Exception as exc:
        logger.error("NeuroASSIST template export failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST template export failed: {str(exc)}")


@router.post("/neuroassist/ops/templates/import", response_model=AgentOut, summary="Neuroassist template importieren")
async def import_neuroassist_template(request: AgentTemplateImportRequest):
    try:
        template = _get_agent_ops_template_model().model_validate(request.template)
        return _get_agent_ops_service().import_template(request.tenant_id, template).model_dump(mode="json")
    except Exception as exc:
        logger.error("NeuroASSIST template import failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST template import failed: {str(exc)}")


@router.post("/neuroassist/ops/heartbeats/{capability_key}", response_model=AgentOut, summary="Neuroassist heartbeat aktualisieren")
async def update_neuroassist_heartbeat(capability_key: str, request: AgentHeartbeatUpdateRequest):
    try:
        return _get_agent_ops_service().set_heartbeat(
            request.tenant_id,
            capability_key,
            cadence=request.cadence,
            enabled=request.enabled,
            stale_after_hours=request.stale_after_hours,
            changed_by=request.changed_by,
        ).model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST heartbeat update failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST heartbeat update failed: {str(exc)}")


@router.post("/neuroassist/ops/profiles/{capability_key}", response_model=AgentOut, summary="Neuroassist profile aktualisieren")
async def update_neuroassist_profile(capability_key: str, request: AgentProfileUpdateRequest):
    try:
        return _get_agent_ops_service().set_profile(
            request.tenant_id,
            capability_key,
            owner_role=request.owner_role,
            escalation_role=request.escalation_role,
            review_sla_hours=request.review_sla_hours,
            stale_after_hours=request.stale_after_hours,
            allowed_actions=request.allowed_actions,
            changed_by=request.changed_by,
        ).model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST profile update failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST profile update failed: {str(exc)}")


@router.post("/neuroassist/ops/skill-packs/{skill_pack_key}", response_model=AgentOut, summary="Neuroassist skill pack aktualisieren")
async def update_neuroassist_skill_pack(skill_pack_key: str, request: AgentSkillPackUpdateRequest):
    try:
        return _get_agent_ops_service().update_skill_pack(
            request.tenant_id,
            skill_pack_key,
            skills=request.skills,
            prompt_contracts=request.prompt_contracts,
            changed_by=request.changed_by,
        ).model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST skill pack update failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST skill pack update failed: {str(exc)}")


@router.get("/neuroassist/ops/skill-packs", response_model=list[AgentOut], summary="Neuroassist skill packs auflisten")
async def list_neuroassist_skill_packs(tenant_id: str = "system"):
    try:
        return [item.model_dump(mode="json") for item in _get_agent_ops_service().list_skill_packs(tenant_id)]
    except Exception as exc:
        logger.error("NeuroASSIST skill packs failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST skill packs failed: {str(exc)}")


@router.get("/neuroassist/ops/plugin-boundary-review", response_model=AgentOut, summary="Neuroassist plugin boundary review abrufen")
async def get_neuroassist_plugin_boundary_review(tenant_id: str = "system"):
    try:
        return _get_agent_ops_service().build_plugin_boundary_review(tenant_id).model_dump(mode="json")
    except Exception as exc:
        logger.error("NeuroASSIST plugin boundary review failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST plugin boundary review failed: {str(exc)}")


@router.get("/agents/low-stock/status", response_model=AgentOut, summary="Low-Stock-Agent Status abrufen")
async def get_low_stock_agent_status():
    from ....workers.low_stock_agent import AGENT_ENABLED, MAX_ORDER_FACTOR, NATS_URL

    return {
        "agent": "low-stock-bestellvorschlag",
        "enabled": AGENT_ENABLED,
        "nats_url": NATS_URL,
        "subject": "erp.lager.bestand_unterschritten",
        "max_order_factor": MAX_ORDER_FACTOR,
        "mode": "event-driven" if AGENT_ENABLED else "manual-or-batch",
    }


@router.post("/agents/low-stock/simulate", response_model=AgentOut, summary="Low-Stock-Event simulieren")
async def simulate_low_stock_event(request: LowStockSimulateRequest):
    from ....workers.low_stock_agent import LowStockEvent, handle_low_stock_event

    result = await handle_low_stock_event(
        LowStockEvent(
            tenant_id=request.tenant_id,
            artikel_id=request.artikel_id,
            artikel_name=request.artikel_name,
            bestand=request.bestand,
            mindestbestand=request.mindestbestand,
            einheit=request.einheit,
            lieferant_id=request.lieferant_id,
            durchschnittlicher_verbrauch_pro_tag=request.durchschnittlicher_verbrauch_pro_tag,
        )
    )
    return {
        "erfolg": result.erfolg,
        "vorschlag_id": result.vorschlag_id,
        "artikel_id": result.artikel_id,
        "empfohlene_menge": result.empfohlene_menge,
        "begruendung": result.begruendung,
        "fehler": result.fehler,
    }

