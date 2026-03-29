"""
Neuro Planner — NC-A3/A4
Generiert einen ausfuehrbaren Plan aus einem klassifizierten Intent.
Integriert die Verification Engine (NC-001) zur Vorab-Pruefung.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from app.agents.neuro_intent_engine import IntentResult, RiskClass

logger = logging.getLogger(__name__)


class StepType(str, Enum):
    QUERY = "query"
    COMMAND = "command"
    GATE = "gate"
    NOTIFICATION = "notification"
    VALIDATION = "validation"


@dataclass
class PlanStep:
    step_id: str = field(default_factory=lambda: str(uuid4())[:8])
    order: int = 0
    type: StepType = StepType.COMMAND
    action: str = ""
    description: str = ""
    entity_type: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = False
    rollback_action: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "order": self.order,
            "type": self.type.value,
            "action": self.action,
            "description": self.description,
            "entity_type": self.entity_type,
            "parameters": self.parameters,
            "requires_approval": self.requires_approval,
            "rollback_action": self.rollback_action,
        }


@dataclass
class ExecutionPlan:
    plan_id: str = field(default_factory=lambda: str(uuid4()))
    intent: str = ""
    capability: Optional[str] = None
    steps: list[PlanStep] = field(default_factory=list)
    risk_class: str = "low"
    requires_human_approval: bool = False
    verification_status: Optional[str] = None
    verification_trace_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "intent": self.intent,
            "capability": self.capability,
            "steps": [s.to_dict() for s in self.steps],
            "risk_class": self.risk_class,
            "requires_human_approval": self.requires_human_approval,
            "verification_status": self.verification_status,
            "verification_trace_id": self.verification_trace_id,
            "created_at": self.created_at,
            "step_count": len(self.steps),
        }


PLAN_TEMPLATES: dict[str, list[dict]] = {
    "bestellung_anlegen": [
        {"type": "validation", "action": "validate_supplier", "description": "Lieferant pruefen", "entity_type": "supplier"},
        {"type": "query", "action": "check_inventory", "description": "Lagerbestand pruefen", "entity_type": "article"},
        {"type": "command", "action": "create_purchase_order", "description": "Bestellung anlegen", "entity_type": "purchase_order", "requires_approval": True, "rollback": "cancel_purchase_order"},
        {"type": "notification", "action": "notify_supplier", "description": "Lieferant benachrichtigen", "entity_type": "notification"},
    ],
    "skonto_pruefen": [
        {"type": "query", "action": "list_open_invoices", "description": "Offene Rechnungen mit Skonto laden", "entity_type": "invoice"},
        {"type": "command", "action": "calculate_skonto_savings", "description": "Skonto-Ersparnis berechnen", "entity_type": "finance"},
        {"type": "command", "action": "generate_skonto_report", "description": "Skonto-Bericht erstellen", "entity_type": "report"},
    ],
    "compliance_pruefen": [
        {"type": "query", "action": "load_compliance_registers", "description": "Compliance-Register laden", "entity_type": "compliance"},
        {"type": "command", "action": "run_compliance_checks", "description": "Pruefungen ausfuehren", "entity_type": "compliance"},
        {"type": "gate", "action": "compliance_approval", "description": "Compliance-Freigabe", "entity_type": "approval", "requires_approval": True},
    ],
    "datenqualitaet_pruefen": [
        {"type": "query", "action": "scan_master_data", "description": "Stammdaten scannen", "entity_type": "master_data"},
        {"type": "command", "action": "detect_duplicates", "description": "Duplikate erkennen", "entity_type": "master_data"},
        {"type": "command", "action": "generate_dq_report", "description": "DQ-Bericht erstellen", "entity_type": "report"},
    ],
    "ausnahme_behandeln": [
        {"type": "query", "action": "load_exception_context", "description": "Ausnahme-Kontext laden", "entity_type": "exception"},
        {"type": "validation", "action": "assess_impact", "description": "Auswirkung bewerten", "entity_type": "exception"},
        {"type": "gate", "action": "exception_approval", "description": "Ausnahme-Freigabe", "entity_type": "approval", "requires_approval": True},
        {"type": "command", "action": "execute_resolution", "description": "Loesung ausfuehren", "entity_type": "exception", "rollback": "revert_resolution"},
    ],
    "auftrag_anlegen": [
        {"type": "validation", "action": "validate_customer", "description": "Kunde pruefen", "entity_type": "customer"},
        {"type": "query", "action": "check_availability", "description": "Verfuegbarkeit pruefen", "entity_type": "article"},
        {"type": "command", "action": "create_sales_order", "description": "Auftrag anlegen", "entity_type": "sales_order", "rollback": "cancel_sales_order"},
    ],
    "rechnung_erstellen": [
        {"type": "validation", "action": "validate_delivery", "description": "Lieferschein pruefen", "entity_type": "delivery_note"},
        {"type": "command", "action": "create_invoice", "description": "Rechnung erstellen", "entity_type": "invoice", "requires_approval": True, "rollback": "cancel_invoice"},
        {"type": "command", "action": "post_to_journal", "description": "FIBU-Buchung", "entity_type": "journal_entry"},
    ],
    "lagerbestand_abfragen": [
        {"type": "query", "action": "query_stock_levels", "description": "Lagerbestaende abfragen", "entity_type": "inventory"},
    ],
    "freigabe_erteilen": [
        {"type": "query", "action": "load_pending_approvals", "description": "Offene Freigaben laden", "entity_type": "approval"},
        {"type": "gate", "action": "human_approval", "description": "Manuelle Freigabe", "entity_type": "approval", "requires_approval": True},
    ],
}


def generate_plan(intent_result: IntentResult, context: Optional[dict] = None) -> ExecutionPlan:
    ctx = context or {}
    plan = ExecutionPlan(
        intent=intent_result.intent,
        capability=intent_result.matched_capability,
        risk_class=intent_result.risk_class.value,
    )

    template = PLAN_TEMPLATES.get(intent_result.intent, [])

    if not template:
        plan.steps.append(PlanStep(
            order=1,
            type=StepType.QUERY,
            action="fallback_search",
            description=f"Kein Plan-Template fuer Intent '{intent_result.intent}' — Fallback-Suche",
            entity_type="unknown",
        ))
        return plan

    for i, step_def in enumerate(template, 1):
        step = PlanStep(
            order=i,
            type=StepType(step_def["type"]),
            action=step_def["action"],
            description=step_def["description"],
            entity_type=step_def.get("entity_type", ""),
            parameters={**intent_result.parameters, **ctx.get("extra_params", {})},
            requires_approval=step_def.get("requires_approval", False),
            rollback_action=step_def.get("rollback"),
        )
        plan.steps.append(step)

    if intent_result.risk_class in (RiskClass.HIGH, RiskClass.CRITICAL):
        plan.requires_human_approval = True

    return plan


def verify_plan(plan: ExecutionPlan, tenant_id: str = "system", db=None) -> ExecutionPlan:
    try:
        from app.services.neuro_verification_engine import verify_plan as _verify

        verify_input = {
            "action": plan.intent,
            "entity_type": plan.steps[0].entity_type if plan.steps else "unknown",
            "requires_approval": plan.requires_human_approval,
            "amount": plan.steps[0].parameters.get("amount") if plan.steps else None,
        }
        result = _verify(verify_input, tenant_id, db)
        plan.verification_status = result.status.value
        plan.verification_trace_id = result.trace_id
    except Exception as exc:
        logger.warning("Plan verification failed: %s", exc)
        plan.verification_status = "error"

    return plan
