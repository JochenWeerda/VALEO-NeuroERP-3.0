"""Workflow delivery and optimization history without DB, network or LLM."""
import asyncio
from types import SimpleNamespace

import pytest

from app.core.sse import SSEHub
from app.routers import workflow_router as routes
from app.agents.workflows.system_optimizer import SystemOptimizerAgent


class Repository:
    def __init__(self):
        self.state = "draft"
        self.audits = []

    def get_status_with_version(self, domain, number):
        return self.state, "v1"

    def set_status(self, domain, number, state, **kwargs):
        self.state = state

    def add_audit(self, domain, number, previous, state, action, **kwargs):
        self.audits.append(SimpleNamespace(
            ts=123, from_state=previous, to_state=state, action=action,
            user=kwargs["user"], reason=kwargs["reason"],
        ))

    def get_audit(self, domain, number):
        return self.audits


@pytest.fixture(autouse=True)
def forbid_database(monkeypatch):
    from sqlalchemy.engine import Engine
    from app.core.tenant_context import set_current_tenant_id, reset_current_tenant_id
    def forbidden(*args, **kwargs):
        raise AssertionError("This contract must not open a database connection")
    monkeypatch.setattr(Engine, "connect", forbidden)
    context = set_current_tenant_id("system")
    try:
        yield
    finally:
        reset_current_tenant_id(context)


@pytest.mark.parametrize("operation", ["transition", "audit"])
def test_sse_is_delivered_before_success(monkeypatch, operation):
    hub = SSEHub()
    monkeypatch.setattr(routes, "sse_hub", hub)
    monkeypatch.setattr(routes.workflow, "next", lambda *args, **kwargs: (True, "submitted", "ok"))
    repo = Repository()
    async def scenario():
        queue = await hub.subscribe("workflow", tenant_id="system")
        if operation == "transition":
            result = await routes.do_transition("sales", "contract-probe", "submit", {"reason": "probe"}, repo)
            assert result == {"ok": True, "state": "submitted"}
            event = queue.get_nowait()
            assert event["fromState"] == "draft" and event["toState"] == "submitted"
            assert repo.audits[0].reason == "probe"
        else:
            result = await routes.audit("sales", "contract-probe", repo)
            assert result == {"ok": True, "items": []}
            event = queue.get_nowait()
            assert event["type"] == "audit_access" and event["count"] == 0
        assert event["number"] == "contract-probe"
        assert event["domain"] == "sales"
        await hub.unsubscribe("workflow", queue, tenant_id="system")
    asyncio.run(scenario())


@pytest.mark.parametrize("operation", ["transition", "audit"])
def test_notification_failure_does_not_invalidate_success(monkeypatch, caplog, operation):
    async def failed_broadcast(*args, **kwargs):
        raise RuntimeError("private subscriber data")
    monkeypatch.setattr(routes, "sse_hub", SimpleNamespace(broadcast=failed_broadcast))
    monkeypatch.setattr(routes.workflow, "next", lambda *args, **kwargs: (True, "submitted", "ok"))
    repo = Repository()
    if operation == "transition":
        result = asyncio.run(routes.do_transition("sales", "contract-probe", "submit", {}, repo))
        assert repo.state == "submitted" and len(repo.audits) == 1
    else:
        result = asyncio.run(routes.audit("sales", "contract-probe", repo))
    assert result["ok"] is True
    assert "notification delivery failed" in caplog.text
    assert "private subscriber data" not in caplog.text


def test_invalid_transition_never_publishes(monkeypatch):
    from fastapi import HTTPException
    hub = SSEHub()
    monkeypatch.setattr(routes, "sse_hub", hub)
    monkeypatch.setattr(routes.workflow, "next", lambda *args, **kwargs: (False, "draft", "blocked"))
    repo = Repository()
    async def scenario():
        queue = await hub.subscribe("workflow", tenant_id="system")
        with pytest.raises(HTTPException) as error:
            await routes.do_transition("sales", "contract-probe", "submit", {}, repo)
        assert error.value.status_code == 400
        assert queue.empty() and repo.state == "draft" and repo.audits == []
        await hub.unsubscribe("workflow", queue, tenant_id="system")
    asyncio.run(scenario())


@pytest.mark.parametrize("limit,expected", [(100, [1, 2, 3]), (2, [2, 3]), (1, [3]), (0, [])])
def test_optimizer_history_is_callable_and_bounded(limit, expected):
    agent = SystemOptimizerAgent()
    agent.optimization_history = [{"action_taken": i} for i in [1, 2, 3]]
    result = agent.get_optimization_history(limit)
    assert [row["action_taken"] for row in result] == expected
    result.clear()
    assert len(agent.optimization_history) == 3


def test_optimizer_rejects_negative_history_limit():
    with pytest.raises(ValueError):
        SystemOptimizerAgent().get_optimization_history(-1)
