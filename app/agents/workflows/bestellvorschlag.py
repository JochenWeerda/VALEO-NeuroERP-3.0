"""
Bestellvorschlag Agent Workflow

Produktiver Einkaufs-Workflow mit echtem Approval- und Command-Contract.
Kein localhost-Loopback, keine Fallback-Bestellnummern und keine Auto-Freigabe.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph

from app.core.business_commands import BusinessCommand, CommandStatus
from app.core.command_dispatcher import CommandDispatcher
from app.core.database import SessionLocal
from app.core.dependency_container import container
from app.core.human_approval_gate import evaluate_approval_requirement, get_default_approval_rules
from app.core.uuid7 import uuid7
from app.infrastructure.models.einkauf_models import EinkaufBestellung, EinkaufBestellungPosition
from app.infrastructure.repositories import ArticleRepository, StockMovementRepository
from app.services.numbering_service import get_numbering

logger = logging.getLogger(__name__)

BESTELLVORSCHLAG_AKTIONSTYP = "BESTELLUNG_ANLEGEN"
NEUROASSIST_ISSUER = "neuroassist.bestellvorschlag"
NEUROASSIST_ISSUER_ROLE = "buyer"
NEUROASSIST_WORKFLOW_KEY = "bestellvorschlag"


class BestellvorschlagWorkflowError(RuntimeError):
    """Workflow contract violation."""


class BestellvorschlagState(TypedDict):
    """State for Bestellvorschlag workflow."""

    messages: Annotated[list[BaseMessage], lambda x, y: x + y]
    correlation_id: str
    tenant_id: str

    low_stock_articles: list[dict[str, Any]]
    sales_history: list[dict[str, Any]]
    supplier_recommendations: list[dict[str, Any]]

    ai_insights: dict[str, Any]
    ai_recommendations: list[str]

    proposal: dict[str, Any] | None
    approval_requirement: dict[str, Any] | None
    approval_record: dict[str, Any] | None
    gate_decisions: list[dict[str, Any]]
    approved: bool
    rejection_reason: str | None

    command_result: dict[str, Any] | None
    order_id: str | None
    created_at: datetime | None
    current_stage_key: str
    stage_transition_log: list[dict[str, Any]]


def _safe_decimal(value: Any, default: str = "0") -> Decimal:
    try:
        if value is None:
            return Decimal(default)
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def _coerce_optional_decimal(value: Decimal) -> Decimal | None:
    return None if value == Decimal("0") else value


def _resolve_supplier_id(article: Any) -> str | None:
    for field in ("preferred_supplier_id", "supplier_id", "lieferant_id", "std_lieferant_id"):
        value = getattr(article, field, None)
        if value:
            return str(value)
    return None


def _build_approval_requirement(proposal: dict[str, Any]) -> dict[str, Any]:
    total_estimated_cost = _safe_decimal(proposal.get("total_estimated_cost"))
    context = {
        "betrag_eur": float(total_estimated_cost),
        "datensaetze_count": len(proposal.get("items", [])),
    }
    return evaluate_approval_requirement(
        BESTELLVORSCHLAG_AKTIONSTYP,
        context,
        get_default_approval_rules(),
    ).as_dict()


def _mark_stage(
    state: BestellvorschlagState,
    stage_key: str,
    *,
    detail: str | None = None,
) -> BestellvorschlagState:
    state["current_stage_key"] = stage_key
    transition = {
        "stage_key": stage_key,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if detail:
        transition["detail"] = detail
    state["stage_transition_log"].append(transition)
    return state


def _record_gate_decision(
    state: BestellvorschlagState,
    *,
    gate_type: str,
    status: str,
    reason: str,
    required_role: str | None = None,
) -> BestellvorschlagState:
    decision = {
        "gate_type": gate_type,
        "status": status,
        "reason": reason,
        "required_role": required_role,
        "schema_version": 1,
    }
    state["gate_decisions"] = [
        entry for entry in state.get("gate_decisions", []) if entry.get("gate_type") != gate_type
    ]
    state["gate_decisions"].append(decision)
    return state


async def _collect_purchase_order_items(
    tenant_id: str,
    proposal_items: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    article_repo = container.resolve(ArticleRepository)
    items: list[dict[str, Any]] = []
    supplier_ids: set[str] = set()

    for proposal_item in proposal_items:
        article_id = proposal_item["article_id"]
        article = await article_repo.get_by_id(article_id, tenant_id)
        if article is None:
            raise BestellvorschlagWorkflowError(
                f"Article '{article_id}' not found for tenant '{tenant_id}'"
            )

        supplier_id = _resolve_supplier_id(article)
        if not supplier_id:
            raise BestellvorschlagWorkflowError(
                f"Article '{article_id}' has no resolvable supplier contract"
            )
        supplier_ids.add(supplier_id)

        items.append(
            {
                "article_id": article_id,
                "artikel_nr": str(
                    getattr(article, "article_number", None)
                    or getattr(article, "artikel_nr", None)
                    or article_id
                ),
                "artikel_bezeichnung": str(
                    getattr(article, "name", None)
                    or proposal_item.get("article_name")
                    or article_id
                ),
                "menge": float(proposal_item["order_quantity"]),
                "einheit": getattr(article, "unit", None) or "Stk",
                "einzelpreis": _coerce_optional_decimal(
                    _safe_decimal(getattr(article, "purchase_price", None))
                ),
                "preis_einheit": "1",
            }
        )

    if len(supplier_ids) != 1:
        raise BestellvorschlagWorkflowError(
            "Bestellvorschlag enthaelt Positionen mit mehreren Lieferanten; "
            "ein Workflow erzeugt genau eine Bestellung"
        )

    return items, next(iter(supplier_ids))


def _dispatch_purchase_order_command(state: BestellvorschlagState) -> dict[str, Any]:
    dispatcher = CommandDispatcher()
    command = BusinessCommand(
        command_id=str(uuid7()),
        tenant_id=state["tenant_id"],
        aggregate_type="purchase_order",
        aggregate_id=state["correlation_id"],
        command_name="CreatePurchaseOrder",
        workflow_key=NEUROASSIST_WORKFLOW_KEY,
        issued_by=NEUROASSIST_ISSUER,
        idempotency_key=state["correlation_id"],
        payload={
            "proposal_created_at": state["proposal"]["created_at"] if state["proposal"] else None,
            "approval_requirement": state.get("approval_requirement"),
            "approval_record": state.get("approval_record"),
        },
    )
    result = dispatcher.dispatch(
        command,
        aggregate_state={"approval_status": "approved" if state.get("approved") else "pending"},
        issuer_role=NEUROASSIST_ISSUER_ROLE,
    )
    if result.status != CommandStatus.ACCEPTED:
        raise BestellvorschlagWorkflowError(
            f"CreatePurchaseOrder rejected: {result.error.code if result.error else 'UNKNOWN'}"
        )
    return result.model_dump(mode="json")


def _persist_purchase_order(
    *,
    tenant_id: str,
    supplier_id: str,
    items: list[dict[str, Any]],
    correlation_id: str,
    ai_recommendations: list[str],
) -> str:
    session = SessionLocal()
    try:
        bestellung = EinkaufBestellung(
            id=uuid7(),
            tenant_id=tenant_id,
            bestellnummer=get_numbering().next_number("purchase_order"),
            lieferant_id=supplier_id,
            bestelldatum=date.today(),
            status="entwurf",
            versand_art="email",
            notiz=(
                "NeuroASSIST Bestellvorschlag "
                f"({correlation_id}). Empfehlungen: {', '.join(ai_recommendations) or 'keine'}"
            ),
            erstellt_von=NEUROASSIST_ISSUER,
        )
        session.add(bestellung)
        session.flush()

        for pos_nr, item in enumerate(items, start=1):
            session.add(
                EinkaufBestellungPosition(
                    id=uuid7(),
                    bestellung_id=bestellung.id,
                    pos_nr=pos_nr,
                    article_id=item["article_id"],
                    artikel_nr=item["artikel_nr"],
                    artikel_bezeichnung=item["artikel_bezeichnung"],
                    menge=item["menge"],
                    menge_geliefert=0,
                    menge_offen=item["menge"],
                    einheit=item["einheit"],
                    einzelpreis=item["einzelpreis"],
                    preis_einheit=item["preis_einheit"],
                )
            )

        session.commit()
        return str(bestellung.id)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def analyze_stock_levels(state: BestellvorschlagState) -> BestellvorschlagState:
    """Step 1: Analyze current stock levels and identify low stock."""

    _mark_stage(state, "analysis", detail="Analyze stock levels")
    logger.info("Analyzing stock levels (tenant: %s)", state["tenant_id"])
    try:
        article_repo = container.resolve(ArticleRepository)
        articles = await article_repo.get_all(state["tenant_id"], limit=1000)
        low_stock_articles: list[dict[str, Any]] = []
        for article in articles:
            if article.min_stock_level and article.current_stock < article.min_stock_level:
                shortage = article.min_stock_level - article.current_stock
                low_stock_articles.append(
                    {
                        "article_id": str(article.id),
                        "name": article.name,
                        "current": float(article.current_stock or 0),
                        "min": float(article.min_stock_level or 0),
                        "shortage": float(shortage),
                        "unit": article.unit or "Stk",
                    }
                )
        state["low_stock_articles"] = low_stock_articles
    except Exception as exc:
        logger.error("Failed to analyze stock levels: %s", exc)
        state["low_stock_articles"] = []
    return state


async def check_sales_history(state: BestellvorschlagState) -> BestellvorschlagState:
    """Step 2: Check historical sales data to predict demand."""

    _mark_stage(state, "analysis", detail="Check sales history")
    logger.info("Checking sales history")
    try:
        stock_movement_repo = container.resolve(StockMovementRepository)
        sales_history: list[dict[str, Any]] = []

        for article in state["low_stock_articles"]:
            movements = await stock_movement_repo.get_all(
                state["tenant_id"],
                limit=1000,
                article_id=article["article_id"],
            )
            if not movements:
                continue

            monthly_sales: dict[str, float] = {}
            for movement in movements:
                if getattr(movement, "movement_type", None) != "outbound":
                    continue
                month_key = (
                    movement.created_at.strftime("%Y-%m")
                    if getattr(movement, "created_at", None)
                    else "unknown"
                )
                monthly_sales[month_key] = monthly_sales.get(month_key, 0.0) + abs(
                    float(getattr(movement, "quantity", 0) or 0)
                )

            if not monthly_sales:
                continue

            avg_monthly_sales = sum(monthly_sales.values()) / len(monthly_sales)
            sorted_months = sorted(monthly_sales.keys())
            trend = "stable"
            if len(sorted_months) >= 3:
                recent_sales = [monthly_sales[m] for m in sorted_months[-3:]]
                if recent_sales[-1] > recent_sales[0] * 1.1:
                    trend = "increasing"
                elif recent_sales[-1] < recent_sales[0] * 0.9:
                    trend = "decreasing"

            sales_history.append(
                {
                    "article_id": article["article_id"],
                    "avg_monthly_sales": float(avg_monthly_sales),
                    "trend": trend,
                    "total_movements": len(movements),
                }
            )

        state["sales_history"] = sales_history
    except Exception as exc:
        logger.error("Failed to check sales history: %s", exc)
        state["sales_history"] = []
    return state


async def generate_order_proposal(state: BestellvorschlagState) -> BestellvorschlagState:
    """Step 3: Generate purchase order proposal based on analysis and approval contract."""

    _mark_stage(state, "proposal", detail="Generate proposal")
    logger.info("Generating order proposal")

    stock_data = "\n".join(
        [
            f"- {article['name']}: Current {article['current']}, Min {article['min']}, Shortage {article['shortage']}"
            for article in state["low_stock_articles"]
        ]
    )
    sales_data = "\n".join(
        [
            f"- {history['article_id']}: {history['avg_monthly_sales']} units/month, Trend: {history['trend']}"
            for history in state["sales_history"]
        ]
    )

    context = f"""
