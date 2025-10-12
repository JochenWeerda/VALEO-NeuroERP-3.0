"""
Bestellvorschlag Agent Workflow
Analyzes stock levels and generates purchase order proposals
"""

import logging
from typing import TypedDict, Annotated
from datetime import datetime

logger = logging.getLogger(__name__)


# Workflow State
class BestellvorschlagState(TypedDict):
    """State for Bestellvorschlag workflow."""
    correlation_id: str
    tenant_id: str
    
    # Analysis results
    low_stock_articles: list[dict]
    sales_history: list[dict]
    supplier_recommendations: list[dict]
    
    # Proposal
    proposal: dict | None
    approved: bool
    rejection_reason: str | None
    
    # Output
    order_id: str | None
    created_at: datetime | None


# Workflow Nodes
async def analyze_stock_levels(state: BestellvorschlagState) -> BestellvorschlagState:
    """
    Step 1: Analyze current stock levels and identify low stock.
    """
    logger.info(f"Analyzing stock levels (tenant: {state['tenant_id']})")
    
    # TODO: Query database for low stock articles
    # For now, mock data
    state["low_stock_articles"] = [
        {"article_id": "1", "name": "Weizen Premium", "current": 50, "min": 100, "shortage": 50},
        {"article_id": "2", "name": "Sojaschrot", "current": 20, "min": 80, "shortage": 60},
    ]
    
    logger.info(f"Found {len(state['low_stock_articles'])} low stock articles")
    return state


async def check_sales_history(state: BestellvorschlagState) -> BestellvorschlagState:
    """
    Step 2: Check historical sales data to predict demand.
    """
    logger.info("Checking sales history")
    
    # TODO: Query sales history
    state["sales_history"] = [
        {"article_id": "1", "avg_monthly_sales": 200, "trend": "increasing"},
        {"article_id": "2", "avg_monthly_sales": 150, "trend": "stable"},
    ]
    
    return state


async def generate_order_proposal(state: BestellvorschlagState) -> BestellvorschlagState:
    """
    Step 3: Generate purchase order proposal based on analysis.
    """
    logger.info("Generating order proposal")
    
    # Simple algorithm: Order to reach min_stock + 1 month safety
    proposals = []
    
    for article in state["low_stock_articles"]:
        # Find sales history
        history = next(
            (h for h in state["sales_history"] if h["article_id"] == article["article_id"]),
            None
        )
        
        if history:
            # Order quantity = shortage + 1 month safety stock
            order_qty = article["shortage"] + history["avg_monthly_sales"]
            proposals.append({
                "article_id": article["article_id"],
                "article_name": article["name"],
                "order_quantity": order_qty,
                "reason": f"Low stock ({article['current']}/{article['min']}) + safety stock",
                "estimated_cost": order_qty * 50  # Mock price
            })
    
    state["proposal"] = {
        "created_at": datetime.utcnow().isoformat(),
        "items": proposals,
        "total_estimated_cost": sum(p["estimated_cost"] for p in proposals)
    }
    
    logger.info(f"Generated proposal with {len(proposals)} items")
    return state


async def wait_for_human_approval(state: BestellvorschlagState) -> BestellvorschlagState:
    """
    Step 4: Wait for human approval (interrupt point).
    """
    logger.info("Waiting for human approval...")
    
    # This is a checkpoint - workflow pauses here
    # User must call /approve or /reject endpoint
    
    # For prototype, auto-approve after logging
    logger.warning("AUTO-APPROVING for prototype (TODO: Real approval UI)")
    state["approved"] = True
    
    return state


async def create_purchase_order(state: BestellvorschlagState) -> BestellvorschlagState:
    """
    Step 5: Create purchase order if approved.
    """
    if not state["approved"]:
        logger.info("Proposal rejected, skipping order creation")
        return state
    
    logger.info("Creating purchase order")
    
    # TODO: Call Purchase Order API
    state["order_id"] = f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    state["created_at"] = datetime.utcnow()
    
    logger.info(f"Purchase order created: {state['order_id']}")
    return state


# Workflow-Builder (Phase 3 - wird mit LangGraph erweitert)
def build_bestellvorschlag_workflow():
    """
    Build the Bestellvorschlag workflow graph.
    
    For Phase 3, this will use LangGraph.
    For now, simple sequential execution.
    """
    async def run_workflow(tenant_id: str, correlation_id: str) -> BestellvorschlagState:
        """Execute workflow sequentially."""
        state: BestellvorschlagState = {
            "correlation_id": correlation_id,
            "tenant_id": tenant_id,
            "low_stock_articles": [],
            "sales_history": [],
            "supplier_recommendations": [],
            "proposal": None,
            "approved": False,
            "rejection_reason": None,
            "order_id": None,
            "created_at": None,
        }
        
        # Execute steps
        state = await analyze_stock_levels(state)
        state = await check_sales_history(state)
        state = await generate_order_proposal(state)
        state = await wait_for_human_approval(state)
        
        if state["approved"]:
            state = await create_purchase_order(state)
        
        return state
    
    return run_workflow

