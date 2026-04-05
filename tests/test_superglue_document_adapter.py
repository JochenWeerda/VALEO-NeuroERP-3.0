import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.document_adapter import SuperglueDocumentAdapter


def test_superglue_document_adapter_maps_documents():
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "status": "completed",
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
                    },
                },
            )
        ),
    )
    adapter = SuperglueDocumentAdapter(client=client)

    results = adapter.search_documents(tenant_id="tenant-a", query="4711")

    assert len(results) == 1
    assert results[0].document_id == "doc-1"
    assert results[0].metadata["contract_no"] == "4711"
