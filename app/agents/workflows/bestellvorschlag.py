"""
Bestellvorschlag Agent Workflow
Analyzes stock levels and generates purchase order proposals using LangGraph and OpenAI
"""

import logging
from typing import TypedDict, Annotated, Dict, Any
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


# Workflow State
class BestellvorschlagState(TypedDict):
    """State for Bestellvorschlag workflow."""
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]
    correlation_id: str
    tenant_id: str

    # Analysis results
    low_stock_articles: list[dict]
    sales_history: list[dict]
    supplier_recommendations: list[dict]

    # AI Analysis
    ai_insights: Dict[str, Any]
    ai_recommendations: list[str]

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
    Step 3: Generate purchase order proposal based on analysis using AI insights.
    """
    logger.info("Generating AI-enhanced order proposal")

    # Prepare data for AI analysis
    stock_data = "\n".join([
        f"- {article['name']}: Current {article['current']}, Min {article['min']}, Shortage {article['shortage']}"
        for article in state["low_stock_articles"]
    ])

    sales_data = "\n".join([
        f"- {history['article_id']}: {history['avg_monthly_sales']} units/month, Trend: {history['trend']}"
        for history in state["sales_history"]
    ])

    context = f"""
Current Stock Levels:
{stock_data}

Sales History:
{sales_data}

Please analyze this inventory data and provide intelligent purchase recommendations.
Consider seasonal patterns, supplier lead times, and optimal order quantities.
"""

    try:
        # Import here to avoid circular imports
        from services.ai.app.services.openai_service import analyze_text

        ai_analysis = await analyze_text(
            text=context,
            task="Analyze inventory levels and sales data to generate optimal purchase order recommendations for agricultural products",
            context={"domain": "agricultural_procurement", "tenant_id": state["tenant_id"]}
        )

        state["ai_insights"] = ai_analysis
        state["ai_recommendations"] = ai_analysis.get("recommendations", [])

        # Add AI insights to messages
        state["messages"].append(AIMessage(
            content=f"AI Analysis Complete: {ai_analysis.get('insights', [])}",
            additional_kwargs={"analysis": ai_analysis}
        ))

    except Exception as e:
        logger.warning(f"AI analysis failed, falling back to simple algorithm: {e}")
        state["ai_insights"] = {"error": str(e)}
        state["ai_recommendations"] = []

    # Enhanced algorithm with AI insights
    proposals = []

    for article in state["low_stock_articles"]:
        # Find sales history
        history = next(
            (h for h in state["sales_history"] if h["article_id"] == article["article_id"]),
            None
        )

        if history:
            # Base calculation: shortage + 1 month safety stock
            base_qty = article["shortage"] + history["avg_monthly_sales"]

            # AI-enhanced adjustment based on trend
            if history["trend"] == "increasing":
                adjusted_qty = base_qty * 1.2  # 20% increase for growth
            elif history["trend"] == "stable":
                adjusted_qty = base_qty * 1.1  # 10% safety buffer
            else:
                adjusted_qty = base_qty * 0.9  # Conservative for declining

            order_qty = max(adjusted_qty, article["shortage"])  # Never go below shortage

            proposals.append({
                "article_id": article["article_id"],
                "article_name": article["name"],
                "order_quantity": round(order_qty, 2),
                "reason": f"AI-optimized: Low stock ({article['current']}/{article['min']}) + trend-adjusted safety stock",
                "estimated_cost": order_qty * 50,  # Mock price
                "ai_factors": [f"Trend: {history['trend']}", f"Base qty: {base_qty}"]
            })

    state["proposal"] = {
        "created_at": datetime.utcnow().isoformat(),
        "items": proposals,
        "total_estimated_cost": sum(p["estimated_cost"] for p in proposals),
        "ai_insights": state["ai_insights"],
        "ai_recommendations": state["ai_recommendations"]
    }

    logger.info(f"Generated AI-enhanced proposal with {len(proposals)} items")
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


# Workflow-Builder with LangGraph
def build_bestellvorschlag_workflow():
    """
    Build the Bestellvorschlag workflow graph using LangGraph.
    """
    workflow = StateGraph(BestellvorschlagState)

    # Add nodes
    workflow.add_node("analyze_stock", analyze_stock_levels)
    workflow.add_node("check_history", check_sales_history)
    workflow.add_node("generate_proposal", generate_order_proposal)
    workflow.add_node("wait_approval", wait_for_human_approval)
    workflow.add_node("create_order", create_purchase_order)

    # Set entry point
    workflow.set_entry_point("analyze_stock")

    # Add edges
    workflow.add_edge("analyze_stock", "check_history")
    workflow.add_edge("check_history", "generate_proposal")
    workflow.add_edge("generate_proposal", "wait_approval")

    # Conditional edge from approval
    def should_create_order(state: BestellvorschlagState) -> str:
        """Decide if order should be created based on approval."""
        if state.get("approved"):
            return "create_order"
        return END

    workflow.add_conditional_edges(
        "wait_approval",
        should_create_order,
        {
            "create_order": "create_order",
            END: END
        }
    )

    workflow.add_edge("create_order", END)

    # Compile with checkpointer
    from langgraph.checkpoint.sqlite import SqliteSaver
    checkpointer = SqliteSaver.from_conn_string("data/bestellvorschlag_workflows.db")

    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["wait_approval"]  # Human-in-the-Loop checkpoint
    )

    return app


async def run_bestellvorschlag_workflow(tenant_id: str, correlation_id: str) -> BestellvorschlagState:
    """
    Execute Bestellvorschlag workflow using LangGraph.
    """
    workflow = build_bestellvorschlag_workflow()

    initial_state: BestellvorschlagState = {
        "messages": [HumanMessage(content="Generate purchase order proposal")],
        "correlation_id": correlation_id,
        "tenant_id": tenant_id,
        "low_stock_articles": [],
        "sales_history": [],
        "supplier_recommendations": [],
        "ai_insights": {},
        "ai_recommendations": [],
        "proposal": None,
        "approved": False,
        "rejection_reason": None,
        "order_id": None,
        "created_at": None,
    }

    config = {"configurable": {"thread_id": correlation_id}}

    # Run until checkpoint
    result = await workflow.ainvoke(initial_state, config)

    logger.info(f"Bestellvorschlag workflow paused at approval checkpoint: {correlation_id}")
    return result

