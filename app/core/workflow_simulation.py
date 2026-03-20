from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SimulationScenario(str, Enum):
    STANDARD_APPROVAL = "standard_approval"
    ESCALATION = "escalation"
    REJECTION = "rejection"
    FOUR_EYES_EXCEPTION = "four_eyes_exception"
    SLA_BREACH = "sla_breach"


class SimulationInput(BaseModel):
    tenant_id: str
    process_key: str                        # z.B. "ap_invoice_approval"
    scenario: SimulationScenario
    workflow_definition_version: str = "1.0.0"
    context: dict[str, Any] = Field(default_factory=dict)
    schema_version: int = 1


class WorkflowSandboxPreviewInput(BaseModel):
    tenant_id: str
    process_key: str
    scenario: SimulationScenario = SimulationScenario.STANDARD_APPROVAL
    workflow_definition_version: str = "1.0.0"
    simulation_date: date | None = None
    sandbox_mode: str = "preview"
    context: dict[str, Any] = Field(default_factory=dict)
    schema_version: int = 1


class SimulationStepResult(BaseModel):
    step_name: str
    outcome: str                            # "passed", "blocked", "escalated", "approved", "rejected"
    reason: str
    elapsed_hours: float = 0.0
    schema_version: int = 1


class SimulationResult(BaseModel):
    tenant_id: str
    process_key: str
    scenario: SimulationScenario
    workflow_definition_version: str
    steps: list[SimulationStepResult]
    final_status: str                       # "completed", "rejected", "escalated", "pending_approval"
    explainability: dict[str, Any] = Field(default_factory=dict)
    simulated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class WorkflowSandboxPreviewResult(BaseModel):
    tenant_id: str
    process_key: str
    workflow_definition_version: str
    simulation_date: date
    sandbox_mode: str
    simulation: SimulationResult
    warnings: list[str] = Field(default_factory=list)
    recommended_next_action: str
    schema_version: int = 1


def simulate_workflow(input: SimulationInput) -> SimulationResult:
    """
    Fuehrt eine Workflow-Simulation auf Basis des Szenarios durch.
    Keine DB-Abfragen — rein modellbasiert.
    """
    steps: list[SimulationStepResult] = []

    if input.scenario == SimulationScenario.STANDARD_APPROVAL:
        steps = [
            SimulationStepResult(step_name="submit", outcome="passed",
                                 reason="Rechnung eingereicht", elapsed_hours=0.0),
            SimulationStepResult(step_name="waiting_approval", outcome="approved",
                                 reason="Freigabe erteilt innerhalb SLA", elapsed_hours=12.0),
            SimulationStepResult(step_name="post", outcome="passed",
                                 reason="Verbuchung erfolgt", elapsed_hours=0.5),
        ]
        final_status = "completed"

    elif input.scenario == SimulationScenario.REJECTION:
        steps = [
            SimulationStepResult(step_name="submit", outcome="passed",
                                 reason="Rechnung eingereicht", elapsed_hours=0.0),
            SimulationStepResult(step_name="waiting_approval", outcome="rejected",
                                 reason="Freigabe verweigert: Betrag ueber Limit", elapsed_hours=4.0),
        ]
        final_status = "rejected"

    elif input.scenario == SimulationScenario.ESCALATION:
        steps = [
            SimulationStepResult(step_name="submit", outcome="passed",
                                 reason="Rechnung eingereicht", elapsed_hours=0.0),
            SimulationStepResult(step_name="waiting_approval", outcome="escalated",
                                 reason="SLA ueberschritten: 72h ohne Freigabe", elapsed_hours=72.0),
        ]
        final_status = "escalated"

    elif input.scenario == SimulationScenario.FOUR_EYES_EXCEPTION:
        steps = [
            SimulationStepResult(step_name="submit", outcome="passed",
                                 reason="Rechnung eingereicht", elapsed_hours=0.0),
            SimulationStepResult(step_name="waiting_approval", outcome="blocked",
                                 reason="4-Augen-Pflicht: zweite Freigabe fehlt", elapsed_hours=2.0),
            SimulationStepResult(step_name="second_approval", outcome="approved",
                                 reason="Zweite Freigabe erteilt", elapsed_hours=1.0),
            SimulationStepResult(step_name="post", outcome="passed",
                                 reason="Verbuchung nach 4-Augen-Freigabe", elapsed_hours=0.5),
        ]
        final_status = "completed"

    elif input.scenario == SimulationScenario.SLA_BREACH:
        steps = [
            SimulationStepResult(step_name="submit", outcome="passed",
                                 reason="Rechnung eingereicht", elapsed_hours=0.0),
            SimulationStepResult(step_name="waiting_approval", outcome="escalated",
                                 reason="WARNING nach 24h, CRITICAL nach 72h — automatische Eskalation",
                                 elapsed_hours=96.0),
        ]
        final_status = "escalated"

    else:
        steps = []
        final_status = "unknown"

    total_hours = sum(s.elapsed_hours for s in steps)
    explainability = {
        "scenario": input.scenario,
        "process_key": input.process_key,
        "definition_version": input.workflow_definition_version,
        "total_simulated_hours": total_hours,
        "step_count": len(steps),
        "final_status": final_status,
        "rule_chain": [
            {"step": s.step_name, "outcome": s.outcome, "reason": s.reason}
            for s in steps
        ],
    }

    return SimulationResult(
        tenant_id=input.tenant_id,
        process_key=input.process_key,
        scenario=input.scenario,
        workflow_definition_version=input.workflow_definition_version,
        steps=steps,
        final_status=final_status,
        explainability=explainability,
    )


