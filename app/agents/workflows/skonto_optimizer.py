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


# Workflow Nodes
def fetch_open_invoices(state: SkontoOptimizerState) -> dict:
    """Fetch all open invoices with skonto opportunities."""
    logger.info("Fetching open invoices...")
    
    # TODO: Real database query
    # For now, mock data
    mock_invoices = [
        {
            "invoice_id": "INV-001",
            "supplier": "Raiffeisen AG",
            "amount": Decimal("10000.00"),
            "due_date": datetime.now() + timedelta(days=30),
            "skonto_rate": Decimal("0.03"),  # 3%
            "skonto_days": 14,
            "potential_saving": Decimal("300.00")
        },
        {
            "invoice_id": "INV-002",
            "supplier": "BayWa Agrar",
            "amount": Decimal("5000.00"),
            "due_date": datetime.now() + timedelta(days=20),
            "skonto_rate": Decimal("0.02"),  # 2%
            "skonto_days": 10,
            "potential_saving": Decimal("100.00")
        },
    ]
    
    return {"invoices": mock_invoices}


def calculate_optimal_plan(state: SkontoOptimizerState) -> dict:
    """Calculate optimal payment plan to maximize discounts."""
    logger.info("Calculating optimal payment plan...")
    
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
    
    return {
        "optimized_payment_plan": payment_plan,
        "total_discount": total_discount
    }


def generate_recommendations(state: SkontoOptimizerState) -> dict:
    """Generate actionable recommendations."""
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
    
    return {"recommendations": recommendations}


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
        recommendations=[]
    )
    
    result = workflow.invoke(initial_state)
    
    return {
        "payment_plan": result["optimized_payment_plan"],
        "total_discount": float(result["total_discount"]),
        "recommendations": result["recommendations"]
    }

