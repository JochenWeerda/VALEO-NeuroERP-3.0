from __future__ import annotations

import asyncio

import pytest
from langchain_core.messages import HumanMessage

from app.agents.workflows import bestellvorschlag as workflow


class _DummyArticle:
    def __init__(
        self,
        *,
        article_id: str,
        supplier_id: str | None,
        purchase_price: float = 12.5,
        unit: str = "kg",
        name: str = "Mais",
        article_number: str = "ART-1",
    ) -> None:
        self.id = article_id
        self.supplier_id = supplier_id
        self.purchase_price = purchase_price
        self.unit = unit
        self.name = name
        self.article_number = article_number


class _DummyArticleRepository:
    def __init__(self, article: _DummyArticle | None) -> None:
        self._article = article

    async def get_by_id(self, article_id: str, tenant_id: str):
        return self._article


def _base_state() -> workflow.BestellvorschlagState:
    return {
        "messages": [HumanMessage(content="Generate purchase order proposal")],
        "correlation_id": "corr-1",
        "tenant_id": "tenant-1",
        "low_stock_articles": [],
        "sales_history": [],
        "supplier_recommendations": [],
        "ai_insights": {},
        "ai_recommendations": [],
        "proposal": None,
        "approval_requirement": None,
        "approval_record": None,
        "approved": False,
        "rejection_reason": None,
        "command_result": None,
        "order_id": None,
        "created_at": None,
    }


def test_generate_order_proposal_sets_human_approval_for_high_value():
    state = _base_state()
    state["low_stock_articles"] = [
        {
            "article_id": "A-1",
            "name": "Mais",
            "current": 10.0,
            "min": 500.0,
            "shortage": 490.0,
            "unit": "kg",
        }
    ]
    state["sales_history"] = [
        {
            "article_id": "A-1",
            "avg_monthly_sales": 200.0,
            "trend": "increasing",
            "total_movements": 12,
        }
    ]

    result = asyncio.run(workflow.generate_order_proposal(state))

    assert result["approval_requirement"]["aktions_typ"] == "BESTELLUNG_ANLEGEN"
    assert result["approval_requirement"]["requires_human_approval"] is True
    assert result["approved"] is False


def test_wait_for_human_approval_requires_explicit_decision():
    state = _base_state()
    state["approval_requirement"] = {"requires_human_approval": True}

    with pytest.raises(workflow.BestellvorschlagWorkflowError, match="Human approval decision missing"):
        asyncio.run(workflow.wait_for_human_approval(state))


def test_create_purchase_order_rejects_missing_supplier_contract(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        workflow.container,
        "resolve",
        lambda cls: _DummyArticleRepository(_DummyArticle(article_id="A-1", supplier_id=None)),
    )
    state = _base_state()
    state["approved"] = True
    state["proposal"] = {
        "created_at": "2026-03-16T00:00:00+00:00",
        "items": [{"article_id": "A-1", "article_name": "Mais", "order_quantity": 10.0}],
        "total_estimated_cost": 500.0,
    }

    with pytest.raises(workflow.BestellvorschlagWorkflowError, match="no resolvable supplier contract"):
        asyncio.run(workflow.create_purchase_order(state))


def test_create_purchase_order_dispatches_and_persists_via_contracts(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        workflow.container,
        "resolve",
        lambda cls: _DummyArticleRepository(_DummyArticle(article_id="A-1", supplier_id="SUP-1")),
    )

    captured: dict[str, object] = {}

    def _fake_persist(**kwargs):
        captured.update(kwargs)
        return "PO-1"

    monkeypatch.setattr(workflow, "_persist_purchase_order", _fake_persist)

    state = _base_state()
    state["approved"] = True
    state["approval_requirement"] = {
        "aktions_typ": "BESTELLUNG_ANLEGEN",
        "requires_human_approval": False,
    }
    state["proposal"] = {
        "created_at": "2026-03-16T00:00:00+00:00",
        "items": [{"article_id": "A-1", "article_name": "Mais", "order_quantity": 10.0}],
        "total_estimated_cost": 500.0,
    }

    result = asyncio.run(workflow.create_purchase_order(state))

    assert result["order_id"] == "PO-1"
    assert result["command_result"]["status"] == "executed"
    assert captured["supplier_id"] == "SUP-1"
    assert captured["tenant_id"] == "tenant-1"
