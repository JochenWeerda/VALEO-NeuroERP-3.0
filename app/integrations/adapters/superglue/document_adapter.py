"""Pilot document adapter backed by Superglue."""

from __future__ import annotations

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.ports.document_port import DocumentMetadata, DocumentPort
from app.integrations.services.superglue_connector_registry import build_superglue_connector_binding
from app.integrations.services.superglue_execution_service import normalize_superglue_run_result
from app.integrations.services.superglue_secret_resolver import resolve_superglue_auth_token


class SuperglueDocumentAdapter(DocumentPort):
    def __init__(self, client: SuperglueClient | None = None) -> None:
        self._client = client

    def search_documents(self, *, tenant_id: str, query: str, limit: int = 10) -> list[DocumentMetadata]:
        client = self._client or SuperglueClient(auth_token=resolve_superglue_auth_token(tenant_id))
        binding = build_superglue_connector_binding(tenant_id=tenant_id, connector_key="document_search")
        payload = client.request(
            "POST",
            f"/v1/tools/{binding.tool_id}/run",
            mode="rest",
            json={
                "inputs": {
                    "tenantId": tenant_id,
                    "query": query,
                    "limit": limit,
                    "credentials": binding.run_credentials,
                }
            },
        )
        run_data = normalize_superglue_run_result(payload)["result"]
        if not isinstance(run_data, dict):
            run_data = {"documents": run_data if isinstance(run_data, list) else []}
        items = run_data.get("documents") or run_data.get("items") or []
        return [
            DocumentMetadata(
                document_id=str(item["id"]),
                title=str(item.get("title") or item["id"]),
                source_system=str(item.get("source_system", "superglue")),
                mime_type=str(item.get("mime_type", "application/octet-stream")),
                url=str(item.get("url", "")),
                tags=list(item.get("tags", [])),
                metadata={str(k): str(v) for k, v in dict(item.get("metadata", {})).items()},
            )
            for item in items
        ]
