"""
Neuro Simulation Engine — NC-005
Dry-Run und What-If Simulationen fuer Neuro-Core Entscheidungen.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from app.services.neuro_verification_engine import verify_plan

logger = logging.getLogger(__name__)


@dataclass
class SimulationResult:
    run_id: str = field(default_factory=lambda: str(uuid4()))
    mode: str = "dry_run"
    verification_status: str = ""
    violations: list[dict] = field(default_factory=list)
    side_effects: list[str] = field(default_factory=list)
    recommendation: str = ""
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id, "mode": self.mode,
            "verification_status": self.verification_status,
            "violations": self.violations, "side_effects": self.side_effects,
            "recommendation": self.recommendation, "completed_at": self.completed_at,
        }


_results: dict[str, SimulationResult] = {}


def simulate_dry_run(plan: dict, tenant_id: str = "system") -> SimulationResult:
    verification = verify_plan(plan, tenant_id)
    result = SimulationResult(
        mode="dry_run",
        verification_status=verification.status.value,
        violations=[v.to_dict() if hasattr(v, "to_dict") else {"type": v.type.value, "message": v.message} for v in verification.violations],
    )

    if verification.status.value == "approved":
        result.side_effects = _predict_side_effects(plan)
        result.recommendation = "Plan kann ausgefuehrt werden."
    elif verification.status.value == "warning":
        result.side_effects = _predict_side_effects(plan)
        result.recommendation = "Plan hat Warnungen — manuelle Pruefung empfohlen."
    else:
        result.recommendation = "Plan wurde abgelehnt — Violations beheben."

    _results[result.run_id] = result
    return result


def simulate_what_if(plan: dict, current_state: dict, tenant_id: str = "system") -> SimulationResult:
    result = simulate_dry_run(plan, tenant_id)
    result.mode = "what_if"

    changes = []
    for key, new_val in plan.get("params", {}).items():
        old_val = current_state.get(key)
        if old_val != new_val:
            changes.append(f"{key}: {old_val} -> {new_val}")
    result.side_effects.extend(changes)

    _results[result.run_id] = result
    return result


def get_simulation_result(run_id: str) -> Optional[SimulationResult]:
    return _results.get(run_id)


def _predict_side_effects(plan: dict) -> list[str]:
    effects = []
    action = plan.get("action", "")
    entity = plan.get("entity_type", "")

    if action == "delete":
        effects.append(f"{entity} wird geloescht — abhaengige Daten pruefen")
    if action == "cancel":
        effects.append(f"{entity} wird storniert — Folgeprozesse werden gestoppt")
    if plan.get("amount", 0) > 10000:
        effects.append("Hoher Betrag — Liquiditaetspruefung empfohlen")
    if plan.get("target_state") == "completed":
        effects.append("Abschluss — keine weiteren Aenderungen moeglich")

    return effects
