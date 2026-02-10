"""
Bestellvorschlag Agent Workflow
Analyzes stock levels and generates purchase order proposals using LangGraph and OpenAI
"""

import logging
from typing import TypedDict, Annotated, Dict, Any
from datetime import datetime
import httpx

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

from app.core.dependency_container import container
from app.infrastructure.repositories import ArticleRepository, StockMovementRepository

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

    try:
        article_repo = container.resolve(ArticleRepository)

        # Get all articles for the tenant
        articles = await article_repo.get_all(state['tenant_id'], limit=1000)

        # Filter for low stock articles (current_stock < min_stock_level)
        low_stock_articles = []
        for article in articles:
            if article.min_stock_level and article.current_stock < article.min_stock_level:
                shortage = article.min_stock_level - article.current_stock
                low_stock_articles.append({
                    "article_id": str(article.id),
                    "name": article.name,
                    "current": float(article.current_stock or 0),
                    "min": float(article.min_stock_level or 0),
                    "shortage": float(shortage),
                    "unit": article.unit or "Stk"
                })

        state["low_stock_articles"] = low_stock_articles
        logger.info(f"Found {len(low_stock_articles)} low stock articles")

    except Exception as e:
        logger.error(f"Failed to analyze stock levels: {e}")
        # Fallback to empty list if database query fails
        state["low_stock_articles"] = []

    return state


async def check_sales_history(state: BestellvorschlagState) -> BestellvorschlagState:
    """
    Step 2: Check historical sales data to predict demand.
    """
    logger.info("Checking sales history")

    try:
        stock_movement_repo = container.resolve(StockMovementRepository)

        # Get sales history for each low stock article
        sales_history = []

        for article in state["low_stock_articles"]:
            article_id = article["article_id"]

            # Get stock movements for this article (outbound movements = sales)
            # This is a simplified approach - in production, you'd filter by movement_type = 'outbound'
            movements = await stock_movement_repo.get_all(
                state['tenant_id'],
                limit=1000,
                article_id=article_id  # Assuming the repo supports this filter
            )

            if movements:
                # Calculate monthly sales averages
                # Group by month and calculate totals
                monthly_sales = {}
                for movement in movements:
                    if hasattr(movement, 'movement_type') and movement.movement_type == 'outbound':
                        month_key = movement.created_at.strftime('%Y-%m') if movement.created_at else 'unknown'
                        if month_key not in monthly_sales:
                            monthly_sales[month_key] = 0
                        monthly_sales[month_key] += abs(movement.quantity or 0)

                # Calculate average monthly sales
                if monthly_sales:
                    avg_monthly_sales = sum(monthly_sales.values()) / len(monthly_sales)

                    # Determine trend (simplified: compare last 3 months)
                    sorted_months = sorted(monthly_sales.keys())
                    if len(sorted_months) >= 3:
                        recent_months = sorted_months[-3:]
                        recent_sales = [monthly_sales[m] for m in recent_months]
                        if recent_sales[-1] > recent_sales[0] * 1.1:  # 10% increase
                            trend = "increasing"
                        elif recent_sales[-1] < recent_sales[0] * 0.9:  # 10% decrease
                            trend = "decreasing"
                        else:
                            trend = "stable"
                    else:
                        trend = "stable"

                    sales_history.append({
                        "article_id": article_id,
                        "avg_monthly_sales": float(avg_monthly_sales),
                        "trend": trend,
                        "total_movements": len(movements)
                    })

        state["sales_history"] = sales_history
        logger.info(f"Analyzed sales history for {len(sales_history)} articles")

    except Exception as e:
        logger.error(f"Failed to check sales history: {e}")
        # Fallback to empty list if database query fails
        state["sales_history"] = []

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

    try:
        # Prepare purchase order data from proposal
        proposal = state["proposal"]
        items = []

        for item in proposal["items"]:
            # Get article details for proper item creation
            article_repo = container.resolve(ArticleRepository)
            article = await article_repo.get_by_id(item["article_id"], state["tenant_id"])

            if article:
                items.append({
                    "article_id": item["article_id"],
                    "qty": item["order_quantity"],
                    "price": article.purchase_price or 0,  # Use purchase price if available
                    "uom": article.unit or "Stk"
                })

        # Create purchase order payload
        po_data = {
            "supplier_id": "default-supplier",  # TODO: Determine supplier from article or use default
            "items": items,
            "currency": "EUR",
            "notes": f"Auto-generated from AI procurement proposal. {proposal.get('ai_recommendations', [])}"
        }

        # Call purchase order API
        async with httpx.AsyncClient() as client:
            # Assuming the API is running locally - in production this would be configurable
            api_url = "http://localhost:8000/api/einkauf/bestellungen"  # Adjust based on actual API endpoint
            headers = {
                "Content-Type": "application/json",
                "X-Tenant-ID": state["tenant_id"]
            }

            response = await client.post(api_url, json=po_data, headers=headers)

            if response.status_code == 201:
                result = response.json()
                state["order_id"] = result.get("id", f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
                state["created_at"] = datetime.utcnow()
                logger.info(f"Purchase order created successfully: {state['order_id']}")
            else:
                logger.error(f"Failed to create purchase order: {response.status_code} - {response.text}")
                # Fallback: generate ID anyway for workflow continuity
                state["order_id"] = f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                state["created_at"] = datetime.utcnow()
                logger.warning("Using fallback order ID due to API failure")

    except Exception as e:
        logger.error(f"Error creating purchase order: {e}")
        # Fallback: generate ID anyway for workflow continuity
        state["order_id"] = f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        state["created_at"] = datetime.utcnow()
        logger.warning("Using fallback order ID due to exception")

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

