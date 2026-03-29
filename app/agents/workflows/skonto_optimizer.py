"""
Skonto-Optimizer Workflow
AI-Agent to maximize cash discount opportunities
"""

from typing import Annotated, List, TypedDict, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import operator

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END

import logging

logger = logging.getLogger(__name__)


# State Definition
class SkontoOptimizerState(TypedDict):
    """State for skonto optimization workflow."""
    messages: Annotated[List[BaseMessage], operator.add]
    invoices: List[dict]
    payment_date: datetime
    available_cash: Decimal
    optimized_payment_plan: List[dict]
    total_discount: Decimal
    recommendations: List[str]
    current_stage_key: str
    stage_transition_log: List[dict]
    gate_decisions: List[dict]


def _mark_stage(state: SkontoOptimizerState, stage_key: str, detail: str) -> None:
    state["current_stage_key"] = stage_key
    state["stage_transition_log"].append(
        {
            "stage_key": stage_key,
            "timestamp": datetime.utcnow().isoformat(),
            "detail": detail,
        }
    )


def _set_policy_gate(state: SkontoOptimizerState, status: str, reason: str) -> None:
    state["gate_decisions"] = [
        decision for decision in state.get("gate_decisions", []) if decision.get("gate_type") != "policy_gate"
    ]
    state["gate_decisions"].append(
        {
            "gate_type": "policy_gate",
            "status": status,
            "reason": reason,
            "required_role": None,
            "schema_version": 1,
        }
    )


# Workflow Nodes
def fetch_open_invoices(state: SkontoOptimizerState) -> dict:
    """Fetch all open invoices with skonto opportunities."""
    logger.info("Fetching open invoices...")
    _mark_stage(state, "analysis", "Fetch open invoices")
    
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text

        db = SessionLocal()
        try:
            rows = db.execute(text("""
                SELECT oi.id            AS invoice_id,
                       oi.debitor_id    AS supplier,
                       oi.amount,
                       oi.due_date,
                       COALESCE(oi.skonto_rate, 0)  AS skonto_rate,
                       COALESCE(oi.skonto_days, 0)  AS skonto_days
                FROM domain_shared.open_items oi
                WHERE oi.status = 'open'
                  AND oi.skonto_rate IS NOT NULL
                  AND oi.skonto_rate > 0
                  AND oi.due_date >= CURRENT_DATE
                ORDER BY (oi.amount * oi.skonto_rate) DESC
                LIMIT 200
            """)).fetchall()

            invoices = []
            for r in rows:
                amt = Decimal(str(r.amount))
                rate = Decimal(str(r.skonto_rate))
                invoices.append({
                    "invoice_id": str(r.invoice_id),
                    "supplier": str(r.supplier or ""),
                    "amount": amt,
                    "due_date": r.due_date if hasattr(r.due_date, "year") else datetime.now() + timedelta(days=30),
                    "skonto_rate": rate,
                    "skonto_days": int(r.skonto_days),
                    "potential_saving": (amt * rate).quantize(Decimal("0.01")),
                })
        finally:
            db.close()
    except Exception as exc:
        logger.warning("DB query for open invoices failed, using empty list: %s", exc)
        invoices = []

    return {
        "invoices": invoices,
        "current_stage_key": state["current_stage_key"],
        "stage_transition_log": state["stage_transition_log"],
    }


