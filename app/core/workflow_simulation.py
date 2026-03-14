from __future__ import annotations
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


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
