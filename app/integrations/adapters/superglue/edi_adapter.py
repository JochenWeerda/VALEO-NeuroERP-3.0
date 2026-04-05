"""Read-only partner/legacy preview adapter backed by Superglue."""

from __future__ import annotations

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.ports.partner_adapter_port import PartnerAdapterPort, PartnerPreview
from app.integrations.services.superglue_secret_resolver import resolve_superglue_auth_token


class SupergluePartnerPreviewAdapter(PartnerAdapterPort):
    def __init__(self, client: SuperglueClient | None = None) -> None:
        self._client = client

    def preview_partner_mapping(
        self,
        *,
        tenant_id: str,
        partner_key: str,
        sample_payload: dict[str, str] | None = None,
    ) -> PartnerPreview:
        client = self._client or SuperglueClient(auth_token=resolve_superglue_auth_token(tenant_id))
        payload = client.request(
            "POST",
            "/v1/tools/sg.partner.adapter.preview/run",
            mode="rest",
            json={
                "inputs": {
                    "tenantId": tenant_id,
                    "partnerKey": partner_key,
                    "samplePayload": sample_payload or {},
                }
            },
        )
        run_data = payload.get("data", {})
        return PartnerPreview(
            partner_key=partner_key,
            title=str(run_data.get("title", partner_key)),
            mapped_steps=list(run_data.get("mapped_steps", [])),
            notices=list(run_data.get("notices", [])),
            metadata={str(k): str(v) for k, v in dict(run_data.get("metadata", {})).items()},
        )