def calculate_optimal_plan(state: SkontoOptimizerState) -> dict:
    """Calculate optimal payment plan to maximize discounts."""
    logger.info("Calculating optimal payment plan...")
    _mark_stage(state, "proposal", "Calculate skonto payment proposal")
    
    invoices = state["invoices"]
    available = state["available_cash"]
    payment_date = state["payment_date"]
    
    # Sort by savings potential (highest first)
    sorted_invoices = sorted(
        invoices,
        key=lambda x: x["potential_saving"],
        reverse=True
    )
    
    payment_plan = []
    remaining_cash = available
    total_discount = Decimal("0.00")
    
    for invoice in sorted_invoices:
        skonto_deadline = invoice["due_date"] - timedelta(
            days=30 - invoice["skonto_days"]
        )
        
        # Can we pay within skonto period?
        if payment_date <= skonto_deadline:
            discounted_amount = (
                invoice["amount"] * (1 - invoice["skonto_rate"])
            )
            
            if remaining_cash >= discounted_amount:
                payment_plan.append({
                    "invoice_id": invoice["invoice_id"],
                    "supplier": invoice["supplier"],
                    "original_amount": invoice["amount"],
                    "payment_amount": discounted_amount,
                    "discount": invoice["potential_saving"],
                    "payment_date": payment_date
                })
                remaining_cash -= discounted_amount
                total_discount += invoice["potential_saving"]
    
    if payment_plan:
        _set_policy_gate(
            state,
            "allowed",
            "Finance review can proceed with the proposed skonto plan.",
        )
    else:
        _set_policy_gate(
            state,
            "allowed",
            "No blocking finance policy issue; no skonto opportunity selected.",
        )

    return {
        "optimized_payment_plan": payment_plan,
        "total_discount": total_discount,
        "current_stage_key": state["current_stage_key"],
        "stage_transition_log": state["stage_transition_log"],
        "gate_decisions": state["gate_decisions"],
    }


def generate_recommendations(state: SkontoOptimizerState) -> dict:
    """Generate actionable recommendations."""
    _mark_stage(state, "closure", "Generate skonto recommendations and close run")
    recommendations = []
    
    total_discount = state["total_discount"]
    plan = state["optimized_payment_plan"]
    
    if total_discount > Decimal("0"):
        recommendations.append(
            f"✅ Empfehlung: {len(plan)} Rechnungen mit Skonto "
            f"bezahlen → Ersparnis {total_discount}€"
        )
    
    unpaid_invoices = len(state["invoices"]) - len(plan)
    if unpaid_invoices > 0:
        recommendations.append(
            f"⚠️ {unpaid_invoices} Rechnungen können nicht mit Skonto "
            f"bezahlt werden (Liquidität erhöhen?)"
        )
    
    return {
        "recommendations": recommendations,
        "current_stage_key": state["current_stage_key"],
        "stage_transition_log": state["stage_transition_log"],
        "gate_decisions": state["gate_decisions"],
    }


# Build Workflow
def build_skonto_workflow():
    """Build the skonto optimization workflow."""
    workflow = StateGraph(SkontoOptimizerState)
    
    workflow.add_node("fetch_invoices", fetch_open_invoices)
    workflow.add_node("calculate_plan", calculate_optimal_plan)
    workflow.add_node("generate_recs", generate_recommendations)
    
    workflow.set_entry_point("fetch_invoices")
    workflow.add_edge("fetch_invoices", "calculate_plan")
    workflow.add_edge("calculate_plan", "generate_recs")
    workflow.add_edge("generate_recs", END)
    
    return workflow.compile()


# Execute workflow
async def optimize_skonto(
    available_cash: Decimal,
    payment_date: Optional[datetime] = None
) -> dict:
    """Execute skonto optimization workflow."""
    workflow = build_skonto_workflow()
    
    initial_state = SkontoOptimizerState(
        messages=[HumanMessage(content="Optimize Skonto")],
        invoices=[],
        payment_date=payment_date or datetime.now(),
        available_cash=available_cash,
        optimized_payment_plan=[],
        total_discount=Decimal("0.00"),
        recommendations=[],
        current_stage_key="intake",
        stage_transition_log=[
            {
                "stage_key": "intake",
                "timestamp": datetime.utcnow().isoformat(),
                "detail": "Skonto workflow run created",
            }
        ],
        gate_decisions=[],
    )
    
    result = workflow.invoke(initial_state)
    
    return {
        "payment_plan": result["optimized_payment_plan"],
        "total_discount": float(result["total_discount"]),
        "recommendations": result["recommendations"],
        "current_stage_key": result["current_stage_key"],
        "stage_transition_log": result["stage_transition_log"],
        "gate_decisions": result["gate_decisions"],
    }