def _build_sandbox_warnings(input: WorkflowSandboxPreviewInput, simulation: SimulationResult) -> list[str]:
    warnings: list[str] = []
    context = input.context or {}
    if simulation.final_status in {"rejected", "escalated"}:
        warnings.append("Simulation zeigt Blockade oder Eskalation; Workflow vor Go-Live nachschärfen.")
    if input.sandbox_mode.lower() not in {"preview", "sandbox"}:
        warnings.append(f"Unbekannter sandbox_mode {input.sandbox_mode!r}; Preview wurde im Standardmodus gebaut.")
    wf_status = str(context.get("workflow_definition_status") or "").upper()
    if wf_status and wf_status not in {"AKTIV", "ACTIVE"}:
        warnings.append(f"Workflow-Definition ist nicht aktiv ({wf_status}).")
    if context.get("requires_migration"):
        warnings.append("Context meldet Migrationsbedarf fuer die Ziel-Workflow-Version.")
    if context.get("draft_only"):
        warnings.append("Sandbox laeuft gegen einen Entwurfs-Kontext; Ergebnisse nicht produktionsreif.")
    if input.simulation_date is None:
        warnings.append("Kein Simulationstag gesetzt; Preview basiert auf dem aktuellen Stichtag.")
    return warnings


def _recommended_next_action(simulation: SimulationResult) -> str:
    if simulation.final_status == "completed":
        return "Workflow kann als Sandbox-Kandidat in den Go-Live-Review uebernommen werden."
    if simulation.final_status == "rejected":
        return "Regeln, Limits und Freigabegrenzen vor der Freigabe ueberarbeiten."
    if simulation.final_status == "escalated":
        return "SLA- und Eskalationspfade pruefen, bevor die neue Workflow-Version freigegeben wird."
    return "Simulation erneut pruefen und fehlende Prozesskontexte nachreichen."


def preview_workflow_sandbox(input: WorkflowSandboxPreviewInput) -> WorkflowSandboxPreviewResult:
    simulation = simulate_workflow(
        SimulationInput(
            tenant_id=input.tenant_id,
            process_key=input.process_key,
            scenario=input.scenario,
            workflow_definition_version=input.workflow_definition_version,
            context=input.context,
        )
    )
    warnings = _build_sandbox_warnings(input, simulation)
    return WorkflowSandboxPreviewResult(
        tenant_id=input.tenant_id,
        process_key=input.process_key,
        workflow_definition_version=input.workflow_definition_version,
        simulation_date=input.simulation_date or date.today(),
        sandbox_mode=input.sandbox_mode,
        simulation=simulation,
        warnings=warnings,
        recommended_next_action=_recommended_next_action(simulation),
    )
