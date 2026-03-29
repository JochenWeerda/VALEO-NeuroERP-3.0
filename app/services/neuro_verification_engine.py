"""
Neuro Verification Engine — NC-001
Formale Verifikationsschicht zwischen Planner und Action Layer.
Prueft jeden Plan VOR Ausfuehrung auf Pre-Conditions, Policy, Integritaet, Zustandsuebergaenge.
"""

from __future__ import annotations

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
        }


ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["submitted", "cancelled"],
    "submitted": ["approved", "rejected", "cancelled"],
    "approved": ["in_progress", "cancelled"],
    "in_progress": ["completed", "failed", "cancelled"],
    "completed": [],
    "failed": ["in_progress", "cancelled"],
    "cancelled": [],
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


def check_policy_conformity(plan: dict, tenant_id: str, db: Optional[Session] = None) -> list[Violation]:
    violations = []
    action = plan.get("action", "")
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
    violations = []
    current_state = plan.get("current_state", "")
    target_state = plan.get("target_state", "")

    if not current_state or not target_state:
        return violations

    allowed = ALLOWED_TRANSITIONS.get(current_state, [])
    if target_state not in allowed:
        violations.append(Violation(
            ViolationType.INVALID_TRANSITION,
            f"Uebergang '{current_state}' -> '{target_state}' nicht erlaubt. Erlaubt: {allowed}",
            "target_state",
        ))

    return violations


def verify_plan(plan: dict, tenant_id: str = "system", db: Optional[Session] = None) -> VerificationResult:
    result = VerificationResult(plan_summary=f"{plan.get('action', '?')} on {plan.get('entity_type', '?')}")

    result.violations.extend(check_preconditions(plan))
    result.violations.extend(check_policy_conformity(plan, tenant_id, db))
    result.violations.extend(check_data_integrity(plan))
    result.violations.extend(check_state_transition(plan))

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
                "details": __import__("json").dumps(result.to_dict()),
            })
            db.commit()
        except Exception as exc:
            logger.warning("Audit log write failed: %s", exc)

    return result
