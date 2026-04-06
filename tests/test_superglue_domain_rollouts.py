import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.services.superglue_domain_rollouts import (
    build_superglue_domain_rollout_summary,
    preview_superglue_domain_rollout,
)
from app.integrations.services.superglue_execution_service import SuperglueExecutionService


def test_superglue_domain_rollout_summary_surfaces_rollout_domains():
    summary = build_superglue_domain_rollout_summary("tenant-a")

    assert summary["tenant_id"] == "tenant-a"
    assert summary["domain_count"] >= 6
    assert any(domain["domain_key"] == "finance" for domain in summary["domains"])


def test_superglue_domain_rollout_preview_executes_domain_connector(monkeypatch):
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "runId": "run-preview",
                    "status": "success",
                    "data": {
                        "data": {
                            "export": {
                                "id": "exp-1",
                                "artifacts": [
                                    {"id": "artifact-1", "name": "bundle.csv", "url": "https://example.test/bundle.csv"}
                                ],
                            }
                        }
                    },
                },
            )
        ),
    )
    monkeypatch.setattr(
        "app.integrations.services.superglue_execution_service.resolve_superglue_auth_token",
        lambda tenant_id: "tenant-token",
    )
    preview = preview_superglue_domain_rollout(
        tenant_id="tenant-a",
        domain_key="finance",
        parameters={"human_confirmation": False},
        execution_service=SuperglueExecutionService(client=client),
    )

    assert preview["domain_key"] == "finance"
    assert preview["preview_count"] == 1
    assert preview["previews"][0]["artifacts"][0]["uri"] == "https://example.test/bundle.csv"
