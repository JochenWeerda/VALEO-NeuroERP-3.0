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
            "GET",
            f"/api/customers/{customer_id}/profile-preview",
            mode="rest",
            params={"tenant_id": tenant_id},
        )
        return CustomerProfilePreview(
            customer_id=str(payload.get("customer_id", customer_id)),
            display_name=str(payload.get("display_name") or payload.get("name") or customer_id),
            status=str(payload.get("status", "active")),
            email=str(payload["email"]) if payload.get("email") else None,
            city=str(payload["city"]) if payload.get("city") else None,
            tags=[str(item) for item in payload.get("tags", [])],
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata", {})).items()},
        )
