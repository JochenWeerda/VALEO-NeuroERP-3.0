"""Pilot document adapter backed by Superglue."""

from __future__ import annotations

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.ports.document_port import DocumentMetadata, DocumentPort
from app.integrations.services.superglue_secret_resolver import resolve_superglue_auth_token


class SuperglueDocumentAdapter(DocumentPort):
    def __init__(self, client: SuperglueClient | None = None) -> None:
        self._client = client

    def search_documents(self, *, tenant_id: str, query: str, limit: int = 10) -> list[DocumentMetadata]:
        client = self._client or SuperglueClient(auth_token=resolve_superglue_auth_token(tenant_id))
        payload = client.request(
            "POST",
            "/v1/tools/sg.document.search/run",
            mode="rest",
            json={"inputs": {"tenantId": tenant_id, "query": query, "limit": limit}},
        )
        run_data = payload.get("data", {})
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