Current Stock Levels:
{stock_data}

Sales History:
{sales_data}

Please analyze this inventory data and provide intelligent purchase recommendations.
Consider seasonal patterns, supplier lead times, and optimal order quantities.
"""

    try:
        from services.ai.app.services.openai_service import analyze_text

        ai_analysis = await analyze_text(
            text=context,
            task="Analyze inventory levels and sales data to generate optimal purchase order recommendations for agricultural products",
            context={"domain": "agricultural_procurement", "tenant_id": state["tenant_id"]},
        )
        state["ai_insights"] = ai_analysis
        state["ai_recommendations"] = ai_analysis.get("recommendations", [])
        state["messages"].append(
            AIMessage(
                content=f"AI Analysis Complete: {ai_analysis.get('insights', [])}",
                additional_kwargs={"analysis": ai_analysis},
            )
        )
    except Exception as exc:
        logger.warning("AI analysis failed, falling back to deterministic algorithm: %s", exc)
        state["ai_insights"] = {"error": str(exc)}
        state["ai_recommendations"] = []

    proposals: list[dict[str, Any]] = []
    for article in state["low_stock_articles"]:
        history = next(
            (h for h in state["sales_history"] if h["article_id"] == article["article_id"]),
            None,
        )
        if not history:
            continue

        base_qty = article["shortage"] + history["avg_monthly_sales"]
        if history["trend"] == "increasing":
            adjusted_qty = base_qty * 1.2
        elif history["trend"] == "stable":
            adjusted_qty = base_qty * 1.1
        else:
            adjusted_qty = base_qty * 0.9

        order_qty = max(adjusted_qty, article["shortage"])
        proposals.append(
            {
                "article_id": article["article_id"],
                "article_name": article["name"],
                "order_quantity": round(order_qty, 2),
                "reason": (
                    "Contract-based: Low stock plus trend-adjusted safety stock"
                ),
                "estimated_cost": round(order_qty * 50, 2),
                "ai_factors": [f"Trend: {history['trend']}", f"Base qty: {base_qty}"],
            }
        )

    proposal = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "items": proposals,
        "total_estimated_cost": round(sum(p["estimated_cost"] for p in proposals), 2),
        "ai_insights": state["ai_insights"],
        "ai_recommendations": state["ai_recommendations"],
    }
    approval_requirement = _build_approval_requirement(proposal)

    state["proposal"] = proposal
    state["approval_requirement"] = approval_requirement
    state["approval_record"] = None
    state["command_result"] = None
    state["approved"] = not approval_requirement["requires_human_approval"]
    if approval_requirement["requires_human_approval"]:
        _mark_stage(state, "approval", detail="Human approval required")
        _record_gate_decision(
            state,
            gate_type="approval_gate",
            status="deferred",
            reason="Human approval is still pending before execution.",
            required_role="human_operator",
        )
    else:
        _mark_stage(state, "execution", detail="Approval gate resolved automatically")
        _record_gate_decision(
            state,
            gate_type="approval_gate",
            status="allowed",
            reason="No explicit human approval required for this run.",
            required_role=None,
        )
    logger.info(
        "Generated proposal with %s items; approval required=%s",
        len(proposals),
        approval_requirement["requires_human_approval"],
    )
    return state


async def wait_for_human_approval(state: BestellvorschlagState) -> BestellvorschlagState:
    """Step 4: Human approval checkpoint."""

    _mark_stage(state, "approval", detail="Await human approval")
    requirement = state.get("approval_requirement") or {}
    if not requirement.get("requires_human_approval"):
        return state
    if state.get("approved") or state.get("approval_record"):
        return state
    raise BestellvorschlagWorkflowError("Human approval decision missing for bestellvorschlag")


async def create_purchase_order(state: BestellvorschlagState) -> BestellvorschlagState:
    """Step 5: Create purchase order if approved."""

    if not state.get("approved"):
        _record_gate_decision(
            state,
            gate_type="approval_gate",
            status="blocked",
            reason="Human approval rejected the proposed action.",
            required_role="human_operator",
        )
        _mark_stage(state, "closure", detail="Workflow closed after rejected approval")
        logger.info("Proposal rejected, skipping purchase order creation")
        return state
    if not state.get("proposal"):
        raise BestellvorschlagWorkflowError("Proposal missing before purchase order creation")

    _mark_stage(state, "execution", detail="Execute purchase-order creation")
    logger.info("Creating purchase order via command contract")
    items, supplier_id = await _collect_purchase_order_items(
        state["tenant_id"],
        state["proposal"]["items"],
    )
    command_result = _dispatch_purchase_order_command(state)
    order_id = _persist_purchase_order(
        tenant_id=state["tenant_id"],
        supplier_id=supplier_id,
        items=items,
        correlation_id=state["correlation_id"],
        ai_recommendations=state.get("ai_recommendations", []),
    )

    command_result["status"] = CommandStatus.EXECUTED.value
    command_result["aggregate_id"] = order_id
    state["command_result"] = command_result
    state["order_id"] = order_id
    state["created_at"] = datetime.now(timezone.utc)
    _mark_stage(state, "verification", detail="Verify purchase-order creation")
    _mark_stage(state, "closure", detail="Workflow closed after verified execution")
    logger.info("Purchase order created successfully: %s", order_id)
    return state


def build_bestellvorschlag_workflow():
    """Build the Bestellvorschlag workflow graph using LangGraph."""

    workflow = StateGraph(BestellvorschlagState)
    workflow.add_node("analyze_stock", analyze_stock_levels)
    workflow.add_node("check_history", check_sales_history)
    workflow.add_node("generate_proposal", generate_order_proposal)
    workflow.add_node("wait_approval", wait_for_human_approval)
    workflow.add_node("create_order", create_purchase_order)

    workflow.set_entry_point("analyze_stock")
    workflow.add_edge("analyze_stock", "check_history")
    workflow.add_edge("check_history", "generate_proposal")

    def next_after_proposal(state: BestellvorschlagState) -> str:
        requirement = state.get("approval_requirement") or {}
        if requirement.get("requires_human_approval"):
            return "wait_approval"
        return "create_order"

    workflow.add_conditional_edges(
        "generate_proposal",
        next_after_proposal,
        {
            "wait_approval": "wait_approval",
            "create_order": "create_order",
        },
    )

    def after_approval(state: BestellvorschlagState) -> str:
        return "create_order" if state.get("approved") else END

    workflow.add_conditional_edges(
        "wait_approval",
        after_approval,
        {
            "create_order": "create_order",
            END: END,
        },
    )
    workflow.add_edge("create_order", END)

    import sqlite3
    from pathlib import Path

    from langgraph.checkpoint.sqlite import SqliteSaver

    database_path = Path("data/bestellvorschlag_workflows.db")
    database_path.parent.mkdir(parents=True, exist_ok=True)
    checkpointer = SqliteSaver(
        sqlite3.connect(database_path, check_same_thread=False)
    )
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["wait_approval"],
    )


async def run_bestellvorschlag_workflow(tenant_id: str, correlation_id: str) -> BestellvorschlagState:
    """Execute Bestellvorschlag workflow using LangGraph."""

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
        "approval_requirement": None,
        "approval_record": None,
        "gate_decisions": [],
        "approved": False,
        "rejection_reason": None,
        "command_result": None,
        "order_id": None,
        "created_at": None,
        "current_stage_key": "intake",
        "stage_transition_log": [
            {
                "stage_key": "intake",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detail": "Workflow run created",
            }
        ],
    }
    result = await workflow.ainvoke(
        initial_state,
        {"configurable": {"thread_id": correlation_id}},
    )
    logger.info("Bestellvorschlag workflow reached state for correlation_id=%s", correlation_id)
    return result
