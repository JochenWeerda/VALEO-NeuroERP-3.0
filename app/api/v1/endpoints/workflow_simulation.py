from __future__ import annotations

from fastapi import APIRouter
from app.core.workflow_simulation import (
    SimulationScenario,
    SimulationInput,
    SimulationResult,
    WorkflowSandboxPreviewInput,
    WorkflowSandboxPreviewResult,
    simulate_workflow,
    preview_workflow_sandbox,
)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.workflow_simulation_schemas import WorkflowSimulationOut


router = APIRouter(prefix="/workflow/simulation", tags=["workflow", "simulation"])

_SCENARIO_DESCRIPTIONS: dict[str, str] = {
    SimulationScenario.STANDARD_APPROVAL: (
        "Standardfall: Rechnung wird eingereicht und innerhalb der SLA-Zeit freigegeben."
    ),
    SimulationScenario.ESCALATION: (
        "Eskalation: SLA-Grenze von 72h wird ueberschritten, automatische Eskalation."
    ),
    SimulationScenario.REJECTION: (
        "Ablehnung: Freigabe wird verweigert, z.B. wegen Ueberschreitung des Betragslimits."
    ),
    SimulationScenario.FOUR_EYES_EXCEPTION: (
        "4-Augen-Pflicht: Zweite Freigabe erforderlich (Ausnahmeregel bei Hochrisikobelegen)."
    ),
    SimulationScenario.SLA_BREACH: (
        "SLA-Verletzung: WARNING nach 24h, CRITICAL nach 72h — Eskalation nach 96h."
    ),
}


@router.get("/scenarios", summary="Alle verfuegbaren Simulationsszenarien",
    response_model=list[WorkflowSimulationOut]
)
def list_scenarios() -> list[dict]:
    """Gibt alle SimulationScenario-Werte mit ihrer Beschreibung zurueck."""
    return [
        {
            "scenario": scenario.value,
            "description": _SCENARIO_DESCRIPTIONS.get(scenario, ""),
        }
        for scenario in SimulationScenario
    ]


@router.get("/sandbox/scenarios", summary="Sandbox-Szenarien fuer neue Workflows",
    response_model=list[WorkflowSimulationOut]
)
def list_sandbox_scenarios() -> list[dict]:
    """Gibt die Sandbox-Szenarien mit Hinweisen fuer den Go-Live-Review zurueck."""
    return [
        {
            "scenario": scenario.value,
            "description": _SCENARIO_DESCRIPTIONS.get(scenario, ""),
            "sandbox_ready": True,
        }
        for scenario in SimulationScenario
    ]


@router.post("/run", response_model=SimulationResult, summary="Workflow-Simulation ausfuehren")
def run_simulation(body: SimulationInput) -> SimulationResult:
    """Fuehrt eine modellbasierte Workflow-Simulation fuer das angegebene Szenario durch."""
    return simulate_workflow(body)


@router.post(
    "/preview",
    response_model=WorkflowSandboxPreviewResult,
    summary="Workflow-Sandbox-Preview ausfuehren",
)
def preview_simulation(body: WorkflowSandboxPreviewInput) -> WorkflowSandboxPreviewResult:
    """Fuehrt eine Sandbox-Vorschau fuer neue oder geaenderte Workflows aus."""
    return preview_workflow_sandbox(body)


@router.post(
    "/sandbox/preview",
    response_model=WorkflowSandboxPreviewResult,
    summary="Workflow-Sandbox-Preview ausfuehren",
)
def preview_workflow_sandbox_endpoint(body: WorkflowSandboxPreviewInput) -> WorkflowSandboxPreviewResult:
    """Alias fuer den Sandbox-Preview-Contract mit explizitem Sandbox-Pfad."""
    return preview_workflow_sandbox(body)


@router.get(
    "/scenarios/{scenario}/description",
    summary="Beschreibung eines Szenarios",
    response_model=WorkflowSimulationOut
)
def get_scenario_description(scenario: SimulationScenario) -> dict:
    """Gibt die kurze Beschreibung eines einzelnen Simulationsszenarios zurueck."""
    return {
        "scenario": scenario.value,
        "description": _SCENARIO_DESCRIPTIONS.get(scenario, ""),
    }
