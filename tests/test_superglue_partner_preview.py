import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.edi_adapter import SupergluePartnerPreviewAdapter
from app.integrations.services.superglue_connector_registry import build_superglue_connector_binding


def test_superglue_partner_preview_adapter_maps_preview(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/tools/tenant-a.sg.partner.adapter.preview/run"
        payload = __import__("json").loads(request.content.decode("utf-8"))
        assert payload["inputs"]["credentials"] == {"apiKey": "edi-key"}
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "data": {
                    "data": {
                        "title": "Legacy EDI Preview",
                        "mapped_steps": ["extract", "map", "preview"],
                        "notices": ["read-only"],
                        "metadata": {"partner": "legacy-a"},
                    }
                },
            },
        )

    binding = build_superglue_connector_binding(tenant_id="tenant-a", connector_key="partner_edi")
    binding.run_credentials["apiKey"] = "edi-key"
    monkeypatch.setattr(
        "app.integrations.adapters.superglue.edi_adapter.build_superglue_connector_binding",
        lambda tenant_id, connector_key: binding,
    )
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(handler),
    )
    adapter = SupergluePartnerPreviewAdapter(client=client)

    result = adapter.preview_partner_mapping(
        tenant_id="tenant-a",
        partner_key="legacy-a",
        sample_payload={"document_type": "ORDERS"},
    )

    assert result.partner_key == "legacy-a"
    assert result.mapped_steps == ["extract", "map", "preview"]
    assert result.metadata["partner"] == "legacy-a"
