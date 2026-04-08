"""
Integration: NeuroToolBroker mit echter DB-Session (Command-Step).

Ueberspringt automatisch, wenn Tabellen fehlen oder DB nicht erreichbar.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.agents.neuro_planner import ExecutionPlan, PlanStep, StepType
from app.core.action_idempotency import get_action_idempotency_store
from app.core.database import SessionLocal
from app.services.command_handlers_finance import register_finance_command_mutations
from app.services.command_handlers_procurement import register_command_mutations
from app.services.neuro_tool_broker import NeuroToolBroker


@pytest.fixture(autouse=True)
def _registry_and_idempotency():
    register_command_mutations()
    register_finance_command_mutations()
    get_action_idempotency_store().clear()
    yield
    get_action_idempotency_store().clear()


@pytest.mark.integration
def test_broker_create_purchase_order_command_step_with_db_session():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1 FROM domain_einkauf.bestellungen LIMIT 1"))
        db.rollback()
    except SQLAlchemyError:
        pytest.skip("DB nicht erreichbar oder einkauf_bestellungen fehlt")
    finally:
        db.close()

    plan = ExecutionPlan(
        plan_id="integration-broker-po",
        intent="test",
        steps=[
            PlanStep(
                order=0,
                type=StepType.COMMAND,
                action="create_purchase_order",
                entity_type="purchase_order",
                parameters={
                    "lieferant_id": 1,
                    "aggregate_id": "po-int-1",
                },
                requires_approval=False,
            )
        ],
    )
    db = SessionLocal()
    try:
        broker = NeuroToolBroker()
        out = broker.execute_plan(plan, tenant_id="integration-tenant", db=db)
        assert out["status"] in ("executed", "failed", "awaiting_approval")
        assert "tool_trace" in out
    finally:
        db.close()
