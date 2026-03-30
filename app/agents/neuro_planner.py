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

from app.agents.neuro_intent_engine import IntentCategory, IntentResult, RiskClass

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
        plan.steps = _generate_dynamic_steps(intent_result, ctx)
        if intent_result.risk_class in (RiskClass.HIGH, RiskClass.CRITICAL):
            plan.requires_human_approval = True
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


def _generate_dynamic_steps(intent_result: IntentResult, context: dict[str, Any]) -> list[PlanStep]:
    shared_parameters = {
        **intent_result.parameters,
        **context.get("extra_params", {}),
        "_dynamic_plan": True,
        "_intent_category": intent_result.category.value,
        "_source_intent": intent_result.intent,
    }

    dynamic_steps: list[dict[str, Any]]

    if intent_result.category == IntentCategory.NAVIGATION:
        dynamic_steps = [
            {
                "type": StepType.QUERY,
                "action": "resolve_navigation_target",
                "description": f"Navigationsziel fuer Intent '{intent_result.intent}' aufloesen",
                "entity_type": "route",
            },
            {
                "type": StepType.COMMAND,
                "action": "open_navigation_target",
                "description": "Zielansicht oeffnen",
                "entity_type": "route",
            },
        ]
    elif intent_result.category == IntentCategory.APPROVAL:
        dynamic_steps = [
            {
                "type": StepType.QUERY,
                "action": "load_pending_approvals",
                "description": "Offene Freigabefaelle fuer den Kontext laden",
                "entity_type": "approval",
            },
            {
                "type": StepType.GATE,
                "action": "human_approval",
                "description": "Passende Freigabeentscheidung einholen",
                "entity_type": "approval",
                "requires_approval": True,
            },
        ]
    elif intent_result.matched_capability:
        dynamic_steps = [
            {
                "type": StepType.VALIDATION,
                "action": "validate_dynamic_request",
                "description": "Anfrage fuer dynamische Capability-Ausfuehrung validieren",
                "entity_type": "request",
            },
            {
                "type": StepType.COMMAND,
                "action": "delegate_capability_workflow",
                "description": "Dynamischen Capability-Run delegieren",
                "entity_type": "capability_run",
            },
            {
                "type": StepType.NOTIFICATION,
                "action": "summarize_dynamic_result",
                "description": "Ergebnis fuer den Nutzer zusammenfassen",
                "entity_type": "response",
            },
        ]
    elif intent_result.category == IntentCategory.ANALYSIS:
        dynamic_steps = [
            {
                "type": StepType.QUERY,
                "action": "collect_business_context",
                "description": "Fachkontext fuer die Analyse sammeln",
                "entity_type": "context",
            },
            {
                "type": StepType.COMMAND,
                "action": "run_dynamic_analysis",
                "description": "Dynamische Analyse ohne statisches Template ausfuehren",
                "entity_type": "analysis",
            },
            {
                "type": StepType.NOTIFICATION,
                "action": "summarize_findings",
                "description": "Analyseergebnis strukturieren und zusammenfassen",
                "entity_type": "response",
            },
        ]
    elif intent_result.category == IntentCategory.QUERY:
        dynamic_steps = [
            {
                "type": StepType.QUERY,
                "action": "collect_business_context",
                "description": "Kontext fuer die Anfrage sammeln",
                "entity_type": "context",
            },
            {
                "type": StepType.COMMAND,
                "action": "synthesize_query_answer",
                "description": "Antwort aus dem verfuegbaren Kontext ableiten",
                "entity_type": "response",
            },
        ]
    elif intent_result.category == IntentCategory.COMMAND:
        dynamic_steps = [
            {
                "type": StepType.VALIDATION,
                "action": "validate_dynamic_request",
                "description": "Unbekannten Command-Kontext validieren",
                "entity_type": "request",
            },
            {
                "type": StepType.QUERY,
                "action": "collect_business_context",
                "description": "Abhaengige Stammdaten und Prozesskontext laden",
                "entity_type": "context",
            },
            {
                "type": StepType.COMMAND,
                "action": "execute_dynamic_command",
                "description": "Heuristisch abgeleiteten Command ausfuehren",
                "entity_type": "operation",
                "requires_approval": intent_result.risk_class in (RiskClass.MEDIUM, RiskClass.HIGH, RiskClass.CRITICAL),
            },
        ]
    else:
        dynamic_steps = [
            {
                "type": StepType.QUERY,
                "action": "collect_business_context",
                "description": "Basis-Kontext fuer unbekannten Intent sammeln",
                "entity_type": "unknown",
            },
            {
                "type": StepType.QUERY,
                "action": "fallback_search",
                "description": f"Kein Template fuer Intent '{intent_result.intent}' - Fallback-Suche mit Kontext",
                "entity_type": "unknown",
            },
        ]

    return [
        PlanStep(
            order=index,
            type=step_def["type"],
            action=step_def["action"],
            description=step_def["description"],
            entity_type=step_def.get("entity_type", ""),
            parameters=dict(shared_parameters),
            requires_approval=step_def.get("requires_approval", False),
            rollback_action=step_def.get("rollback"),
        )
        for index, step_def in enumerate(dynamic_steps, 1)
    ]


def verify_plan(plan: ExecutionPlan, tenant_id: str = "system", db=None) -> ExecutionPlan:
    """
    Wave 2: Verifies ALL steps, not just the first one.
    Passes the full steps list to the Verification Engine for per-step checks.
    """
    try:
        from app.services.neuro_verification_engine import verify_plan as _verify

        first_step = plan.steps[0] if plan.steps else None
        action = first_step.action if first_step else plan.intent
        is_create = any(w in action for w in ("create", "anlegen", "generate", "check", "query", "validate", "scan", "load", "list", "calculate", "detect", "assess", "notify", "fallback", "resolve", "collect", "synthesize", "delegate", "summarize", "run_dynamic", "execute_dynamic", "open_navigation"))

        verify_input = {
            "action": "create" if is_create else action,
            "entity_type": first_step.entity_type if first_step else "unknown",
            "requires_approval": plan.requires_human_approval,
            "amount": first_step.parameters.get("amount") if first_step else None,
            "steps": [s.to_dict() for s in plan.steps],
        }
        result = _verify(verify_input, tenant_id, db)
        plan.verification_status = result.status.value
        plan.verification_trace_id = result.trace_id
    except Exception as exc:
        logger.warning("Plan verification failed: %s", exc)
        plan.verification_status = "error"

    return plan
