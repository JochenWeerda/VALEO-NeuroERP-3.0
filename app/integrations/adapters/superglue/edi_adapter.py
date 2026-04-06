"""Read-only partner/legacy preview adapter backed by Superglue."""

from __future__ import annotations

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.ports.partner_adapter_port import PartnerAdapterPort, PartnerPreview
from app.integrations.services.superglue_connector_registry import build_superglue_connector_binding
from app.integrations.services.superglue_execution_service import normalize_superglue_run_result
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
        binding = build_superglue_connector_binding(tenant_id=tenant_id, connector_key="partner_edi")
        payload = client.request(
            "POST",
            f"/v1/tools/{binding.tool_id}/run",
            mode="rest",
            json={
                "inputs": {
                    "tenantId": tenant_id,
                    "partnerKey": partner_key,
                    "samplePayload": sample_payload or {},
                    "credentials": binding.run_credentials,
                }
            },
        )
        run_data = normalize_superglue_run_result(payload)["result"]
        if not isinstance(run_data, dict):
            run_data = {}
        return PartnerPreview(
            partner_key=partner_key,
            title=str(run_data.get("title", partner_key)),
            mapped_steps=list(run_data.get("mapped_steps", [])),
            notices=list(run_data.get("notices", [])),
            metadata={str(k): str(v) for k, v in dict(run_data.get("metadata", {})).items()},
        )
