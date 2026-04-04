import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.edi_adapter import SupergluePartnerPreviewAdapter


def test_superglue_partner_preview_adapter_maps_preview():
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "title": "Legacy EDI Preview",
                    "mapped_steps": ["extract", "map", "preview"],
                    "notices": ["read-only"],
                    "metadata": {"partner": "legacy-a"},
                },
            )
        ),
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
