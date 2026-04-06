import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.customer_profile_adapter import SuperglueCustomerProfileAdapter
from app.integrations.services.superglue_connector_registry import build_superglue_connector_binding


def test_superglue_customer_profile_adapter_maps_preview(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/tools/tenant-a.sg.customer.profile.preview/run"
        payload = __import__("json").loads(request.content.decode("utf-8"))
        assert payload["inputs"]["credentials"] == {"accessToken": "crm-token"}
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "data": {
                    "data": {
                        "customer_id": "cust-7",
                        "display_name": "Musterkunde Nord",
                        "status": "active",
                        "external_id": "crm-77",
                        "email": "nord@example.test",
                        "phone": "+49-123",
                        "city": "Bremen",
                        "country": "DE",
                        "tags": ["crm", "preview"],
                        "metadata": {"source": "legacy-crm"},
                    }
                },
            },
        )

    binding = build_superglue_connector_binding(tenant_id="tenant-a", connector_key="customer_profile")
    binding.run_credentials["accessToken"] = "crm-token"
    monkeypatch.setattr(
        "app.integrations.adapters.superglue.customer_profile_adapter.build_superglue_connector_binding",
        lambda tenant_id, connector_key: binding,
    )
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(handler),
    )
    adapter = SuperglueCustomerProfileAdapter(client=client)

    result = adapter.get_customer_profile(tenant_id="tenant-a", customer_id="cust-7")

    assert result.customer_id == "cust-7"
    assert result.display_name == "Musterkunde Nord"
    assert result.external_id == "crm-77"
    assert result.phone == "+49-123"
    assert result.city == "Bremen"
    assert result.country == "DE"
    assert result.metadata["source"] == "legacy-crm"
