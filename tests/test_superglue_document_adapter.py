import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.document_adapter import SuperglueDocumentAdapter
from app.integrations.services.superglue_connector_registry import build_superglue_connector_binding


def test_superglue_document_adapter_maps_documents(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/tools/tenant-a.sg.document.search/run"
        payload = __import__("json").loads(request.content.decode("utf-8"))
        assert payload["inputs"]["credentials"] == {"apiKey": "doc-key"}
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "data": {
                    "data": {
                        "documents": [
                            {
                                "id": "doc-1",
                                "title": "Contract 4711",
                                "source_system": "sharepoint",
                                "mime_type": "application/pdf",
                                "url": "https://documents.example/doc-1",
                                "tags": ["contract"],
                                "metadata": {"contract_no": "4711"},
                            }
                        ]
                    }
                },
            },
        )

    binding = build_superglue_connector_binding(tenant_id="tenant-a", connector_key="document_search")
    binding.run_credentials["apiKey"] = "doc-key"
    monkeypatch.setattr(
        "app.integrations.adapters.superglue.document_adapter.build_superglue_connector_binding",
        lambda tenant_id, connector_key: binding,
    )
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(handler),
    )
    adapter = SuperglueDocumentAdapter(client=client)

    results = adapter.search_documents(tenant_id="tenant-a", query="4711")

    assert len(results) == 1
    assert results[0].document_id == "doc-1"
    assert results[0].metadata["contract_no"] == "4711"
