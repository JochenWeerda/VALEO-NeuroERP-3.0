"""
Neuro Verification Engine — NC-001 / Wave 2
Formale Verifikationsschicht zwischen Planner und Action Layer.
Prueft jeden Plan VOR Ausfuehrung auf Pre-Conditions, Policy, Integritaet, Zustandsuebergaenge.

Wave 2 Aenderungen:
- check_policy_conformity() nutzt jetzt evaluate_policy_set() aus der Policy Engine
- check_state_transition() nutzt StateGraphService.validate_transition() statt lokalem Dict
- verify_plan() unterstuetzt per-Step Verification (steps-Liste)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class VerificationStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    WARNING = "warning"


class ViolationType(str, Enum):
    PRECONDITION_FAILED = "precondition_failed"
    POLICY_VIOLATION = "policy_violation"
    DATA_INTEGRITY = "data_integrity"
    INVALID_TRANSITION = "invalid_transition"


@dataclass
class Violation:
    type: ViolationType
    message: str
    field: Optional[str] = None
    severity: str = "error"


@dataclass
class VerificationResult:
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    status: VerificationStatus = VerificationStatus.APPROVED
    violations: list[Violation] = field(default_factory=list)
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    plan_summary: str = ""
    step_results: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "status": self.status.value,
            "violations": [
                {"type": v.type.value, "message": v.message, "field": v.field, "severity": v.severity}
                for v in self.violations
            ],
            "checked_at": self.checked_at,
            "plan_summary": self.plan_summary,
            "step_results": self.step_results,
        }


# ---------------------------------------------------------------------------
# Mapping: entity_type → StateNodeType + StatePhase fuer State-Graph-Lookup
# ---------------------------------------------------------------------------

_ENTITY_TO_NODE_TYPE: dict[str, str] = {
    "purchase_order": "bestellung",
    "sales_order": "bestellung",
    "invoice": "rechnung",
    "delivery_note": "lieferschein",
    "credit_note": "gutschrift",
    "contract": "kontrakt",
    "customer": "kunde",
    "inventory": "lagerbestand",
    "approval": "freigabe",
}

_PHASE_MAPPING: dict[str, str] = {
    "draft": "entwurf",
    "open": "offen",
    "submitted": "offen",
    "in_progress": "in_bearbeitung",
    "approved": "freigegeben",
    "completed": "abgeschlossen",
    "cancelled": "storniert",
    "archived": "archiviert",
}


def check_preconditions(plan: dict) -> list[Violation]:
    violations = []
    if not plan.get("action"):
        violations.append(Violation(ViolationType.PRECONDITION_FAILED, "Aktion fehlt im Plan", "action"))
    if not plan.get("entity_type"):
        violations.append(Violation(ViolationType.PRECONDITION_FAILED, "Entity-Typ fehlt", "entity_type"))
    if not plan.get("entity_id") and plan.get("action") != "create":
        violations.append(Violation(ViolationType.PRECONDITION_FAILED, "Entity-ID fehlt fuer nicht-create Aktion", "entity_id"))
    return violations


def check_policy_conformity(
    plan: dict,
    tenant_id: str,
    db: Optional[Session] = None,
    *,
    policy_sets: Optional[list] = None,
    now: Optional[datetime] = None,
) -> list[Violation]:
    """
    Wave 2: Policy-Engine-Integration.

    1. Sucht passende PolicySets (uebergeben oder Default-Agrar-Sets)
    2. Wertet evaluate_policy_set() aus
    3. Mapped PolicyAktion → Violation severity
    4. Haelt hardcoded Fallback-Regeln fuer Rueckwaertskompatibilitaet
    """
    violations = []
    action = plan.get("action", "")
    entity_type = plan.get("entity_type", "")
    prozess_key = plan.get("prozess_key", entity_type)

    # --- Phase 1: Policy Engine evaluation ---
    try:
        from app.core.policy_code_engine import (
            PolicyAktion,
            PolicyEvaluationResult,
            apply_tenant_overrides,
            evaluate_policy_set,
            get_default_agrar_policy_sets,
        )

        available_sets = policy_sets or get_default_agrar_policy_sets()
        matching_sets = [ps for ps in available_sets if ps.prozess_key == prozess_key]

        kontext = {
            "aktion": action,
            "entity_type": entity_type,
            "betrag_eur": plan.get("amount", 0),
            "brutto_eur": plan.get("amount", 0),
            "rolle": plan.get("role", ""),
            "tenant_id": tenant_id,
            **plan.get("policy_context", {}),
        }

        for ps in matching_sets:
            result: PolicyEvaluationResult = evaluate_policy_set(ps, kontext)

            if result.abgelehnt:
                for treffer in result.treffer:
                    if treffer.aktion == PolicyAktion.ABGELEHNT:
                        violations.append(Violation(
                            ViolationType.POLICY_VIOLATION,
                            f"Policy abgelehnt: {treffer.bezeichnung} — {treffer.begruendung}",
                            severity="error",
                        ))
            elif result.eskalation_erforderlich:
                for treffer in result.treffer:
                    if treffer.aktion == PolicyAktion.ESKALATION:
                        violations.append(Violation(
                            ViolationType.POLICY_VIOLATION,
                            f"Eskalation erforderlich: {treffer.bezeichnung} — {treffer.begruendung}",
                            severity="warning",
                        ))
            else:
                for treffer in result.treffer:
                    if treffer.aktion == PolicyAktion.WARNUNG:
                        violations.append(Violation(
                            ViolationType.POLICY_VIOLATION,
                            f"Policy-Warnung: {treffer.bezeichnung} — {treffer.begruendung}",
                            severity="warning",
                        ))

    except Exception as exc:
        logger.warning("Policy Engine evaluation failed, using fallback: %s", exc)

    # --- Phase 2: Hardcoded fallback rules (Rueckwaertskompatibilitaet) ---
    requires_approval = plan.get("requires_approval", False)

    if action in ("delete", "cancel") and not plan.get("reason"):
        violations.append(Violation(ViolationType.POLICY_VIOLATION, "Loeschung/Stornierung erfordert Begruendung", "reason"))

    if requires_approval and not plan.get("approved_by"):
        violations.append(Violation(
            ViolationType.POLICY_VIOLATION,
            "Aktion erfordert Freigabe (approved_by fehlt)",
            "approved_by",
            severity="warning",
        ))

    amount = plan.get("amount", 0)
    if isinstance(amount, (int, float)) and amount > 50000 and not plan.get("four_eyes_approved"):
        violations.append(Violation(
            ViolationType.POLICY_VIOLATION,
            f"Betrag {amount} EUR ueberschreitet 4-Augen-Grenze (50.000 EUR)",
            "four_eyes_approved",
        ))

    return violations


def check_data_integrity(plan: dict) -> list[Violation]:
    violations = []
    params = plan.get("params", {})

    for key, value in params.items():
        if isinstance(value, str) and len(value) > 10000:
            violations.append(Violation(ViolationType.DATA_INTEGRITY, f"Feld '{key}' ueberschreitet Maximallaenge", key))
        if value is None and key in plan.get("required_fields", []):
            violations.append(Violation(ViolationType.DATA_INTEGRITY, f"Pflichtfeld '{key}' ist leer", key))

    return violations


def check_state_transition(plan: dict) -> list[Violation]:
    """
    Wave 2: Nutzt StateGraphService.validate_transition() statt lokalem Dict.
    Mapped entity_type und Phasen-Strings auf StateNodeType/StatePhase.
    """
    violations = []
    current_state = plan.get("current_state", "")
    target_state = plan.get("target_state", "")

    if not current_state or not target_state:
        return violations

    entity_type = plan.get("entity_type", "")

    try:
        from app.core.neuro_state_graph import (
            StateGraphService,
            StateGraphValidationError,
            StateNodeType,
            StatePhase,
        )

        node_type_str = _ENTITY_TO_NODE_TYPE.get(entity_type)
        from_phase_str = _PHASE_MAPPING.get(current_state, current_state)
        to_phase_str = _PHASE_MAPPING.get(target_state, target_state)

        if node_type_str:
            try:
                node_type = StateNodeType(node_type_str)
                from_phase = StatePhase(from_phase_str)
                to_phase = StatePhase(to_phase_str)
                StateGraphService.validate_transition(node_type, from_phase, to_phase)
            except StateGraphValidationError as exc:
                violations.append(Violation(
                    ViolationType.INVALID_TRANSITION,
                    str(exc),
                    "target_state",
                ))
            except ValueError:
                # Unknown phase/type — fall through to log
                logger.debug("State graph lookup skipped: unknown type/phase for %s", entity_type)
        else:
            logger.debug("No state graph mapping for entity_type=%s", entity_type)

    except ImportError:
        logger.warning("StateGraphService not available, state transition check skipped")

    return violations


def _verify_single(plan: dict, tenant_id: str, db: Optional[Session] = None, **kwargs) -> list[Violation]:
    """Verify a single plan/step dict and return all violations."""
    violations = []
    violations.extend(check_preconditions(plan))
    violations.extend(check_policy_conformity(plan, tenant_id, db, **kwargs))
    violations.extend(check_data_integrity(plan))
    violations.extend(check_state_transition(plan))
    return violations


def verify_plan(plan: dict, tenant_id: str = "system", db: Optional[Session] = None) -> VerificationResult:
    """
    Wave 2: Verifies the plan and optionally each step individually.

    If plan contains a "steps" list, each step is verified separately and
    results are collected in step_results. The overall status is the worst
    across all steps.
    """
    result = VerificationResult(plan_summary=f"{plan.get('action', '?')} on {plan.get('entity_type', '?')}")

    # Verify the plan-level dict
    result.violations.extend(_verify_single(plan, tenant_id, db))

    # Wave 2: Per-step verification
    # Steps are intermediate operations within a plan — they get policy, data
    # integrity, and state transition checks but NOT precondition checks (which
    # are plan-level: action/entity_type/entity_id requirements).
    steps = plan.get("steps", [])
    for step in steps:
        step_plan = {
            "action": step.get("action", plan.get("action", "")),
            "entity_type": step.get("entity_type", plan.get("entity_type", "")),
            "entity_id": step.get("entity_id", plan.get("entity_id", "")),
            "requires_approval": step.get("requires_approval", False),
            "amount": step.get("parameters", {}).get("amount", plan.get("amount")),
            "params": step.get("parameters", {}),
            "current_state": step.get("current_state", ""),
            "target_state": step.get("target_state", ""),
            "prozess_key": step.get("prozess_key", plan.get("prozess_key", "")),
            "policy_context": step.get("policy_context", plan.get("policy_context", {})),
        }
        step_violations = []
        step_violations.extend(check_policy_conformity(step_plan, tenant_id, db))
        step_violations.extend(check_data_integrity(step_plan))
        step_violations.extend(check_state_transition(step_plan))

        step_status = "approved"
        if any(v.severity == "error" for v in step_violations):
            step_status = "rejected"
        elif step_violations:
            step_status = "warning"

        result.step_results.append({
            "step_id": step.get("step_id", ""),
            "action": step_plan["action"],
            "status": step_status,
            "violations": [
                {"type": v.type.value, "message": v.message, "field": v.field, "severity": v.severity}
                for v in step_violations
            ],
        })
        result.violations.extend(step_violations)

    # Determine overall status
    errors = [v for v in result.violations if v.severity == "error"]
    warnings = [v for v in result.violations if v.severity == "warning"]

    if errors:
        result.status = VerificationStatus.REJECTED
    elif warnings:
        result.status = VerificationStatus.WARNING
    else:
        result.status = VerificationStatus.APPROVED

    if db:
        try:
            db.execute(text("""
                INSERT INTO domain_shared.audit_logs (id, action, actor, entity_type, entity_id, details, created_at)
                VALUES (:id, :action, :actor, :etype, :eid, :details, NOW())
            """), {
                "id": result.trace_id,
                "action": f"verification.{result.status.value}",
                "actor": "neuro-verification-engine",
                "etype": plan.get("entity_type", "unknown"),
                "eid": plan.get("entity_id", ""),
                "details": json.dumps(result.to_dict()),
            })
            db.commit()
        except Exception as exc:
            logger.warning("Audit log write failed: %s", exc)

    return result
