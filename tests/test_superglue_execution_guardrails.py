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
