import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.services.superglue_execution_service import SuperglueExecutionService


def test_superglue_execution_service_rejects_unknown_tool():
    service = SuperglueExecutionService(
        client=SuperglueClient(
            base_url="https://api.superglue.dev",
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True})),
        )
    )

    result = service.execute_tool(
        tenant_id="tenant-a",
        correlation_id="corr-1",
        tool_id="sg.unknown",
        execution_mode="read",
        target_kind="document",
        payload={},
    )

    assert result.result_status == "error"
    assert result.errors
    assert "Unbekanntes Superglue-Tool" in result.errors[0].message


def test_superglue_execution_service_rejects_invalid_mode():
    service = SuperglueExecutionService(
        client=SuperglueClient(
            base_url="https://api.superglue.dev",
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True})),
        )
    )

    result = service.execute_tool(
        tenant_id="tenant-a",
        correlation_id="corr-2",
        tool_id="sg.document.metadata",
        execution_mode="execute",
        target_kind="document",
        payload={},
    )

    assert result.result_status == "error"
    assert result.errors
    assert "nicht erlaubt" in result.errors[0].message


def test_superglue_execution_service_requires_human_confirmation_for_execute(monkeypatch):
    monkeypatch.setattr(
        "app.integrations.services.superglue_execution_service.settings.SUPERGLUE_EXECUTION_ENABLED",
        True,
    )
    service = SuperglueExecutionService(
        client=SuperglueClient(
            base_url="https://api.superglue.dev",
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True})),
        )
    )

    result = service.execute_tool(
        tenant_id="tenant-a",
        correlation_id="corr-3",
        tool_id="tenant-a.sg.finance.export.bundle",
        execution_mode="execute",
        target_kind="external_api",
        payload={"idempotency_key": "exp-1"},
    )

    assert result.result_status == "error"
    assert "human_confirmation" in result.errors[0].message
