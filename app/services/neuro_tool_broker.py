"""
Neuro Tool Broker - NC-A6 / NC-A7
Centralized tool and command orchestration for Neuro-Core execution plans.

NC-A7 additions:
- Real OpenAPI execution via NeuroToolExecutionService (replaces simulation)
- Persistent State-Graph mutations after successful execution
- Per-step audit trace in the Decision Protocol
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agents.neuro_planner import ExecutionPlan, PlanStep, StepType
from app.core.action_execution import ActionExecutionRequest, ActionExecutionService
from app.core.mcp_tool_contracts import MCPToolContract, MCPToolKategorie, get_process_kernel_mcp_tools
from app.core.neuro_state_graph import StateGraphService, StateNode, StateNodeType, StatePhase
from app.integrations.services.superglue_capability_service import SuperglueCapabilityService
from app.services.neuro_tool_execution import NeuroToolExecutionService
from app.services.neuro_verification_engine import verify_plan

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolBinding:
    kind: str
    target_name: str
    aggregate_type: str | None = None
    agent_type: str | None = None
    category: MCPToolKategorie | None = None
    target_node_type: StateNodeType | None = None
    target_phase: StatePhase | None = None


_ACTION_BINDINGS: dict[str, ToolBinding] = {
    "validate_supplier": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_process_data_quality_validate",
        category=MCPToolKategorie.VALIDIEREN,
    ),
    "check_inventory": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_inventory_bestand_get",
        category=MCPToolKategorie.BERECHNEN,
    ),
    "create_purchase_order": ToolBinding(
        kind="command",
        target_name="CreatePurchaseOrder",
        aggregate_type="purchase_order",
        agent_type="procurement_agent",
        target_node_type=StateNodeType.BESTELLUNG,
        target_phase=StatePhase.OFFEN,
    ),
    "notify_supplier": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_workflow_checkpoint_create",
        category=MCPToolKategorie.SCHREIBEN,
    ),
    "list_open_invoices": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_finance_open_items_get",
        category=MCPToolKategorie.LESEN,
    ),
    "calculate_skonto_savings": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_finance_sla_check",
        category=MCPToolKategorie.VALIDIEREN,
    ),
    "generate_skonto_report": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_workflow_checkpoint_create",
        category=MCPToolKategorie.SCHREIBEN,
    ),
    "load_compliance_registers": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_compliance_policy_evaluate",
        category=MCPToolKategorie.BERECHNEN,
    ),
    "run_compliance_checks": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_compliance_intrastat_validate",
        category=MCPToolKategorie.VALIDIEREN,
    ),
    "scan_master_data": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_process_data_quality_validate",
        category=MCPToolKategorie.VALIDIEREN,
    ),
    "detect_duplicates": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_process_data_quality_validate",
        category=MCPToolKategorie.VALIDIEREN,
    ),
    "generate_dq_report": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_workflow_checkpoint_create",
        category=MCPToolKategorie.SCHREIBEN,
    ),
    "load_exception_context": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_workflow_instance_status",
        category=MCPToolKategorie.LESEN,
    ),
    "assess_impact": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_workflow_approval_evaluate",
        category=MCPToolKategorie.VALIDIEREN,
    ),
    "execute_resolution": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_process_action_execute",
        category=MCPToolKategorie.SCHREIBEN,
    ),
    "validate_customer": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_process_data_quality_validate",
        category=MCPToolKategorie.VALIDIEREN,
    ),
    "check_availability": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_inventory_bestand_get",
        category=MCPToolKategorie.BERECHNEN,
    ),
    "create_sales_order": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_process_action_execute",
        category=MCPToolKategorie.SCHREIBEN,
        target_node_type=StateNodeType.BESTELLUNG,
        target_phase=StatePhase.OFFEN,
    ),
    "validate_delivery": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_workflow_instance_status",
        category=MCPToolKategorie.LESEN,
    ),
    "create_invoice": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_process_action_execute",
        category=MCPToolKategorie.SCHREIBEN,
        target_node_type=StateNodeType.RECHNUNG,
        target_phase=StatePhase.OFFEN,
    ),
    "post_to_journal": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_process_action_execute",
        category=MCPToolKategorie.SCHREIBEN,
        target_node_type=StateNodeType.RECHNUNG,
        target_phase=StatePhase.FREIGEGEBEN,
    ),
    "query_stock_levels": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_inventory_bestand_get",
        category=MCPToolKategorie.BERECHNEN,
    ),
    "load_pending_approvals": ToolBinding(
        kind="mcp_tool",
        target_name="valeo_workflow_instance_status",
        category=MCPToolKategorie.LESEN,
    ),
}

_GATE_BINDING = ToolBinding(
    kind="gate",
    target_name="human_approval",
    target_node_type=StateNodeType.FREIGABE,
    target_phase=StatePhase.FREIGEGEBEN,
)


def execute_plan(
    plan: ExecutionPlan,
    *,
    tenant_id: str = "system",
    context: Optional[dict[str, Any]] = None,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    broker = NeuroToolBroker()
    return broker.execute_plan(plan, tenant_id=tenant_id, context=context, db=db)


class NeuroToolBroker:
    def __init__(
        self,
        *,
        action_execution_service: ActionExecutionService | None = None,
        tool_execution_service: NeuroToolExecutionService | None = None,
        superglue_capability_service: SuperglueCapabilityService | None = None,
    ) -> None:
        self._registry = get_process_kernel_mcp_tools()
        self._action_execution_service = action_execution_service or ActionExecutionService()
        self._tool_execution_service = tool_execution_service or NeuroToolExecutionService()
        self._superglue_capability_service = superglue_capability_service or SuperglueCapabilityService()

    def execute_plan(
        self,
        plan: ExecutionPlan,
        *,
        tenant_id: str = "system",
        context: Optional[dict[str, Any]] = None,
        db: Optional[Session] = None,
    ) -> dict[str, Any]:
        ctx = context or {}
        tool_trace: list[dict[str, Any]] = []
        executed_steps: list[dict[str, Any]] = []
        state_transitions: list[dict[str, Any]] = []
        rollback_plan: list[dict[str, Any]] = []

        for step in plan.steps:
            binding = self._resolve_binding(step, plan.capability)
            step_verification = self._verify_step(step, binding, tenant_id, ctx, db)
            state_transition = self._build_state_transition(step, binding, tenant_id, ctx)
            if state_transition:
                state_transitions.append(state_transition)

            trace_entry = {
                "step_id": step.step_id,
                "order": step.order,
                "action": step.action,
                "step_type": step.type.value,
                "binding_kind": binding.kind,
                "binding_target": binding.target_name,
                "verification_status": step_verification["status"],
                "verification_trace_id": step_verification["trace_id"],
                "state_transition": state_transition,
            }

            if step_verification["status"] == "rejected":
                trace_entry["status"] = "blocked"
                trace_entry["error"] = "verification_rejected"
                tool_trace.append(trace_entry)
                rollback_plan = self._build_rollback_plan(plan, executed_steps)
                return {
                    "status": "failed",
                    "executed_steps": executed_steps,
                    "tool_trace": tool_trace,
                    "rollback_plan": rollback_plan,
                    "state_summary": self._build_state_summary(state_transitions),
                    "message": f"Step '{step.action}' wurde durch Verification blockiert.",
                }

            if plan.requires_human_approval or step.requires_approval or step.type == StepType.GATE:
                trace_entry["status"] = "pending_approval"
                trace_entry["approval_required"] = True
                tool_trace.append(trace_entry)
                executed_steps.append(
                    {
                        "step_id": step.step_id,
                        "action": step.action,
                        "status": "pending_approval",
                    }
                )
                return {
                    "status": "awaiting_approval",
                    "executed_steps": executed_steps,
                    "tool_trace": tool_trace,
                    "rollback_plan": rollback_plan,
                    "state_summary": self._build_state_summary(state_transitions),
                    "message": f"Step '{step.action}' wartet auf menschliche Freigabe.",
                }

            execution = self._execute_step(step, plan, binding, tenant_id, ctx, db)
            trace_entry.update(execution["trace"])
            tool_trace.append(trace_entry)
            executed_steps.append(
                {
                    "step_id": step.step_id,
                    "action": step.action,
                    "status": execution["step_status"],
                }
            )

            # NC-A7: persist state transition after successful execution
            if execution["step_status"] in ("executed", "delegated") and state_transition:
                self._persist_state_transition(state_transition, step, binding, tenant_id, db)

            # NC-A7: record per-step audit trace in decision protocol
            self._record_step_audit(
                plan_id=plan.plan_id,
                step=step,
                binding=binding,
                execution=execution,
                state_transition=state_transition,
                tenant_id=tenant_id,
                db=db,
            )

            if execution["step_status"] == "failed":
                rollback_plan = self._build_rollback_plan(plan, executed_steps[:-1])
                return {
                    "status": "failed",
                    "executed_steps": executed_steps,
                    "tool_trace": tool_trace,
                    "rollback_plan": rollback_plan,
                    "state_summary": self._build_state_summary(state_transitions),
                    "message": f"Step '{step.action}' ist fehlgeschlagen.",
                }

        return {
            "status": "executed",
            "executed_steps": executed_steps,
            "tool_trace": tool_trace,
            "rollback_plan": rollback_plan,
            "state_summary": self._build_state_summary(state_transitions),
            "message": f"Plan mit {len(plan.steps)} Schritten ueber Broker orchestriert.",
        }

    def _resolve_binding(self, step: PlanStep, capability: str | None) -> ToolBinding:
        if step.type == StepType.GATE:
            return _GATE_BINDING

        binding = _ACTION_BINDINGS.get(step.action)
        if binding:
            return binding

        if self._superglue_capability_service.can_handle(
            capability=capability,
            action=step.action,
            parameters=step.parameters,
        ):
            return ToolBinding(kind="superglue", target_name=str(step.parameters.get("superglue_tool_id", step.action)))

        if capability:
            return ToolBinding(kind="capability", target_name=capability)

        fallback_category = {
            StepType.QUERY: MCPToolKategorie.LESEN,
            StepType.VALIDATION: MCPToolKategorie.VALIDIEREN,
            StepType.COMMAND: MCPToolKategorie.SCHREIBEN,
            StepType.NOTIFICATION: MCPToolKategorie.ESKALIEREN,
        }.get(step.type, MCPToolKategorie.LESEN)
        fallback = next(iter(self._registry.by_kategorie(fallback_category)), None)
        if fallback:
            return ToolBinding(
                kind="mcp_tool",
                target_name=fallback.tool_name,
                category=fallback.kategorie,
            )
        return ToolBinding(kind="generic", target_name=step.action)

    def _verify_step(
        self,
        step: PlanStep,
        binding: ToolBinding,
        tenant_id: str,
        context: dict[str, Any],
        db: Optional[Session],
    ) -> dict[str, Any]:
        verification_input = {
            "action": step.action,
            "entity_type": step.entity_type or binding.aggregate_type or "unknown",
            "entity_id": step.parameters.get("entity_id") or step.parameters.get("aggregate_id") or step.step_id,
            "requires_approval": step.requires_approval,
            "amount": step.parameters.get("amount"),
            "params": step.parameters,
            "current_state": context.get("state_graph_node", {}).get("current_phase"),
            "target_state": binding.target_phase.value if binding.target_phase else None,
            "policy_context": {
                **dict(context.get("policy_context", {})),
                **dict(step.parameters.get("policy_context", {})),
            },
            "tenant_policy_overrides": (
                step.parameters.get("tenant_policy_overrides")
                or context.get("tenant_policy_overrides")
                or context.get("policy_overrides")
            ),
        }
        result = verify_plan(verification_input, tenant_id, db)
        return {"status": result.status.value, "trace_id": result.trace_id}

    def _build_state_transition(
        self,
        step: PlanStep,
        binding: ToolBinding,
        tenant_id: str,
        context: dict[str, Any],
    ) -> dict[str, Any] | None:
        if binding.target_node_type is None or binding.target_phase is None:
            return None

        state_ctx = context.get("state_graph_node") or {}
        current_phase = state_ctx.get("current_phase")
        if current_phase is None:
            return None

        try:
            node = StateNode(
                node_id=state_ctx.get("node_id", step.step_id),
                node_type=StateNodeType(state_ctx.get("node_type", binding.target_node_type.value)),
                phase=StatePhase(current_phase),
                tenant_id=tenant_id,
                aggregate_id=state_ctx.get("aggregate_id", step.parameters.get("aggregate_id", step.step_id)),
                aggregate_type=state_ctx.get("aggregate_type", step.entity_type or binding.aggregate_type or "unknown"),
                label=state_ctx.get("label", step.description or step.action),
                metadata=state_ctx.get("metadata", {}),
            )
            transition = StateGraphService.build_transition(
                transition_id=f"{step.step_id}-transition",
                node=node,
                to_phase=binding.target_phase,
                triggered_by="neuro-tool-broker",
                reason=step.description or step.action,
                evidence_refs=[step.step_id],
            )
        except Exception as exc:
            logger.info("State transition skipped for step %s: %s", step.action, exc)
            return {
                "node_id": state_ctx.get("node_id", step.step_id),
                "status": "skipped",
                "reason": str(exc),
            }

        return {
            "node_id": transition.node_id,
            "from_phase": transition.from_phase.value,
            "to_phase": transition.to_phase.value,
            "context_hash": transition.context_hash,
            "status": "planned",
        }

    def _execute_step(
        self,
        step: PlanStep,
        plan: ExecutionPlan,
        binding: ToolBinding,
        tenant_id: str,
        context: dict[str, Any],
        db: Optional[Session] = None,
    ) -> dict[str, Any]:
        if binding.kind == "command":
            return self._dispatch_command(step, plan, binding, tenant_id, db)
        if binding.kind == "mcp_tool":
            return self._execute_tool_contract(step, binding, tenant_id, context)
        if binding.kind == "superglue":
            return self._execute_superglue_step(step, plan, binding, tenant_id)
        if binding.kind == "capability":
            return {
                "step_status": "delegated",
                "trace": {
                    "status": "delegated",
                    "result": {"capability": binding.target_name},
                },
            }
        if binding.kind == "generic":
            return {
                "step_status": "executed",
                "trace": {
                    "status": "executed",
                    "result": {"mode": "generic_fallback"},
                },
            }
        return {
            "step_status": "skipped",
            "trace": {"status": "skipped", "result": {"reason": "unsupported_binding"}},
        }

    def _dispatch_command(
        self,
        step: PlanStep,
        plan: ExecutionPlan,
        binding: ToolBinding,
        tenant_id: str,
        db: Optional[Session] = None,
    ) -> dict[str, Any]:
        request = ActionExecutionRequest(
            command_name=binding.target_name,
            aggregate_type=binding.aggregate_type or step.entity_type or "unknown",
            aggregate_id=step.parameters.get("aggregate_id", f"{plan.plan_id}-{step.order}"),
            payload=step.parameters,
            tenant_id=tenant_id,
            issuer_role=binding.agent_type,
            issuer_type="ai_agent",
            idempotency_key=f"{plan.plan_id}:{step.step_id}",
            human_confirmation=step.requires_approval,
        )
        aggregate_state = dict(step.parameters)
        if binding.target_name == "CreatePurchaseOrder":
            aggregate_state.setdefault("approval_status", "approved")

        result = self._action_execution_service.execute(
            request, aggregate_state=aggregate_state, db=db
        )
        if result.status.value in {"rejected"}:
            return {
                "step_status": "failed",
                "trace": {
                    "status": "failed",
                    "result": result.model_dump(mode="json"),
                },
            }
        if result.status.value == "pending_approval":
            return {
                "step_status": "pending_approval",
                "trace": {
                    "status": "pending_approval",
                    "result": result.model_dump(mode="json"),
                },
            }
        return {
            "step_status": "executed",
            "trace": {
                "status": "executed",
                "result": result.model_dump(mode="json"),
            },
        }

    def _execute_tool_contract(
        self,
        step: PlanStep,
        binding: ToolBinding,
        tenant_id: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        contract = self._registry.by_tool_name(binding.target_name)
        if contract is None:
            return {
                "step_status": "failed",
                "trace": {
                    "status": "failed",
                    "result": {"error": f"Unknown tool contract '{binding.target_name}'"},
                },
            }
        payload = self._tool_execution_service.execute_contract(
            contract,
            parameters=step.parameters,
            tenant_id=tenant_id,
            context={
                **context,
                "entity_type": step.entity_type,
                "action_type": step.action,
                "policy_context": {
                    **dict(context.get("policy_context", {})),
                    **dict(step.parameters.get("policy_context", {})),
                },
                "tenant_policy_overrides": (
                    step.parameters.get("tenant_policy_overrides")
                    or context.get("tenant_policy_overrides")
                    or context.get("policy_overrides")
                ),
            },
        )
        payload["category"] = contract.kategorie.value
        payload["requires_approval"] = contract.requires_approval

        # NC-A7: distinguish real execution from fallback
        mode = payload.get("mode", "unknown")
        if mode == "fallback_contract":
            http_status = payload.get("http_status")
            if http_status and http_status >= 500:
                return {
                    "step_status": "failed",
                    "trace": {"status": "failed", "result": payload},
                }
            # 4xx or transport errors: degraded but not hard failure
            return {
                "step_status": "degraded",
                "trace": {"status": "degraded", "result": payload},
            }

        return {
            "step_status": "executed",
            "trace": {"status": "executed", "result": payload},
        }

    def _execute_superglue_step(
        self,
        step: PlanStep,
        plan: ExecutionPlan,
        binding: ToolBinding,
        tenant_id: str,
    ) -> dict[str, Any]:
        payload = self._superglue_capability_service.execute_step(
            tenant_id=tenant_id,
            capability=plan.capability,
            action=step.action,
            parameters=step.parameters,
        )
        if payload.get("result_status") != "success":
            status = "failed" if str(payload.get("execution_mode")) == "execute" else "degraded"
            return {
                "step_status": status,
                "trace": {"status": status, "result": payload},
            }
        return {
            "step_status": "executed",
            "trace": {"status": "executed", "result": payload},
        }

    # ------------------------------------------------------------------
    # NC-A7: State-Graph Mutation Persistence
    # ------------------------------------------------------------------

    def _persist_state_transition(
        self,
        state_transition: dict[str, Any],
        step: PlanStep,
        binding: ToolBinding,
        tenant_id: str,
        db: Optional[Session],
    ) -> None:
        """Persist a planned state transition to the database after successful execution."""
        if db is None or state_transition.get("status") != "planned":
            return
        try:
            from app.infrastructure.models.neuro_state_models import (
                StateNodeRecord,
                StateTransitionRecord,
            )
            node_id = state_transition["node_id"]

            # Update the node's current phase
            existing_node = db.query(StateNodeRecord).filter_by(
                node_id=node_id, tenant_id=tenant_id,
            ).first()
            if existing_node:
                existing_node.phase = state_transition["to_phase"]
            else:
                # Create a minimal node record if it doesn't exist yet
                new_node = StateNodeRecord(
                    node_id=node_id,
                    node_type=binding.target_node_type.value if binding.target_node_type else "unknown",
                    phase=state_transition["to_phase"],
                    tenant_id=tenant_id,
                    aggregate_id=step.parameters.get("aggregate_id", node_id),
                    aggregate_type=step.entity_type or binding.aggregate_type or "unknown",
                    label=step.description or step.action,
                    metadata_={},
                )
                db.add(new_node)

            # Record the transition
            transition_record = StateTransitionRecord(
                transition_id=f"{step.step_id}-transition",
                node_id=node_id,
                from_phase=state_transition["from_phase"],
                to_phase=state_transition["to_phase"],
                tenant_id=tenant_id,
                triggered_by="neuro-tool-broker",
                reason=step.description or step.action,
                context_hash=state_transition.get("context_hash", ""),
                evidence_refs=json.dumps([step.step_id]),
                schema_version=1,
            )
            db.add(transition_record)
            db.commit()

            state_transition["status"] = "committed"
            logger.info(
                "State transition persisted: %s %s → %s",
                node_id, state_transition["from_phase"], state_transition["to_phase"],
            )
        except Exception as exc:
            logger.warning("State transition persistence failed for step %s: %s", step.action, exc)
            try:
                db.rollback()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # NC-A7: Per-Step Decision Trace
    # ------------------------------------------------------------------

    def _record_step_audit(
        self,
        *,
        plan_id: str,
        step: PlanStep,
        binding: ToolBinding,
        execution: dict[str, Any],
        state_transition: dict[str, Any] | None,
        tenant_id: str,
        db: Optional[Session],
    ) -> None:
        """Write a per-step audit entry to the decision protocol table."""
        if db is None:
            return
        trace_id = str(uuid4())
        now = datetime.now(timezone.utc)
        step_audit = {
            "trace_id": trace_id,
            "plan_id": plan_id,
            "step_id": step.step_id,
            "step_order": step.order,
            "action": step.action,
            "step_type": step.type.value,
            "entity_type": step.entity_type,
            "binding_kind": binding.kind,
            "binding_target": binding.target_name,
            "step_status": execution["step_status"],
            "execution_mode": execution.get("trace", {}).get("result", {}).get("mode"),
            "http_status": execution.get("trace", {}).get("result", {}).get("http_status"),
            "state_transition": state_transition,
            "recorded_at": now.isoformat(),
        }
        try:
            db.execute(text("""
                INSERT INTO domain_shared.neuro_step_audit_trace
                    (id, tenant_id, plan_id, step_id, step_order, action,
                     step_type, binding_kind, binding_target, step_status,
                     execution_detail, recorded_at)
                VALUES
                    (:id, :tid, :plan_id, :step_id, :step_order, :action,
                     :step_type, :binding_kind, :binding_target, :step_status,
                     :detail, :recorded_at)
            """), {
                "id": trace_id,
                "tid": tenant_id,
                "plan_id": plan_id,
                "step_id": step.step_id,
                "step_order": step.order,
                "action": step.action,
                "step_type": step.type.value,
                "binding_kind": binding.kind,
                "binding_target": binding.target_name,
                "step_status": execution["step_status"],
                "detail": json.dumps(step_audit),
                "recorded_at": now,
            })
            try:
                from app.core.metrics import neuro_kernel_audit_inserts_total

                neuro_kernel_audit_inserts_total.inc()
            except Exception:
                pass
            db.commit()
        except Exception as exc:
            logger.debug("Step audit trace write skipped (table may not exist): %s", exc)
            try:
                db.rollback()
            except Exception:
                pass

    def _build_rollback_plan(
        self,
        plan: ExecutionPlan,
        executed_steps: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        executed_step_ids = {entry["step_id"] for entry in executed_steps}
        rollback_plan: list[dict[str, Any]] = []
        for step in reversed(plan.steps):
            if step.step_id not in executed_step_ids or not step.rollback_action:
                continue
            rollback_plan.append(
                {
                    "step_id": step.step_id,
                    "rollback_action": step.rollback_action,
                    "original_action": step.action,
                }
            )
        return rollback_plan

    def _build_state_summary(self, state_transitions: list[dict[str, Any]]) -> dict[str, Any]:
        relevant = [
            t for t in state_transitions
            if t and t.get("status") in ("planned", "committed")
        ]
        return {
            "transition_count": len(relevant),
            "transitions": relevant,
        }
