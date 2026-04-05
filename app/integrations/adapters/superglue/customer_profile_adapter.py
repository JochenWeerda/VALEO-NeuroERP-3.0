"""Read-only customer profile preview adapter backed by Superglue."""

from __future__ import annotations

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.ports.customer_profile_port import CustomerProfilePort, CustomerProfilePreview
from app.integrations.services.superglue_secret_resolver import resolve_superglue_auth_token


class SuperglueCustomerProfileAdapter(CustomerProfilePort):
    def __init__(self, client: SuperglueClient | None = None) -> None:
        self._client = client

    def preview_customer_profile(self, *, tenant_id: str, customer_id: str) -> CustomerProfilePreview:
        client = self._client or SuperglueClient(auth_token=resolve_superglue_auth_token(tenant_id))
        payload = client.request(
            "POST",
            "/v1/tools/sg.customer.profile.preview/run",
            mode="rest",
            json={"inputs": {"tenantId": tenant_id, "customerId": customer_id}},
        )
        run_data = payload.get("data", {})
        return CustomerProfilePreview(
            customer_id=str(run_data.get("customer_id", customer_id)),
            display_name=str(run_data.get("display_name") or run_data.get("name") or customer_id),
            status=str(run_data.get("status", "active")),
            email=str(run_data["email"]) if run_data.get("email") else None,
            city=str(run_data["city"]) if run_data.get("city") else None,
            tags=[str(item) for item in run_data.get("tags", [])],
            metadata={str(k): str(v) for k, v in dict(run_data.get("metadata", {})).items()},
        )
