"""Integration-style Unit-Tests: GDPR module_export (httpx gemockt)."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.services import module_export


class _FakeResponse:
    status_code = 200

    def __init__(self, url: str, headers: dict | None) -> None:
        self._payload = {"mock": True, "url": url, "headers": headers or {}}

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


class FakeAsyncClient:
    def __init__(self, *_, **__) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        pass

    async def get(self, url: str, headers=None):  # noqa: ANN001
        return _FakeResponse(url, headers)


@pytest.fixture(autouse=True)
def patch_async_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(module_export.httpx, "AsyncClient", FakeAsyncClient)


@pytest.mark.asyncio
async def test_collect_skips_core_when_base_unconfigured(monkeypatch: pytest.MonkeyPatch):
    from app.config.settings import settings

    monkeypatch.setattr(settings, "CRM_CORE_BASE_URL", "")

    contact_id = uuid4()
    out = await module_export.collect_contact_modules(
        tenant_id="t-1",
        contact_id=contact_id,
        data_areas=["contacts"],
    )
    mod = out["modules"]["crm_core_contact"]
    assert mod["skipped"] is True
    assert "not configured" in mod["reason"].lower()


@pytest.mark.asyncio
async def test_collect_all_hits_configured_bases(monkeypatch: pytest.MonkeyPatch):
    from app.config.settings import settings

    monkeypatch.setattr(settings, "CRM_CORE_BASE_URL", "http://core.test/api/v1")
    monkeypatch.setattr(settings, "CRM_SALES_BASE_URL", "http://sales.test/api/v1")
    monkeypatch.setattr(settings, "CRM_CONSENT_BASE_URL", "http://consent.test/api/v1")
    monkeypatch.setattr(settings, "CRM_MARKETING_BASE_URL", "http://mkt.test/api/v1")
    monkeypatch.setattr(settings, "INTERNAL_SERVICE_TOKEN", "secret")

    contact_id = uuid4()
    out = await module_export.collect_contact_modules(
        tenant_id="t-1",
        contact_id=contact_id,
        data_areas=["all"],
    )
    modules = out["modules"]
    assert modules["crm_core_contact"]["url"].startswith("http://core.test")
    assert modules["crm_sales_opportunities"]["mock"] is True
    assert "Bearer secret" in modules["crm_consent"]["headers"]["Authorization"]
