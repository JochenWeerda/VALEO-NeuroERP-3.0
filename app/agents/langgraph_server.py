"""
LangGraph Server
Real workflow execution with state persistence and checkpoints
"""

import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .workflows.bestellvorschlag import (
    BestellvorschlagState,
    analyze_stock_levels,
    check_sales_history,
    generate_order_proposal,
    wait_for_human_approval,
    create_purchase_order,
    run_bestellvorschlag_workflow
)

logger = logging.getLogger(__name__)


def build_bestellvorschlag_graph() -> StateGraph:
    """
    Build the Bestellvorschlag workflow as LangGraph.
    
    Returns:
        Compiled workflow with SQLite checkpointer
    """
    workflow = StateGraph(BestellvorschlagState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_stock_levels)
    workflow.add_node("history", check_sales_history)
    workflow.add_node("proposal", generate_order_proposal)
    workflow.add_node("approval", wait_for_human_approval)
    workflow.add_node("create_order", create_purchase_order)
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    # Add edges
    workflow.add_edge("analyze", "history")
    workflow.add_edge("history", "proposal")
    workflow.add_edge("proposal", "approval")
    
    # Conditional edge from approval
    def should_create_order(state: BestellvorschlagState) -> Literal["create_order", "__end__"]:
        """Decide if order should be created based on approval."""
        if state.get("approved"):
            return "create_order"
        return "__end__"
    
    workflow.add_conditional_edges(
        "approval",
        should_create_order,
        {
            "create_order": "create_order",
            "__end__": END
        }
    )
    
    workflow.add_edge("create_order", END)
    
    # Compile with checkpointer and interrupt before approval
    checkpointer = SqliteSaver.from_conn_string("data/workflows.db")
    
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["approval"]  # Human-in-the-Loop checkpoint
    )
    
    logger.info("Bestellvorschlag workflow compiled with LangGraph")
    return app


# Global workflow instance
_bestellvorschlag_workflow = None


def get_bestellvorschlag_workflow():
    """Get the global Bestellvorschlag workflow instance."""
    global _bestellvorschlag_workflow
    if _bestellvorschlag_workflow is None:
        _bestellvorschlag_workflow = build_bestellvorschlag_graph()
    return _bestellvorschlag_workflow


async def invoke_bestellvorschlag(tenant_id: str, correlation_id: str) -> BestellvorschlagState:
    """
    Invoke Bestellvorschlag workflow using the new LangGraph implementation.

    Returns state at checkpoint (before approval).
    """
    # Use the new LangGraph-based workflow
    result = await run_bestellvorschlag_workflow(tenant_id, correlation_id)

    logger.info(f"Bestellvorschlag workflow paused at approval checkpoint: {correlation_id}")
    return result


async def resume_bestellvorschlag(
    workflow_id: str, 
    approved: bool, 
    rejection_reason: str | None = None
) -> BestellvorschlagState:
    """
    Resume Bestellvorschlag workflow after approval/rejection.
    """
    workflow = get_bestellvorschlag_workflow()
    
    config = {"configurable": {"thread_id": workflow_id}}
    
    # Get current state from checkpoint
    state = await workflow.aget_state(config)
    
    if state is None:
        raise ValueError(f"Workflow {workflow_id} not found")
    
    # Update state with approval decision
    state.values["approved"] = approved
    if rejection_reason:
        state.values["rejection_reason"] = rejection_reason
    
    # Resume from checkpoint
    result = await workflow.ainvoke(None, config)
    
    logger.info(f"Workflow {workflow_id} resumed: approved={approved}")
    return result

