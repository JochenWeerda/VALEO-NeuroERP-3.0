"""Read-only customer profile preview adapter backed by Superglue."""

from __future__ import annotations

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.ports.customer_profile_port import CustomerProfilePort, CustomerProfilePreview
from app.integrations.services.superglue_connector_registry import build_superglue_connector_binding
from app.integrations.services.superglue_execution_service import normalize_superglue_run_result
from app.integrations.services.superglue_secret_resolver import resolve_superglue_auth_token


class SuperglueCustomerProfileAdapter(CustomerProfilePort):
    def __init__(self, client: SuperglueClient | None = None) -> None:
        self._client = client

    def get_customer_profile(self, *, tenant_id: str, customer_id: str) -> CustomerProfilePreview:
        client = self._client or SuperglueClient(auth_token=resolve_superglue_auth_token(tenant_id))
        binding = build_superglue_connector_binding(tenant_id=tenant_id, connector_key="customer_profile")
        payload = client.request(
            "POST",
            f"/v1/tools/{binding.tool_id}/run",
            mode="rest",
            json={
                "inputs": {
                    "tenantId": tenant_id,
                    "customerId": customer_id,
                    "credentials": binding.run_credentials,
                }
            },
        )
        run_data = normalize_superglue_run_result(payload)["result"]
        if not isinstance(run_data, dict):
            run_data = {}
        return CustomerProfilePreview(
            customer_id=str(run_data.get("customer_id", customer_id)),
            display_name=str(run_data.get("display_name") or run_data.get("name") or customer_id),
            status=str(run_data.get("status", "active")),
            external_id=str(run_data["external_id"]) if run_data.get("external_id") else None,
            email=str(run_data["email"]) if run_data.get("email") else None,
            phone=str(run_data["phone"]) if run_data.get("phone") else None,
            city=str(run_data["city"]) if run_data.get("city") else None,
            country=str(run_data["country"]) if run_data.get("country") else None,
            tags=[str(item) for item in run_data.get("tags", [])],
            metadata={str(k): str(v) for k, v in dict(run_data.get("metadata", {})).items()},
        )

    def preview_customer_profile(self, *, tenant_id: str, customer_id: str) -> CustomerProfilePreview:
        return self.get_customer_profile(tenant_id=tenant_id, customer_id=customer_id)
