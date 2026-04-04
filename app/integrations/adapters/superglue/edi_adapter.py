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
            "/api/partner-adapters/preview",
            mode="rest",
            json={"tenant_id": tenant_id, "partner_key": partner_key, "sample_payload": sample_payload or {}},
        )
        return PartnerPreview(
            partner_key=partner_key,
            title=str(payload.get("title", partner_key)),
            mapped_steps=list(payload.get("mapped_steps", [])),
            notices=list(payload.get("notices", [])),
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata", {})).items()},
        )
