import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.customer_profile_adapter import SuperglueCustomerProfileAdapter


def test_superglue_customer_profile_adapter_maps_preview():
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "status": "completed",
                    "data": {
                        "customer_id": "cust-7",
                        "display_name": "Musterkunde Nord",
                        "status": "active",
                        "email": "nord@example.test",
                        "city": "Bremen",
                        "tags": ["crm", "preview"],
                        "metadata": {"source": "legacy-crm"},
                    },
                },
            )
        ),
    )
    adapter = SuperglueCustomerProfileAdapter(client=client)

    result = adapter.preview_customer_profile(tenant_id="tenant-a", customer_id="cust-7")

    assert result.customer_id == "cust-7"
    assert result.display_name == "Musterkunde Nord"
    assert result.city == "Bremen"
    assert result.metadata["source"] == "legacy-crm"
