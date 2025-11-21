from __future__ import annotations

from typing import AsyncGenerator

import httpx
import pytest

from app.workflow.registration import register_intrastat_workflow

WORKFLOW_BASE_URL = "http://workflow-service"  # wird via monkeypatch gesetzt


@pytest.fixture
async def mock_workflow(monkeypatch) -> AsyncGenerator[None, None]:
    original_post = httpx.AsyncClient.post

    async def fake_post(self, url: str, json: dict, timeout: float | None = None, **kwargs):  # type: ignore[override]
        assert url.endswith("/api/v1/workflows/definitions")
        definition = json
        assert definition["name"] == "intrastat_monthly_cycle"
        assert any(transition["event_type"] == "intrastat.submission.failed" for transition in definition["transitions"])
        return httpx.Response(status_code=201)

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    try:
        yield
    finally:
        monkeypatch.setattr(httpx.AsyncClient, "post", original_post)


@pytest.mark.asyncio
async def test_register_intrastat_workflow_contract(monkeypatch, mock_workflow) -> None:
    monkeypatch.setattr("app.workflow.registration.settings.WORKFLOW_SERVICE_URL", WORKFLOW_BASE_URL)
    await register_intrastat_workflow()
